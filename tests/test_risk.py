import pytest
from onur_drive.risk import AlertPolicy
from onur_drive.schema import Detection, FrameState, Provenance, DistanceSample

def state(sequence, ts=1, provenance=Provenance.SIMULATED, camera="front"):
    return FrameState(camera,ts,provenance,960,540,sequence)

def car():return Detection("car",.91,(10,10,90,90))

def test_three_frames_before_alert():
    p=AlertPolicy()
    assert p.process(state(1),1,[car()]) == []
    assert p.process(state(2),1.1,[car()]) == []
    alerts=p.process(state(3),1.2,[car()]);assert len(alerts)==1
    assert alerts[0].code=="FRONT_CAR"

def test_stale_frame_rejected_and_warns_once():
    p=AlertPolicy()
    first=p.process(state(1),3.0,[car()])
    assert first[0].code=="CAMERA_STALE"
    assert p.process(state(2),3.1,[car()]) == []

def test_unvalidated_frames_never_produce_driving_alert():
    p=AlertPolicy()
    for i in range(10):
        assert p.process(state(i+1,1+i/10,Provenance.UNVALIDATED),1+i/10,[car()]) == []

def test_unknown_distance_never_triggers():
    p=AlertPolicy()
    s=DistanceSample(3,90,1,authorized=False,calibrated=False,confidence=.99)
    assert p.check_distance(s,1,Provenance.VALIDATED) is None

def test_validated_headway_simulation():
    p=AlertPolicy()
    s=DistanceSample(9,90,1,authorized=True,calibrated=True,source="simulated_sensor",confidence=.99)
    a=p.check_distance(s,1,Provenance.SIMULATED)
    assert a and a.code=="FOLLOWING_GAP"
    assert "Fren" not in a.text and "hızlan" not in a.text

def test_outdated_sensor_rejected():
    p=AlertPolicy()
    s=DistanceSample(9,90,1,authorized=True,calibrated=True,source="verified_range_sensor",confidence=.99)
    assert p.check_distance(s,1.5,Provenance.VALIDATED) is None

def test_impossible_sample_does_not_trigger():
    p=AlertPolicy()
    s=DistanceSample(-9,90,1,authorized=True,calibrated=True,source="verified_range_sensor",confidence=.99)
    assert p.check_distance(s,1,Provenance.VALIDATED) is None

def test_wrong_camera_has_no_front_alert():
    p=AlertPolicy()
    for i in range(4):
        output=p.process(state(i+1,1+i/10, camera="rear"),1+i/10,[car()]);assert output==[]

def test_repeated_sequence_is_ignored():
    p=AlertPolicy()
    p.process(state(1),1,[car()])
    p.process(state(1),1,[car()])
    assert p.process(state(2),1,[car()]) == []
