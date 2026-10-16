"""Deterministic read-only notification policy. Safety gates are fail closed."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import replace
from .schema import Alert, Level, Detection, DistanceSample, FrameState, Provenance

class AlertPolicy:
    """Not a certified driver safety algorithm.

    Most video-only messages are object-visibility *information*, not driving
    instructions. Safety-critical following-distance messages require independently
    verified range and ego speed. Unknown or uncalibrated measurements never pass.
    """
    def __init__(self, min_confirmed_frames=3, cooldown_s=12, stale_s=.8):
        self.min_confirmed_frames=min_confirmed_frames
        self.cooldown_s=cooldown_s
        self.stale_s=stale_s
        self.seen=defaultdict(int)
        self.last_emitted={}
        self.last_seq={}
        self._unavailable_sent=set()

    def _emit(self, code, level, message, now, evidence):
        if now-self.last_emitted.get(code, float('-inf')) < self.cooldown_s:
            return None
        self.last_emitted[code]=now
        return Alert(code,level,message,now,evidence)

    def process(self, state: FrameState, now: float, detections: list[Detection], distance: DistanceSample | None = None):
        if now-state.monotonic_s > self.stale_s or now < state.monotonic_s-.25:
            if state.camera_id not in self._unavailable_sent:
                self._unavailable_sent.add(state.camera_id)
                return [Alert("CAMERA_STALE",Level.UNAVAILABLE,"Kamera görüntüsü güncel değil.", now, {"camera":state.camera_id})]
            return []
        if state.camera_id in self._unavailable_sent:
            self._unavailable_sent.remove(state.camera_id)
        if self.last_seq.get(state.camera_id)==state.sequence:
            return []
        self.last_seq[state.camera_id]=state.sequence
        outputs=[]
        relevant={"car","truck","bus","motorcycle","bicycle","person"}
        observed={d.category for d in detections if d.confidence >= .65 and d.category in relevant}
        for cat in relevant:
            key=(state.camera_id,cat)
            self.seen[key] = min(100,self.seen[key]+1) if cat in observed else 0
        if state.provenance == Provenance.UNVALIDATED:
            # Do not emit actionable audio for unvalidated sources; annotations only.
            return []
        if state.camera_id=="front":
            for cat,word in (("person","Yaya"),("motorcycle","Motosiklet"),("car","Araç")):
                if self.seen[("front",cat)]>=self.min_confirmed_frames:
                    a=self._emit("FRONT_"+cat.upper(),Level.INFO,f"Ön görüntüde {word.lower()} algılandı.",now, {"class":cat,"camera":"front","source":state.provenance.value})
                    if a:outputs.append(a)
                    break  # one concise message per frame
        if state.camera_id in ("left","right"):
            for cat in ("car","motorcycle","person"):
                if self.seen[(state.camera_id,cat)]>=self.min_confirmed_frames:
                    side="Sol" if state.camera_id=="left" else "Sağ"
                    a=self._emit(f"SIDE_{state.camera_id.upper()}_{cat.upper()}",Level.INFO,f"{side} kamerada {dict(car='araç', motorcycle='motosiklet', person='yaya')[cat]} algılandı.",now,{"camera":state.camera_id,"class":cat})
                    if a:outputs.append(a)
                    break
        if distance is not None:
            a=self.check_distance(distance,now,state.provenance)
            if a:outputs.append(a)
        return outputs

    def check_distance(self, sample: DistanceSample, now: float, provenance: Provenance):
        if not sample.authorized or not sample.calibrated or sample.confidence < .95:
            return None
        if provenance == Provenance.UNVALIDATED:
            return None
        if sample.source not in ("simulated_sensor", "verified_range_sensor"):
            return None
        if now-sample.monotonic_s > .25 or now < sample.monotonic_s-.1:
            return None
        if not (0 < sample.distance_m < 500 and 0 <= sample.ego_speed_kmh <= 260):
            return None
        speed=sample.ego_speed_kmh / 3.6
        if speed < 4: return None
        following_time=sample.distance_m/speed
        if following_time >= 1.5: return None
        return self._emit("FOLLOWING_GAP",Level.CAUTION,
                          "Takip mesafesi kısa görünüyor; çevreni kontrol et.",now,
                          {"headway_s":round(following_time,2),"sensor":sample.source,"simulated":provenance==Provenance.SIMULATED})
