#!/usr/bin/env python3
"""Disassemble the unpacked ArcElite image (work/arcelite/ilite_aif.bin) to a labelled ARM listing.
usage: arc_disasm.py IMAGE.bin OUT.s   (needs capstone: uv run --no-project --with capstone python3 -I ...)
Image is an AIF: base &8000, header 0x80 bytes, RO size at +0x14 (code+rodata), RW size at +0x18.
Data words: ldr pc-relative literals, printable string runs, undecodable words. Labels: bl targets are fn_, other branch targets are l_."""
import re, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
from capstone.arm import ARM_OP_IMM

BASE = 0x8000
SWI = {0x00: 'OS_WriteC', 0x01: 'OS_WriteS', 0x02: 'OS_Write0', 0x03: 'OS_NewLine', 0x04: 'OS_ReadC', 0x05: 'OS_CLI',
       0x06: 'OS_Byte', 0x07: 'OS_Word', 0x08: 'OS_File', 0x09: 'OS_Args', 0x0A: 'OS_BGet', 0x0B: 'OS_BPut',
       0x0C: 'OS_GBPB', 0x0D: 'OS_Find', 0x0E: 'OS_ReadLine', 0x0F: 'OS_Control', 0x10: 'OS_GetEnv', 0x11: 'OS_Exit',
       0x12: 'OS_SetEnv', 0x13: 'OS_IntOn', 0x14: 'OS_IntOff', 0x15: 'OS_CallBack', 0x16: 'OS_EnterOS', 0x17: 'OS_BreakPt',
       0x18: 'OS_BreakCtrl', 0x19: 'OS_UnusedSWI', 0x1A: 'OS_UpdateMEMC', 0x1B: 'OS_SetCallBack', 0x1C: 'OS_Mouse',
       0x1D: 'OS_Heap', 0x1E: 'OS_Module', 0x1F: 'OS_Claim', 0x20: 'OS_Release', 0x21: 'OS_ReadUnsigned',
       0x22: 'OS_GenerateEvent', 0x23: 'OS_ReadVarVal', 0x24: 'OS_SetVarVal', 0x25: 'OS_GSInit', 0x26: 'OS_GSRead',
       0x27: 'OS_GSTrans', 0x28: 'OS_BinaryToDecimal', 0x29: 'OS_FSControl', 0x2A: 'OS_ChangeDynamicArea',
       0x2B: 'OS_GenerateError', 0x2C: 'OS_ReadEscapeState', 0x2D: 'OS_EvaluateExpression', 0x2E: 'OS_SpriteOp',
       0x2F: 'OS_ReadPalette', 0x30: 'OS_ServiceCall', 0x31: 'OS_ReadVduVariables', 0x32: 'OS_ReadPoint',
       0x33: 'OS_UpCall', 0x34: 'OS_CallAVector', 0x35: 'OS_ReadModeVariable', 0x36: 'OS_RemoveCursors',
       0x37: 'OS_RestoreCursors', 0x38: 'OS_SWINumberToString', 0x39: 'OS_SWINumberFromString', 0x3A: 'OS_ValidateAddress',
       0x3B: 'OS_CallAfter', 0x3C: 'OS_CallEvery', 0x3D: 'OS_RemoveTickerEvent', 0x3E: 'OS_InstallKeyHandler',
       0x3F: 'OS_CheckModeValid', 0x40: 'OS_ChangeEnvironment', 0x41: 'OS_ClaimScreenMemory', 0x42: 'OS_ReadMonotonicTime',
       0x43: 'OS_SubstituteArgs', 0x44: 'OS_PrettyPrint', 0x45: 'OS_Plot', 0x46: 'OS_WriteN', 0x47: 'OS_AddToVector',
       0x48: 'OS_WriteEnv', 0x49: 'OS_ReadArgs', 0x4A: 'OS_ReadRAMFsLimits', 0x4B: 'OS_ClaimDeviceVector',
       0x4C: 'OS_ReleaseDeviceVector', 0x4D: 'OS_DelinkApplication', 0x4E: 'OS_RelinkApplication',
       0x4F: 'OS_HeapSort', 0x50: 'OS_ExitAndDie', 0x51: 'OS_ReadMemMapInfo', 0x52: 'OS_ReadMemMapEntries',
       0x53: 'OS_SetMemMapEntries', 0x54: 'OS_AddCallBack', 0x55: 'OS_ReadDefaultHandler', 0x56: 'OS_SetECFOrigin',
       0x57: 'OS_SerialOp', 0x58: 'OS_ReadSysInfo', 0x59: 'OS_Confirm', 0x5A: 'OS_ChangedBox', 0x5B: 'OS_CRC',
       0x5C: 'OS_ReadDynamicArea', 0x5D: 'OS_PrintChar', 0x5E: 'OS_ChangeRedirection', 0x5F: 'OS_RemoveCallBack',
       0x60: 'OS_FindMemMapEntries', 0x61: 'OS_SetColour', 0x6B: 'OS_Pointer', 0x6C: 'OS_ScreenMode',
       0x6D: 'OS_DynamicArea', 0x70: 'OS_Memory', 0x7F: 'OS_ConvertStandardDateAndTime'}
