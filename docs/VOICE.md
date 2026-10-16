# Turkish natural speech assets

The event engine does not generate open-ended speech. It maps accepted event codes to immutable safety-reviewed Turkish phrases in `src/onur_drive/voice.py`. It rejects any mismatched phrase. This avoids model hallucinations. No audio is played by default.

To use natural spoken voice, record/generate clean licensed Turkish WAV files and place them in `assets/voice/` (folder may be created by operator):

| WAV filename | Exactly required phrase |
|---|---|
| FRONT_CAR.wav | Ön görüntüde araç algılandı. |
| FRONT_PERSON.wav | Ön görüntüde yaya algılandı. |
| FRONT_MOTORCYCLE.wav | Ön görüntüde motosiklet algılandı. |
| SIDE_RIGHT_CAR.wav | Sağ kamerada araç algılandı. |
| SIDE_LEFT_CAR.wav | Sol kamerada araç algılandı. |
| FOLLOWING_GAP.wav | Takip mesafesi kısa görünüyor; çevreni kontrol et. |
| CAMERA_STALE.wav | Kamera görüntüsü güncel değil. |

Side person/motorcycle phrases are also listed in `voice.py`. Use consistent sample rate, mono PCM WAV, and verify playback locally; no voice cloning of third parties without permission. For a future offline studio, Chatterbox Multilingual V3 is an option but requires model weights/hardware, license and Turkish quality verification; it is NOT integrated into this environment. Edge TTS is NOT used.

`onur-drive --source multi-synthetic --voice --voice-dir assets/voice` will play matching WAV clips when present. Android diagnostic app also tests onboard installed tr-TR TTS only (quality may vary).
