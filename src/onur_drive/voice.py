"""Turkish voice notification. Only preapproved texts. No AI hallucinated commands.

Preferred runtime: pre-recorded natural speech at assets/voice/{code}.wav.
Optional dev fallback: installed espeak Turkish voice; disabled by default.
"""
from pathlib import Path
import shutil
import subprocess
import threading

APPROVED = {
 "FRONT_CAR": "Ön görüntüde araç algılandı.",
 "FRONT_PERSON": "Ön görüntüde yaya algılandı.",
 "FRONT_MOTORCYCLE": "Ön görüntüde motosiklet algılandı.",
 "FOLLOWING_GAP": "Takip mesafesi kısa görünüyor; çevreni kontrol et.",
 "CAMERA_STALE": "Kamera görüntüsü güncel değil.",
 "SIDE_RIGHT_CAR": "Sağ kamerada araç algılandı.",
 "SIDE_LEFT_CAR": "Sol kamerada araç algılandı.",
 "SIDE_RIGHT_MOTORCYCLE": "Sağ kamerada motosiklet algılandı.",
 "SIDE_LEFT_MOTORCYCLE": "Sol kamerada motosiklet algılandı.",
 "SIDE_RIGHT_PERSON": "Sağ kamerada yaya algılandı.",
 "SIDE_LEFT_PERSON": "Sol kamerada yaya algılandı.",
}
class Speaker:
    def __init__(self, enabled=False, voice_dir=None, allow_espeak=False):
        self.enabled=enabled
        self.voice_dir=Path(voice_dir or "assets/voice")
        self.allow_espeak=allow_espeak
        self._busy=threading.Lock()
    def speak(self, alert):
        if not self.enabled or self._busy.locked():return False
        # Only whitelisted warning IDs can speak without installed verified voice packs.
        if alert.code not in APPROVED or alert.text != APPROVED[alert.code]:return False
        prerecorded=self.voice_dir/f"{alert.code}.wav"
        if prerecorded.is_file() and shutil.which("ffplay"):
            cmd=["ffplay","-nodisp","-autoexit","-loglevel","quiet",str(prerecorded)]
        elif self.allow_espeak and shutil.which("espeak"):
            cmd=["espeak","-v","tr","-s","145",alert.text]
        else:return False
        def run():
            with self._busy:
                try: subprocess.run(cmd,timeout=10,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
                except (OSError,subprocess.TimeoutExpired):pass
        threading.Thread(target=run,daemon=True).start()
        return True
