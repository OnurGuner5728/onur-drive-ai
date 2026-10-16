"""Demo source, real video source, and optional locally-supplied YOLOX ONNX model.

Important: the synthetic detector is only valid on synthetic frames.
OpenCV motion regions are unclassified and must not cause safety advice.
"""
from __future__ import annotations
import math
from pathlib import Path
import cv2
import numpy as np
from .schema import Detection, COCO_CLASSES

class SyntheticScene:
    def __init__(self, width=960, height=540):
        self.width, self.height = width, height
        self.counter = 0

    def read(self):
        self.counter += 1
        w, h = self.width, self.height
        im = np.full((h,w,3), (32, 43, 55), dtype=np.uint8)
        cv2.rectangle(im, (0,0),(w,int(h*.45)),(120,100,70),-1)
        cv2.rectangle(im, (0,int(h*.43)),(w,h),(54,57,62),-1)
        p = math.sin(self.counter*.07)*28
        cv2.line(im,(int(w*.49),int(h*.43)),(int(w*.25),h),(240,240,235),4)
        cv2.line(im,(int(w*.51),int(h*.43)),(int(w*.75),h),(240,240,235),4)
        for k in range(4):
            y=int(h*.5+k*55+(self.counter*3)%55)
            cv2.line(im,(w//2-4,y),(w//2-4,min(h,y+30)),(230,205,65),3)
        objects=[]
        # deterministic approaching lead vehicle, no real geometry
        scale= 0.58 + .15*(1+math.sin(self.counter*.03))
        x=int(w*.47+p); y=int(h*.51+35*scale)
        bw,bh=int(140*scale),int(104*scale)
        box=(x-bw//2,y-bh//2,x+bw//2,y+bh//2)
        cv2.rectangle(im,(box[0],box[1]),(box[2],box[3]),(40,100,230),-1)
        cv2.rectangle(im,(box[0]+10,box[1]+12),(box[2]-10,box[1]+bh//2),(150,190,230),-1)
        cv2.circle(im,(box[0]+18,box[3]),8,(18,18,18),-1)
        cv2.circle(im,(box[2]-18,box[3]),8,(18,18,18),-1)
        objects.append(Detection("car", .97, box))
        # person on shoulder after frame 50
        if self.counter>50:
            px=int(w*.80); py=int(h*.56)
            cv2.circle(im,(px,py-25),8,(190,160,150),-1)
            cv2.line(im,(px,py-14),(px,py+18),(240,220,100),9)
            cv2.line(im,(px,py+18),(px-9,py+43),(240,220,100),4)
            cv2.line(im,(px,py+18),(px+9,py+43),(240,220,100),4)
            objects.append(Detection("person",.98,(px-16,py-35,px+16,py+46)))
        cv2.putText(im,"SENTETIK TEST / GERCEK YOL DEGIL",(24,34),cv2.FONT_HERSHEY_SIMPLEX,.78,(30,245,245),2,cv2.LINE_AA)
        return im,objects

class VideoSource:
    def __init__(self, spec: str):
        # Only explicitly supplied local video/device. Never auto-scan head-unit devices.
        self.spec = spec
        if spec.startswith("camera:"):
            src=int(spec.split(":",1)[1])
        else:
            src=str(Path(spec).expanduser())
            if not Path(src).is_file():
                raise FileNotFoundError(src)
        self.cap=cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise RuntimeError(f"Video source cannot be opened: {spec}")

    def read(self):
        ok,frame=self.cap.read()
        return (frame if ok else None), []

    def close(self):
        self.cap.release()

class NoDetector:
    name="none"
    def infer(self,frame): return []

class HogPersonDetector:
    """Bundled OpenCV pedestrian detector, not validated for automotive use."""
    name="opencv_hog_person_experimental"
    def __init__(self):
        self.hog=cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    def infer(self,frame):
        h,w=frame.shape[:2]
        resized=cv2.resize(frame,(min(640,w),int(h*min(640,w)/w)))
        rects, weights=self.hog.detectMultiScale(resized,winStride=(8,8),padding=(8,8),scale=1.1)
        scale=w/resized.shape[1]
        out=[]
        for (x,y,bw,bh),score in zip(rects,weights):
            conf=max(.01,min(.99,float(score)/3))
            if conf < .35: continue
            out.append(Detection("person",conf,tuple(int(v*scale) for v in (x,y,x+bw,y+bh))))
        return out

class MotionDetector:
    """Motion candidate visualization for stationary cameras ONLY. No object classification."""
    name="unclassified_motion_stationary_only"
    def __init__(self):
        self.bg=cv2.createBackgroundSubtractorMOG2(history=100,varThreshold=25,detectShadows=False)
        self.count=0
    def infer(self,frame):
        self.count += 1
        mask=self.bg.apply(frame)
        if self.count < 20: return []
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((4,4),np.uint8))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        out=[]
        for cnt in contours:
            if cv2.contourArea(cnt) < 1000: continue
            x,y,w,h=cv2.boundingRect(cnt)
            out.append(Detection("unclassified_motion",.50,(x,y,x+w,y+h)))
        return out

class YoloXOnnxDetector:
    """YOLOX COCO ONNX decoded output [1,N,85].

    Accepts exported models with built-in grid decoding (decode_in_inference=True).
    Raw grid/anchor outputs are rejected rather than misinterpreted.
    """
    name="yolox_onnx_experimental"
    def __init__(self, path: str, input_size=416, conf=.4, nms=.45):
        p=Path(path)
        if not p.is_file(): raise FileNotFoundError(f"ONNX model is missing: {p}")
        self.net=cv2.dnn.readNetFromONNX(str(p))
        self.size=input_size
        self.conf=conf
        self.nms=nms

    @staticmethod
    def postprocess(out, frame_shape, ratio: float, conf=.4, nms=.45):
        a=np.asarray(out)
        if a.ndim == 3 and a.shape[0]==1: a=a[0]
        if a.ndim != 2 or a.shape[1] != 85:
            raise ValueError(f"Unsupported YOLOX output shape {a.shape}; expected [N,85]")
        h,w=frame_shape[:2]
        candidate_boxes=[]; scores=[]; kinds=[]
        for r in a:
            label=int(np.argmax(r[5:]))
            score=float(r[4]*r[5+label])
            if score<conf or label >= len(COCO_CLASSES) or not np.isfinite(score):continue
            cx,cy,bw,bh=map(float,r[:4])
            if not np.all(np.isfinite([cx,cy,bw,bh])) or bw<=0 or bh<=0:continue
            x1=max(0, min(w-1,int((cx-bw/2)/ratio)))
            y1=max(0, min(h-1,int((cy-bh/2)/ratio)))
            x2=max(0, min(w,int((cx+bw/2)/ratio)))
            y2=max(0, min(h,int((cy+bh/2)/ratio)))
            if x2<=x1 or y2<=y1:continue
            candidate_boxes.append([x1,y1,x2-x1,y2-y1]);scores.append(score);kinds.append(COCO_CLASSES[label])
        if not candidate_boxes:return []
        # Category-aware NMS prevents a car from suppressing a nearby person.
        result=[]
        for kind in sorted(set(kinds)):
            idxs=[i for i,k in enumerate(kinds) if k==kind]
            retained=cv2.dnn.NMSBoxes([candidate_boxes[i] for i in idxs], [scores[i] for i in idxs],conf,nms)
            for ki in np.array(retained).reshape(-1):
                j=idxs[int(ki)]; x,y,bw,bh=candidate_boxes[j]
                result.append(Detection(kind,float(scores[j]),(x,y,x+bw,y+bh)))
        return result

    def infer(self, frame):
        h,w=frame.shape[:2]
        ratio=min(self.size/h,self.size/w)
        im=cv2.resize(frame,(int(w*ratio),int(h*ratio)))
        padded=np.full((self.size,self.size,3),114,dtype=np.uint8)
        padded[:im.shape[0],:im.shape[1]]=im
        blob=np.ascontiguousarray(padded.transpose(2,0,1),dtype=np.float32)[None,...]
        self.net.setInput(blob)
        output=self.net.forward()
        return self.postprocess(output,frame.shape,ratio,self.conf,self.nms)
