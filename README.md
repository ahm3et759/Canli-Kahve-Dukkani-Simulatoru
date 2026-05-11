
# ☕  Çok Şubeli Kahve Dükkanı Simülatörü

Bu proje, bir kahve zincirindeki şubelerin performansını, müşteri akışını, barista yoğunluğunu ve bekleme sürelerini analiz etmek için geliştirilmiş olay tabanlı (discrete-event) bir simülasyon aracıdır. Arka planda `SimPy` kullanılarak işletilen matematiksel model, `Streamlit` ve `Plotly` ile geliştirilen modern bir web paneli aracılığıyla görselleştirilmektedir.

## ✨ Temel ve Yeni Özellikler

 **Çoklu Şube Desteği (YENİ):** Aynı anda birden fazla şubeyi (Kadıköy, Beşiktaş vb.) simüle edebilir ve sonuçları birbiriyle karşılaştırabilirsiniz.
 
 **Dinamik Şube Ekleme (YENİ):** Arayüz üzerinden dilediğiniz isimde yeni bir şube yaratıp anında simülasyona dahil edebilirsiniz.
 
 **Şubeye Özel Ayarlar (YENİ):** Her şube için bağımsız barista sayısı ve müşteri geliş aralığı tanımlayabilirsiniz (Örn: Kadıköy'de 4 barista varken Beşiktaş'ta 2 barista olması).
 
 **Farklı Kahve Türleri (YENİ):** Müşteriler; Filtre Kahve (~1 dk), Latte (~3 dk) veya Frappuccino (~5 dk) sipariş edebilir. Her siparişin hazırlık süresi türüne göre dinamik olarak hesaplanır.
 
 **VIP / Online Sipariş Önceliği (YENİ):** Öncelikli kuyruk mantığı (`PriorityResource`) sayesinde, VIP veya online sipariş veren müşteriler (🚀) sırayı atlayarak beklemeden hizmet alırlar.
 
 **Canlı Veri Akışı:** Simülasyon sonuçları, animasyonlu bir akış ile saniye saniye ekrana yansıtılarak "canlı" bir izleme deneyimi sunar.
 
 **İnteraktif Web Paneli:** Kod yazmaya gerek kalmadan tüm parametreleri arayüz üzerinden değiştirebilme imkanı sağlar.

---

## 📂 Proje Yapısı

Sistem mimarisi, simülasyon mantığı ile görsel arayüzü birbirinden ayıran iki temel dosyadan oluşmaktadır:

| Dosya Adı | Açıklama |
| :--- | :--- |
| `benzetim.py` | Simülasyonun çekirdek motorudur. Temel `SimPy` mantığını barındırır. Komut satırından bağımsız olarak (tek şube modunda) çalıştırılabilir. |
| `dashboard.py` | `Streamlit` tabanlı ana kullanıcı arayüzüdür. Çok şubeli mantığı, VIP kuyruklarını ve canlı grafikleri yöneten gelişmiş versiyondur. |

---

## ⚙️ Kurulum ve Gereksinimler

Projeyi kendi bilgisayarınızda çalıştırmak için **Python 3.7+** yüklü olmalıdır. Gerekli kütüphaneleri kurmak için terminalinizde aşağıdaki adımları izleyin.

**Kurulum Komutu:**
```bash
pip install simpy streamlit pandas plotly
```

---

## 🚀 Kullanım

### 1. Web Paneli (Dashboard) Olarak Çalıştırma (Önerilen)
Tüm yeni özellikleri, şube karşılaştırmalarını ve görsel arayüzü kullanmak için terminalde şu komutu çalıştırın:

```bash
streamlit run dashboard.py
```
Bu komut, tarayıcınızda (genellikle `http://localhost:8501`) interaktif simülasyon panelini açacaktır.

### 2. Komut Satırı (CLI) Üzerinden Çalıştırma
Sadece ham verileri ve temel tek şube analizini komut satırından görmek isterseniz:

```bash
python benzetim.py
```

---

## 📊 Arayüz Sekmeleri (Dashboard)

Web panelini başlattığınızda sizi üç ana sekme karşılayacaktır:

1. **📊 Şubeler Canlı Akış:** Seçilen tüm şubelerin kendilerine ait alt sekmelerinde canlı kuyruk grafiklerini, bekleme sürelerini ve renk kodlu (VIP/Normal) canlı log akışını gösterir.
2. **📈 Detaylı Analizler (Karşılaştırmalar):** Şubelerin bekleme sürelerini (Kutu ve Histogram grafikleriyle) karşılaştırır. Ayrıca ağ genelinde en çok satılan kahve türlerini gösteren pasta ve sütun grafikleri barındırır.
3. **📋 Rapor:** Toplam hizmet alan müşteri, VIP sipariş oranı ve şube bazlı detaylı performans tablolarını (DataFrame) sunar.

---

**Geliştirici Notu:** *Bu araç, kapasite planlaması ve işgücü optimizasyonu yapmak isteyen işletme yöneticileri için tahmine değil, veriye dayalı bir "Karar Destek Sistemi" olarak tasarlanmıştır.*
