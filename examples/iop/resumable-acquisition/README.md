# Continuous records / 连续记录

将任何已注册仪器的一项操作按批保存；设备、操作和参数由提交者指定。仪器驱动仍负责采集与数据格式，Runtime 保存返回的数据、顺序和程序进度。

```sh
iop package examples/iop/resumable-acquisition --resources my-device \
  --parameters '{"device":"my-device","operation":"read_batch","batches":100}'
iop checkpoints RUN_ID
iop resume RUN_ID --request-id continue-1
```

程序从保存的 `next` 继续。每批使用稳定的操作 ID；操作已经完成而进度尚未保存时，读取原结果并补存数据。同一数据块重复上传只保存一次。若仪器在返回结果之前失联，先通过该仪器说明中的状态读取操作确定执行结果，再决定如何继续。

The package accepts any registered device operation. Each batch retains its original response as JSON Lines. Progress is saved after the operation and binary transfer complete. Stable operation IDs reuse completed results; chunk sequence numbers make repeated uploads idempotent. A device action with an unknown outcome is resolved from instrument state before continuation. Use a device's hardware timing and buffered acquisition for synchronized or high-rate sampling; this loop organizes returned batches.
