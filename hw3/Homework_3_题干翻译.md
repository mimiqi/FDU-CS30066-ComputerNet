# 计算机网络作业三：题干翻译

原题：[Homework_3.pdf](Homework_3.pdf)。保留原题题号、变量、数值及两段 HTTP 报文。原 PDF 没有配图。

报文中的 `<cr>` 和 `<lf>` 分别表示一个回车字符和一个换行字符。为便于阅读，以下报文按这些分隔标记重新分行；原文中的字段名、拼写、日期、引号及 HTML 内容均保留，不作修正。代码块中的额外排版换行不表示报文新增了字符。

## P3-1

判断下列说法是正确还是错误。

**(a)** 用户请求一个包含一些文本和三幅图像的 Web 页面。为了获取这个页面，客户机会发送一条请求报文，并接收四条响应报文。

**(b)** 两个不同的 Web 页面，例如 `www.mit.edu/research.html` 和 `www.mit.edu/students.html`，可以通过同一条持久连接传送。

**(c)** 当浏览器与源服务器之间采用非持久连接时，单个 TCP 报文段有可能携带两条不同的 HTTP 请求报文。

**(d)** HTTP 响应报文中的 `Date:` 首部指出了响应中所包含对象的最后修改时间。

**(e)** HTTP 响应报文的报文体绝不会为空。

## P3-2

下面给出一段浏览器发送 HTTP GET 报文时由 Wireshark 捕获的 ASCII 字符串，即一条 HTTP GET 报文的实际内容。`<cr><lf>` 表示回车和换行；例如，文本中的 `<cr>` 表示 HTTP 首部该位置实际包含的一个回车字符。

请回答下列问题，并指出你从下面 HTTP GET 报文的什么位置找到了答案。

```text
GET /cs453/index.html HTTP/1.1<cr><lf>
Host: gaia.cs.umass.edu<cr><lf>
User-Agent: Mozilla/5.0 (Windows;U; Windows NT 5.1; en-US; rv:1.7.2) Gecko/20040804 Netscape/7.2 (ax) <cr><lf>
Accept:ext/xml, application/xml, application/xhtml+xml, text/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5<cr><lf>
Accept-Language: en-us,en;q=0.5<cr><lf>
AcceptEncoding: zip,deflate<cr><lf>
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7<cr><lf>
Keep-Alive: 300<cr><lf>
Connection:keep-alive<cr><lf>
<cr><lf>
```

**(a)** 浏览器请求的文档的 URL 是什么？

**(b)** 浏览器使用的是哪个 HTTP 版本？

**(c)** 浏览器请求的是非持久连接还是持久连接？

**(d)** 运行该浏览器的主机的 IP 地址是什么？

**(e)** 发起这条报文的浏览器是什么类型？为什么 HTTP 请求报文中需要包含浏览器类型？

## P3-3

下面的文本是服务器对上一题 HTTP GET 报文作出的响应。请回答下列问题，并指出你从下面报文的什么位置找到了答案。

```text
HTTP/1.1 200 OK<cr><lf>
Date: Tue, 07 Mar 200812:39:45GMT<cr><lf>
Server: Apache/2.0.52 (Fedora)<cr><lf>
Last-Modified: Sat, 10 Dec2005 18:27:46GMT<cr><lf>
ETag: ”526c3-f22-a88a4c80”<cr><lf>
AcceptRanges: bytes<cr><lf>
Content-Length: 3874<cr><lf>
Keep-Alive: timeout=max=100<cr><lf>
Connection: Keep-Alive<cr><lf>
Content-Type: text/html; charset=ISO-8859-1<cr><lf>
<cr><lf>
<!doctype html public ”-//w3c//dtd html 4.0transitional//en”><lf>
<html><lf>
<head><lf>
 <meta http-equiv=”Content-Type”content=”text/html; charset=iso-8859-1”><lf>
 <metaname=”GENERATOR” content=”Mozilla/4.79 [en] (Windows NT5.0; U) Netscape]”><lf>
 <title>CMPSCI 453 / 591 / NTU-ST550ASpring 2005 homepage</title><lf>
</head><lf>
<much more document text following here (not shown)>
```

**(a)** 服务器是否成功找到了该文档？该文档的响应是在什么时间生成的？

