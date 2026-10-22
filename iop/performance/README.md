# Scheduling measurements / 调度运行测量

One local run per case, 5,000 operations, 128 simulated devices, 64 operation workers. Operations return immediately; execution includes SQLite recording. Environment: Linux x86_64, glibc 2.39, Python 3.12.14, 9 visible CPUs.

| Case | Execution time | Operations / second |
| --- | ---: | ---: |
| 0.4.0, serial dependency chain | 20.4080 s | 245.0 |
| 0.5.0, serial dependency chain | 3.2136 s | 1555.9 |
| 0.5.0, independent operations | 3.0307 s | 1649.8 |

The serial chain took 6.35× less execution time in this run. The change replaces repeated full-graph scans with dependency counts and ready queues. These measurements describe local scheduling and recording; actual instrument throughput depends on instrument, transport and storage behavior. They are single runs, not a distribution of repeated measurements.

本次串行依赖链用时从 20.4080 秒降至 3.2136 秒。操作本身立即返回，测量包含本机调度与 SQLite 记录；这些数值不表示真实仪器的采样率。每个情况只运行一次，环境与原始输出见 [results.json](results.json)。

```sh
PYTHONPATH=src python scripts/benchmark_iop.py --pattern serial --steps 5000
PYTHONPATH=src python scripts/benchmark_iop.py --pattern parallel --steps 5000
```

To compare the previous release, run the same script with that release's `src` directory on `PYTHONPATH`. Submission time is reported separately. Physical measurements should report the instrument model, operation, completion condition and returned data.
