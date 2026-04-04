import simpy
import random
import statistics
import argparse
import json

# Simülasyon parametreleri - Konfigürasyon sözlüğü
DEFAULT_CONFIG = {
    "barista_sayisi": 2,
    "musteri_gelis_araligi": 3,  # Ortalama 3 dakikada bir müşteri gelir
    "kahve_yapim_suresi_min": 2,  # Kahve yapımı en az 2 dakika
    "kahve_yapim_suresi_max": 5,  # Kahve yapımı en fazla 5 dakika
    "simulasyon_suresi": 120,  # Simülasyon 120 dakika (2 saat) sürecek
    "random_seed": 42
}

class KahveDukkani:
    def __init__(self, env, barista_sayisi, kahve_min, kahve_max):
        self.env = env
        # Baristalar, simülasyonda sınırlı bir kaynak (Resource) olarak tanımlanır
        self.barista = simpy.Resource(env, barista_sayisi)
        self.kahve_min = kahve_min
        self.kahve_max = kahve_max

    def kahve_yap(self, musteri):
        # Kahve yapım süresi belirtilen aralıkta rastgele belirlenir
        yapim_suresi = random.uniform(self.kahve_min, self.kahve_max)
        yield self.env.timeout(yapim_suresi)
        print(f"{self.env.now:.2f} dakikada {musteri} adlı müşterinin kahvesi hazırlandı.")

def musteri(env, isim, dukkan, bekleme_sureleri):
    # Müşterinin dükkana geldiği an
    gelis_zamani = env.now
    print(f"{gelis_zamani:.2f} dakikada {isim} kahve dükkanına geldi.")

    # Baristadan hizmet talep et
    with dukkan.barista.request() as sira:
        # Sıranın bize gelmesini bekle
        yield sira

        # Sıra geldiğinde bekleme süresini hesapla
        bekleme_suresi = env.now - gelis_zamani
        bekleme_sureleri.append(bekleme_suresi)
        print(f"{env.now:.2f} dakikada {isim} sipariş vermeye başladı. (Kuyrukta bekleme: {bekleme_suresi:.2f} dk)")

        # Kahve yapım sürecini başlat ve bitmesini bekle
        yield env.process(dukkan.kahve_yap(isim))
        print(f"{env.now:.2f} dakikada {isim} kahvesini alıp dükkandan ayrıldı.")

def musteri_olusturucu(env, dukkan, bekleme_sureleri, musteri_araligi):
    sayac = 1
    # İlk müşteri simülasyon başlar başlamaz gelsin
    env.process(musteri(env, f"Müşteri {sayac}", dukkan, bekleme_sureleri))

    while True:
        # Sonraki müşterinin gelmesi için rastgele bir süre (üstel dağılım) geçer
        yield env.timeout(random.expovariate(1.0 / musteri_araligi))
        sayac += 1
        env.process(musteri(env, f"Müşteri {sayac}", dukkan, bekleme_sureleri))

def hesapla_istatistikler(bekleme_sureleri):
    if not bekleme_sureleri:
        return None

    return {
        "toplam_musteri": len(bekleme_sureleri),
        "ortalama_bekleme": statistics.mean(bekleme_sureleri),
        "medyan_bekleme": statistics.median(bekleme_sureleri),
        "max_bekleme": max(bekleme_sureleri),
        "min_bekleme": min(bekleme_sureleri),
        "std_sapma": statistics.stdev(bekleme_sureleri) if len(bekleme_sureleri) > 1 else 0,
        "musteri_saat_basina": len(bekleme_sureleri) / (DEFAULT_CONFIG["simulasyon_suresi"] / 60)
    }

def yazdir_rapor(istatistikler):
    print("\n" + "=" * 50)
    print("        KAHVE DÜKKANI SİMÜLASYON RAPORU")
    print("=" * 50)
    print(f"Toplam hizmet alan müşteri sayısı    : {istatistikler['toplam_musteri']}")
    print(f"Ortalama bekleme süresi              : {istatistikler['ortalama_bekleme']:.2f} dakika")
    print(f"Medyan bekleme süresi                : {istatistikler['medyan_bekleme']:.2f} dakika")
    print(f"En uzun bekleme süresi               : {istatistikler['max_bekleme']:.2f} dakika")
    print(f"En kısa bekleme süresi               : {istatistikler['min_bekleme']:.2f} dakika")
    print(f"Bekleme süresi standart sapması      : {istatistikler['std_sapma']:.2f} dakika")
    print(f"Saat başı ortalama müşteri sayısı    : {istatistikler['musteri_saat_basina']:.2f}")
    print("=" * 50)

def main(config=None):
    if config is None:
        config = DEFAULT_CONFIG

    bekleme_sureleri = []

    # Simülasyon Kurulumu ve Çalıştırılması
    print("Kahve Dükkanı Simülasyonu Başlatılıyor...")
    print("-" * 50)
    random.seed(config["random_seed"])  # Sonuçların her çalıştırmada aynı olması için seed

    # Simülasyon ortamını oluştur
    env = simpy.Environment()

    # Kahve dükkanını oluştur
    dukkan = KahveDukkani(env, config["barista_sayisi"], config["kahve_yapim_suresi_min"], config["kahve_yapim_suresi_max"])

    # Müşteri oluşturucu süreci ortama ekle
    env.process(musteri_olusturucu(env, dukkan, bekleme_sureleri, config["musteri_gelis_araligi"]))

    # Simülasyonu belirtilen süre boyunca çalıştır
    env.run(until=config["simulasyon_suresi"])

    # Simülasyon bittikten sonra istatistikleri hesapla ve yazdır
    istatistikler = hesapla_istatistikler(bekleme_sureleri)
    if istatistikler:
        yazdir_rapor(istatistikler)
    else:
        print("\nHiç müşteri gelmedi.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kahve Dükkanı Simülasyonu")
    parser.add_argument("--config", type=str, help="Konfigürasyon dosyası (JSON)")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    if args.config:
        with open(args.config, 'r') as f:
            config.update(json.load(f))

    main(config)