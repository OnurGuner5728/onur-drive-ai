# V4L2 salt okunur yetenek envanteri

Yalnızca Linux tabanlı ve erişim yetkisi **önceden verilmiş** cihazlarda çalışır.

```
g++ -std=c++17 -O2 -Wall -Wextra v4l2_capability_probe.cpp -o v4l2_capability_probe
./v4l2_capability_probe /dev/video0
```

`VIDIOC_QUERYCAP` / `VIDIOC_ENUM_FMT` ile kapasite/format bilgilerini okur. Video akışını başlatmaz, V4L2 ayarlarını değiştirmez, CAN sistemleriyle etkileşmez. `O_RDONLY` kullanır. Erişim yetkisi yoksa hata verip durur. `/dev/videoN` varlığı fabrika kameralarına bağlanılabileceğini ispatlamaz.
