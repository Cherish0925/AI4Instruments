"""Instrument identity, shared access, saved descriptions and connection changes."""
import copy
import json
import socketserver
import threading
import time
import unittest
from types import SimpleNamespace
import sys
from unittest.mock import patch
from ai4instruments.iop import IOPError
from ai4instruments.iop.discovery import normalize
from ai4instruments.iop.identification import profiles, validate_profile
from ai4instruments.iop.network_discovery import announcement
from . import test_service as fixture


class Instrument(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            command = line.decode().strip()
            self.server.commands.append(command)
            if command == '*IDN?':
                self.server.entered.set()
                self.server.release.wait(4)
                response = self.server.identity
            else:
                response = '1.25'
            if '?' in command:
                self.wfile.write((response+'\n').encode())
                self.wfile.flush()


class IdentificationCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def instrument(self, serial='001'):
        server = socketserver.ThreadingTCPServer(('127.0.0.1',0), Instrument)
        server.daemon_threads = True
        server.identity = 'Stanford_Research_Systems,SR830,'+serial+',1.0'
        server.commands = []
        server.entered, server.release = threading.Event(), threading.Event()
        server.release.set()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server, {'transport':'tcp','address':'127.0.0.1:'+str(server.server_address[1]),
                        'provider':'lxi-network','protocol':'scpi','connection':{'transport':'tcp',
                        'host':'127.0.0.1','port':server.server_address[1],'timeout':1}}

    def scan(self, rows, available=True):
        with patch('ai4instruments.iop.discovery.discover', return_value=normalize({'connections':copy.deepcopy(rows),
             'providers':[{'name':'lxi-network','available':available},{'name':'serial','available':True}]})):
            return self.engine.scan()

    def test_identity_registers_model_operations_and_survives_restart(self):
        server, row = self.instrument()
        result = self.scan([row])
        instrument = next(r for r in result['instruments'] if r.get('identity',{}).get('model'))
        device = instrument['device_id']
        self.assertEqual(instrument['status'],'ready')
        self.assertEqual(server.commands,['*IDN?'])
        self.assertIn('read_x',self.engine.descriptions[device]['operations'])
        self.assertEqual(self.client.submit([{'device':device,'operation':'read_x','id':'x'}]).result(3)['x']['value'],1.25)
        n = len(server.commands)
        self.scan([row]); self.scan([row])
        self.assertEqual(len(server.commands),n)
        self.assertEqual(self.client.schema('instrument-profile')['title'],'IOP Instrument Model Description')
        saved=json.loads((self.engine.home/'config.json').read_text())
        self.assertEqual(next(d for d in saved['devices'] if d['id']==device)['identity']['serial_number'],'001')
        self.assertEqual(self.engine.store.discovery_records()[instrument['key']]['device_id'],device)
        from ai4instruments.iop.engine import Engine
        self.engine.close()
        self.engine=Engine(self.temp.name,saved)
        self.engine.start()
        self.assertIn(device,self.engine.devices)
        self.assertEqual(self.engine.inventory()['instruments'][0]['present'],None)

    def test_registered_identity_uses_scheduler_and_registration_stays_idempotent(self):
        server,row=self.instrument()
        record={'driver':'scpi','config':row['connection']}
        device=self.client.register(record)['id']
        run=self.client.identify(device)
        run.result(3)
        self.assertEqual(self.client.register(record)['id'],device)
        with self.assertRaisesRegex(IOPError,'already registered'):
            self.client.register(dict(record,id=device,config=dict(record['config'],port=1)))
        self.assertIn('read_y',self.engine.descriptions[device]['operations'])

    def test_bare_serial_and_usb_are_not_sent_commands(self):
        rows=[{'transport':'serial','address':'COM7','provider':'serial','manufacturer':'USB bridge'},
              {'transport':'usb','address':'1-2','provider':'usb-inventory','name':'Keyboard'}]
        with patch('ai4instruments.iop.drivers.SCPI.exchange') as exchange:
            result=self.scan(rows)
        exchange.assert_not_called()
        self.assertFalse(result['instruments'][0]['identity'])
        self.assertEqual(result['instruments'][0]['required'],['protocol','communication_parameters'])

    def test_duplicate_endpoint_is_queried_once_and_sdk_driver_is_saved(self):
        server,row=self.instrument()
        alias=dict(row,transport='visa',address='TCPIP0::127.0.0.1::'+str(server.server_address[1])+'::SOCKET')
        result=self.scan([row,alias,{'transport':'sdk','address':'example:serial1','provider':'sdk-example',
             'identity':{'manufacturer':'Example','model':'Virtual','serial_number':'1'},'identity_source':'example-sdk',
             'device':{'id':'sdk-device','driver':'simulated','config':{'kind':'meter'}}}])
        self.assertEqual(server.commands,['*IDN?'])
        self.assertEqual(len([d for d in self.engine.device_records.values() if d['driver']=='scpi']),1)
        self.assertEqual(self.engine.descriptions['sdk-device']['identity']['model'],'Virtual')
        self.scan([row])
        self.assertEqual(server.commands,['*IDN?'])

    def test_parallel_identification_and_manual_registration_share_connection(self):
        server,row=self.instrument(); server.release.clear()
        thread=threading.Thread(target=self.scan,args=([row],));thread.start()
        try:
            self.assertTrue(server.entered.wait(2))
            with self.assertRaisesRegex(IOPError,'identification is in progress'):
                self.client.register({'driver':'scpi','config':row['connection']})
            self.client.submit([{'device':'stage','operation':'position','id':'position'}]).result(2)
        finally:
            server.release.set();thread.join(5)
        self.assertFalse(thread.is_alive())

    def test_endpoint_change_keeps_id_and_provider_failure_does_not_rebind(self):
        first,row1=self.instrument();second,row2=self.instrument()
        old=self.scan([row1])['instruments'][0]['device_id']
        self.scan([row2],available=False)
        self.assertEqual(self.engine.device_records[old]['config']['port'],first.server_address[1])
        self.scan([row2])
        self.assertEqual(self.engine.device_records[old]['config']['port'],second.server_address[1])
        self.assertEqual(len([d for d in self.engine.device_records.values() if d['driver']=='scpi']),1)

    def test_new_model_description_applies_without_replacing_existing_operations(self):
        server,row=self.instrument();server.identity='Example,Custom,SN4,1'
        result=self.scan([row]);device=result['instruments'][0]['device_id']
        self.assertEqual(result['instruments'][0]['required'],['model_operations'])
        profile={'id':'example-custom','match':{'manufacturer':'Example','model':'Custom'},'config':{
            'operations':{'temperature':{'query':'TEMP?','parameters':{},'result':{'type':'number','unit':'K'}}}}}
        self.client.save_instrument_profile(profile)
        self.assertIn('temperature',self.engine.descriptions[device]['operations'])
        self.assertEqual(self.client.submit([{'device':device,'operation':'temperature','id':'t'}]).result(3)['t']['value'],1.25)
        with self.assertRaisesRegex(IOPError,'exactly one'):
            self.client.save_instrument_profile(dict(profile,config={'operations':{'bad':{}}}))

    def test_reconnect_checks_identity_before_sending_experiment_command(self):
        server,row=self.instrument();device=self.scan([row])['instruments'][0]['device_id']
        server.identity='Stanford_Research_Systems,SR830,DIFFERENT,1.0'
        self.client.reconnect(device)
        with self.assertRaisesRegex(IOPError,'Different instrument'):
            self.client.submit([{'device':device,'operation':'read_x','id':'x'}]).result(3)
        self.assertNotIn('OUTP? 1',server.commands)

    def test_background_identity_waits_for_an_active_device_operation(self):
        server,row=self.instrument()
        device=self.client.register({'driver':'scpi','config':row['connection']})['id']
        driver=self.engine.devices[device]
        original=driver.invoke
        entered,release=threading.Event(),threading.Event()
        def invoke(operation,*args):
            if operation=='query':
                entered.set()
                release.wait(4)
            return original(operation,*args)
        with patch.object(driver,'invoke',side_effect=invoke):
            run=self.client.submit([{'id':'measure','device':device,'operation':'query','arguments':{'command':'MEAS?'}}])
            try:
                self.assertTrue(entered.wait(2))
                result=self.scan([row])
                identity=next(r for r in result['instruments'] if r.get('device_id')==device)
                self.assertEqual(identity['status'],'identifying')
                self.assertEqual(server.commands,[])
            finally:
                release.set()
            run.result(3)
        done=self.engine.store.wait_operation(identity['operation_id'],3)
        self.assertEqual(done['state'],'completed')
        self.assertEqual(server.commands,['MEAS?','*IDN?'])


class ProviderCase(unittest.TestCase):
    def test_windows_and_macos_inventory_preserve_os_metadata(self):
        from ai4instruments.iop.discovery import _usb
        windows=[{'PNPDeviceID':'USB\\VID_1234&PID_5678\\SER1','Name':'Instrument interface',
                  'Manufacturer':'Interface vendor','PNPClass':'USB','Service':'WinUSB','ConfigManagerErrorCode':0}]
        with patch('ai4instruments.iop.discovery.platform.system',return_value='Windows'), \
             patch('ai4instruments.iop.discovery._command',return_value=json.dumps(windows)) as command:
            rows,status=_usb()
        self.assertEqual(rows[0]['vid'],0x1234)
        self.assertEqual(rows[0]['driver'],'WinUSB')
        self.assertIn('Present = TRUE',command.call_args.args[0][-1])
        self.assertNotIn('identity',rows[0])
        mac={'SPUSBDataType':[{'_name':'bus','_items':[{'_name':'Camera','vendor_id':'0x1234 (Vendor)',
             'product_id':'0x5678','serial_num':'SER1','location_id':'0x001'}]}]}
        with patch('ai4instruments.iop.discovery.platform.system',return_value='Darwin'), \
             patch('ai4instruments.iop.discovery._command',return_value=json.dumps(mac)):
            rows,status=_usb()
        self.assertEqual(rows[0]['serial_number'],'SER1')
        self.assertTrue(status[0]['available'])

    def test_sdk_enumeration_reads_vendor_identity_and_channels(self):
        from ai4instruments.iop.discovery_worker import nidaqmx_devices,pylon_devices
        device=SimpleNamespace(name='Dev1',product_type='DAQ model',dev_serial_num=0x1234,is_simulated=False)
        for group in ('ai_physical_chans','ao_physical_chans','di_lines','do_lines','ci_physical_chans','co_physical_chans'):
            setattr(device,group,[SimpleNamespace(name='Dev1/'+group)])
        system=SimpleNamespace(System=SimpleNamespace(local=lambda:SimpleNamespace(devices=[device])))
        with patch.dict(sys.modules,{'nidaqmx.system':system}):
            rows=nidaqmx_devices()
        self.assertEqual(rows[0]['identity']['serial_number'],'1234')
        self.assertEqual(rows[0]['channels']['ai_physical_chans'],['Dev1/ai_physical_chans'])
        info=SimpleNamespace(**{name:(lambda value=value:value) for name,value in {
            'GetVendorName':'Basler','GetModelName':'Camera model','GetSerialNumber':'123',
            'GetFullName':'camera-address','GetFriendlyName':'Camera','GetDeviceClass':'BaslerUsb'}.items()})
        factory=SimpleNamespace(GetInstance=lambda:SimpleNamespace(EnumerateDevices=lambda:[info]))
        with patch.dict(sys.modules,{'pypylon':SimpleNamespace(pylon=SimpleNamespace(TlFactory=factory))}):
            rows=pylon_devices()
        self.assertEqual(rows[0]['identity']['model'],'Camera model')
        self.assertEqual(rows[0]['address'],'pylon:camera-address')

    def test_lxi_uses_advertised_control_address(self):
        class Info:
            name='meter._scpi-raw._tcp.local.'
            server='meter.local.'
            port=5025
            properties={b'Manufacturer':b'Example',b'Model':b'M1',b'SerialNumber':b'S123'}
            def parsed_scoped_addresses(self):return ['192.168.1.10']
        row=announcement('_scpi-raw._tcp.local.',Info())
        self.assertEqual(row['connection'],{'transport':'tcp','host':'192.168.1.10','port':5025})
        self.assertEqual(row['identity']['serial_number'],'S123')
        Info.properties[b'Address']=b'TCPIP::meter.local::hislip0::INSTR'
        self.assertEqual(announcement('_hislip._tcp.local.',Info())['connection']['resource'],Info.properties[b'Address'].decode())

    def test_usb_relationship_does_not_merge_distinct_ports(self):
        rows=[dict(transport=t,address=a,vid=v,pid=p,serial_number='SER1') for t,a,v,p in
              [('serial','COM7',6790,29987),('usb','1-2','1a86','7523'),('visa','USB0::6790::29987::SER1::INSTR',6790,29987)]]
        result=normalize({'connections':rows})
        self.assertEqual(len(result['groups']),3)
        self.assertIn('serial:COM7',result['connections'][1]['related_connections'])

    def test_bundled_descriptions_have_precise_model_matches(self):
        catalog=profiles({})
        self.assertGreaterEqual(len(catalog),4)
        for profile in catalog:
            validate_profile(profile)
            self.assertTrue(profile['documentation'])
