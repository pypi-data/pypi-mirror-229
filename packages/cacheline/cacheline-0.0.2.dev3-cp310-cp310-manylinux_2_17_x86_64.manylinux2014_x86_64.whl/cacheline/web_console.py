from __future__ import annotations

import os


def start_web_console(
    cmd_args: list[str],
    writable: bool = True,
    once: bool = True,
    port: int = 1998,
    interface: str | None = None,
    credential: str | None = None,
    cwd: str | None = None,
):
    pid = os.fork()
    if pid == 0:
        from cacheline._web_console import start_web_console as _start_web_console

        _start_web_console(
            cmd_args,
            writable=writable,
            once=once,
            port=port,
            interface=interface,
            credential=credential,
            cwd=cwd,
        )
    else:
        os.waitpid(pid, 0)
