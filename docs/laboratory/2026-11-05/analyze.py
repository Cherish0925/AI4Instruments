"""Read the published laboratory archive; never import its instrument programs.

python analyze.py IOP_vs_direct_records_20261105.zip --output results
Requires numpy. Paths inside Windows ZIP files are normalized in memory.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

SOURCE = "https://github.com/Cherish0925/AI4Instruments/releases/tag/lab-feedback-2026-11-05"
EXPECTED_SHA256 = "eba968248a8c24cef6ab535672fc5fdcf6df6bc22a3b427c6c4f6f7742de3dc0"
SOURCE_COMMIT = "3b576ee99c4cdd6a9b6df36c7bfb43eee597a8ce"


def stats(values):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return {"n": 0}
    return {"n": len(a), "sum": float(a.sum()), "mean": float(a.mean()),
            "median": float(np.median(a)), "p95": float(np.percentile(a, 95)),
            "min": float(a.min()), "max": float(a.max())}


def elapsed_ms(row, start, end):
    return (datetime.fromisoformat(row[end]) - datetime.fromisoformat(row[start])).total_seconds() * 1000


class Archive:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        self.files = {i.filename.replace("\\", "/"): i for i in self.zip.infolist()
                      if not i.filename.endswith(("/", "\\"))}

    def text(self, path):
        return self.zip.read(self.files[path]).decode("utf-8-sig")

    def json(self, path):
        return json.loads(self.text(path))

    def rows(self, path):
        return list(csv.DictReader(io.StringIO(self.text(path))))


def timing(archive):
    sides = {}
    raw = {}
    for side in ("direct", "iop"):
        raw[side] = archive.rows(f"{side}/data_band2/timing.csv")
        grouped = collections.defaultdict(lambda: collections.defaultdict(float))
        for row in raw[side]:
            for field in ("wall_s", "iop_calls", "iop_call_s"):
                grouped[row["step"]][field] += float(row.get(field, 0))
        sides[side] = grouped
    steps = []
    for name, d in sides["direct"].items():
        i = sides["iop"][name]
        steps.append({"step": name, "direct_s": round(d["wall_s"], 3),
                      "iop_s": round(i["wall_s"], 3), "extra_s": round(i["wall_s"] - d["wall_s"], 3),
                      "ratio": i["wall_s"] / d["wall_s"], "iop_calls": int(i["iop_calls"]),
                      "iop_call_s": round(i["iop_call_s"], 3)})
    d, i = (sum(s[f"{side}_s"] for s in steps) for side in ("direct", "iop"))
    without_drift = [s for s in steps if s["step"] != "drift_v1_12"]
    calls = sum(s["iop_calls"] for s in steps)
    call_s = sum(s["iop_call_s"] for s in steps)
    return {"steps": steps, "direct_s": d, "iop_s": i, "extra_s": i - d,
            "ratio": i / d, "ratio_excluding_drift": sum(s["iop_s"] for s in without_drift) /
            sum(s["direct_s"] for s in without_drift), "timed_calls": calls,
            "client_call_s": call_s, "client_call_mean_ms": call_s * 1000 / calls,
            "timing_rows": {s: len(r) for s, r in raw.items()},
            "all_timed_steps_ok": all(r["status"] == "ok" for rows in raw.values() for r in rows)}


def database(archive):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "records.sqlite3"
        with archive.zip.open(archive.files["iop/service_home/records.sqlite3"]) as src, path.open("wb") as dst:
            import shutil
            shutil.copyfileobj(src, dst)
        db = sqlite3.connect(f"file:{path.as_posix()}?mode=ro&immutable=1", uri=True)
        operations = [json.loads(r[0]) for r in db.execute("select body from operations order by created")]
        groups = collections.defaultdict(list)
        for op in operations:
            groups[f"{op['device']}.{op['operation']}"].append(op)
        by_operation = {}
        for name, ops in groups.items():
            by_operation[name] = {"count": len(ops),
                                  "queue_ms": stats([elapsed_ms(o, "created", "started") for o in ops]),
                                  "execution_ms": stats([elapsed_ms(o, "started", "ended") for o in ops])}
        fields = collections.Counter()
        run_duration = []
        run_shapes = collections.Counter()
        reservations = collections.Counter()
        for body, in db.execute("select body from runs"):
            run = json.loads(body)
            run_shapes[(run["kind"], run["name"])] += 1
            reservations[bool(run["resources"])] += 1
            run_duration.append(elapsed_ms(run, "created", "ended"))
            for key in ("devices", "device_configurations", "spec", "result"):
                fields[key] += len(json.dumps(run.get(key), ensure_ascii=False, separators=(",", ":")).encode())
        counts = {t: db.execute(f"select count(*) from {t}").fetchone()[0] for t in
                  ("runs", "operations", "events", "artifacts", "device_versions", "platform_versions",
                   "checkpoints", "streams", "stream_chunks", "resource_holds")}
        output = {"counts": counts, "operation_states": dict(collections.Counter(o["state"] for o in operations)),
                  "by_operation": by_operation,
                  "queue_ms": stats([elapsed_ms(o, "created", "started") for o in operations]),
                  "execution_ms": stats([elapsed_ms(o, "started", "ended") for o in operations]),
                  "run_duration_ms": stats(run_duration), "run_field_bytes": dict(fields),
                  "run_kinds_and_names": [{"kind": k, "name": n, "count": c} for (k, n), c in run_shapes.items()],
                  "runs_with_reservations": reservations[True],
                  "failed_operations": dict(collections.Counter(f"{o['device']}.{o['operation']}" for o in operations if o["state"] == "failed")),
                  "errors": dict(collections.Counter(o["error"] for o in operations if o.get("error"))),
                  "first_created_utc": operations[0]["created"], "last_ended_utc": operations[-1]["ended"],
                  "artifact_names": dict(db.execute("select name,count(*) from artifacts group by name")),
                  "event_kinds": dict(db.execute("select kind,count(*) from events group by kind"))}
        db.close()
    return output, operations


def spectra(archive):
    prefixes = {s: f"{s}/data_band2/" for s in ("direct", "iop")}
    metas = {s: {p[len(prefix):]: archive.json(p) for p in archive.files
                 if p.startswith(prefix) and p.endswith(".json")} for s, prefix in prefixes.items()}
    common = sorted(metas["direct"].keys() & metas["iop"].keys())
    rows = []
    mismatches = []
    for relative in common:
        data = {s: np.loadtxt(io.StringIO(archive.text(prefix + relative[:-5] + ".csv")),
                             delimiter=",", skiprows=1) for s, prefix in prefixes.items()}
        d, i = data["direct"], data["iop"]
        assert d.shape == i.shape == (401, 9), relative
        assert np.isfinite(d).all() and np.isfinite(i).all(), relative
        assert np.array_equal(d[:, 0], i[:, 0]), relative
        assert np.array_equal(d[:, 0], np.linspace(900e6, 1300e6, 401)), relative
        for key in ("v1_set", "v2_set", "v3_set", "pow1_dBm", "pow2_dBm", "dev_power_dBm"):
            dv, iv = (metas[s][relative].get(key) for s in ("direct", "iop"))
            if dv != iv:
                mismatches.append({"file": relative, "field": key, "direct": dv, "iop": iv})
        mask = (d[:, 0] >= 1e9) & (d[:, 0] <= 1.25e9)
        row = {"dataset": relative.split("/")[0], "file": relative[:-5] + ".csv"}
        for channel, col in (("s21", 1), ("s12", 5)):
            zd, zi = d[:, col] + 1j * d[:, col + 1], i[:, col] + 1j * i[:, col + 1]
            dbd, dbi = 20 * np.log10(np.abs(zd)), 20 * np.log10(np.abs(zi))
            difference = dbi[mask] - dbd[mask]
            row[channel + "_rms_db"] = float(np.sqrt(np.mean(difference ** 2)))
            row[channel + "_max_abs_db"] = float(np.max(np.abs(difference)))
            row[channel + "_peak_delta_db"] = float(dbi.max() - dbd.max())
            row[channel + "_global_peak_delta_mhz"] = float((d[dbi.argmax(), 0] - d[dbd.argmax(), 0]) / 1e6)
            row[channel + "_complex_relative_l2"] = float(np.linalg.norm(zi[mask] - zd[mask]) / np.linalg.norm(zd[mask]))
        row["peak_amplitude_ratio_delta"] = float(
            10 ** ((i[:, 3].max() - i[:, 7].max()) / 20) - 10 ** ((d[:, 3].max() - d[:, 7].max()) / 20))
        rows.append(row)
    by_dataset = {}
    for dataset in sorted({r["dataset"] for r in rows}):
        selected = [r for r in rows if r["dataset"] == dataset]
        by_dataset[dataset] = {"pairs": len(selected)}
        for key in ("s21_rms_db", "s12_rms_db", "peak_amplitude_ratio_delta"):
            by_dataset[dataset][key] = stats([r[key] for r in selected])
    result = {"direct_count": len(metas["direct"]), "iop_count": len(metas["iop"]), "pairs": len(common),
              "direct_unmatched": sorted(metas["direct"].keys() - metas["iop"].keys()),
              "iop_unmatched": sorted(metas["iop"].keys() - metas["direct"].keys()),
              "points_per_spectrum": 401, "grid_hz": [900000000, 1300000000, 1000000],
              "comparison_window_hz": [1000000000, 1250000000], "setpoint_mismatches": mismatches,
              "by_dataset": by_dataset, "s21_rms_db": stats([r["s21_rms_db"] for r in rows]),
              "s12_rms_db": stats([r["s12_rms_db"] for r in rows]),
              "largest_s21_rms": sorted(rows, key=lambda r: r["s21_rms_db"], reverse=True)[:5],
              "largest_s12_rms": sorted(rows, key=lambda r: r["s12_rms_db"], reverse=True)[:5],
              "metadata": {s: {"with_sweep_settings": sum("sweep" in m for m in ms.values()),
                                "with_instrument_identity": sum("instrument" in m for m in ms.values()),
                                "first_timestamp_local": min(m["timestamp"] for m in ms.values()),
                                "last_timestamp_local": max(m["timestamp"] for m in ms.values())} for s, ms in metas.items()},
              "iop_run_id_values": dict(collections.Counter(m.get("iop_run_id") for m in metas["iop"].values()))}
    return result, rows


def fit_tables(archive):
    output = []
    for name in sorted(archive.files):
        if not name.startswith("direct/data_band2/") or not name.endswith("_params.csv"):
            continue
        other = "iop/" + name[len("direct/"):]
        if other not in archive.files:
            continue
        d, i = ({r["file"]: r for r in archive.rows(n)} for n in (name, other))
        common = sorted(d.keys() & i.keys())
        row = {"table": name[len("direct/data_band2/"):], "pairs": len(common)}
        for key in ("f0_MHz", "kappa1_MHz", "kappa2_abs_MHz", "kappa2_arg_deg", "nrmse_pct"):
            diff = np.array([float(i[c][key]) - float(d[c][key]) for c in common])
            if key.endswith("_deg"):
                diff = (diff + 180) % 360 - 180
            row[key + "_absolute_delta"] = stats(np.abs(diff))
        def phase(r):
            k1 = float(r["kappa1_MHz"])
            k2 = complex(float(r["kappa2_re_MHz"]), float(r["kappa2_im_MHz"]))
            return np.degrees(np.angle((k1 + k2) / k1))
        row["phase_step_absolute_delta_deg"] = stats([abs((phase(i[c]) - phase(d[c]) + 180) % 360 - 180) for c in common])
        output.append(row)
    return output


def measurement_links(archive, operations):
    """Recover archived acquisition links by exact numeric content, then timestamp.

    This reconstruction is for this archive. Runtime-generated acquisition IDs
    should carry these links when a measurement is made.
    """
    def signature(values):
        return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes()).digest()
    readings = collections.defaultdict(list)
    for op in operations:
        if op["operation"] == "read_sdata" and op["state"] == "completed":
            raw = np.fromstring(op["result"]["value"], sep=",")
            readings[(op["arguments"]["ch"], signature(raw))].append(op)
    output = []
    for path in sorted(archive.files):
        if not path.startswith("iop/data_band2/") or not path.endswith(".json"):
            continue
        meta = archive.json(path)
        saved = datetime.fromisoformat(meta["timestamp"]).replace(tzinfo=timezone(timedelta(hours=8)))
        data = np.loadtxt(io.StringIO(archive.text(path[:-5] + ".csv")), delimiter=",", skiprows=1)
        row = {"file": path[len("iop/data_band2/"):-5] + ".csv", "saved_local": meta["timestamp"]}
        for channel, col in ((1, 1), (2, 5)):
            matches = readings[(channel, signature(data[:, col:col+2].ravel()))]
            # Metadata records a local wall time truncated to seconds, after file writing.
            # Retain ambiguity instead of silently choosing a convenient duplicate.
            candidates = [op for op in matches if -1 < (saved - datetime.fromisoformat(op["ended"])).total_seconds() < 5]
            row[f"ch{channel}_candidate_count"] = len(candidates)
            if len(candidates) == 1:
                op = candidates[0]
                for key in ("id", "run_id", "started", "ended"):
                    row[f"ch{channel}_{key}"] = op[key]
        output.append(row)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.archive.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("This analysis refers to the published 2026-11-05 archive; the supplied archive differs.")
    a = Archive(args.archive)
    spec, pairs = spectra(a)
    db, operations = database(a)
    links = measurement_links(a, operations)
    result = {"source": SOURCE, "archive_sha256": digest, "source_commit": SOURCE_COMMIT,
              "archive_bytes": args.archive.stat().st_size, "files": len(a.files),
              "uncompressed_bytes": sum(f.file_size for f in a.files.values()),
              "timing": timing(a), "database": db, "spectra": spec, "fit_tables": fit_tables(a),
              "reconstructed_links": {"measurements": len(links),
                                      "unique_both_channels": sum(r["ch1_candidate_count"] == r["ch2_candidate_count"] == 1 for r in links),
                                      "method": "Exact float64 trace content and metadata time (-1 < save-minus-operation-end < 5 seconds); no nearest-match substitution."},
              "storage": {"database_bytes": a.files["iop/service_home/records.sqlite3"].file_size,
                          "run_files_bytes": sum(f.file_size for n, f in a.files.items() if n.startswith("iop/service_home/runs/")),
                          "scientific_csv_bytes_each_side": {s: sum(a.files[f"{s}/data_band2/{p['file']}"].file_size for p in pairs) for s in ("direct", "iop")}}}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "findings.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (args.output / "spectra.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(pairs[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(pairs)
    with (args.output / "measurement-operations.csv").open("w", newline="", encoding="utf-8") as f:
        fields = list(dict.fromkeys(k for row in links for k in row))
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(links)
    print(json.dumps({"timing": result["timing"], "spectra_pairs": spec["pairs"],
                      "s21_rms_db": spec["s21_rms_db"], "s12_rms_db": spec["s12_rms_db"],
                      "storage": result["storage"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
