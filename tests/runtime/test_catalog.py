"""Installed model descriptions work independently of SDK imports and file ordering."""
import copy
import importlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from ai4instruments.iop.catalog import InstrumentCatalog, select
from ai4instruments.iop.identification import description
from . import test_service as fixture


def profile(name='example-meter', model='M1'):
    return {'id': name, 'match': {'manufacturer': 'Example', 'model': model},
            'config': {'operations': {'temperature': {'query': 'TEMP?', 'parameters': {},
                      'result': {'type': 'number', 'unit': 'K'}}}},
            'documentation': ['https://example.org/instrument-manual']}


class CatalogCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def install_metadata(self, broken=False):
        root = Path(self.temp.name) / 'packages'
        package = root / 'iop_fixture_vendor'
        folder = package / 'instruments'
        folder.mkdir(parents=True)
        (package / '__init__.py').write_text('raise RuntimeError("A catalogue read must not load the SDK")\n')
        (folder / 'model.json').write_text(json.dumps(profile()))
        if broken:
            (folder / 'invalid.json').write_text('{')
        metadata = root / 'iop_fixture_vendor-1.2.0.dist-info'
        metadata.mkdir()
        (metadata / 'METADATA').write_text('Metadata-Version: 2.1\nName: iop-fixture-vendor\nVersion: 1.2.0\n')
        (metadata / 'entry_points.txt').write_text('[ai4instruments.instrument_profiles]\ncatalogue = iop_fixture_vendor:instruments\n')
        with patch.object(sys, 'path', [str(root), *sys.path]):
            importlib.invalidate_caches()
            self.engine.instrument_catalog = InstrumentCatalog()
        self.assertNotIn('iop_fixture_vendor', sys.modules)

    def test_package_files_are_loaded_without_sdk_imports(self):
        self.install_metadata()
        page = self.client.instrument_catalog(manufacturer='example', model='M1')
        self.assertEqual(page['total'], 1)
        p = page['profiles'][0]
        self.assertEqual(p['source']['package'], 'iop-fixture-vendor')
        self.assertEqual(p['source']['version'], '1.2.0')
        self.assertNotIn('config', p)
        self.assertEqual(p['operations'], ['temperature'])
        details = self.client.instrument_catalog(id=p['id'], details=True)['profiles'][0]
        self.assertEqual(details['config']['operations']['temperature']['query'], 'TEMP?')
        self.assertEqual(self.client.instrument_catalog(manufacturer='different')['total'], 0)
        first = self.client.instrument_catalog(limit=1)
        self.assertEqual(first['next_offset'], 1)
        second = self.client.instrument_catalog(offset=1, limit=1)
        self.assertNotEqual(first['profiles'][0]['id'], second['profiles'][0]['id'])

    def test_invalid_package_file_does_not_hide_other_instruments(self):
        self.install_metadata(broken=True)
        page = self.client.instrument_catalog()
        self.assertGreaterEqual(page['total'], 5)
        self.assertEqual(len(page['errors']), 1)
        self.assertEqual(page['errors'][0]['file'], 'invalid.json')
        context = self.client.context()
        self.assertTrue(any(s['action'] == 'read_instrument_catalog' for s in context['next_steps']))
        self.client.submit([{'id': 'position', 'device': 'stage', 'operation': 'position'}]).result(3)

    def test_narrower_identity_and_local_choice_take_precedence(self):
        base = profile('family', ['M1', 'M2'])
        base['source'] = {'kind': 'package'}
        narrow = profile('M1-firmware')
        narrow['match']['firmware'] = '2.0'
        narrow['source'] = {'kind': 'package'}
        identity = {'manufacturer': 'Example', 'model': 'M1', 'firmware': '2.0'}
        for rows in ([base, narrow], [narrow, base]):
            selected, alternatives = select(identity, rows)
            self.assertEqual(selected['id'], narrow['id'])
            self.assertEqual(alternatives, [])
        local = dict(base, id='laboratory', source={'kind': 'local'})
        self.assertEqual(select(identity, [local, narrow])[0]['id'], 'laboratory')

    def test_conflicting_descriptions_do_not_pick_by_install_order(self):
        first, second = profile('first'), profile('second')
        second['config']['operations']['temperature']['query'] = 'T?'
        identity = {'manufacturer': 'Example', 'model': 'M1'}
        for rows in ([first, second], [second, first]):
            record = description(identity, {'transport': 'tcp', 'host': 'localhost'}, rows)
            self.assertNotIn('operations', record['config'])
            self.assertEqual({p['id'] for p in record['profile_candidates']}, {'first', 'second'})

    def test_model_choice_uses_existing_versioned_configuration(self):
        self.install_metadata()
        record = {'id': 'catalog-meter', 'driver': 'scpi', 'identity': {'manufacturer': 'Example', 'model': 'M1'},
                  'config': {'host': '127.0.0.1', 'port': 1}}
        self.client.register(record)
        selected = self.client.instrument_catalog(model='M1', details=True)['profiles'][0]
        current = self.client.device_history('catalog-meter')[0]
        definition = copy.deepcopy(current['definition'])
        definition['config']['operations'] = selected['config']['operations']
        definition['instrument_profile'] = selected['id']
        self.client.configure_device('catalog-meter', definition, current['revision'])
        self.assertEqual(self.client.device_history('catalog-meter')[0]['revision'], current['revision'] + 1)
        self.assertIn('temperature', self.engine.descriptions['catalog-meter']['operations'])
