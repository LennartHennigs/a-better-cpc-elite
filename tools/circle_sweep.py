"""Sweep the planet/sun disc routine (todoDrawFilledCircle, &E787) with cpcxray and report out-of-bounds writes.

Run with cpcxray's own interpreter from work/xray/ (see CLAUDE.md):
  ~/.local/share/uv/tools/cpcxray/bin/python -I tools/circle_sweep.py FLAGS STEP RADII OUTFILE [ADDR:HEX]
  FLAGS  comma list of circleOffsetXhi flag values 0-15 (bit0/1 x/y sign, bit2/3 x/y overflow)
  STEP   stride for the x and y offset bytes (0-255)
  RADII  comma list of drawradius values
  ADDR:HEX  optional patch applied after every snapshot load, e.g. 245C:18 disables the line-count clamp
Needs work/xray/output/firebird_in_flight.sna (the game launched from Lave: disk_insert, sna_load
firebird_at_entry.sna, run 8 s, hold n and space, press 1, run 6 s, sna_save). Writes below &A000 that are
not on the whitelist (idle ISR writes, circle variables and code at &20C0-&28FF, the stack at &7480) are logged
as JSON lines (the separator is a literal backslash-n; split on it). Each call: ~5 ms.
"""
import asyncio, json, sys, re, time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
def J(res):
    t=res.content[0].text if res.content else ""
    try: return json.loads(t)
    except Exception: return t
TRAP=0x0005; SP0=0x7490
flags=[int(v) for v in sys.argv[1].split(",")]
xs=range(0,256,int(sys.argv[2])); ys=range(0,256,int(sys.argv[2]))
rads=[int(v) for v in sys.argv[3].split(",")]
out=open(sys.argv[4],"w")
PAT=re.compile(r"PC=([0-9A-F]{4})\s+write\s+([0-9A-F]{4})\s+([0-9A-F]{2})")
async def main():
    p=StdioServerParameters(command="cpcxray",args=["mcp","--config","config/cpc6128.toml"])
    async with stdio_client(p) as (r,w):
        async with ClientSession(r,w) as s:
            await s.initialize()
            async def c(n,**a): return J(await s.call_tool(n,a))
            await c("disk_insert",drive="A",path="disk/Elite_UK_Firebird_cracked_trainer.dsk")
            PATCH=sys.argv[5] if len(sys.argv)>5 else ""
            async def reload():
                await c("sna_load",path="output/firebird_in_flight.sna")
                if PATCH:
                    a_,d_=PATCH.split(":"); await c("memory_write",address=int(a_,16),data=d_)
            await reload()
            # baseline: ISR writes below 0xA000 over idle run
            await c("bus_trace_start",kinds=["write"],start=0,end=0x9FFF,capacity=2000)
            await c("run",max_instructions=200000)
            tr=await c("bus_trace_read",last=2000)
            W0=set(int(PAT.search(l).group(2),16) for l in tr["lines"] if PAT.search(l))
            await reload()
            WL=set(W0)|set(range(0x7480,0x7492))|set(range(0x20C0,0x2900))|set(range(0x1C20,0x1C30))
            # learn circle-legit writes from a few fully-visible cases
            async def run1(fl,x,y,rad,lo,hi):
                await c("memory_write",address=0x20C7,data=f"{y:02X} {x:02X} {fl:02X} {rad:02X}")
                await c("memory_write",address=SP0,data=f"{TRAP&255:02X} {TRAP>>8:02X}")
                await c("registers_set",values={"pc":0xE787,"sp":SP0})
                await c("bus_trace_start",kinds=["write"],start=lo,end=hi,capacity=2000)
                r1=await c("run_until",address=TRAP,max_instructions=400000)
                g=await c("registers_get")
                tr=await c("bus_trace_read",last=2000)
                ws=[(int(m.group(1),16),int(m.group(2),16),m.group(3)) for m in (PAT.search(l) for l in tr["lines"]) if m]
                return r1,g,ws
            LEG=set()
            for case in [(0,100,30,60),(3,100,30,60),(0,11,13,255),(12,201,17,200),(1,150,50,40),(2,30,200,80)]:
                r1,g,ws=await run1(*case,0,0x9FFF)
                LEG|=set(a for _,a,_ in ws)
            await reload()
            WL|=LEG
            print("whitelist size",len(WL),file=sys.stderr)
            n=0;bad=0;t=time.time()
            for fl in flags:
                for x in xs:
                    for y in ys:
                        for rad in rads:
                            r1,g,ws=await run1(fl,x,y,rad,0,0x9FFF)
                            odd=[(hex(pc),hex(a),v) for pc,a,v in ws if a not in WL]
                            fail=(r1["reason"]!="address_reached" or g["sp"]!=SP0+2)
                            n+=1
                            if odd or fail:
                                bad+=1
                                out.write(json.dumps({"fl":fl,"x":x,"y":y,"r":rad,"reason":r1["reason"],"ins":r1["instructions"],"sp":hex(g["sp"]),"odd":odd[:6]})+"\\n"); out.flush()
                                await reload()
            print("done",n,"calls",bad,"anomalies",time.time()-t,file=sys.stderr)
asyncio.run(main())
