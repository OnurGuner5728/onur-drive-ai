import numpy as np
import pytest
from onur_drive.vision import SyntheticScene,YoloXOnnxDetector,NoDetector

def test_synthetic_source_has_label_and_car():
    im, objects = SyntheticScene().read()
    assert im.shape == (540,960,3)
    assert objects[0].category == "car"

def test_onnx_parser_rejects_wrong_output():
    with pytest.raises(ValueError):YoloXOnnxDetector.postprocess(np.zeros((1,84)),(400,400,3),1)

def test_onnx_parser_single_detection():
    out=np.zeros((3,85),dtype=np.float32)
    out[0,:5]=[160,150,80,60,.91]
    out[0,5+2]=.95
    objects=YoloXOnnxDetector.postprocess(out,(300,400,3),1)
    assert len(objects)==1
    assert objects[0].category=="car"
    assert objects[0].box==(120,120,200,180)

def test_no_detector_returns_no_fake_objects():
    assert NoDetector().infer(np.zeros((30,30,3),np.uint8))==[]
