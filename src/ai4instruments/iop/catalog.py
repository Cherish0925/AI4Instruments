"""Read instrument descriptions shipped with installed packages without importing their SDKs."""
import copy
import importlib.util
import json
from importlib.metadata import entry_points
from pathlib import Path


def _directories(entry):
    module, separator, folder = entry.value.partition(':')
    parts, folders = module.split('.'), folder.split('.')
    if not separator or any(not part.isidentifier() for part in parts + folders):
        raise ValueError('Use a resource directory such as vendor_package:instruments')
    spec = importlib.util.find_spec(parts[0])
    if spec is None or not spec.submodule_search_locations:
        raise ValueError('Instrument description package is not installed: ' + parts[0])
    # Finding the top-level package does not execute __init__.py or load a vendor SDK.
    return [Path(root).joinpath(*parts[1:], *folders) for root in spec.submodule_search_locations]


class InstrumentCatalog:
    def __init__(self):
        from .identification import validate_profile
        directory = Path(__file__).with_name('instruments')
        if not directory.exists():
            directory = Path(__file__).resolve().parents[3] / 'iop' / 'instruments'
        self.records, self.errors = [], []

        def read(path, source):
            try:
                profile = validate_profile(json.loads(path.read_text(encoding='utf-8')))
                # Source is assigned by the loader, never accepted from the file.
                self.records.append({**profile, 'source': {**source, 'file': path.name}})
            except (OSError, ValueError, KeyError, TypeError) as error:
                self.errors.append({'source': source, 'file': path.name, 'error': str(error)})

        for path in sorted(directory.glob('*.json')):
            read(path, {'kind': 'builtin'})
        entries = sorted(entry_points(group='ai4instruments.instrument_profiles'),
                         key=lambda e: ((e.dist.metadata.get('Name', '') if e.dist else ''), e.name, e.value))
        for entry in entries:
            source = {'kind': 'package', 'name': entry.name, 'resource': entry.value,
                      'package': entry.dist.metadata['Name'] if entry.dist else None,
                      'version': entry.dist.version if entry.dist else None}
            try:
                paths = sorted({p for directory in _directories(entry) for p in directory.glob('*.json')})
                if not paths:
                    raise ValueError('No instrument JSON descriptions found in ' + entry.value)
                for path in paths:
                    read(path, source)
            except (OSError, ValueError, ImportError, AttributeError) as error:
                self.errors.append({'source': source, 'error': str(error)})

    def profiles(self, config):
        from .identification import validate_profile
        local = [{**validate_profile(copy.deepcopy(p)), 'source': {'kind': 'local'}}
                 for p in config.get('instrument_profiles', [])]
        return copy.deepcopy(self.records) + local

    def summary(self, config, match=None, profile_id=None, offset=0, limit=50, details=False):
        profiles = self.profiles(config)
        for key, value in (match or {}).items():
            if value:
                profiles = [p for p in profiles if key not in p['match'] or value.strip().casefold() in
                            [v.strip().casefold() for v in (p['match'][key] if isinstance(p['match'][key], list) else [p['match'][key]])]]
        if profile_id:
            profiles = [p for p in profiles if p['id'] == profile_id]
        offset, limit = max(0, int(offset)), min(200, max(1, int(limit)))
        page = profiles[offset:offset + limit]
        return {'profiles': page if details else [{k: p[k] for k in ('id', 'match', 'source', 'documentation') if k in p} |
                            {'operations': list(p['config']['operations'])} for p in page],
                'total': len(profiles), 'offset': offset, 'next_offset': offset + limit if offset + limit < len(profiles) else None,
                'errors': copy.deepcopy(self.errors)}


def select(identity, profiles):
    """Prefer local descriptions, then installed packages, then the built-in set.

    Within a source tier, narrower identity matches win. Equally applicable
    descriptions remain explicit alternatives rather than depending on file order.
    """
    from .identification import profile_matches
    candidates = [p for p in profiles if profile_matches(p, identity)]
    if not candidates:
        return None, []
    priority = {'builtin': 0, 'package': 1, 'local': 2}
    rank = max(priority.get(p.get('source', {}).get('kind', 'local'), 2) for p in candidates)
    candidates = [p for p in candidates if priority.get(p.get('source', {}).get('kind', 'local'), 2) == rank]

    def narrower(first, second):
        def constraints(profile):
            return {k: {v.strip().casefold() for v in (values if isinstance(values, list) else [values])}
                    for k, values in profile['match'].items()}
        a, b = constraints(first), constraints(second)
        return a != b and all(k in a and a[k] <= values for k, values in b.items())

    candidates = [p for p in candidates if not any(narrower(q, p) for q in candidates)]
    if len(candidates) == 1:
        return candidates[0], []
    return None, [{'id': p['id'], 'source': p.get('source', {'kind': 'local'})} for p in candidates]
