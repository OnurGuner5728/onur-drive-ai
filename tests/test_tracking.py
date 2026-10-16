from onur_drive.tracking import IoUTracker,iou
from onur_drive.schema import Detection

def d(x=10,kind='car'):return Detection(kind,.9,(x,10,x+100,60))

def test_box_iou():
    assert iou((0,0,10,10),(0,0,10,10))==1
    assert iou((0,0,10,10),(20,20,30,30))==0

def test_track_id_stable_when_overlap():
    t=IoUTracker()
    first=t.update([d()])[0].track_id
    second=t.update([d(20)])[0].track_id
    assert first==second

def test_track_id_distinct_classes():
    t=IoUTracker()
    car=t.update([d()])[0].track_id
    person=t.update([d(10,'person')])[0].track_id
    assert person!=car

def test_track_expires_on_missing_frames():
    t=IoUTracker(max_lost=1)
    one=t.update([d()])[0].track_id
    t.update([]);t.update([])
    two=t.update([d()])[0].track_id
    assert two!=one
