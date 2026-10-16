"""CLI for a *local-only* simulation or explicitly supplied video source."""
import argparse
from pathlib import Path
from .service import CameraRunner, make_app
from .vision import NoDetector, HogPersonDetector, MotionDetector, YoloXOnnxDetector

def build_parser():
    p=argparse.ArgumentParser(description="Onur Drive AI offline LAB (not safe for live driving)")
    p.add_argument("--source",default="synthetic",help="synthetic, multi-synthetic, local video, camera:N, or multi:front=...;right=...;rear=...;left=...")
    p.add_argument("--detector",default="none",choices=["none","hog-person","motion","yolox"])
    p.add_argument("--model",help="Locally provided decoded YOLOX COCO ONNX model")
    p.add_argument("--input-size",type=int,default=416)
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--save-events",help="Optional local diagnostic directory; snapshots contain video data")
    p.add_argument("--voice",action="store_true",help="Only speaks when prerecorded approved WAV clips are present")
    p.add_argument("--voice-dir",default="assets/voice")
    p.add_argument("--espeak-dev-fallback",action="store_true",help="Use robotic eSpeak only as explicit dev fallback")
    return p

def main():
    p=build_parser();args=p.parse_args()
    if args.source in ("synthetic", "multi-synthetic") and args.detector!="none":p.error("synthetic source uses its own labeled ground-truth; detector must be none")
    if args.source not in ("synthetic","multi-synthetic") and args.detector=="none":
        print("Note: live/video preview is ON, AI detections OFF (no model supplied).")
    if args.detector=="motion" and args.source.startswith("camera:"):
        p.error("motion detector is not suitable for a moving-vehicle camera")
    if args.detector=="yolox" and not args.model:p.error("--model /path/to/decoded-yolox.onnx is required")
    if args.port<1024 or args.port>65535:p.error("port must be 1024..65535")
    detector={"none":lambda:NoDetector(),"hog-person":lambda:HogPersonDetector(),"motion":lambda:MotionDetector(),"yolox":lambda:YoloXOnnxDetector(args.model,args.input_size)}[args.detector]()
    runner=CameraRunner(args.source,detector,args.save_events,voice_enabled=args.voice,voice_dir=args.voice_dir,
                        allow_espeak=args.espeak_dev_fallback)
    import uvicorn
    print(f"LAB ONLY: http://127.0.0.1:{args.port} | no vehicle control | no hardware bypass")
    uvicorn.run(make_app(runner),host="127.0.0.1",port=args.port,log_level="warning")

if __name__=="__main__":main()
