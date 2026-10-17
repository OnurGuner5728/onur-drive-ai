# ONUR DRIVE AI — MG HS 2023

> **HEDEF: ARAÇ İÇİNDE ÇALIŞAN YAPAY ZEKÂ SÜRÜŞ ASİSTANI.** Şu anda MG HS fabrika kameraları ve ACC/radar sensörleriyle çalışan sürüm **henüz yok**. Kesin donanım protokolü veya yetkili görüntü arayüzü saptanmadı. Araç kontrolüne müdahale yoktur.

## 1. Araç multimedya ekranı (öncelik)

**Android kamera erişim test APK'si (v0.2):** [GitHub Android sürümleri](https://github.com/OnurGuner5728/onur-drive-ai/releases/tag/v0.2.0-headunit-probe) — **derleme başarılı olursa** buradan indirilebilir.

Bu dosya Windows uygulaması değil, standart Android APK'dir. Multimedya sistemin üçüncü taraf APK kurulumunu **normal kullanıcı arayüzünden** destekliyorsa park halinde kurulabilir. İçindeki **Gerçek Kamera Testi** yalnızca kamuya açık `Camera2` arayüzünü dener; gerçek görüntü elde edilirse ilk bağlantı kanıtı oluşur. MG HS 2023'te kurulum veya kamera erişimi doğrulanmış değil. Araç OEM korumalarını aşan yöntemler bu projede bulunmaz.

**Olası durumlar:** 
- APK araç multimedya sistemine kurulabiliyorsa ve Camera2 canlı kareleri gösteriyorsa → görüntü işleme entegrasyonuna devam edilir.
- APK kurulabiliyor ama Camera2 kameraları yoksa → OEM kamera akışı farklı arayüzdedir; bu APK ile açılamaz.
- APK yüklenemiyorsa → fabrika yazılımının normal kullanıcı uygulama erişimi kapalıdır; ek donanım ve OEM yazılım değişikliği olmadan uygulanabilirliği gösterilemez.

Araç içi APK testi: [android-diagnostics/README.md](android-diagnostics/README.md). Mevcut paket **sertifikalı ADAS değildir, trafikte sürüş uyarısı için kullanılmaz.**

## 2. Windows laboratuvar sürümü (ARAÇ İÇİN DEĞİL)

Windows'ta 4 **sentetik** kamera demosunu tek tıkla açmak için [v0.2 LAB ZIP](https://github.com/OnurGuner5728/onur-drive-ai/releases/download/v0.2.0-lab/OnurDriveAI-Windows-TekTik-LAB-v0.2.zip) dosyasını bilgisayara indirip `BASLAT.bat` dosyasını çalıştırabilirsin. Bu dosya araca yüklenmez.

## ☕ Bir kahve ısmarla

