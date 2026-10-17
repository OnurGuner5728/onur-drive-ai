# ONUR DRIVE AI — Evrensel araç kamera/video arayüzü tarayıcısı (v0.3)

**Araçta kullanılmak üzere hazırlanmış Android APK; Windows ZIP değil.** Yalnızca multimedya sistemi normal üçüncü taraf APK kurulumunu destekliyorsa kurulabilir.

## Bir düğmeyle cihaz keşfi

1. Araç tamamen park halindeyken [v0.3 Android Scanner](https://github.com/OnurGuner5728/onur-drive-ai/releases/tag/v0.3.0-universal-scanner) sürümünden APK indir.
2. Araç multimedya sistemi APK kurulumunu normal kullanıcı arayüzünde destekliyorsa yükle. Android Auto, MG HS'nin kamera sistemine erişim sağlamaz.
3. **TÜM KAMERA / VİDEO ÇIKIŞLARINI TARA** düğmesine bas.
4. **Tanı raporunu kaydet** düğmesiyle JSON dosyasını kaydet.
5. Sadece Camera2 listesinde cihaz varsa, **FABRİKA KAMERASI ERİŞİMİNİ TEST ET (PARK)** seçeneğiyle normal Android kamera izinlerinden canlı görüntü açmayı dene.

## Taranan arayüzler (salt okunur)

- Android üretici/model/çipset ve işletim sistemi bilgileri.
- Normal uygulamaların görebildiği Camera2 kamera kimlikleri, fiziksel alt kamera kimlikleri, özellikler ve çözünürlükler.
- Linux video cihaz **isimleri ve dosya özelliği**: `/dev/videoN`, `/dev/mediaN`, `/dev/v4l-subdevN`.
- `/sys/class/video4linux` aygıt adları görünürse onları okur.
- Android UsbManager aygıt envanteri.

Tarama V4L2 kamera cihazlarını açmaz; `canRead()` yalnızca bir Java erişim ipucudur, canlı görüntü erişimini **kanıtlamaz**. Standart Camera2 erişimi yalnızca açıkça başlatılan park halinde görüntü testinde denenir.

## Sonuçların yorumlanması

Camera2 boş çıkarsa OEM kameraların yok olduğu anlamına gelmez. Bazı otomobiller EVS veya yalnızca üretici uygulamalarına tanınan `SYSTEM_CAMERA` arayüzlerini kullanır. Bunlar normal üçüncü taraf APK tarafından görülemeyebilir. Hız nedeniyle kamera akışı kesiliyorsa tarayıcı bunu değiştirmez.

Bu sürüm **MG HS 2023 fabrika kameralarına erişimi, otomobilde kurulumu veya ACC verilerini henüz doğrulamıyor.** Kontrol komutları, root, yetki yükseltme, araç yazılımı güncelleme ve hız sınırını aşma bulunmaz. Canlı trafikte güvenlik amaçlı kullanmayın.

[Kaynak kod](https://github.com/OnurGuner5728/onur-drive-ai) · [Patreon — Bir kahve ısmarla](https://www.patreon.com/c/onurguner)
