"""P3-9: a small Python 3 TCP client with newline-delimited messages."""

import argparse
import socket
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=12000)
    parser.add_argument("--source-port", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--message", default="hello network")
    args = parser.parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(args.timeout)
        client.bind(("0.0.0.0", args.source_port))
        client.connect((args.host, args.port))
        print(f"LOCAL {client.getsockname()} REMOTE {client.getpeername()}")
        client.sendall((args.message + "\n").encode("utf-8"))
        response = bytearray()
        while b"\n" not in response:
            data = client.recv(4096)
            if not data:
                raise ConnectionError("Server closed before a complete response")
            response.extend(data)
        print("RESPONSE " + response.split(b"\n", 1)[0].decode("utf-8"))


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"ERROR {type(error).__name__}: {error}")
        sys.exit(1)
