""" RED STONE のチャットを棒読みちゃんに流すやつ

    Dependency
    ----------
    * 棒読みちゃん
        https://chi.usamimi.info/Program/Application/BouyomiChan/
        HTTP連携で通信
    * winpcap https://www.win10pcap.org/ja/
    * chardet https://github.com/chardet/chardet
    * dpkt https://dpkt.readthedocs.io/en/latest/
    * pcap-ct https://github.com/karpierz/pcap-ct

    See Also
    --------
    ぱぱみら for GUI版のソースコード
    https://papamira.herokuapp.com/gui
"""

import csv
import re
import socket
import subprocess
from sys import argv

import chardet
import dpkt
import pcap

from _filter import FILTERS

RS_PORTS = [54631, 54632, 54633, 56621]

config = {"DEBUG": False}


def choice_interface() -> str:
    """生きてるインターフェイスを選ぶ"""
    rows = (ret := subprocess.check_output("getmac /V /FO CSV")).decode(chardet.detect(ret)["encoding"]).splitlines()

    table = []
    for i, row in enumerate(csv.reader(rows)):
        if i == 0:
            continue
        if m := re.search(r"\{.*\}", row[3]):
            table.append((row[0], row[1], m[0]))

    if len(table) == 1:
        return table[0][2]

    for i, row in enumerate(table):
        print(i, row[0], row[1], row[2])

    choice = int(input("? "))
    return table[choice][2]


def dump(buf: bytes) -> str:
    nwrap = 32
    return "\n".join(
        " ".join(map(lambda a: f"{a:02X}", buf[nwrap * i : nwrap * i + nwrap])) for i in range(len(buf) // nwrap + 1)
    )


def callback(data: bytes):
    for f in FILTERS:
        if m := re.search(f.regex, data):
            # if f.name != "NOP":
            #     print(f.name, data)
            f.action(m)
            break
    else:
        if config["DEBUG"]:
            if data[0:2] in (
                b"\x0c\x00",
                b"\x0e\x00",
                b"\x14\x00",
                b"\x1a\x00",
                b"\x1c\x00",
                b"\x1e\x00",
                b"\x5a\x00",
                b"\x8e\x00",
                b"\x9c\x00",
            ):
                return
            print(data)
            print(repr(data.decode("cp932", "ignore")))
            print(dump(data))
            print("-" * 79)


def main():
    host = socket.gethostbyname(socket.gethostname())
    sniffer = pcap.pcap(name=choice_interface(), promisc=True, timeout_ms=100)
    sniffer.setfilter(
        f'tcp and ({" || ".join(f"port {p}" for p in RS_PORTS)}) and \
        host {host}'
    )

    for _, buf in sniffer:
        eth = dpkt.ethernet.Ethernet(buf)
        try:
            payload: bytes = eth.ip.tcp.data  # type: ignore
        except AttributeError:
            continue  # drop ipv6
        if not payload:
            continue

        callback(payload)


if __name__ == "__main__":
    if len(argv) >= 2 and argv[1] == "debug":
        config["DEBUG"] = True
    main()
