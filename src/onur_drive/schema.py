"""Strict data contracts. Missing data is always unknown, never zero or safe."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Level(str, Enum):
    INFO = "INFO"
    CAUTION = "CAUTION"
    UNAVAILABLE = "UNAVAILABLE"

class Provenance(str, Enum):
    SIMULATED = "SIMULATED"
    UNVALIDATED = "UNVALIDATED"
    VALIDATED = "VALIDATED"

@dataclass(frozen=True)
class Detection:
    category: str
    confidence: float
    box: tuple[int,int,int,int]
    camera_id: str = "front"
    track_id: Optional[int] = None

    def __post_init__(self):
        if not (0 <= self.confidence <= 1):
            raise ValueError("confidence must be in [0, 1]")
        x1, y1, x2, y2 = self.box
        if x2 <= x1 or y2 <= y1:
            raise ValueError("invalid bounding box")

@dataclass(frozen=True)
class DistanceSample:
    distance_m: float
    ego_speed_kmh: float
    monotonic_s: float
    authorized: bool = False
    calibrated: bool = False
    source: str = "unknown"
    confidence: float = 0.0

@dataclass(frozen=True)
class Alert:
    code: str
    level: Level
    text: str
    timestamp_s: float
    evidence: dict = field(default_factory=dict)

@dataclass(frozen=True)
class FrameState:
    camera_id: str
    monotonic_s: float
    provenance: Provenance
    width: int
    height: int
    sequence: int

COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
]
