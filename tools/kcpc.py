#!/usr/bin/env python3
"""Minimal client for the konCePCja IPC port (built by scripts/install-koncepcja.sh into ~/.local/share/koncepcja).

usage as a module:  from kcpc import Kcpc;  k = Kcpc.start("work/elite128.dsk");  k.cmd("step frame 50");  k.cmd("screenshot /path.png");  k.stop()
Commands are one text line each, the reply one line ("OK ..." or "ERR ..."); see docs/ipc-protocol.md in the konCePCja tree.
"""
import socket
import subprocess
import time
from pathlib import Path

EXE = Path.home() / ".local/share/koncepcja/koncepcja"


class Kcpc:
    def __init__(self, proc, port):
        self.proc, self.port = proc, port
        for _ in range(100):
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=30)
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("no IPC connection")
        self.f = self.s.makefile("rwb", buffering=0)

    @classmethod
    def start(cls, disk, model=2, extra=(), port=6543):
        args = [str(EXE), "--headless", "-O", f"system.model={model}", *extra, str(disk)]
        proc = subprocess.Popen(args, cwd=EXE.parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return cls(proc, port)

    def cmd(self, line):
        self.f.write((line + "\n").encode())
        return self.f.readline().decode().strip()

    def stop(self):
        try:
            self.cmd("quit")
        except Exception:
            pass
        self.proc.terminate()
        self.proc.wait(timeout=10)
