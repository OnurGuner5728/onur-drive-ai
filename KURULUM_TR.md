# ONUR DRIVE AI · MG HS 2023 · Kurulum ve sınırlar

## Bu paket şu anda neyi kurar?

- ✅ Dört kameralı **sentetik** laboratuvar simülasyonu (gerçek araç görüntüsü değil)
- ✅ Yerel tarayıcı paneli, anotasyonlu görüntü, nesne/sınıf bilgisi ve olay kaydı
- ✅ Python video işleme katmanı, çoklu kamera kaynağı adaptörü ve ONNX YOLOX parser
- ✅ Türkçe kısa uyarı karar sistemi, yalnızca güvenilir koşullarda konuşma kapısı
- ✅ Python testleri, yerel AVI/MP4/camera:N oynatma
- ✅ MG HS için **salt okunur** standart ADB envanteri ve Android tanılama uygulaması kaynak kodu
- ✅ V4L2 Linux cihazı yetenek kontrolü C++ kaynak kodu
- ❌ MG HS üzerine gerçek kurulum YAPILMADI
- ❌ MG HS'nin gerçek AVM/ADAS kamerasına erişildiği doğrulanmadı
- ❌ Sürekli fabrika kamera görüntüsü elde edildiği doğrulanmadı
- ❌ Araç işlemcisinde çalışan Android APK oluşmadı (Android SDK yok)
- ❌ Gerçek araç algılama ağırlığı ve doğal Türkçe ses dosyaları paketlenmedi
- ❌ ACC/radar takip mesafesi verisine erişim yok

**Önemli:** Bu bir sürüş güvenlik sistemi değil. Gerçek trafikte yönlendirme için kullanılamaz. OEM görüntü hız sınırlayıcısını aşmaz. Fren/gaz/direksiyon sistemine yazılım kodu bulunmaz.

## Bilgisayarda çalıştırma

Windows: `install_and_run_windows.bat` dosyasını çift tıkla. Python 3.10+ ve paket bağımlılıklarını indirebilmek için internet gerekir.

Linux/Mac: `./install_and_run_linux_macos.sh` çalıştır.

Arayüz: `http://127.0.0.1:8765` (yalnızca aynı bilgisayardan). Dört görüntü kaynağı sentetiktir.

Sadece tekrar çalıştırmak: Windows `run_demo.bat`, Linux/Mac `./run_demo.sh` (varsayılan dört kamera simülasyonu). Oynatılabilir örnek: `examples/onur_drive_4cam_SIMULASYON.mp4`.

## Kendi video kaydını test etme

```
python -m onur_drive.cli --source "C:\\path\\video.mp4" --detector hog-person
```

Bu, yalnızca OpenCV'nin sınırlı insan dedektörüyle laboratuvar analizidir. Gerçek araç tespiti için YOLOX ONNX model ağırlığını ayrıca eklemelisin. Ham ONNX model dosyası ZIP'te yoktur; `README.md` açıklıyor. Onaylanmamış görüntü kaynağından sürüşe yönelik sesli uyarı devre dışıdır.

## MG HS'ye bağlanma sırası

1. Araç park halindeyken multimedya yazılım sürümü/işletim sistemi yalnızca normal sistem menüsünden görülmeli.
2. Mevcut yetkilerle Android APK kurulabiliyorsa (yetki kırmadan), `android-diagnostics/` projesi ayrı bir Android SDK yüklü bilgisayarda derlenebilir. Bu APK yalnızca sistem bilgisi/Camera2 listesi/TTS testi yapar. OEM kamerayı başlatmaz.
3. Standart ADB zaten yetkilendirilmişse `onur-probe --output mg_hs_probe.json` komutu sadece sabit ve zararsız okuma komutlarını yürütür. Yetki yoksa erişim açmaya veya korumayı kaldırmaya çalışmaz.
4. Yetkilendirilmiş ve **belgelenmiş** fabrika kamera akışı bulunursa önce park halinde kayıt, kaynak aygıt sağlığı ve OEM öncelik testi yapılır. Aracın OEM geri-vites ve 360° işlevinin bozulmaması şarttır.
5. Hız eşiği üzerindeki **gerçek ham akış sürekliliği** yalnızca uygun kontrollü test ortamında doğrulanabilir. OEM hız eşiği değiştirilmez. Ham akış kesiliyorsa ek donanım olmadan çözüm **NO-GO**.
6. ACC ölçümü için ayrıca izinli ve doğrulanmış veri erişim yolu gerekir. Radar mesafesi bilinmiyorsa takip mesafesi uyarısı kapalıdır.

## Karar: ulaşılmayan hedef nasıl raporlanır?

`ACCESS_DENIED` = Arayüze izin yok. `NO_VIDEO_SOURCE` = Görüntü akışı bulunamadı. `STREAM_STOPS` = OEM UI kapanınca ham görüntü de kesiliyor. Bu durumların hiçbirine firmware/hız/CAN müdahalesi yapılmaz.

Bu adımlar tamamlanmadıkça "araç üzerine kuruldu" veya "MG kameraları çalışıyor" denemez. Aracına uzaktan fiziksel/sistem erişimim olmadığı için bunları kendi başıma ölçemiyorum.


## GitHub'a push ve otomatik APK derlemesi

- Repo: https://github.com/OnurGuner5728/onur-drive-ai
- Actions: https://github.com/OnurGuner5728/onur-drive-ai/actions
- `Laboratory CI and Android diagnostic APK` akışında **başarılı** bir çalıştırma aç; `Artifacts` içinden `onur-drive-readonly-android-diagnostics-debug` dosyasını indir. Bu dosya yalnızca tanılama içindir, araç kamerasına erişim sağlamaz.
- `onur-drive-lab-demo` çıktısı, gerçek araç görüntüsü içermeyen sentetik MP4/JPG örneğidir.
- Çevrimdışı Linux laboratuvarı: `ONUR_DRIVE_OFFLINE=1 ./install_and_run_linux_macos.sh` (önceden yüklü `cv2,numpy,fastapi,uvicorn,yaml,pytest` zorunlu; ağ kullanılmaz).
- GitHub'da APK derlenmesi, araca APK yükleme yetkisi veya MG HS kamera erişimi olduğu anlamına gelmez.
- Adım adım doğrulama sonuçları: `docs/KURULUM_DOGRULAMA_2026-10-17.md`.

