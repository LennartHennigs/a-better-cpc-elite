#!/usr/bin/env python3
"""Run ArcElite's Squeeze-style decompressor in unicorn: arc_unpack_emu.py IN_DEC.bin OUT.bin
IN is the output of arc_unlayer.py. Needs unicorn (uv run --with unicorn)."""
import struct, sys
from unicorn import *
from unicorn.arm_const import *
d = open(sys.argv[1], 'rb').read()
base = 0x8000
mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
mu.mem_map(0, 0x1000000)
mu.mem_write(base, d)
mu.reg_write(UC_ARM_REG_LR, 0x8008)
mu.reg_write(UC_ARM_REG_SP, 0x800000)
hist = []
def stop_at(uc, addr, size, ud):
    hist.append(addr); del hist[:-12]
    if addr == 0x3FD68:     # mov pc,r8: decompression finished
        r = {n: uc.reg_read(getattr(__import__('unicorn.arm_const', fromlist=['x']), f'UC_ARM_REG_{n.upper()}')) for n in ('r8', 'r7', 'r6', 'sb', 'sl', 'fp', 'ip')}
        print({k: hex(v) for k, v in r.items()})
        uc.emu_stop()
mu.hook_add(UC_HOOK_CODE, stop_at)
try:
    mu.emu_start(0x3FB20, 0x7FFFFFF, count=200_000_000)
except UcError as e:
    print('error', e, hex(mu.reg_read(UC_ARM_REG_PC)), [hex(h) for h in hist], 'r8', hex(mu.reg_read(UC_ARM_REG_R8)), 'r4', hex(mu.reg_read(UC_ARM_REG_R4)))
mem = bytes(mu.mem_read(base, 0x100000 - base))
open(sys.argv[2], 'wb').write(mem)
