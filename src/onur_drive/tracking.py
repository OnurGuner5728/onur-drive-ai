"""Lightweight per-camera IoU tracker for event debouncing (not ByteTrack or ADAS)."""
from __future__ import annotations
from dataclasses import replace
from .schema import Detection

def iou(a, b):
    x1=max(a[0],b[0]);y1=max(a[1],b[1]);x2=min(a[2],b[2]);y2=min(a[3],b[3])
    inter=max(0,x2-x1)*max(0,y2-y1)
    va=max(0,a[2]-a[0])*max(0,a[3]-a[1]);vb=max(0,b[2]-b[0])*max(0,b[3]-b[1])
    return inter/(va+vb-inter) if va+vb-inter>0 else 0.0

class IoUTracker:
    def __init__(self, min_iou=.2, max_lost=7):
        self.min_iou=min_iou
        self.max_lost=max_lost
        self.next_id=1
        self.active={}

    def update(self, detections:list[Detection]):
        # Each instance serves exactly ONE physical camera. Do not fuse identities.
        age={key:lost+1 for key,(det,lost) in self.active.items()}
        result=[];used=set()
        ordered=sorted(detections,key=lambda d:d.confidence,reverse=True)
        for d in ordered:
            matches=[]
            for k,(old,lost) in self.active.items():
                if k in used or d.category != old.category:continue
                overlap=iou(d.box,old.box)
                if overlap>=self.min_iou:matches.append((overlap,k))
            if matches:
                _,key=max(matches)
            else:
                key=self.next_id;self.next_id+=1
            used.add(key);result.append(replace(d,track_id=key))
            self.active[key]=(d,0)
            age[key]=0
        for key in list(self.active):
            if key not in used:
                self.active[key]=(self.active[key][0],age[key])
                if age[key]>self.max_lost:del self.active[key]
        return result
