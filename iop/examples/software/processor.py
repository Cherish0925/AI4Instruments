"""Example executable: read an IOP request, transform an array and save results."""
import csv
import json
import os
import statistics
import sys
from pathlib import Path

request = json.load(sys.stdin)
arguments = request['arguments']
values = [value * arguments['scale'] for value in arguments['values']]
with (Path(os.environ['IOP_OUTPUT_DIR']) / 'values.csv').open('w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file); writer.writerow(['index', 'value']); writer.writerows(enumerate(values))
Path(os.environ['IOP_RESULT_FILE']).write_text(json.dumps({
    'count': len(values), 'mean': statistics.mean(values), 'values': values,
}), encoding='utf-8')
