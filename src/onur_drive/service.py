"""Local-only FastAPI dashboard with an optional read-only video runner."""
from __future__ import annotations
from collections import deque
from dataclasses import asdict
from pathlib import Path
from contextlib import asynccontextmanager
import json
import threading
import time
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from .schema import FrameState, Provenance
from .vision import SyntheticScene, VideoSource, NoDetector
from .multicam import QuadSyntheticSource, QuadVideoSource, compose_mosaic
from .risk import AlertPolicy
from .voice import Speaker
from .tracking import IoUTracker

DASHBOARD = """<!doctype html><html lang='tr'><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Onur Drive AI | Laboratuvar</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#070f1b;color:#ecf2fa;margin:0}header{display:flex;justify-content:space-between;align-items:center;padding:24px 4vw;border-bottom:1px solid #263448}.brand{font-weight:800;letter-spacing:2px;color:#6fe7d3}.tag{color:#f7bb62;border:1px solid #9e6837;border-radius:12px;padding:9px 12px;font-size:12px}main{max-width:1350px;margin:auto;padding:28px 4vw;display:grid;grid-template-columns:1fr 310px;gap:22px}.panel{border:1px solid #27354a;border-radius:18px;background:#101a2a;overflow:hidden}h2{font-size:17px;padding:20px;margin:0}.view{display:block;width:100%;background:#080d16}aside{display:flex;flex-direction:column;gap:18px}.metric{padding:18px;border-top:1px solid #253144}.metric strong{display:block;font-size:20px;margin-top:6px}.value{color:#95a6bd;font-size:12px;text-transform:uppercase;letter-spacing:1px}.history{padding:16px;font-size:14px;min-height:200px}.history div{padding:10px 0;border-bottom:1px solid #293344}.foot{margin:18px 4vw 30px;color:#9babbe;font-size:13px}.warn{color:#ffc66f}@media(max-width:830px){main{grid-template-columns:1fr}}
</style><header><div><div class='brand'>ONUR DRIVE AI</div><div style='font-size:12px;color:#9bacbf;margin-top:5px'>GÖRÜNTÜ İŞLEME LABORATUVARI · v0.1</div></div><span class='tag'>SÜRÜŞ GÜVENLİĞİ İÇİN ONAYLI DEĞİL</span></header><main><section class='panel'><h2>Canlı işleme önizlemesi</h2><img class='view' src='/stream' alt='Video önizleme'><div class='metric'><span class='value'>Kaynak</span><strong id='source'>Bağlanıyor</strong></div></section><aside><section class='panel'><h2>Algılama sağlığı</h2><div class='metric'><span class='value'>Durum</span><strong id='state'>Bekleniyor</strong></div><div class='metric'><span class='value'>Kare</span><strong id='fps'>—</strong></div><div class='metric'><span class='value'>Nesne</span><strong id='objects'>—</strong></div><div class='metric'><span class='value'>Uyarı</span><strong id='alert'>—</strong></div></section><section class='panel'><h2>Olay günlüğü</h2><div class='history' id='history'>Henüz uyarı yok.</div></section></aside></main><div class='foot'>Bu sistem deneysel bir laboratuvar prototipidir. Kameranın gördüğü alanın güvenli olduğunu asla varsaymayın. Fren, gaz, direksiyon veya ACC kontrolü bulunmaz.</div><script>
async function tick(){try{const r=await fetch('/api/status',{cache:'no-store'});const j=await r.json(); for(const [id,value] of Object.entries({source:j.source,state:j.state,fps:j.fps+' FPS',objects:j.objects,alert:j.last_alert||'—'})){document.getElementById(id).textContent=value};document.getElementById('history').innerHTML=j.history.slice(-5).reverse().map(e=>'<div>'+escapeHtml(e.text)+'</div>').join('')||'Henüz uyarı yok.';}catch(e){document.getElementById('state').textContent='BAĞLANTI YOK';}}
function escapeHtml(t){return t.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}
setInterval(tick,750);tick();</script></html>"""

