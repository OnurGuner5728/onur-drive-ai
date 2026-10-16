"""Head-unit metadata inventory using only standard, previously authorized ADB read operations.

Never attempts root, elevation, hidden engineer menus, firmware changes, writes,
video capture, broadcasts, service calls or any CAN message.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

READ_COMMANDS = {
 "android_release": ["getprop", "ro.build.version.release"],
 "android_sdk": ["getprop", "ro.build.version.sdk"],
 "product_model": ["getprop", "ro.product.model"],
 "hardware": ["getprop", "ro.hardware"],
 "camera_nodes": ["ls", "/dev"],
 "media_camera": ["dumpsys", "media.camera"],
 "services": ["service", "list"],
}
# /dev/video0..3 is a presence hint, NOT a guess that MG HS uses these camera IDs.

def run_adb(serial, parts, timeout=8):
    cmd=["adb"]+(["-s",serial] if serial else [])+["shell"]+parts
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,check=False)
        return {"exit_code":r.returncode,"stdout":r.stdout[:35000],"stderr":r.stderr[:1200]}
    except subprocess.TimeoutExpired:
        return {"exit_code":None,"error":"TIMEOUT"}
    except OSError as e:
        return {"exit_code":None,"error":type(e).__name__}

def inspect(serial=None):
    if shutil.which("adb") is None:
        return {"status":"ADB_NOT_INSTALLED","instructions":"Install Android Platform Tools; no modifications performed."}
    r=subprocess.run(["adb","devices"],capture_output=True,text=True,timeout=8,check=False)
    devices=[line.split()[0] for line in r.stdout.splitlines()[1:] if line.strip().endswith("\tdevice")]
    if serial:
        if serial not in devices:
            return {"status":"DEVICE_NOT_AUTHORIZED","authorized_device_count":len(devices)}
    elif len(devices)!=1:
        return {"status":"EXPECT_EXACTLY_ONE_AUTHORIZED_DEVICE","authorized_device_count":len(devices)}
    serial=serial or devices[0]
    result={"status":"READ_ONLY_PROBE_COMPLETED","timestamp_unix":int(time.time()),"data":{}}
    for k,cmd in READ_COMMANDS.items():
        out=run_adb(serial,cmd)
        if k == "camera_nodes" and "stdout" in out:
            out["stdout"]="\n".join(line for line in out["stdout"].splitlines() if re.fullmatch(r"video[0-9]+",line.strip()))
        if k == "services" and "stdout" in out:
            # Only service names relevant to cameras and cars; avoid gathering unrelated data.
            out["stdout"]="\n".join(line for line in out["stdout"].splitlines() if re.search(r"camera|vehicle|car_service|evs",line,re.I))
        if k == "media_camera" and "stdout" in out:
            # redact long lines that could contain camera calibration/vendor system detail.
            out["stdout"]="\n".join(line[:150] for line in out["stdout"].splitlines()[:70])
        result["data"][k]=out
    result["limitations"]=["Camera nodes are not proof of stream access.","No raw frames or ACC/radar data were requested.","No writes or configuration changes were performed."]
    return result

def main():
    p=argparse.ArgumentParser(description="Read-only, standard ADB metadata inventory")
    p.add_argument("--serial",help="ADB-authorized device serial, if more than one")
    p.add_argument("--output",default="mg_hs_probe.json")
    args=p.parse_args()
    report=inspect(args.serial)
    path=Path(args.output)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{report['status']} -> {path}")

if __name__=="__main__":main()
