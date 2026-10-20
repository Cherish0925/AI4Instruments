# Contract example / 契约示例

[measurement-contract.json](measurement-contract.json) illustrates a device description, an accepted operation, an observation and a completed acquisition. It is a design example with synthetic values, not an implemented protocol or a physical measurement record.

The example keeps four distinctions visible:

- `queued` does not mean that a physical outcome has been observed.
- The wavelength setting is tracked; the power reading is reported by the device interface.
- Unavailable calibration and uncertainty are explicit, not invented numerical values.
- Completing an acquisition does not establish that a research objective has been achieved.

该 JSON 用合成数据说明设备描述、操作受理、观测与采集结束的关系。波长设定为 tracked，功率读数为 reported；未知校准与未提供的不确定度分别保留；采集结束与研究目标达成分开记录。文件不连接硬件。
