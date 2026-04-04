
---

# ☕ Canlı Kahve Dükkanı Simülatörü

Bu proje, bir kahve dükkanındaki müşteri akışını, barista yoğunluğunu ve bekleme sürelerini analiz etmek için geliştirilmiş olay tabanlı (discrete-event) bir simülasyon aracıdır. Arka planda `SimPy` kullanılarak işletilen matematiksel model, `Streamlit` ve `Plotly` ile geliştirilen modern bir web paneli aracılığıyla görselleştirilmektedir.

## ✨ Temel Özellikler

* **Olay Tabanlı Simülasyon:** Müşteri gelişleri ve kahve yapım süreleri istatistiksel dağılımlara (üstel ve tekdüze) dayalı olarak modellenmiştir.
* **Canlı Veri Akışı:** Simülasyon sonuçları, animasyonlu bir akış ile saniye saniye ekrana yansıtılarak "canlı" bir izleme deneyimi sunar.
* **İnteraktif Web Paneli:** Kod yazmaya gerek kalmadan barista sayısı, müşteri geliş hızı ve simülasyon süresi gibi parametreleri arayüz üzerinden değiştirebilme imkanı sağlar.
* **Detaylı Raporlama:** Kuyruk uzunlukları, bekleme süreleri dağılımı (histogram) ve ortalama/medyan istatistikleri otomatik olarak hesaplanıp raporlanır.
* **Çift Modlu Kullanım:** İster görsel arayüzle (Dashboard), ister komut satırı (CLI) üzerinden çalıştırılabilir.

---

## 📂 Proje Yapısı

Sistem mimarisi, simülasyon mantığı ile görsel arayüzü birbirinden ayıran iki temel dosyadan oluşmaktadır:

| Dosya Adı | Açıklama |
| :--- | :--- |
| `benzetim.py` | Simülasyonun çekirdek motorudur. Nesne yönelimli olarak `SimPy` sınıflarını barındırır. Komut satırından bağımsız olarak çalıştırılabilir. |
| `dashboard.py` | `Streamlit` tabanlı kullanıcı arayüzüdür. Parametre girişlerini alır, arka planda simülasyonu tetikler ve grafikleri ekrana çizer. |

---

## ⚙️ Kurulum ve Gereksinimler

Projeyi kendi bilgisayarınızda çalıştırmak için **Python 3.7+** yüklü olmalıdır. Gerekli kütüphaneleri kurmak için terminalinizde aşağıdaki adımları izleyin.

**Gerekli Kütüphaneler:**
* `simpy`
* `streamlit`
* `pandas`
* `plotly`

**Kurulum Komutu:**
```bash
pip install simpy streamlit pandas plotly
```

---

## 🚀 Kullanım

Projeyi ihtiyacınıza göre iki farklı şekilde çalıştırabilirsiniz:

### 1. Web Paneli (Dashboard) Olarak Çalıştırma
Görsel arayüzü, canlı grafikleri ve parametre kaydırıcılarını (slider) kullanmak için terminalde şu komutu çalıştırın:

```bash
streamlit run dashboard.py
```
Bu komut, varsayılan tarayıcınızda (genellikle `http://localhost:8501`) interaktif simülasyon panelini otomatik olarak açacaktır.

### 2. Komut Satırı (CLI) Üzerinden Çalıştırma
Sadece ham verileri, istatistiksel çıktıları ve logları terminal üzerinden hızlıca görmek isterseniz çekirdek dosyayı çalıştırabilirsiniz:

```bash
python benzetim.py
```
*Gelişmiş CLI Kullanımı:* Kendi JSON konfigürasyon dosyanızı vererek parametreleri dışarıdan da besleyebilirsiniz: `python benzetim.py --config ayarlar.json`

---

## 📊 Arayüz Sekmeleri (Dashboard)

Web panelini başlattığınızda sizi üç ana sekme karşılayacaktır:

1. **Canlı İzleme:** Simülasyon akarken anlık kuyruk uzunluğu alan grafiğini, bekleme sürelerini ve saniye saniye dökülen log metinlerini gösterir.
2. **Detaylı Grafikler:** Simülasyon tamamlandıktan sonra, tüm müşterilerin bekleme süresi dağılımlarını bir Histogram üzerinde incelemenizi sağlar.
3. **Rapor:** Toplam hizmet alan müşteri, maksimum/medyan bekleme süreleri ve standart sapmaları içeren nihai veri tablosunu (DataFrame) sunar.

---

**Geliştirici Notu:** *Bu araç, kapasite planlaması ve işgücü optimizasyonu yapmak isteyen işletme yöneticileri için tahmine değil, veriye dayalı bir "Karar Destek Sistemi" olarak tasarlanmıştır.*