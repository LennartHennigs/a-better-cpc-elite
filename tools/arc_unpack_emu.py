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
mu.hook_add(UC_HOOK_CODE, lambda uc, addr, size, ud: uc.emu_stop(), begin=0x8004, end=0x8004)   # the decompressor jumps to the program start when done
mu.emu_start(0x3FB20, 0x7FFFFFF, count=200_000_000)
mem = bytes(mu.mem_read(base, 0x100000 - base))
open(sys.argv[2], 'wb').write(mem)
