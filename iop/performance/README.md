# IOP Runtime 0.8.0

同一台 Linux x86_64 主机上交替运行 0.7.0 与 0.8.0，每项各 3 次，以下为执行用时中位数。模拟操作立即返回，包含 SQLite 保存；程序调用包含本机 HTTP 通信。

| 工作 | 0.7.0 | 0.8.0 | 用时比 |
| --- | ---: | ---: | ---: |
| 5000 步串行依赖 | 3.346 s | 3.091 s | 1.08× |
| 5000 个独立操作 | 2.995 s | 1.508 s | 1.99× |
| 实验程序连续调用 200 次 | 10.607 s | 0.965 s | 10.99× |

串行流程变化较小；独立操作减少了每轮重复队列复制和逐项开始记录提交。程序连续调用移除了固定 50 ms 等待，直接等待目标操作完成。三个场景使用相同的执行逻辑、完成记录与资源安排。

These are local runtime measurements, not physical instrument sampling rates. The table reports medians of three alternating runs per version. Parallel workflow scheduling benefits from grouped start records; sequential SDK calls avoid the former fixed 50 ms polling delay. The serial dependency chain has a smaller improvement.

[完整测量数据 / Raw measurements](0.8.0.json) · [程序调用测量脚本](../../scripts/benchmark_iop_program.py)

```sh
PYTHONPATH=src python scripts/benchmark_iop_program.py --steps 200
```

---

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
