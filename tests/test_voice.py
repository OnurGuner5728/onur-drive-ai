from onur_drive.voice import Speaker
from onur_drive.schema import Alert,Level

def test_speech_disabled_by_default():
    s=Speaker()
    assert not s.speak(Alert('FRONT_CAR',Level.INFO,'Ön görüntüde araç algılandı.',2))

def test_unapproved_phrasing_cannot_speak():
    s=Speaker(enabled=True,allow_espeak=True)
    assert not s.speak(Alert('FRONT_CAR',Level.INFO,'Hızlan!',2))
