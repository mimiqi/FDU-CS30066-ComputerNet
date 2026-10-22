# Checkpoint 0：网络热身参考讲解

依据：[本校任务说明](../check0/check0.pdf)。基础资料见 [check0/examples](../check0/examples/README.md)。

## 手动联网部分的操作与解释

本校讲义要求先通过浏览器访问 `http://cs144.keithw.org/hello`，再在实验机用 `telnet cs144.keithw.org http` 建立连接，逐行输入：

```http
GET /hello HTTP/1.1
Host: cs144.keithw.org
Connection: close

```

最后还要输入一次回车，送出空行。请求行指定资源路径，Host 指定目标网站，空行结束头部；`Connection: close` 便于客户端读到响应结束。这里展示的是手动输入形式，写进程序时必须显式使用 `\r\n`，末尾为 `\r\n\r\n`。

**浏览器、telnet 与 webget 的结果为什么不同？** 浏览器通常显示解释后的正文；telnet 和本实验的 webget 显示原始响应，因此还会看到状态行和响应头。应比较同一次请求的正文与完整性，动态时间等头部字段不必逐字相同。

监听练习在一个终端运行讲义给出的 `netcat -v -l -p 9090`，另一个终端运行 `telnet localhost 9090`。连接后双方输入的字节都能到达对端，说明 TCP 是双向字节流；终端等到回车再发送是交互工具/终端的行为，不代表 TCP 自带“按行消息边界”。关闭服务端后，客户端会观察到连接结束。不同 netcat 发行版的参数可能不同，先核对本机帮助。

## webget 的解题主线

把手动输入的 HTTP 请求转换为程序操作：解析命令行中的主机与路径，通过课程的 Address、TCPSocket 建立连接，发送请求，持续读取并输出，直到接收方向 EOF。协议行尾和末尾空行可查 [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html)。

应分开思考三件事：连接向哪个主机建立、HTTP 的 Host 写什么、请求路径是什么。它们有关联，但不是把整个 URL 原样塞入所有参数。程序必须处理测试传入的其他主机和路径。

**为什么一次 read 不够？** 一次调用返回的是当时取得的一部分字节。网页响应的长度与一次读取的长度没有必然关系；必须按接口约定循环读到 EOF。最终输出包含收到的完整响应，不应混入调试日志。

## ByteStream 的一种可行设计

下述是根据接口约定推导的设计方案：用字符串块队列保存数据，另记队首已消费偏移、当前缓存量、累计写入量、累计移除量及关闭/错误状态。

1. push 只接受剩余容量允许的前缀；空前缀不必创建队列节点。
2. peek 返回队首尚未消费的连续片段；它不需要一次暴露所有缓存块。
3. pop 消费队首前缀，跨过整块时移除该块，并继续处理剩余消费量。
4. close 结束写入；只有关闭且缓存为空时，读端才结束。

该设计避免每消费一个字节就搬移全部剩余数据。是否满足性能要求仍需测量。`peek()` 的 string_view 指向队列持有的数据，不能指向函数结束时就销毁的临时字符串；语言背景见 [string_view 工作草案](https://eel.is/c++draft/string.view)。

## 手算答案

容量为 4，依次 `push("abc")`、`pop(2)`、`push("def")`、`close()`：

- 最终逻辑内容为 `cdef`，缓存 4 字节，剩余容量 0。
- 累计写入 6 字节，累计移除 2 字节。
- 写入端已关闭，读端还没有结束；再消费 4 字节才结束。

可用三个关系检查状态：`buffered = pushed - popped`；`available + buffered = capacity`；`finished = closed && buffered == 0`。

## 常见问题的答案

| 问题 | 答案 |
| --- | --- |
| 总共能写入多少字节？ | 容量限制同时缓存量；持续读写可让累计量远大于容量。 |
| peek 是否算消费？ | 不算，只有 pop 才改变移除计数。 |
| 空缓冲是否就是 EOF？ | 不是；写入端未关闭时仍可能继续到来数据。 |
| 关闭后能否丢弃未读数据？ | 不能，已有数据应继续可读。 |

## 验证与参考

在课程项目根目录执行 `cmake --build build --target check_webget` 和 `cmake --build build --target check0`。检查空流、小容量、部分接收、跨块消费、关闭后读尽，并保存本校要求的截图；吞吐率需超过 0.1 Gbit/s。

本校报告要求记录手动获取网页、webget 测试、ByteStream 测试三类结果，以及实际尝试、报错和修复过程；提交包含 `minnow` 与 `report.pdf` 的压缩包，打包时不包含 `build`。报告与截图要在实验机完成后生成，本目录不代填实验结果。

- 参考实现 A：[ByteStream](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/src/byte_stream.cc)。
- 参考实现 B：[ByteStream](https://github.com/top-tree/minnow/blob/13f45de3ce948503443815a5ca27b259a2f1507b/src/byte_stream.cc)、[webget](https://github.com/top-tree/minnow/blob/13f45de3ce948503443815a5ca27b259a2f1507b/apps/webget.cc)。
- 原作者记录：[PCloud Checkpoint 0](https://pcloud.dev/cs144-checkpoint-0/)。

参考仓库可能是整套实验完成后的状态，webget 可能已切换自写 TCP，使用前对照本校 Check0 要求的系统 TCPSocket。