**(b)** 该文档最后一次修改是什么时候？

**(c)** 返回的文档共有多少字节？

**(d)** 返回文档的前 5 个字节是什么？服务器是否同意使用持久连接？

## P3-4

假设你在 Web 浏览器中单击一个链接以获取一个 Web 页面。本地主机尚未缓存与该 URL 对应的 IP 地址，因此需要通过 DNS 查询获得该 IP 地址。

假设本地主机在获得 DNS 返回的 IP 地址之前，需要依次访问 $n$ 台 DNS 服务器，各次访问产生的往返时间依次为 $\mathrm{RTT}_1,\ldots,\mathrm{RTT}_n$。进一步假设，该链接对应的 Web 页面恰好只包含一个对象，即少量 HTML 文本。用 $\mathrm{RTT}_0$ 表示本地主机与存放该对象的服务器之间的往返时间。

假设该对象的传输时间为零，那么从客户机单击链接到收到该对象，一共经过多长时间？

## P3-5

沿用 P3-4 的情境，现在假设 HTML 文件引用了同一台服务器上的 8 个非常小的对象。忽略传输时间，分别求下列情况下获取完整页面所需的时间。

**(a)** 使用非持久 HTTP，且不允许并行 TCP 连接。

**(b)** 使用非持久 HTTP，且浏览器被配置为允许 6 条并行连接。

**(c)** 使用持久 HTTP。

## P3-6

考虑一条很短的、长 10 米的链路，发送方在两个方向上都能以 150 bit/s 的速率传输。假设包含数据的分组长 100,000 bit，而仅包含控制信息（例如 ACK 或握手信息）的分组长 200 bit。假设 $N$ 条并行连接中的每条连接都能获得链路带宽的 $1/N$。

现在考虑 HTTP 协议。假设每个下载对象的大小均为 100 Kbit，并且最先下载的对象引用了同一发送方提供的另外 10 个对象。

在这种情况下，通过多条并行的非持久 HTTP 连接进行并行下载是否有意义？现在改为考虑持久 HTTP。与非持久 HTTP 相比，你是否预期会获得显著的性能提升？请给出理由并解释。

其中，$1\ \mathrm{Kbit}=1\times10^3\ \mathrm{bit}$。

## P3-7

考虑将一个大小为 $F=20\ \mathrm{Gbit}$ 的文件分发给 $N$ 个对等方。服务器的上传速率为 $u_s=30\ \mathrm{Mbps}$，每个对等方的下载速率为 $d_i=2\ \mathrm{Mbps}$，上传速率为 $u$。

针对 $N=10,100,1000$，以及 $u=300\ \mathrm{Kbps},700\ \mathrm{Kbps},2\ \mathrm{Mbps}$，制作一个图表，列出 $N$ 与 $u$ 的每一种组合在客户机-服务器分发方式和 P2P 分发方式下的最短分发时间。

其中，$1\ \mathrm{Gbit}=1\times10^9\ \mathrm{bit}$。

## P3-8

考虑采用客户机-服务器架构，将一个大小为 $F$ bit 的文件分发给 $N$ 个对等方。假设采用流体模型：服务器可以同时向多个对等方发送数据，并且可以为各个对等方分配不同的发送速率，只要这些速率之和不超过 $u_s$。

**(a)** 假设 $u_s/N\leq d_{\min}$。请给出一种分发方案，使分发时间为 $NF/u_s$。

**(b)** 假设 $u_s/N\geq d_{\min}$。请给出一种分发方案，使分发时间为 $F/d_{\min}$。

**(c)** 由此说明，在一般情况下，最短分发时间为

$$
\max\left\{\frac{NF}{u_s},\frac{F}{d_{\min}}\right\}.
$$

## P3-9

在一台主机上安装并编译 Python 程序 `TCPClient` 和 `UDPClient`，在另一台主机上安装并编译 `TCPServer` 和 `UDPServer`。

**(a)** 假设先运行 `TCPClient`，再运行 `TCPServer`，会发生什么？为什么？

**(b)** 假设先运行 `UDPClient`，再运行 `UDPServer`，会发生什么？为什么？

**(c)** 如果客户机端与服务器端使用不同的端口号，会发生什么？
