import time
from onur_drive.service import CameraRunner,make_app

def test_simulator_and_json_api():
    runner=CameraRunner(fps_limit=30)
    runner.start()
    time.sleep(.25)
    stats=runner.status()
    runner.stop()
    assert stats['source']=='synthetic'
    assert stats['frames']>0
    assert stats['verified_oem_access'] is False
    assert stats['vehicle_control']=='NOT_IMPLEMENTED'
    assert runner.jpeg.startswith(b'\xff\xd8')

def test_fastapi_routes_exist():
    runner=CameraRunner()
    app=make_app(runner)
    routes={r.path for r in app.routes}
    assert {'/','/stream','/api/status'}<=routes

def test_four_camera_demo_generates_mosaic_and_alerts():
    runner=CameraRunner(source_spec="multi-synthetic",fps_limit=15)
    runner.start();time.sleep(.35)
    st=runner.status()
    runner.stop()
    assert st['frames']>0
    assert st['objects']>=3
    assert runner.jpeg.startswith(b'\xff\xd8')
