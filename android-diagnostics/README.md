# Onur Drive AI — Android / MG HS tanılama projesi

**Kaynak kodu, APK değil.** Bu ortamda Android SDK/Gradle bulunmadığı için derleme yapılamadı.

Bu uygulama yalnızca standart Android `Build` bilgilerini ve `CameraManager.getCameraIdList()` listesini okur; ayrıca cihazda kurulu TTS motoruyla Türkçe ses desteğini test eder. **Gerçek fabrika kamera akışı açılmaz.** OEM sistem kameraları genel Camera2 arayüzünde görünmeyebilir.

Gereksinimler: Java 17, Android SDK 35, Android Gradle Plugin 8.9.2, Gradle 8.11.1. SDK ve Gradle indirmesi için internet gerekir. `gradle :app:assembleDebug` komutuyla proje kökünden derlenebilir. APK `app/build/outputs/apk/debug/app-debug.apk` dizininde oluşur.

Uygulama yalnızca araç multimedya sistemi APK yüklemeye resmi/önceden izin veriyorsa, araç park halindeyken kurulmalıdır. Yetki aşma, üretici imzası taklit etme, firmware düşürme, engineering mode kodları, hız sınırı değiştirme veya OEM AVM uygulaması değiştirme dahil değildir. APK kurulumunun MG HS üzerinde mümkün olduğu doğrulanmamıştır.
