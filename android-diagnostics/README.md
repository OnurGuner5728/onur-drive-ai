# ONUR DRIVE AI — MG HS Android kamera bağlantı testi v0.2

Bu **araç Android ekranında çalışması için derlenen APK'dir**, Windows ZIP değil. Doğrudan araç multimedya sistemine yüklenmesi yalnızca aracın resmi/izin verilen APK yükleme arayüzü varsa mümkündür.

## Park halinde, fabrikasyon donanımı değiştirmeden ilk test

1. GitHub Releases'den **OnurDriveAI-MGHS-CameraProbe-v0.2-debug.apk** dosyasını indir ve APK kurulumu desteklenen araç multimedya sistemine aktar.
2. Araç park halindeyken normal Android uygulama kurulum işlemiyle yükle. Aracın sistemi üçüncü taraf uygulama kurmayı desteklemiyorsa burada dur. Android Auto'ya APK kurmak, MG'nin gömülü kamerasına erişim sağlamaz.
3. Uygulamada **FABRİKA KAMERASI ERİŞİMİNİ TEST ET (PARK)** seç. Kamera listesinden erişilebilen bir cihaz seç.
4. **SEÇİLİ KAMERAYI AÇ (PARK)** düğmesine bas ve kamera iznini ver. Gerçek görüntü ve artan kare sayısı çıkarsa standart Camera2 üzerinden görüntü erişimi doğrulanır.
5. Dön ve **Tanı raporunu kaydet** ile cihaz ve Camera2 listesi raporunu JSON olarak al. Kameralar Camera2 listesinde yoksa bu API üzerinden erişim yok demektir, diğer donanım arayüzleri hakkında kesin bilgi vermez.

Uygulama yalnızca kullanıcı başlattığında kamera açmayı dener; arka plana geçerken kamerayı kapatır. **ACC, radar, CAN-BUS, gaz, fren, direksiyon, USB firmware güncellemesi, mühendislik modu, OEM hız sınırlaması değiştirme yok.** Bu üretim kalitesinde bir sürüş yardım sistemi değildir.

MG4 kamera uygulamasına ait /dev/video aygıt adresleri MG HS 2023 için varsayılmaz. Aracın Android çalıştırdığı, APK kurabildiği ve OEM kameralarını Camera2'ye açtığı henüz doğrulanmadı.

Derleme: Java 17, Android SDK 35, Gradle 8.11.1; `gradle :app:assembleDebug`. GitHub CI APK oluşturabilir. APK debug anahtarıyla imzalıdır; gelecekte güncellemede önceki debug sürümün kaldırılması gerekebilir.

[Patreon — Bir kahve ısmarla (isteğe bağlı)](https://www.patreon.com/c/onurguner)
