# Checkpoint 7：端到端联调参考讲解

资料入口：[Winter 2024 讲义归档](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/file/Checkpoint%207-putting%20it%20all%20together.pdf)。2023 历史版对应 check6。

## 这一阶段的答案是什么

答案是一组实际验证结果：主机和路由器组合后能否建立连接、双向传输、分别关闭发送方向、完整传输文件并正常退出。前面模块若正确，这一阶段可能主要是联调和记录，而非新增核心算法。

可从“同机两个进程”开始，再与另一份实现互通并交换客户端/服务端角色。自测只能证明自己的两端在该场景配合成功，与另一份实现互通能暴露双方对协议边界理解的差异。

## 参考操作形式

先检查自己的 starter 是否包含 `apps/endtoend.cc` 及对应程序。[参考实现 A 的入口](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/apps/endtoend.cc) 可辅助理解参数。

2024 讲义通过中继连接两端：服务端选择一个空闲的偶数端口，客户端使用它加一。以下是从项目根目录运行的形式示例，主机和端口需按实际可用环境替换：

```bash
# 服务端终端
./build/apps/endtoend server 中继主机 31000
```

```bash
# 客户端终端
./build/apps/endtoend client 中继主机 31001
```

互相输入文字，验证两个方向都有数据。单侧结束输入应只结束它的发送方向；另一方向可以继续接收，直到对端也结束。中继服务的可达性需要在实验机上确认，历史讲义的主机名不等于已经验证仍可用。

## 文件完整性验证

以下命令仅是实验操作参考，本次未运行：

```bash
# 服务端生成测试文件并在接入后发送
dd if=/dev/urandom of=/tmp/cs144-send.bin bs=1M count=1
./build/apps/endtoend server 中继主机 31000 < /tmp/cs144-send.bin
```

```bash
# 客户端关闭自己的输入方向，保存收到的数据
./build/apps/endtoend client 中继主机 31001 < /dev/null > /tmp/cs144-received.bin
```

分别在文件所在机器上计算：

```bash
sha256sum /tmp/cs144-send.bin
sha256sum /tmp/cs144-received.bin
```

跨两台机器时不要求两份文件都在同一目录；比较各自输出的哈希值，并记录字节数、退出情况。哈希工具说明见 [GNU Coreutils SHA-2 文档](https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html)。

## 怎样定位联调错误

| 现象 | 优先查看的层次 |
| --- | --- |
| 没有任何对端帧 | 中继参数、连通性、运行环境 |
| 反复 ARP，缺少 IPv4 数据 | 下一跳选择、ARP 映射学习、待发队列 |
| 能看到 IP 包，握手不完成 | 路由、TCP SYN/ACK、序列号与校验和 |
| 传输中停顿 | 窗口、ACK、重组缺口与重传计时器 |
| 文件长度不对或哈希不一致 | 部分读取、重组、重复数据、提前结束 |
| 内容正确但不退出 | FIN 确认、半关闭及框架的结束等待逻辑 |

定位时保留帧日志或抓包，使结论对应到具体报文，不以猜测直接跳过某一层。

2024 的 `endtoend` 可在命令最后追加 `debug` 参数打印交换的以太网帧，便于同时观察 ARP 和 TCP/IP。先确认本校入口仍支持该参数；文件传输时也应确认诊断日志没有混入保存数据的 stdout。

## 报告记录模板

| 场景 | 实际结果 | 证据路径 | 修复或说明 |
| --- | --- | --- | --- |
| 同机建立与关闭连接 | 待实验填写 | 待填写 | 待填写 |
| 双向文字传输 | 待实验填写 | 待填写 | 待填写 |
| 文件大小与哈希比较 | 待实验填写 | 待填写 | 待填写 |
| 与另一实现互通并交换角色 | 待实验填写 | 待填写 | 待填写 |

原作者记录：[PCloud Checkpoint 7](https://pcloud.dev/cs144-checkpoint-7/)。其中日志和哈希属于作者当时的实验，只用于理解记录方式。
