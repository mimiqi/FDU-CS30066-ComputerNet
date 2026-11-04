"""P3-9: a TCP server that uppercases one newline-delimited request."""

import argparse
import socket
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=12000)
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((args.host, args.port))
        server.listen(5)
        server.settimeout(args.timeout)
        host, port = server.getsockname()
        print(f"READY TCP {host}:{port}", flush=True)
        while True:
            connection, address = server.accept()
            with connection:
                connection.settimeout(args.timeout)
                request = bytearray()
                while b"\n" not in request:
                    data = connection.recv(4096)
                    if not data:
                        break
                    request.extend(data)
                if b"\n" in request:
                    text = request.split(b"\n", 1)[0].decode("utf-8")
                    connection.sendall((text.upper() + "\n").encode("utf-8"))
                    print(f"RECEIVED {address}: {text}", flush=True)
            if args.once:
                break


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"ERROR {type(error).__name__}: {error}", flush=True)
        sys.exit(1)
