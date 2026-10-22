"""Operation context. Existing drivers can continue to use it as a threading.Event."""
import json
import math
import threading
from pathlib import Path


class Context(threading.Event):
    def __init__(self, run_id, operation_id, output_dir, report):
        super().__init__()
        self.run_id = run_id
        self.operation_id = operation_id
        self.output_dir = Path(output_dir)
        self._report = report

    def progress(self, fraction=None, message='', **values):
        if fraction is not None and (isinstance(fraction, bool) or not isinstance(fraction, (int, float))
                                     or not math.isfinite(fraction) or not 0 <= fraction <= 1):
            raise ValueError('Progress fraction must be between 0 and 1')
        data = {'fraction': fraction, 'message': str(message), **values}
        self._report(json.loads(json.dumps(data, allow_nan=False)))

    def file(self, name):
        from .engine import relative_path
        path = self.output_dir / relative_path(name)
        if not path.resolve().is_relative_to(self.output_dir.resolve()):
            raise ValueError('Operation output must remain inside its output directory')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
