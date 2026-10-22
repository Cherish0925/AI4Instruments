import importlib.util
import json
import socketserver
import struct
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from ai4instruments.iop import Client
from ai4instruments.iop.adapters import Modbus, HTTP
from ai4instruments.iop.config import initialize
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server


class HTTPCase(unittest.TestCase):
    def test_http_description_preserves_parameter_types_and_response(self):
        state={'temperature':298.15}
        class Sensor(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_PUT(self):
                state.update(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                self.do_GET()
            def do_GET(self):
                data=json.dumps(state).encode();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        server=ThreadingHTTPServer(('127.0.0.1',0),Sensor)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        config={'base_url':'http://127.0.0.1:'+str(server.server_port),'operations':{
            'read':{'path':'/temperature','result_path':['temperature'],'unit':'K'},
            'configure':{'method':'PUT','path':'/settings','body':{'interval_s':'${seconds}'}}}}
        driver=HTTP('sensor',config,{})
        try:
            self.assertEqual(driver.invoke('read',{},threading.Event())['value'],298.15)
            response=driver.invoke('configure',{'seconds':2.5},threading.Event())
            self.assertEqual(response['response']['interval_s'],2.5)
        finally:server.shutdown();server.server_close()


@unittest.skipUnless(importlib.util.find_spec('pymodbus'),'Install the devices extra for Modbus communication')
class ModbusCase(unittest.TestCase):
    def test_real_modbus_tcp_read_write_scaling_and_bus_sharing(self):
        registers={0:244};received=[]
        class Instrument(socketserver.StreamRequestHandler):
            def handle(self):
                while True:
                    header=self.rfile.read(7)
                    if not header:return
                    tid,pid,size,unit=struct.unpack('>HHHB',header)
                    pdu=self.rfile.read(size-1);fn=pdu[0];received.append((unit,fn))
                    if fn==3:
                        address,count=struct.unpack('>HH',pdu[1:]);body=bytes([3,count*2])+struct.pack('>'+'H'*count,*[registers.get(address+i,0) for i in range(count)])
                    elif fn==6:
                        address,value=struct.unpack('>HH',pdu[1:]);registers[address]=value;body=pdu
                    else:body=bytes([fn|128,1])
                    self.wfile.write(struct.pack('>HHHB',tid,0,len(body)+1,unit)+body);self.wfile.flush()
        server=socketserver.ThreadingTCPServer(('127.0.0.1',0),Instrument);server.daemon_threads=True
        threading.Thread(target=server.serve_forever,daemon=True).start()
        registry={};config={'host':'127.0.0.1','port':server.server_address[1],'device_id':2,'operations':{
            'temperature':{'function':'read_holding_registers','arguments':{'address':0,'count':1},'scale':0.1,'unit':'degC'},
            'set_temperature':{'function':'write_register','arguments':{'address':1},'scale':0.1,'value_parameter':'celsius'}}}
        a=Modbus('a',config,registry);registry['a']=a;b=Modbus('b',{**config,'device_id':3},registry);registry['b']=b
        try:
            self.assertAlmostEqual(a.invoke('temperature',{},threading.Event())['value'],24.4)
            self.assertTrue(a.invoke('set_temperature',{'celsius':25},threading.Event())['acknowledged'])
            self.assertEqual(registers[1],250)
            b.invoke('read_holding_registers',{'address':1,'count':1},threading.Event())
            self.assertIs(a.connection,b.connection)
            self.assertEqual(received,[(2,3),(2,6),(3,3)])
            self.assertEqual(a.describe()['resources'],b.describe()['resources'])
        finally:a.close();b.close();server.shutdown();server.server_close()


class LaboratoryCase(unittest.TestCase):
    def test_temperature_dosing_weighing_and_acquisition_share_one_runtime(self):
        with tempfile.TemporaryDirectory() as home:
            config=initialize(home,port=0);config['discovery_interval']=0
            engine=Engine(home,config);server=Server(('127.0.0.1',0),engine)
            engine.start();threading.Thread(target=server.serve_forever,daemon=True).start()
            client=Client(engine.endpoint,token=config['token'])
            root=Path(__file__).resolve().parents[2]/'examples/iop/multi-instrument'
            try:
                for record in json.loads((root/'devices.json').read_text()):client.register(record)
                run=client.submit_package(root,resources=['bath','balance','pump','daq','sample'],parameters={'target_mass_g':2.5})
                result=run.result(15)
                self.assertAlmostEqual(result['final_mass_g'],2.5)
                self.assertEqual(result['steps'],3)
                self.assertIn('output/measurements.csv',[f['name'] for f in run.files()])
                ops=run.info()['operation_records']
                self.assertEqual({o['device'] for o in ops},{'bath','balance','pump','daq'})
                self.assertTrue(all(o['state']=='completed' for o in ops))
                self.assertFalse(engine.metrics()['errors'])
            finally:server.shutdown();server.server_close();engine.close()


if __name__=='__main__':unittest.main()
