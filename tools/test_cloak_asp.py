#!/usr/bin/env python3
"""Is the cloaking-mission Asp visible? Spawn an Asp (type &0D) ahead in cpcxray and look at the view and the scanner.

usage (from work/xray):  ~/.local/share/uv/tools/cpcxray/bin/python -I ../../tools/test_cloak_asp.py GATE plain|mark TAG
  GATE = value written to aspMissionState (&504D in the stock code), `mark` sets the marker bit 6 of (ix+38), TAG names output/asp_TAG.png.
Result 2026-11-10 (stock code): `1 mark` hides the wireframe in the front view, the scanner blip stays (UpdateScanner has no marker test); `0 plain` shows both.
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
GATE=int(sys.argv[1]); MARK=sys.argv[2]=="mark"; TAG=sys.argv[3]
TRAP=0x9F00; ASP=0x504D
async def main():
    async with stdio_client(StdioServerParameters(command="cpcxray", args=["mcp","--config","config/cpc6128.toml"])) as (r,w):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(n,a=None):
                x=await s.call_tool(n,a or {}); t="".join(getattr(i,"text","") for i in x.content)
                try: return json.loads(t)
                except ValueError: return t
            async def call(addr, **regs):
                sp=(await c("registers_get"))["sp"]-2
                await c("memory_write",{"address":sp,"data":"%02X %02X"%(TRAP&255,TRAP>>8)})
                await c("registers_set",{"values":{"sp":sp,"pc":addr,**regs}})
                return await c("run",{"max_us":2_000_000,"timeout_s":60})
            await c("disk_insert",{"drive":"A","path":"disk/Elite_UK_Firebird_cracked_trainer.dsk"})
            await c("sna_load",{"path":"output/firebird_in_flight.sna"})
            await c("run",{"max_us":4_000_000,"timeout_s":60})
            safe=(await c("breakpoint_add",{"address":0x5066,"kind":"pc"}))["id"]
            rep=await c("run",{"max_us":10_000_000,"timeout_s":60}); assert rep.get("reason")=="breakpoint",rep
            await c("breakpoint_remove",{"breakpoint_id":safe})
            saved=await c("registers_get")
            await c("breakpoint_add",{"address":TRAP,"kind":"pc"})
            await call(0x816B); ix=(await c("registers_get"))["ix"]
            await call(0x80CD,a=0x0D,ix=ix); ix=(await c("registers_get"))["ix"]
            for off,val in ((0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0x18),(6,0x00),(8,0),(27,0),(37,0x7F)):
                await c("memory_write",{"address":ix+off,"data":"%02X"%val})
            flag=int((await c("memory_read",{"address":ix+32,"length":1}))["hex"],16)
            await c("memory_write",{"address":ix+32,"data":"%02X"%(flag&~0x40)})
            if MARK:
                f=int((await c("memory_read",{"address":ix+38,"length":1}))["hex"],16)
                await c("memory_write",{"address":ix+38,"data":"%02X"%(f|0x40)})
            await c("memory_write",{"address":ASP,"data":"%02X"%GATE})
            await c("memory_write",{"address":0x1C2F,"data":"00 FF 80  00 00 00  B6 7C 01"})
            await call(0x82B8,ix=ix)
            await c("registers_set",{"values":{k:saved[k] for k in ("af","bc","de","hl","ix","iy","sp","pc") if k in saved}})
            await c("run",{"max_us":1_200_000,"timeout_s":60})
            print("gate now", (await c("memory_read",{"address":ASP,"length":1}))["hex"], "slot", (await c("memory_read",{"address":ix+34,"length":1}))["hex"])
            print(await c("screen_image",{"path":"output/asp_%s.png"%TAG}))
asyncio.run(main())