class CameraRunner:
    def __init__(self, source_spec="synthetic", detector=None, record_dir=None, fps_limit=15, voice_enabled=False, voice_dir=None, allow_espeak=False):
        self.source_spec=source_spec
        self.source=(QuadSyntheticSource() if source_spec=="multi-synthetic" else
                     QuadVideoSource(source_spec[6:]) if source_spec.startswith("multi:") else
                     SyntheticScene() if source_spec=="synthetic" else VideoSource(source_spec))
        self.synthetic=source_spec in ("synthetic", "multi-synthetic")
        self.detector=detector or NoDetector()
        self.policy=AlertPolicy()
        self.trackers={name:IoUTracker() for name in ("front","right","rear","left")}
        self.voice=Speaker(enabled=voice_enabled,voice_dir=voice_dir,allow_espeak=allow_espeak)
        self.fps_limit=fps_limit
        self.events=deque(maxlen=100)
        self.jpeg=b""
        self.seq=0;self.running=False; self.stopped=False
        self.state="STARTING"
        self.last_alert=""
        self.objects=0
        self.fps=0.0
        self.last_frame_s=0.0
        self.record_dir=Path(record_dir) if record_dir else None
        if self.record_dir:self.record_dir.mkdir(parents=True,exist_ok=True)
        self.thread=None

    @property
    def provenance(self):
        return Provenance.SIMULATED if self.synthetic else Provenance.UNVALIDATED

    def start(self):
        if self.thread is not None:return
        self.running=True
        self.thread=threading.Thread(target=self._safe_loop,daemon=True)
        self.thread.start()

    def stop(self):
        self.running=False
        if self.thread:self.thread.join(timeout=4)
        if hasattr(self.source,"close"):self.source.close()

    def _log_alert(self,alert):
        event={"code":alert.code,"level":alert.level.value,"text":alert.text,"time":alert.timestamp_s,"evidence":alert.evidence}
        self.events.append(event);self.last_alert=alert.text
        if self.record_dir:
            with (self.record_dir/"events.jsonl").open("a",encoding="utf-8") as f:
                f.write(json.dumps(event,ensure_ascii=False)+"\n")
        self.voice.speak(alert)

    def _safe_loop(self):
        try:self._loop()
        except Exception as exc:
            self.state="ERROR_"+type(exc).__name__
            self.running=False
            self.stopped=True

    def _loop(self):
        prior=time.monotonic()
        while self.running:
            started=time.monotonic()
            if hasattr(self.source, "read_multi"):
                samples=self.source.read_multi()
                if samples is None:
                    self.state="END_OF_SOURCE";break
            else:
                image,labels=self.source.read()
                if image is None:
                    self.state="END_OF_SOURCE";break
                samples={"front":(image,labels)}
            self.seq+=1
            self.objects=0
            rendered={}
            now=time.monotonic()
            for camera_id,(camera_img,synthetic_detections) in samples.items():
                detections=synthetic_detections if self.synthetic else self.detector.infer(camera_img)
                detections=self.trackers[camera_id].update(detections)
                self.objects+=len(detections)
                frame_state=FrameState(camera_id,now,self.provenance,camera_img.shape[1],camera_img.shape[0],self.seq)
                for a in self.policy.process(frame_state,now,detections):self._log_alert(a)
                for d in detections:
                    x1,y1,x2,y2=d.box
                    color=(52,215,120) if d.category!="unclassified_motion" else (0,190,255)
                    cv2.rectangle(camera_img,(x1,y1),(x2,y2),color,2)
                    cv2.putText(camera_img,f"{d.category} {d.confidence:.2f}",(x1,max(14,y1-9)),cv2.FONT_HERSHEY_SIMPLEX,.55,color,2)
                rendered[camera_id]=camera_img
            img=compose_mosaic(rendered) if len(rendered)>1 else rendered["front"]
            cv2.rectangle(img,(0,img.shape[0]-35),(img.shape[1],img.shape[0]),(10,19,29),-1)
            label="SIMULASYON" if self.synthetic else "DOGRULANMAMIS VIDEO - SURUS UYARISI YOK"
            cv2.putText(img,label,(15,img.shape[0]-12),cv2.FONT_HERSHEY_SIMPLEX,.55,(40,225,240),2)
            ok,jpeg=cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,78])
            if ok:self.jpeg=jpeg.tobytes()
            self.last_frame_s=now
            self.fps=round(1/max(.001,now-prior),1);prior=now
            self.state="SIMULATOR" if self.synthetic else "UNVALIDATED_VIDEO"
            if self.record_dir and self.seq % 30==1:
                # ONE diagnostic snapshot only to limit privacy and disk wear
                if self.seq==1:cv2.imwrite(str(self.record_dir/"first_frame.jpg"),img)
            remain=1/max(.1,self.fps_limit)-(time.monotonic()-started)
            if remain>0:time.sleep(remain)
        self.running=False;self.stopped=True

    def status(self):
        stale=self.last_frame_s!=0 and time.monotonic()-self.last_frame_s>2
        return {"state":"FRAME_STALE" if stale else self.state,"source":self.source_spec,
                "fps":self.fps,"objects":self.objects,"last_alert":self.last_alert,
                "history":list(self.events),"frames":self.seq,
                "vehicle_control":"NOT_IMPLEMENTED", "verified_oem_access":False}


def make_app(runner: CameraRunner):
    @asynccontextmanager
    async def lifespan(app):
        runner.start()
        try:
            yield
        finally:
            runner.stop()
    app=FastAPI(title="Onur Drive AI laboratory",docs_url=None,redoc_url=None,lifespan=lifespan)
    @app.get("/",response_class=HTMLResponse)
    def home():return DASHBOARD
    @app.get("/api/status")
    def status():return runner.status()
    @app.get("/stream")
    def stream():
        def frames():
            while runner.running:
                frame=runner.jpeg
                if frame:yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+frame+b"\r\n"
                time.sleep(.09)
        return StreamingResponse(frames(),media_type="multipart/x-mixed-replace; boundary=frame")
    return app
