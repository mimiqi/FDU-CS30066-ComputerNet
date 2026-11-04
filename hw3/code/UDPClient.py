"""P3-9: a Python 3 UDP client; send once, then wait for one reply."""

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
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(args.timeout)
        client.bind(("0.0.0.0", args.source_port))
        sent = client.sendto(args.message.encode("utf-8"), (args.host, args.port))
        print(f"SENT {sent} bytes LOCAL {client.getsockname()}", flush=True)
        response, address = client.recvfrom(65535)
        print(f"RESPONSE {address}: {response.decode('utf-8')}")


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"ERROR {type(error).__name__}: {error}", flush=True)
        sys.exit(1)
