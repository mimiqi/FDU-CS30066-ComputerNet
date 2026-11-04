"""Run P3-9 experiments using this computer's loopback interface only."""

import os
from pathlib import Path
import platform
import py_compile
import queue
import socket
import subprocess
import sys
import threading
import time


HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
RECORD = [
    "# P3-9 本机回环实验记录",
    "",
    "实验日期：2026-11-04（Asia/Shanghai）。",
    f"环境：{platform.platform()}；Python {platform.python_version()}。",
    "",
    "本记录由 `python code/verify_p3_9.py` 实际生成，所有通信仅使用 `127.0.0.1`。",
    "没有进行两台物理主机间的测试。超时与异常为真实输出，未模拟网络返回结果。",
    "各次运行由操作系统分配空闲端口，因此端口数值可能变化。",
    "实验脚本将客户机超时设为 0.6 秒、服务器等待超时设为 1.8 秒；手动运行客户机默认超时为 3 秒。",
    "TCP 的 TimeoutError 表示在该短超时内连接未完成，不能据此推断网络中没有 RST。",
    "",
]


def empty_port(kind):
    with socket.socket(socket.AF_INET, kind) as temporary:
        temporary.bind(("127.0.0.1", 0))
        return temporary.getsockname()[1]


def run_client(protocol, port):
    return subprocess.run(
        [sys.executable, str(HERE / f"{protocol}Client.py"),
         "--host", "127.0.0.1", "--port", str(port),
         "--timeout", "0.6", "--message", "hello network"],
        capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=6,
    )


def start_server(protocol, port=0):
    process = subprocess.Popen(
        [sys.executable, "-u", str(HERE / f"{protocol}Server.py"),
         "--host", "127.0.0.1", "--port", str(port),
         "--timeout", "1.8", "--once"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", env=ENV,
    )
    ready_queue = queue.Queue()
    threading.Thread(target=lambda: ready_queue.put(process.stdout.readline()), daemon=True).start()
    try:
        ready = ready_queue.get(timeout=5).strip()
        if not ready.startswith(f"READY {protocol} "):
            raise RuntimeError(f"Server failed to start: {ready}")
        return process, int(ready.rsplit(":", 1)[1]), ready
    except BaseException:
        process.kill()
        process.communicate()
        raise


def finish_server(process):
    try:
        rest, _ = process.communicate(timeout=5)
        return rest.strip()
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()


def record(title, output, explanation):
    RECORD.extend([f"## {title}", "", "```text", output.strip(), "```", "", explanation, ""])


def main():
    for name in ("TCPClient", "TCPServer", "UDPClient", "UDPServer"):
        py_compile.compile(str(HERE / f"{name}.py"), doraise=True)
    record("语法编译检查", "TCPClient.py: PASS\nTCPServer.py: PASS\nUDPClient.py: PASS\nUDPServer.py: PASS", "四个程序均通过 `py_compile` 检查。")

    for protocol, kind in (("TCP", socket.SOCK_STREAM), ("UDP", socket.SOCK_DGRAM)):
        client = run_client(protocol, empty_port(kind))
        assert client.returncode != 0, client.stdout
        record(f"{protocol}：客户机先运行，服务器未启动", client.stdout + client.stderr,
               "未收到服务器响应；具体异常与操作系统对关闭端口的处理有关。")

    for protocol in ("TCP", "UDP"):
        server, port, ready = start_server(protocol)
        try:
            client = run_client(protocol, port)
            rest = finish_server(server)
        finally:
            if server.poll() is None:
                server.kill()
                server.communicate()
        assert client.returncode == 0 and "HELLO NETWORK" in client.stdout
        assert "RECEIVED" in rest
        record(f"{protocol}：服务器先启动，目的端口正确", ready + "\n" + client.stdout + rest,
               "成功返回大写文本；输出同时显示客户机源端口与服务器端口不同，仍可正常通信。")

    for protocol, kind in (("TCP", socket.SOCK_STREAM), ("UDP", socket.SOCK_DGRAM)):
        server, port, ready = start_server(protocol)
        try:
            wrong_port = empty_port(kind)
            assert wrong_port != port
            client = run_client(protocol, wrong_port)
            rest = finish_server(server)
        finally:
            if server.poll() is None:
                server.kill()
                server.communicate()
        assert client.returncode != 0 and "RECEIVED" not in rest
        record(f"{protocol}：客户机目的端口与服务器端口不一致",
               ready + f"\nCLIENT DESTINATION 127.0.0.1:{wrong_port}\n" + client.stdout + rest,
               "客户机未与预期服务器通信；服务器等待至超时，没有收到请求。")

    port = empty_port(socket.SOCK_DGRAM)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.sendto(b"sent before server starts", ("127.0.0.1", port))
        time.sleep(0.15)
        server, actual_port, ready = start_server("UDP", port)
        rest = finish_server(server)
    assert actual_port == port and "RECEIVED" not in rest and server.returncode != 0
    record("UDP：先发送一次数据报，再启动服务器",
           f"SENT before server started: 127.0.0.1:{port}\n" + ready + "\n" + rest,
           "服务器没有收到之前发送的数据报，最终等待超时；UDP 未自动重传。")

    RECORD.extend(["全部检查通过。", "", "这些实验核对本机 socket 行为，不代表所有网络和操作系统的异常类型都相同。", ""])
    path = HERE / "P3_9_实验记录.md"
    path.write_text("\n".join(RECORD), encoding="utf-8")
    print(f"PASS: syntax checks and 7 loopback experiments; record: {path}")


if __name__ == "__main__":
    main()
