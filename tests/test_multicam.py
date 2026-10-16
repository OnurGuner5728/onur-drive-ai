import cv2
import numpy as np
import pytest
from onur_drive.multicam import QuadSyntheticSource,QuadVideoSource,compose_mosaic,CAMERAS

def test_mosaic_layout():
    f={n:np.ones((45,80,3),np.uint8) for n in CAMERAS}
    assert compose_mosaic(f,80,45).shape==(90,160,3)

def test_quad_synthetic_has_distinct_ids():
    frames=QuadSyntheticSource().read_multi()
    assert set(frames)==set(CAMERAS)
    assert frames['left'][1][0].camera_id=='left'
    assert frames['front'][1][0].camera_id=='front'

def test_quad_video_requires_all_cameras():
    with pytest.raises(ValueError):QuadVideoSource('front=missing.mp4')
