import streamlit as st
import simpy
import random
import pandas as pd
import time
import plotly.express as px

# Dashboard Genel Ayarları
st.set_page_config(
    page_title="Çok Şubeli Kahve Dükkanı Simülatörü",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS için stil ekleme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #8B4513;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        color: #654321;
        font-weight: bold;
    }
    .metric-card {
        background-color: #F5F5DC;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #D2B48C;
        margin-bottom: 10px;
    }
    .sidebar-content {
        background-color: #FFF8DC;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">☕ Canlı Kahve Dükkanı Simülatörü</h1>', unsafe_allow_html=True)
st.markdown("VIP Siparişler, Şubeye Özel Ayarlar ve Farklı Kahve Türleriyle çok daha gerçekçi bir simülasyon!")

# Sidebar - Parametre Ayarları
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
st.sidebar.header("⚙️ Genel Parametreler")

# Şube seçimi ve Dinamik Ekleme
if "mevcut_subeler" not in st.session_state:
    st.session_state.mevcut_subeler = ["Kadıköy", "Beşiktaş", "Şişli", "Bakırköy", "Moda", "Karaköy"]

yeni_sube = st.sidebar.text_input("➕ Yeni Şube Ekle", placeholder="Örn: Üsküdar")
if st.sidebar.button("Şubeyi Kaydet", use_container_width=True):
    if yeni_sube:
        if yeni_sube not in st.session_state.mevcut_subeler:
            st.session_state.mevcut_subeler.append(yeni_sube)
            st.rerun()
        else:
            st.sidebar.warning("Bu şube zaten mevcut!")

SUBELER = st.sidebar.multiselect(
    "Simüle Edilecek Şubeler", 
    st.session_state.mevcut_subeler, 
    default=[s for s in ["Kadıköy", "Beşiktaş"] if s in st.session_state.mevcut_subeler]
)

VIP_ORANI = st.sidebar.slider("Online/VIP Sipariş Oranı (%)", min_value=0, max_value=100, value=20, step=5, help="Sırayı atlayacak VIP müşterilerin oranı")
SIMULASYON_SURESI = st.sidebar.slider("Simülasyon Süresi (dk)", min_value=30, max_value=480, value=120, step=30)
CANLI_HIZ = st.sidebar.slider("Canlı Gösterim Hızı (Saniye/Kademe)", min_value=0.01, max_value=0.5, value=0.05, step=0.01)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Şube Bazlı Ayarlar
sube_ayarlari = {}
if SUBELER:
    st.sidebar.markdown("### 🏢 Şubeye Özel Ayarlar")
    for sube in SUBELER:
        with st.sidebar.expander(f"{sube} Ayarları", expanded=True):
            b_sayisi = st.slider(f"Barista Sayısı", 1, 10, 2, key=f"barista_{sube}")
            g_araligi = st.slider(f"Ort. Geliş Aralığı (dk)", 0.5, 10.0, 3.0, 0.5, key=f"gelis_{sube}")
            sube_ayarlari[sube] = {"barista_sayisi": b_sayisi, "gelis_araligi": g_araligi}

start_btn = st.sidebar.button("🚀 Simülasyonu Başlat", use_container_width=True)
reset_btn = st.sidebar.button("🔄 Sıfırla", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("👉 **Kahve Türleri:** Filtre Kahve (~1 dk), Latte (~3 dk), Frappuccino (~5 dk)")

if reset_btn:
    st.rerun()

if not SUBELER:
    st.warning("Lütfen simülasyon için en az bir şube seçin.")
    st.stop()

# Kahve Türleri ve Yapım Süreleri (min, max dk)
KAHVE_TURLERI = {
    "Filtre Kahve": (1.0, 1.5),
    "Latte": (2.5, 3.5),
    "Frappuccino": (4.5, 5.5)
}

# Simülasyon Sınıfları
class KahveDukkani:
    def __init__(self, env, barista_sayisi, log_callback, queue_callback, sube_adi):
        self.env = env
        self.sube_adi = sube_adi
        # VIP'ler için PriorityResource kullanıyoruz
        self.barista = simpy.PriorityResource(env, barista_sayisi)
        self.log_callback = log_callback
        self.queue_callback = queue_callback

    def kahve_yap(self, musteri, kahve_turu):
        min_s, max_s = KAHVE_TURLERI[kahve_turu]
        yapim_suresi = random.uniform(min_s, max_s)
        yield self.env.timeout(yapim_suresi)
        self.log_callback(f"{self.env.now:05.2f} dk | 🍵 {musteri} [{kahve_turu}] hazır.")
        self.queue_callback(self.env.now, len(self.barista.queue))

def musteri(env, sube_prefix, isim, dukkan, is_vip, kahve_turu, wait_callback):
    gelis_zamani = env.now
    ikon = "🚀" if is_vip else "🚶‍♂️"
    tip_metin = "VIP" if is_vip else "Normal"
    dukkan.log_callback(f"{gelis_zamani:05.2f} dk | {ikon} {isim} ({tip_metin}) geldi. İstek: {kahve_turu}")
    dukkan.queue_callback(gelis_zamani, len(dukkan.barista.queue))

    # PriorityResource'ta düşük sayı = yüksek öncelik. VIP=0, Normal=1
    oncelik = 0 if is_vip else 1

    with dukkan.barista.request(priority=oncelik) as sira:
        yield sira
        bekleme_suresi = env.now - gelis_zamani
        wait_callback(isim, gelis_zamani, bekleme_suresi, kahve_turu, is_vip)

        dukkan.log_callback(f"{env.now:05.2f} dk | 🗣️ {isim} sipariş veriyor. (Kuyruk: {len(dukkan.barista.queue)})")
        dukkan.queue_callback(env.now, len(dukkan.barista.queue))

        yield env.process(dukkan.kahve_yap(isim, kahve_turu))
        dukkan.log_callback(f"{env.now:05.2f} dk | 👋 {isim} ayrıldı.")

def musteri_olusturucu(env, sube_prefix, dukkan, gelis_araligi, vip_orani, wait_callback):
    sayac = 1
    
    def create_cust(s_count):
        is_vip = random.random() < (vip_orani / 100.0)
        # Kahve türünü rastgele seç (Ağırlık da verilebilir ama şimdilik eşit dağılım)
        kahve_turu = random.choice(list(KAHVE_TURLERI.keys()))
        env.process(musteri(env, sube_prefix, f"{sube_prefix} Müşteri {s_count}", dukkan, is_vip, kahve_turu, wait_callback))
        
    create_cust(sayac)

    while True:
        yield env.timeout(random.expovariate(1.0 / gelis_araligi))
        sayac += 1
        create_cust(sayac)

# Arayüz Düzeni ve Yer Tutucular (Placeholders)
tab1, tab2, tab3 = st.tabs(["📊 Canlı İzleme", "📈 Detaylı Analizler", "📋 Rapor"])

placeholders = {}
with tab1:
    st.markdown('<h3 class="sub-header">📊 Şubeler Canlı Akış</h3>', unsafe_allow_html=True)
    sube_tabs = st.tabs(SUBELER)
    for i, sube in enumerate(SUBELER):
        with sube_tabs[i]:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{sube}** - Kuyruk Uzunluğu")
                q_ph = st.empty()
                st.write(f"**{sube}** - Bekleme Süreleri")
                w_ph = st.empty()
            with col2:
                st.markdown(f"**📜 {sube} Canlı Log Akışı**")
                l_ph = st.empty()
            placeholders[sube] = {"q": q_ph, "w": w_ph, "l": l_ph}

with tab2:
    st.markdown('<h3 class="sub-header">🔍 Satış ve Performans Analizi</h3>', unsafe_allow_html=True)
    comp_chart1_ph = st.empty()
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        comp_chart2_ph = st.empty()
    with col2_2:
        comp_chart3_ph = st.empty()

with tab3:
    st.markdown('<h3 class="sub-header">📋 Genel Simülasyon Raporu</h3>', unsafe_allow_html=True)
    report_placeholder = st.empty()

# Simülasyon Butonuna Basıldığında...
if start_btn:
    sim_data = {
        sube: {"logs": [], "waits": [], "queue": []}
        for sube in SUBELER
    }

    def create_log_callback(sube):
        def add_log(msg):
            sim_data[sube]["logs"].append(msg)
        return add_log

    def create_wait_callback(sube):
        def add_wait(isim, zaman, sure, kahve_turu, is_vip):
            sim_data[sube]["waits"].append({
                "Müşteri": isim, 
                "Zaman": zaman, 
                "Bekleme Süresi": sure, 
                "Şube": sube,
                "Kahve Türü": kahve_turu,
                "Müşteri Tipi": "VIP" if is_vip else "Normal"
            })
        return add_wait

    def create_queue_callback(sube):
        def add_queue(zaman, uzunluk):
            sim_data[sube]["queue"].append({"Zaman": zaman, "Uzunluk": uzunluk, "Şube": sube})
        return add_queue

    # Simülasyonu çalıştır
    random.seed(42)
    env = simpy.Environment()
    
    for sube in SUBELER:
        ayarlar = sube_ayarlari[sube]
        dukkan = KahveDukkani(
            env, 
            barista_sayisi=ayarlar["barista_sayisi"], 
            log_callback=create_log_callback(sube), 
            queue_callback=create_queue_callback(sube),
            sube_adi=sube
        )
        env.process(musteri_olusturucu(
            env, 
            sube_prefix=sube, 
            dukkan=dukkan, 
            gelis_araligi=ayarlar["gelis_araligi"],
            vip_orani=VIP_ORANI,
            wait_callback=create_wait_callback(sube)
        ))
        
    env.run(until=SIMULASYON_SURESI)

    # Animasyon ve UI Güncellemeleri
    with st.spinner("Tüm şubeler için simülasyon çalışıyor ve sonuçlar ekrana basılıyor..."):
        max_events = max([len(data["logs"]) for data in sim_data.values()]) if sim_data else 0
        
        if max_events > 0:
            chunk_size = max(1, max_events // 20)

            for i in range(0, max_events, chunk_size):
                progress_ratio = min(1.0, (i + chunk_size + 1) / max_events)

                for sube in SUBELER:
                    data = sim_data[sube]
                    ph = placeholders[sube]

                    # Loglar
                    current_logs_count = int(progress_ratio * len(data["logs"]))
                    current_logs = data["logs"][:current_logs_count]
                    log_text = "\n".join(current_logs[::-1])
                    with ph["l"].container():
                        st.code(log_text, language="markdown")

                    # Kuyruk Grafiği
                    current_q_count = int(progress_ratio * len(data["queue"]))
                    df_q = pd.DataFrame(data["queue"][:current_q_count])
                    if not df_q.empty:
                        fig_q = px.area(df_q, x="Zaman", y="Uzunluk", 
                                        labels={"Zaman": "Zaman (dk)", "Uzunluk": "Kuyruk Uzunluğu"},
                                        color_discrete_sequence=['#8B4513'])
                        fig_q.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                        ph["q"].plotly_chart(fig_q, use_container_width=True, key=f"q_{sube}_{i}")

                    # Bekleme Grafiği
                    current_w_count = int(progress_ratio * len(data["waits"]))
                    df_w = pd.DataFrame(data["waits"][:current_w_count])
                    if not df_w.empty:
                        fig_w = px.bar(df_w, x="Zaman", y="Bekleme Süresi", 
                                       color="Müşteri Tipi",
                                       labels={"Zaman": "Zaman (dk)", "Bekleme Süresi": "Bekleme Süresi (dk)"},
                                       color_discrete_map={"VIP": "#D4AF37", "Normal": "#D2B48C"})
                        fig_w.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                        ph["w"].plotly_chart(fig_w, use_container_width=True, key=f"w_{sube}_{i}")

                time.sleep(CANLI_HIZ)

        # Animasyon Sonu Final Yansıtma
        for sube in SUBELER:
            data = sim_data[sube]
            ph = placeholders[sube]
            log_text = "\n".join(data["logs"][::-1])
            with ph["l"].container():
                st.code(log_text, language="markdown")
                
            if data["queue"]:
                df_q = pd.DataFrame(data["queue"])
                fig_q = px.area(df_q, x="Zaman", y="Uzunluk", color_discrete_sequence=['#8B4513'])
                fig_q.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                ph["q"].plotly_chart(fig_q, use_container_width=True, key=f"q_{sube}_final")
                
            if data["waits"]:
                df_w = pd.DataFrame(data["waits"])
                fig_w = px.bar(df_w, x="Zaman", y="Bekleme Süresi", color="Müşteri Tipi", color_discrete_map={"VIP": "#D4AF37", "Normal": "#D2B48C"})
                fig_w.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                ph["w"].plotly_chart(fig_w, use_container_width=True, key=f"w_{sube}_final")

    # Tüm verileri birleştir
    all_waits = []
    for sube, data in sim_data.items():
        all_waits.extend(data["waits"])
        
    df_all_waits = pd.DataFrame(all_waits)

    if not df_all_waits.empty:
        # Karşılaştırma Grafikleri (Tab 2)
        fig_comp_box = px.box(df_all_waits, x="Şube", y="Bekleme Süresi", color="Müşteri Tipi",
                              title="Şube & Müşteri Tipine Göre Bekleme Süreleri",
                              color_discrete_map={"VIP": "#D4AF37", "Normal": "#8B4513"})
        fig_comp_box.update_layout(height=400)
        comp_chart1_ph.plotly_chart(fig_comp_box, use_container_width=True, key="comp_box_final")

        fig_pie = px.pie(df_all_waits, names="Kahve Türü", title="Tüm Ağda Satılan Kahve Dağılımı", hole=0.3)
        comp_chart2_ph.plotly_chart(fig_pie, use_container_width=True, key="comp_pie_final")

        fig_bar_kahve = px.histogram(df_all_waits, x="Şube", color="Kahve Türü", barmode="group", title="Şubelere Göre Kahve Satışları")
        comp_chart3_ph.plotly_chart(fig_bar_kahve, use_container_width=True, key="comp_bar_kahve_final")

        # Raporlama (Tab 3)
        with report_placeholder.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🌐 Genel Ağ Özeti (Tüm Şubeler)")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Toplam Satış", len(df_all_waits))
            col2.metric("VIP Satış Oranı", f"%{(len(df_all_waits[df_all_waits['Müşteri Tipi'] == 'VIP']) / len(df_all_waits) * 100):.1f}")
            col3.metric("Genel Ortalama Bekleme", f"{df_all_waits['Bekleme Süresi'].mean():.2f} dk")
            col4.metric("Ağ Medyan Bekleme", f"{df_all_waits['Bekleme Süresi'].median():.2f} dk")
            st.markdown('</div>', unsafe_allow_html=True)

            st.subheader("🏢 Şube Bazlı Performans")
            summary_df = df_all_waits.groupby("Şube")["Bekleme Süresi"].agg(['count', 'mean', 'median', 'max']).round(2)
            summary_df.columns = ["Müşteri Sayısı", "Ort. Bekleme (dk)", "Medyan Bekleme (dk)", "Maks. Bekleme (dk)"]
            st.dataframe(summary_df, use_container_width=True)
            
            st.subheader("🔍 Detaylı Tüm Kayıtlar")
            st.dataframe(df_all_waits.sort_values(by="Zaman").reset_index(drop=True), use_container_width=True)
            
    else:
        st.warning("Bu simülasyon ayarlarında hiçbir şubeye müşteri gelmedi.")

    st.success("✅ Gelişmiş Simülasyon Tamamlandı!")
