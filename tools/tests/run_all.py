#!/usr/bin/env python3
"""Run the project's tests and print one line per test. `make test` runs the host part, `make test-emu` the emulator part.

usage: python3 -I tools/tests/run_all.py [--host] [--emu] [--emu128] [--only NAME ...]      (default: --host)

host   no emulator, seconds: check_src.sh for en, de and fr, test_disks.py (needs the disks in build/), test_saves.py (needs disks/)
emu    cpcxray tests with a pass/fail result (the ones that print ALL OK): builds the mission disk and the plain rebuilt disk, copies them to
       work/xray/disk/, runs each test from work/xray with cpcxray's own Python and a timeout. Several minutes. Needs work/xray/output/firebird_in_flight.sna.
emu128 the 128K build (branch elite128): tools/check_src128.sh, tools/build_dsk128.py, the disk to work/xray/disk/elite128.dsk, a fresh output/docked128.sna
       (snap_docked128.py: a stale one silently runs the OLD code), then the 128K tests that print ALL OK. Several minutes.
The screenshot and probe tests (test_star_occlusion, test_station_screens, test_keydelay, test_cloak_asp, test_flight_hull, test_parked_*) have no
pass/fail and are not run here. Exit code 0 only if every test that ran passed.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
T = ROOT / "tools" / "tests"
XRAY = ROOT / "work" / "xray"
CPCX = Path.home() / ".local/share/uv/tools/cpcxray/bin/python"
HOST = [("check_src_en", ["bash", "tools/check_src.sh"]), ("check_src_de", ["bash", "tools/check_src.sh", "de"]), ("check_src_fr", ["bash", "tools/check_src.sh", "fr"]),
        ("test_saves", [sys.executable, "-I", "tools/tests/test_saves.py"]), ("test_disks", [sys.executable, "-I", "tools/tests/test_disks.py"])]
NEEDS_FLIGHT = {"ship_packs128", "spawnvar128"}      # the 128K tests that start from output/flight128.sna (the others from output/docked128.sna)
EMU128 = ["packs128", "ship_packs128", "sellall128", "escdigit128", "filemenu128", "music128", "tools128", "spawnvar128", "laserkeys"]
EMU = ["mission_hook", "mission_flight", "plans", "stolen_ship", "rocks", "trumbles", "trumble_sprites", "launch", "ship_packs", "sellall", "title_ships", "spawnvar", "laserkeys64"]
TIMEOUT = 420


def run(name, cmd, cwd, env=None, need_ok_text=False):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT, env=env)
        out = p.stdout + p.stderr
        ok = p.returncode == 0 and (("ALL OK" in out) if need_ok_text else True)
        note = "" if ok else "  " + (out.strip().splitlines() or ["(no output)"])[-1][:110]
    except subprocess.TimeoutExpired:
        ok, note = False, f"  timeout after {TIMEOUT} s"
    print(f"{'ok  ' if ok else 'FAIL'} {name:24s} {time.time() - t0:5.0f} s{note}", flush=True)
    return ok


def cpcx_env():
    """the environment for the cpcxray scripts (cpcxray is in ~/.local/bin, not on PATH); makes sure work/xray/disk/ exists"""
    (XRAY / "disk").mkdir(exist_ok=True)
    return dict(os.environ, PATH=f"{Path.home() / '.local/bin'}:{os.environ['PATH']}")


def emu128(only):
    if not CPCX.exists():
        print("cpcxray missing: see docs/_build.md (Tests and the emulator)")
        return [False]
    env = cpcx_env()
    for cmd in (["bash", "tools/check_src128.sh"], [sys.executable, "-I", "tools/build_dsk128.py"]):
        if subprocess.run(cmd, cwd=ROOT, capture_output=True).returncode:
            print("FAIL", " ".join(cmd[-1:]), "(run it by hand for the output)")
            return [False]
    shutil.copy(ROOT / "build/elite128.dsk", XRAY / "disk" / "elite128.dsk")
    # absolute script paths: in a worktree work/xray is a symlink to the main checkout, so a relative ../../tools would resolve there
    wanted = [n for n in EMU128 if not only or n in only]
    gens = [("snap_docked128.py", [], "output/docked128.sna", any(n not in NEEDS_FLIGHT for n in wanted)),      # snapshots the tests start from: a stale one silently runs the OLD code
            ("test_flight128.py", ["3"], "output/flight128.sna", any(n in NEEDS_FLIGHT for n in wanted))]
    for script, args, out, needed in gens:
        if needed and not run(script, [str(CPCX), "-I", str(T / script), *args], XRAY, env):      # run() reports a timeout as a FAIL line too
            print(f"generator {script} failed ({out} not made)")
            return [False]
    return [run(f"test_{n}", [str(CPCX), "-I", str(T / f"test_{n}.py")], XRAY, env, need_ok_text=True) for n in wanted]


def main():
    args = sys.argv[1:]
    only = set(args[args.index("--only") + 1:]) if "--only" in args else None
    do_emu = "--emu" in args
    do_emu128 = "--emu128" in args
    do_host = "--host" in args or not (do_emu or do_emu128)
    results = []
    if do_host:
        for name, cmd in HOST:
            if only and name not in only:
                continue
            results.append(run(name, cmd, ROOT))
    if do_emu128:
        results += emu128(only)
    if do_emu:
        if not CPCX.exists() or not (XRAY / "output/firebird_in_flight.sna").exists():
            print("cpcxray or work/xray/output/firebird_in_flight.sna missing: see docs/_build.md (Tests and the emulator)")
            return 2
        env = cpcx_env()
        for flags, default, dest in ((["--missions"], "work/elite_missions.dsk", "elite_missions.dsk"), ([], "work/elite_rebuilt.dsk", "elite_rebuilt.dsk")):
            subprocess.run([sys.executable, "-I", "tools/build_dsk.py"] + flags, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
            shutil.copy(ROOT / default, XRAY / "disk" / dest)
        for n in EMU:
            if only and n not in only:
                continue
            results.append(run(f"test_{n}", [str(CPCX), "-I", str(T / f"test_{n}.py")], XRAY, env, need_ok_text=True))      # absolute: in a worktree work/xray is a symlink into the main checkout, so ../../tools would run main's scripts
    print(f"\n{sum(results)} of {len(results)} passed")
    return 0 if results and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
