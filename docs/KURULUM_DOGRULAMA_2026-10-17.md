# ONUR DRIVE AI — Kurulum Rehberi Doğrulama Kaydı

Tarih: 17 Ekim 2026 · Hedef repo: `OnurGuner5728/onur-drive-ai`

Bu belge `KURULUM_TR.md` adımlarının gerçek durumunu izler; test edilmemiş bir araç işlevi çalışıyor gibi raporlanmaz.

| Rehber adımı | Kanıt / sonuç | Durum |
| --- | --- | --- |
| Python paketinin mevcut ortamda kurulması | `python -m pip show onur-drive-ai`: 0.1.0 editable kurulum mevcut | PASS (lab) |
| Otomatik davranış testleri | `python -m pytest -q`: 26/26 geçti | PASS |
| Yerel sunucu | `./run_demo.sh`: `GET /` ve `GET /api/status` HTTP 200 | PASS |
| Görüntü akışı | `GET /stream`: multipart JPEG akışı doğrulandı | PASS |
| Dört sentetik kamera | `python scripts/render_demo.py`: MP4/JPG üretildi, araç verisi değil | PASS (synthetic) |
| V4L2 tanılama | `g++ -std=c++17 -Wall -Wextra -Werror native/v4l2_capability_probe.cpp -o /tmp/onur_v4l2_probe`: derlendi | PASS (compile only) |
| Standart çevrimiçi Linux kurulum betiği | Kapalı ağ ortamında `setuptools>=68` indirme adımı başarısız; yazılım hatası kanıtı değil | BLOCKED (network) |
| Çevrimdışı Linux laboratuvar çalıştırma | `ONUR_DRIVE_OFFLINE=1 ./install_and_run_linux_macos.sh`: 26 test geçti, HTTP API çalıştı; önceden yüklü bağımlılıkları kullandı | PASS (lab) |
| Windows `.bat` kurulum | Bu oturumda Windows çalıştırma ortamı yok | UNTESTED |
| Android APK derleme | GitHub Actions run [38983758648](https://github.com/OnurGuner5728/onur-drive-ai/actions/runs/38983758648): Android job başarılı, debug APK artifact üretildi | PASS (CI build only; vehicle not installed) |
| MG HS head unit işletim sistemi | Gerçek araç bağlı değil, üretici sürümü bilinmiyor | BLOCKED (vehicle) |
| Camera2 tanılama | APK gerçek multimedya cihazında çalıştırılmadı | BLOCKED (vehicle) |
| Yetkili ADB komutları | ADB bağlantısı yok; izin aşımı yapılmadı | NO ACCESS |
| OEM AVM video akışı | Doğrulanmış ham görüntü arayüzü yok | NO VIDEO SOURCE |
| OEM ekran kapanırken ham akış sürekliliği | Kapalı test alanı ve araç bağlantısı olmadan ölçülemez; hız kilidi kaldırılmadı | UNVERIFIED |
| ACC/radar mesafesi | Doğrulanmış salt okunur kaynak yok | UNVERIFIED |
| Doğal Türkçe TTS | Onaylı WAV varlığı yok; üretim sesi test edilmedi | NOT INSTALLED |
| YOLOX gerçek ağırlık dosyaları | Lisanslı model ağırlığı pakette yok; parser sentetik tensör üzerinde test edildi | NOT INSTALLED |
| Araç fren/gaz/direksiyon/ACC müdahalesi | Kaynak kodda kontrol API'si bulunmuyor | INTENTIONALLY ABSENT |

## Kurulumun tamamlanma koşulu

**Laboratuvar kurulumu doğrulandı; MG HS üzerine üretim kurulumu tamamlanmadı.**
Araçta mevcut yazılım izinleri ve kesintisiz fabrika kamera akışı gözlemlenmeden G1–G7 kapıları geçilemez.
Yeni donanım kullanılmayacak ve araç güvenlik sınırları değiştirilmeyecek. OEM akışına izinli erişim mümkün değilse durum `NO-GO` olur.

GitHub Actions sonuçları: <https://github.com/OnurGuner5728/onur-drive-ai/actions>