#!/usr/bin/env python3
"""Renders a lab-only four-camera synthetic demo video; no actual driving footage."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from onur_drive.multicam import QuadSyntheticSource,compose_mosaic
from onur_drive.risk import AlertPolicy
from onur_drive.schema import FrameState,Provenance
import cv2

root=Path(__file__).resolve().parents[1]
out=root/"examples"/"onur_drive_4cam_SIMULASYON.mp4"
preview=root/"examples"/"onur_drive_4cam_onizleme.jpg"
source=QuadSyntheticSource()
policy=AlertPolicy()
fps=15
writer=cv2.VideoWriter(str(out),cv2.VideoWriter_fourcc(*"mp4v"),fps,(1280,720))
if not writer.isOpened(): raise RuntimeError("VideoWriter cannot open mp4v")
alerts=[]
for i in range(180):
    sources=source.read_multi()
    tiles={}
    for name,(frame,detections) in sources.items():
        for detection in detections:
            x1,y1,x2,y2=detection.box
            cv2.rectangle(frame,(x1,y1),(x2,y2),(68,235,148),2)
            cv2.putText(frame,f"{detection.category}: {detection.confidence:.2f}",(x1,max(20,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.6,(68,235,148),2)
        s=FrameState(name, i/fps,Provenance.SIMULATED,frame.shape[1],frame.shape[0],i+1)
        alerts.extend(policy.process(s,i/fps,detections))
        tiles[name]=frame
    canvas=compose_mosaic(tiles)
    if alerts:
        cv2.rectangle(canvas,(0,666),(1280,720),(6,25,35),-1)
        # cv2 text is ASCII; Turkish dialogue persists in JSON test report.
        cv2.putText(canvas,f"LAB ALERT: {alerts[-1].code}",(20,701),cv2.FONT_HERSHEY_SIMPLEX,.75,(80,235,245),2)
    cv2.rectangle(canvas,(700,676),(1279,719),(10,26,38),-1)
    cv2.putText(canvas,"SIMULASYON - OEM KAMERA DEGIL",(722,705),cv2.FONT_HERSHEY_SIMPLEX,.65,(20,225,245),2)
    if i==95:cv2.imwrite(str(preview),canvas)
    writer.write(canvas)
writer.release()
(root/"examples"/"demo_events.json").write_text(__import__('json').dumps(
    [{"type":a.code,"severity":a.level.value,"spoken_text":a.text,"time":round(a.timestamp_s,2)} for a in alerts],ensure_ascii=False,indent=2),encoding='utf-8')
print('video',out,'size',out.stat().st_size,'preview',preview)