Destek tamamen gönüllüdür: **[Patreon — Onur Güner](https://www.patreon.com/c/onurguner)**.

---



**Status (2026-10-17): Local working laboratory prototype. Not installed in the vehicle.**

Read-only driver-awareness research kit for MG HS 2023 360° AVM + adaptive cruise control, with universal video adapters. This repo contains a working 4-camera synthetic simulator, optional local video/camera analysis, basic per-camera IoU object tracking, Turkish notification rules, dashboard, a hardware capability read-only inventory, Android diagnostic app *source code*, tests and complete next-step gates.

**NOT a certified ADAS device; do not rely on it in traffic.** No gas, brake, steering, ACC, CAN, VHAL write, firmware patch, gear/speed spoofing, or OEM 360 speed-lock bypass exists in this source. **The MG HS factory cameras are not connected and their native interface remains unknown.** The MG4 project is merely precedent for a different car/platform.

## 1. Run tested simulator (Windows / Linux / macOS)

Prerequisites: Python 3.10+ and package installation permissions.

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell alternative: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m onur_drive.cli --source multi-synthetic
```

Open **http://127.0.0.1:8765** in a browser on the *same computer*. It intentionally binds localhost only. Or use `run_demo.sh` / `run_demo.bat` once dependencies are installed.

You can also run a one-camera demo: `onur-drive --source synthetic`.

Lab video: `examples/onur_drive_4cam_SIMULASYON.mp4`. All content is synthetic; no production vehicle access was achieved.

## 2. Process existing real video footage (NOT vehicle installation)

With no car-trained model installed, preview-only:

```bash
onur-drive --source /path/to/already-recorded-video.mp4
```

Experimental HOG pedestrian detector (not validated for driving):

```bash
onur-drive --source /path/to/clip.mp4 --detector hog-person
```

Experimental stationary-camera motion regions (not a vehicle detector; not suitable for a moving car):

```bash
onur-drive --source /path/to/STATIONARY.mp4 --detector motion
```

For actual vehicle/person/motorcycle categories, supply a valid **decoded COCO YOLOX ONNX** file obtained legitimately on your own computer. No pretrained weights are embedded in this zip. Export under license from [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX) with `decode_in_inference=True` and ONNX `[1,N,85]` output, then:

```bash
onur-drive --source /path/to/clip.mp4 --detector yolox --model /path/to/yolox_decoded.onnx --input-size 416
```

Check exported input size/layout and metadata before use. `--input-size 416` is appropriate only for a matching ONNX export. Vehicle-camera FOV, illumination and class thresholds require measured validation; this project has not performed one.

Four **separately authorized** input video sources can be previewed as a mosaic (synchronized display, *not* calibrated bird's-eye mapping):

```bash
onur-drive --source 'multi:front=/path/front.mp4;right=/path/right.mp4;rear=/path/rear.mp4;left=/path/left.mp4' --detector yolox --model /path/to/yolox_decoded.onnx
```

For Linux cameras, explicitly use `camera:N` in place of a path only when the current OS has already authorized capture; this never auto-unlocks OEM interfaces. Multi-source read is sequential; frame timestamps and camera synchronization need native OEM verification for real-time deployment.

## 3. Turkish speech

Structured alerts contain complete Turkish phrasing. Speech is OFF by default. Provide natural, approved voice files (uncompressed `.wav`) in `assets/voice/` using the code in `docs/VOICE.md`. Then use `--voice --voice-dir assets/voice`. Android diagnostic app has a **native Turkish TTS test**; availability depends on vehicle text-to-speech installation. Optional `--espeak-dev-fallback` only for a deliberately robotic developer test; not the production voice solution. No Edge TTS is used.

## 4. Head-unit read-only inspection: no modifications

`onur-probe --output mg_hs_probe.json` runs ONLY if a previously authorized ADB connection exists and Android Platform Tools is installed. If `adb` is not installed/authorized it produces a **NO ACCESS** status without trying any bypass. Inspect `src/onur_drive/probe.py` for the complete command allowlist.

Alternatively build `android-diagnostics/` **on a computer with the Android SDK**. A diagnostic APK was successfully compiled in GitHub Actions; it is **not bundled in the Windows LAB download and has not been installed in any MG HS**. It enumerates ordinary Camera2 cameras, Android platform properties and tests Turkish system TTS; does not capture OEM video or send control commands. Even if Camera2 returns an empty list the OEM camera could still be available through a privileged internal pipeline. See `android-diagnostics/README.md`.

Native Linux read-only V4L2 *format enumeration* example: `native/v4l2_capability_probe.cpp`. No streaming or control ioctls are used.

## 5. Gates before any MG HS in-car implementation

| Gate | Measured acceptance | Failure action |
| --- | --- | --- |
| G1 Head unit | Identified OS/CPU/software, installer/API permission | Stop OEM integration |
| G2 Camera source | Explicit authorized raw front/left/right/rear stream | Stop OEM integration |
| G3 Coexistence | OEM reverse/park/360 still works with separate reader parked | Stop integration |
| G4 Continuity | Native raw stream remains valid after OEM UI auto-closes (controlled track only) | Stop; no OEM speed override |
| G5 Latency | Measured capture timestamp freshness, FPS/drop rate and CPU/thermal overhead | Disable camera-dependent audio |
| G6 Vehicle data | Publicly accessible and verified read-only speed/range interface | No measured gap/TTC warnings |
| G7 Accuracy | Labelled real-world evaluation and false-negative / false-positive review | No safety claims or real driving use |

An unidentified raw video device (`/dev/video14` from MG4, for example) is NOT accepted as proof it belongs to MG HS. No way to guarantee these gates without the actual head unit or technical evidence. Failure is a **NO-GO** given the no-extra-hardware constraint.

## 6. Project structure

```
android-diagnostics/  Android read-only diagnostic UI (sources; CI build verified, not car-tested)
config/               MG HS user-confirmed vs unverified profile
native/               Linux V4L2 read-only metadata inventory
src/onur_drive/       vision, 4-camera broker, risk policy, voice, web UI, ADB metadata probe
scripts/              offline synthetic demonstration video generator
examples/             synthetic demonstration media and sample events
tests/                behavioral tests incl. no unauthorized inference/commands
docs/                 release checklist, voice data contract, provenance and evidence
```

## 7. Protect your privacy

HTTP server binds `127.0.0.1`, writes no video unless `--save-events` explicitly supplied, and writes only the first diagnostic frame plus JSONL event notifications when recording is enabled. Do not use public road recordings or identifiable plates without proper authorization. The program makes no external API calls or telemetry. App has no server cloud integration.

## 8. Reproducible verification

```bash
python -m pip install -e '.[test]'
pytest -q
python scripts/render_demo.py
onur-drive --source multi-synthetic
```

Compare README claims with `docs/STATUS.md` before calling it deployed. Source license: MIT for newly authored code; third-party model weights and datasets are **not** included. No third-party project code was copied from the cited reference implementations.


## GitHub automated build and offline labs

- CI workflow: [.github/workflows/lab-ci.yml](.github/workflows/lab-ci.yml) (Python 3.10/3.13 tests, synthetic video, native V4L2 scanner, Android diagnostic debug APK).
- See the [Actions page](https://github.com/OnurGuner5728/onur-drive-ai/actions) and open a **successful** run to download `onur-drive-readonly-android-diagnostics-debug`. A debug APK is a **diagnostic tool only**, never evidence of MG HS compatibility.
- The standalone example MP4 and JPG are generated via `python scripts/render_demo.py`; build artifacts are not checked into source control.
- On a lab machine with the listed Python dependencies already installed but **no internet**, use `ONUR_DRIVE_OFFLINE=1 ./install_and_run_linux_macos.sh`; this skips all downloads and uses the existing interpreter, and fails if required packages are missing.
- Test outcomes, including unverified vehicle conditions: [docs/KURULUM_DOGRULAMA_2026-10-17.md](docs/KURULUM_DOGRULAMA_2026-10-17.md).
