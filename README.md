# PDF'den 3D STEP (.stp) Çıkarıcı (PDF to STEP Extractor)

Windows 10 / 11 için geliştirilmiş, teknik resim PDF'lerine gömülü 3D CAD modellerini (ISO-10303-21 STEP) tek tıkla dosyanın yanına çıkaran ultra hafif ve hızlı bir araçtır.

---

## ✨ Özellikler

- **WinRAR Rahatlığında**: Herhangi bir PDF dosyasına sağ tıklayıp **"STEP Dosyasını Çıkar"** dediğiniz an model dosyanın olduğu konuma anında çıkarılır.
- **Karışık Seçim Desteği (PDF + Excel vb.)**: Dosya paketindeki PDF'leri ve Excel (`.xlsx`, `.xls`), Word veya diğer dosyaları aynı anda seçip sağ tıklayabilirsiniz. Excel gibi gömülü modeli olmayan dosyalar otomatik es geçilir, yalnızca PDF'lerin içindeki STEP modelleri çıkarılır.
- **Ultra Hızlı ve Kasmayan Yapı**: Arka planda 0.1 saniye içinde çalışır, sisteminizi yormaz, siyah komut penceresi açılmaz.
- **Yerel Windows 10 Bildirimi**: Dosya çıkarıldığında sağ altta Windows bildirimi çıkar ve bildirime tıklayarak doğrudan çıkarılan dosyayı açabilirsiniz.
- **Akıllı Karakter Düzeltmesi**: Türkçe karakter içeren dosya adlarını (`TELEMETRİ PLAKA.stp` vb.) bozulmadan temiz bir şekilde kaydeder.
- **Çoklu Seçim Desteği**: İster 1, ister 10 PDF seçip sağ tıklayın, hepsinin içindeki modelleri tek seferde çıkarır.
- **Ağ Güvenliği & Kilit Kaldırma Entegrasyonu**: Şirket içi yerel ağ paylaşımlarından (`\\192.168.x.x`) dosya kopyalarken çıkan sarı Windows güvenlik uyarılarını ve dosyaların bloke/deaktive olmasını tek tıkla engeller. Klasörlere sağ tıklayıp "Klasördeki Dosya Kilitlerini Kaldır" seçeneğini sunar.
- **Görsel Arayüz (GUI)**: `StepExtractor.exe` dosyasına çift tıklayarak arayüzden dosya seçebilir veya sağ tık menüsünü tek tıkla kurup kaldırabilirsiniz.

---

## 🚀 Kurulum (Tek Tıkla - Hepsi Bir Arada)

1. `c:\Projects\stepextracterfrompdf` klasörüne gidin.
2. [Kurulum.bat](file:///c:/Projects/stepextracterfrompdf/Kurulum.bat) dosyasına çift tıklayın.
3. Artık sisteminiz hazır! Hem STEP Çıkarıcı kurulur hem de şirket ağı güvenlik uyarıları kalıcı olarak çözülür. Yönetici (Administrator) izni bile gerektirmez.

*(Sağ tık menülerini kaldırmak isterseniz istediğiniz zaman [Kaldir.bat](file:///c:/Projects/stepextracterfrompdf/Kaldir.bat) dosyasına çift tıklamanız yeterlidir).*

---

## 🛠️ Dosya Yapısı

- [StepExtractor.exe](file:///c:/Projects/stepextracterfrompdf/StepExtractor.exe) - Bağımsız, derlenmiş çalıştırılabilir program.
- [Kurulum.bat](file:///c:/Projects/stepextracterfrompdf/Kurulum.bat) - Sağ tık menüsüne ekleme betiği.
- [Kaldir.bat](file:///c:/Projects/stepextracterfrompdf/Kaldir.bat) - Sağ tık menüsünden kaldırma betiği.
- [core.py](file:///c:/Projects/stepextracterfrompdf/core.py) - STEP ayrıştırma ve çıkarma çekirdeği.
- [gui.py](file:///c:/Projects/stepextracterfrompdf/gui.py) - Modern Tkinter arayüzü.
- [registry.py](file:///c:/Projects/stepextracterfrompdf/registry.py) - Windows Kayıt Defteri entegrasyonu.
- [notifier.py](file:///c:/Projects/stepextracterfrompdf/notifier.py) - Windows 10 yerel bildirim motoru.
