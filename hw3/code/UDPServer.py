"""P3-9: a Python 3 UDP server returning an uppercased datagram."""

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
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((args.host, args.port))
        server.settimeout(args.timeout)
        host, port = server.getsockname()
        print(f"READY UDP {host}:{port}", flush=True)
        while True:
            request, address = server.recvfrom(65535)
            text = request.decode("utf-8")
            server.sendto(text.upper().encode("utf-8"), address)
            print(f"RECEIVED {address}: {text}", flush=True)
            if args.once:
                break


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"ERROR {type(error).__name__}: {error}", flush=True)
        sys.exit(1)
