"""Four-camera lab broker; camera views never cross-contaminate trackers or evidence.

For live sources, all four must be already authorized by the host OS. Does not
claim that OEM cameras are available, and never starts OEM camera services.
"""
from __future__ import annotations
import cv2
import numpy as np
from .schema import Detection
from .vision import SyntheticScene, VideoSource

CAMERAS=("front","right","rear","left")

class QuadSyntheticSource:
    def __init__(self):
        self.generators={name:SyntheticScene(640,360) for name in CAMERAS}
    def read_multi(self):
        result={}
        for name, generator in self.generators.items():
            im,obj=generator.read()
            im=cv2.convertScaleAbs(im,alpha=1.0, beta={"front":0,"right":-12,"rear":-25,"left":12}[name])
            if name != "front":
                # Synthetic label and sprites demonstrate camera-specific detection dispatch.
                obj=[]
                if name in ("left","right"):
                    h,w=im.shape[:2]
                    box=(int(w*.65),int(h*.5),int(w*.80),int(h*.75))
                    cv2.rectangle(im,box[:2],box[2:],(230,100,50),-1)
                    obj=[Detection("car",.94,box,camera_id=name)]
            result[name]=(im,obj)
        return result
    def close(self):pass

class QuadVideoSource:
    def __init__(self, spec):
        # Example: front=/path/f.mp4,right=/path/r.mp4,rear=/path/b.mp4,left=/path/l.mp4
        parts={}
        for pair in spec.split(';'):
            if '=' not in pair: raise ValueError("Each input must be cam=video_path_or_camera:N")
            name,value=pair.split('=',1)
            if name not in CAMERAS or name in parts or not value:
                raise ValueError("Expected unique front, right, rear, left inputs")
            parts[name]=value
        if set(parts)!=set(CAMERAS):raise ValueError("All four named cameras are required")
        self.sources={name:VideoSource(parts[name]) for name in CAMERAS}
    def read_multi(self):
        out={}
        for name,src in self.sources.items():
            img,_=src.read()
            if img is None:return None
            out[name]=(img,[])
        return out
    def close(self):
        for src in self.sources.values():src.close()

def compose_mosaic(frames:dict, tile_width=640, tile_height=360):
    """Returns display-only 2x2 mosaic, not a fused bird's-eye geometric view."""
    tiles=[]
    for cam in CAMERAS:
        img=frames[cam]
        h,w=img.shape[:2]
        if h<1 or w<1:raise ValueError("Empty image")
        tile=cv2.resize(img,(tile_width,tile_height))
        cv2.rectangle(tile,(0,0),(tile_width,35),(12,24,34),-1)
        cv2.putText(tile,cam.upper(),(14,25),cv2.FONT_HERSHEY_SIMPLEX,.72,(88,234,215),2,cv2.LINE_AA)
        tiles.append(tile)
    return np.vstack([np.hstack(tiles[:2]),np.hstack(tiles[2:])])