SWI_OTHER = {0x400C0: 'Wimp_Initialise', 0x400C1: 'Wimp_CreateWindow', 0x400C4: 'Wimp_OpenWindow', 0x400C7: 'Wimp_Poll',
             0x400D2: 'Wimp_GetWindowState', 0x400DA: 'Wimp_SetPointerShape', 0x40140: 'Sound_Configure',
             0x40141: 'Sound_Enable', 0x40142: 'Sound_Stereo', 0x40143: 'Sound_Speaker', 0x40144: 'Sound_Mode',
             0x40145: 'Sound_LinearHandler', 0x40146: 'Sound_SampleRate', 0x40147: 'Sound_Volume',
            }

def swi_name(n):
    x = n & 0x20000; n &= ~0x20000
    nm = SWI.get(n) or SWI_OTHER.get(n) or ('OS_WriteI+%d' % (n & 0xFF) if 0x100 <= n < 0x200 else f'SWI_{n:X}')
    return ('X' + nm) if x else nm

d = open(sys.argv[1], 'rb').read()
ro = struct.unpack_from('<I', d, 0x14)[0]
size = len(d)
md = Cs(CS_ARCH_ARM, CS_MODE_ARM); md.detail = True
word = lambda a: struct.unpack_from('<I', d, a - BASE)[0]

def printable_run(a):
    """length of a string starting at word address a (NUL-terminated, >=4 printable chars), else 0"""
    o = a - BASE; e = o
    while e < ro and 32 <= d[e] < 127 or (e < ro and d[e] in (9, 10, 13)):
        e += 1
    if e - o >= 4 and e < ro and d[e] == 0:
        return (e + 1 - o + 3) & ~3
    return 0

data = {}          # addr -> ('str'|'word', length)
ins = {}
for a in range(BASE, BASE + ro, 4):
    i = next(md.disasm(d[a - BASE:a - BASE + 4], a), None)
    ins[a] = i
    if i and i.mnemonic.startswith('ldr') and 'pc' in i.op_str and '[pc' in i.op_str:
        m = re.search(r'\[pc, #(-?)(0x[0-9a-f]+|\d+)\]$', i.op_str)
        if m:
            off = int(m.group(2), 0) * (-1 if m.group(1) else 1)
            t = a + 8 + off
            if BASE <= t < BASE + ro and t % 4 == 0:
                data.setdefault(t, ('word', 4))

# string runs: only claim them where the sweep would otherwise print garbage (not in pool words)
a = BASE
while a < BASE + ro:
    if a in data:
        a += data[a][1]; continue
    n = printable_run(a)
    if n:
        data[a] = ('str', n); a += n
    else:
        a += 4

labels = {}
for a, i in ins.items():
    if a in data or not i or i.id == 0 or not i.mnemonic.startswith('b'):
        continue
    if i.operands and i.operands[0].type == ARM_OP_IMM:
        t = i.operands[0].imm & 0xFFFFFFFF
        if BASE <= t < BASE + size:
            if i.mnemonic.startswith('bl') and not i.mnemonic.startswith('blx'):
                labels[t] = 'fn'
            else:
                labels.setdefault(t, 'l')
labels[BASE + 0xC + 8 + (word(BASE + 0xC) & 0xFFFFFF) * 4] = 'entry'   # the bl at &800C

def lab(t):
    k = labels.get(t)
    return {'fn': f'fn_{t:05X}', 'l': f'l_{t:05X}', 'entry': 'entry'}.get(k, f'x_{t:05X}')

out = open(sys.argv[2], 'w')
out.write('; ArcElite 1.14 unpacked AIF image, base &8000. Generated by tools/arc_disasm.py; not hand-edited.\n')
out.write(f'; RO size &{ro:X}, RW size &{struct.unpack_from("<I", d, 0x18)[0]:X}\n')
a = BASE
while a < BASE + ro:
    if a in labels:
        out.write(f'\n{lab(a)}:\n')
    if a in data and data[a][0] == 'str':
        n = data[a][1]; s = d[a - BASE:a - BASE + n].rstrip(b'\0')
        out.write(f'{a:05X}    DCB {s.decode("latin1")!r}, 0\n'); a += n; continue
    if a in data:
        w = word(a)
        c = f'  ; -> {lab(w)}' if w in labels else ''
        out.write(f'{a:05X}    DCD &{w:08X}{c}\n'); a += 4; continue
    i = ins[a]
    if i is None or i.id == 0:
        out.write(f'{a:05X}    DCD &{word(a):08X}\n'); a += 4; continue
    txt = f'{i.mnemonic} {i.op_str}'
    if i.mnemonic.startswith('svc'):
        n = i.operands[0].imm & 0xFFFFFF
        txt = f'SWI{i.mnemonic[3:]} {swi_name(n)}'
    elif i.operands and i.operands[0].type == ARM_OP_IMM and i.mnemonic.startswith('b'):
        t = i.operands[0].imm & 0xFFFFFFFF
        txt = f'{i.mnemonic} {lab(t)}'
    out.write(f'{a:05X}    {txt}\n'); a += 4
# the RW data (initialised) is dumped as words
out.write('\n; ---- initialised data (RW) ----\n')
for a in range(BASE + ro, BASE + size, 4):
    out.write(f'{a:05X}    DCD &{word(a):08X}\n')
print('labels', len(labels), 'fn', sum(1 for v in labels.values() if v == 'fn'), 'data words', len(data))
