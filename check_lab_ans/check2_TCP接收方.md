# Checkpoint 2：Wrap32 与 TCPReceiver 参考讲解

来源入口：[Winter 2024 讲义归档](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/file/Lab%20Checkpoint%202-the%20TCP%20receiver.pdf)、[RFC 9293 的序列号说明](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.4)。

## 三套编号的区别

| 编号 | 起点 | 包含 SYN/FIN 吗？ | 会回绕吗？ |
| --- | --- | --- | --- |
| stream index | 第一个数据字节为 0 | 不包含 | 实验中按 64 位处理 |
| absolute seqno | SYN 为 0 | 包含，各占 1 | 实验中按 64 位处理 |
| wire seqno | SYN 为 ISN | 包含 | 32 位模运算 |

数据的绝对序号通常比 stream index 大 1。SYN、FIN 消耗序号但不是交给应用的字节；两个通信方向各自拥有 ISN。

## wrap / unwrap 的解题推导

令 `M = 2^32`：`wrap(n, ISN) = (n + ISN) mod M`。

对 unwrap，先计算 `r = (wire - ISN) mod M`。所有可能的绝对序号为 `r + kM`。设 checkpoint 所在轮次 `q = floor(checkpoint / M)`，只需比较 q 所在轮次及相邻轮次的合法候选，选距离 checkpoint 最近者。候选必须在 uint64 的合法范围内；比较距离时避免无符号减法下溢。等距候选按课程接口允许的规则处理。

**手算例子：** ISN=100，wire=105，则 r=5。checkpoint=`M+7` 时，`M+5` 比 5 更近，因此 unwrap 返回 `M+5`。直接把 wire-ISN 当成最终结果会错过已经回绕的一轮。

## 接收方怎样工作

1. 尚未收到 SYN 时没有 ISN，也就没有可发送的有效 ACK；按接口要求忽略不能定位的普通数据。
2. 第一个 SYN 确立 ISN。同一条消息可能同时含 SYN、数据和 FIN，不能处理 SYN 后就遗漏数据。
3. 将消息序号展开为绝对序号，计算 payload 起点：`abs_seq + SYN占位 - 1`，再交给重组器。
4. 如果算出的数学起点为负，先裁剪属于流开始之前的前缀，再转换为无符号下标，避免把 -1 变成极大的整数。
5. FIN 表示 payload 后的流终点。何时连续组装到终点由重组器判断。

根据这些定义，设 `A = writer.bytes_pushed()`：

```text
收到 SYN 后的 absolute ACK = 1 + A + (写入端已按序关闭 ? 1 : 0)
发送的 ACK = wrap(absolute ACK, ISN)
通告窗口 = min(writer.available_capacity(), 65535)
```

ACK 依据已按序组装量，不依据应用已读取量；FIN 的确认依据写入端到达终点，不必等应用把缓冲读空。RST 和流错误传播按 starter 的消息结构实现，不能把旧版没有 RST 的结构直接套用过来。

## 接收例子

ISN=500，先收到 SYN，则 ACK=501。先到数据 `seq=504, payload="de", FIN=true`，对应流位置 `[3,5)`，前面有缺口，ACK 仍为 501。再收到 `seq=501, payload="abc"` 后，流得到 `abcde`，FIN 也连续到达，ACK=`500+1+5+1=507`。

即使应用还没有读取 `abcde`，ACK 也已经是 507；窗口则由当前未被应用读走的数据占用情况决定。

## 验证与参考

运行 `check2`，检查回绕点附近、接近 0 的 checkpoint、无 SYN、SYN 携带数据、重复 SYN、乱序 FIN、窗口超过 65535 及 RST。

- 参考实现 A：[wrapping_integers.cc](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/src/wrapping_integers.cc)、[tcp_receiver.cc](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/src/tcp_receiver.cc)。
- 参考实现 B：[tcp_receiver.cc](https://github.com/top-tree/minnow/blob/13f45de3ce948503443815a5ca27b259a2f1507b/src/tcp_receiver.cc)。
- 原作者记录：[PCloud Checkpoint 2](https://pcloud.dev/cs144-checkpoint-2/)。
