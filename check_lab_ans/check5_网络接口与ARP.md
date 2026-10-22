# Checkpoint 5：NetworkInterface 与 ARP 参考讲解

资料入口：[Winter 2024 讲义归档](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/file/Lab%20Checkpoint%205-down%20the%20stack%20%28the%20network%20interface%29.pdf)、[RFC 826](https://www.rfc-editor.org/rfc/rfc826.html)。2023 历史版对应 check4。

## 核心职责

IP 数据报表达最终目的地，以太网帧表达当前链路上的接收者。NetworkInterface 将上层提供的数据报送到指定下一跳，并把收到的 IPv4 帧还原成数据报。ARP 用于取得下一跳 IP 对应的以太网地址。

例如，数据报最终发往远处服务器，而下一跳是本地网关：IP 目的地址继续是服务器，以太网目的地址是网关 MAC。不能把下一跳的 IP 覆盖到数据报的最终目的字段。

## 状态与处理流程

一种易于分析的状态组织是三个映射：`IP→MAC及过期时间`、`IP→最近ARP请求时间`、`IP→待发送数据报队列`。类似划分可见 [原作者 PCloud 的设计记录](https://pcloud.dev/cs144-checkpoint-5/)。

### 发送数据报

缓存命中有效映射时，序列化 IPv4 数据报并装入帧；设置本接口源 MAC、下一跳目的 MAC 和 IPv4 类型，交给输出接口。

缓存未命中时，保存待发数据报，按请求节流规则广播 ARP。重复发送同一下一跳的数据报，应继续排队，但不能每次都新增一个广播请求。

### 接收帧

1. 只处理目的 MAC 为本机或广播的帧。
2. IPv4 类型：按 starter 的解析接口检查内容，成功后交给上层接收队列。
3. ARP 类型：先确认报文有效，从发送方 IP/MAC 学习映射；请求和应答都可能带来有用信息。
4. 学到等待中的下一跳映射后，发送该目的地积压的数据报。
5. 若是询问本机 IP 的 ARP 请求，构造针对请求者的 ARP 应答。

### 时间推进

2024 讲义给出的实验参数是：缓存映射保持 30 秒，同一 IP 的 ARP 请求在 5 秒内不重复发送。这是实验约定，不是 RFC 规定所有系统必须使用这两个常量。

由 tick 推进内部时间，映射到期后不能继续命中。请求冷却期结束意味着下一次发送可再次发起请求；本实验不要求仅靠 tick 就自动不断重发 ARP，也不要求实现完整 ICMP 不可达处理。

## 手算场景

假设 t=0 时向未知下一跳 H 发送数据报 D1，产生一个 ARP 请求并缓存 D1。t=1 秒时再向 H 发送 D2，只缓存 D2。t=2 秒收到 H 的有效 ARP 应答，就应发送 D1、D2，并以学习时刻更新映射有效期。

这个例子同时检查了请求去重、待发队列和映射学习。如果只发送 D2，说明此前缓存没有正确释放；如果每次都广播，说明请求节流状态没有保留。

## 验证与参考

在 2024 编号下检查 `check5`；核对本校目标后再运行。重点覆盖本机/非本机目的 MAC、无效帧、ARP 请求学习、ARP 应答学习、请求节流、映射到期及多个下一跳相互独立。

- 参考实现 A：[network_interface.cc](https://github.com/yyym-y/Stanford-CS144/blob/f6116c31133bf2514db0ae924755520cf3fc236b/src/network_interface.cc)。
- 参考实现 B：[network_interface.cc](https://github.com/top-tree/minnow/blob/13f45de3ce948503443815a5ca27b259a2f1507b/src/network_interface.cc)。

ARP 是地址解析协议；本实验的接口不负责决定 IP 路由，下一跳由上层提供。
