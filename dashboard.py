import streamlit as st
import simpy
import random
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Genel Ayarları
st.set_page_config(
    page_title="Kahve Dükkanı Simülatörü",
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
    }
    .sidebar-content {
        background-color: #FFF8DC;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">☕ Canlı Kahve Dükkanı Simülatörü</h1>', unsafe_allow_html=True)
st.markdown("Bu profesyonel panel, `simpy` tabanlı kahve dükkanı simülasyonunu canlı verilerle grafiksel olarak izlemenizi sağlar. Parametreleri ayarlayarak farklı senaryoları test edin!")

# Sidebar - Parametre Ayarları
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
st.sidebar.header("⚙️ Simülasyon Parametreleri")
BARISTA_SAYISI = st.sidebar.slider("Barista Sayısı", min_value=1, max_value=10, value=2, step=1, help="Hizmet verecek barista sayısı")
MUSTERI_GELIS_ARALIGI = st.sidebar.slider("Ortalama Müşteri Geliş Aralığı (dk)", min_value=0.5, max_value=10.0, value=3.0, step=0.5, help="Müşterilerin ortalama geliş aralığı")
KAHVE_SURELERI = st.sidebar.slider("Kahve Yapım Süresi (Min-Max dk)", min_value=0.5, max_value=10.0, value=(2.0, 5.0), step=0.5, help="Kahve yapım süresi aralığı")
SIMULASYON_SURESI = st.sidebar.slider("Simülasyon Süresi (dk)", min_value=30, max_value=480, value=120, step=30, help="Toplam simülasyon süresi")
CANLI_HIZ = st.sidebar.slider("Canlı Gösterim Hızı (Saniye/Kademe)", min_value=0.01, max_value=0.5, value=0.05, step=0.01, help="Animasyon hızı")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

start_btn = st.sidebar.button("🚀 Simülasyonu Başlat", use_container_width=True)
reset_btn = st.sidebar.button("🔄 Sıfırla", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("👉 **Nasıl Çalışır?**\nParametreleri ayarlayın ve başlat butonuna basın. Uygulama, simülasyonu çalıştırıp verilerini canlı bir akışmış gibi ekrana yansıtacaktır.")

# Simülasyon Sınıfları
class KahveDukkani:
    def __init__(self, env, barista_sayisi, kahve_sureleri, log_callback, queue_callback):
        self.env = env
        self.barista = simpy.Resource(env, barista_sayisi)
        self.kahve_sureleri = kahve_sureleri
        self.log_callback = log_callback
        self.queue_callback = queue_callback

    def kahve_yap(self, musteri):
        yapim_suresi = random.uniform(self.kahve_sureleri[0], self.kahve_sureleri[1])
        yield self.env.timeout(yapim_suresi)
        self.log_callback(f"{self.env.now:05.2f} dk | 🍵 {musteri} kahvesini aldı.")
        self.queue_callback(self.env.now, len(self.barista.queue))

def musteri(env, isim, dukkan, wait_callback):
    gelis_zamani = env.now
    dukkan.log_callback(f"{gelis_zamani:05.2f} dk | 🚶‍♂️ {isim} geldi.")
    dukkan.queue_callback(gelis_zamani, len(dukkan.barista.queue))

    with dukkan.barista.request() as sira:
        yield sira
        bekleme_suresi = env.now - gelis_zamani
        wait_callback(isim, gelis_zamani, bekleme_suresi)

        dukkan.log_callback(f"{env.now:05.2f} dk | 🗣️ {isim} sipariş veriyor. (Kuyruk: {len(dukkan.barista.queue)})")
        dukkan.queue_callback(env.now, len(dukkan.barista.queue))

        yield env.process(dukkan.kahve_yap(isim))
        dukkan.log_callback(f"{env.now:05.2f} dk | 👋 {isim} ayrıldı.")

def musteri_olusturucu(env, dukkan, wait_callback):
    sayac = 1
    env.process(musteri(env, f"Müşteri {sayac}", dukkan, wait_callback))

    while True:
        yield env.timeout(random.expovariate(1.0 / MUSTERI_GELIS_ARALIGI))
        sayac += 1
        env.process(musteri(env, f"Müşteri {sayac}", dukkan, wait_callback))

# Arayüz Düzeni ve Yer Tutucular (Placeholders)
tab1, tab2, tab3 = st.tabs(["📊 Canlı İzleme", "📈 Detaylı Grafikler", "📋 Rapor"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<h3 class="sub-header">📈 Canlı Grafikler</h3>', unsafe_allow_html=True)
        st.write("Zaman İçinde Barista Önündeki Kuyruk Uzunluğu")
        chart_placeholder = st.empty()
        st.write("Müşterilerin Hizmet Öncesi Bekleme Süreleri")
        wait_chart_placeholder = st.empty()

    with col2:
        st.markdown('<h3 class="sub-header">📜 Canlı Log Akışı</h3>', unsafe_allow_html=True)
        log_placeholder = st.empty()

with tab2:
    st.markdown('<h3 class="sub-header">🔍 Detaylı Analiz</h3>', unsafe_allow_html=True)
    detailed_chart_placeholder = st.empty()

with tab3:
    st.markdown('<h3 class="sub-header">📋 Simülasyon Raporu</h3>', unsafe_allow_html=True)
    report_placeholder = st.empty()

# Reset butonu işlevi
if reset_btn:
    st.rerun()

# Simülasyon Butonuna Basıldığında...
if start_btn:
    sim_logs = []
    sim_waits = []
    sim_queue = []

    # Olayları yakalamak için fonksiyonlar (callback)
    def add_log(msg):
        sim_logs.append(msg)

    def add_wait(isim, zaman, sure):
        sim_waits.append({"Müşteri": isim, "Zaman": zaman, "Bekleme Süresi": sure})

    def add_queue(zaman, uzunluk):
        sim_queue.append({"Zaman": zaman, "Uzunluk": uzunluk})

    # Simülasyonu Arka Planda Tek Seferde Çalıştırıyoruz
    random.seed(42)
    env = simpy.Environment()
    dukkan = KahveDukkani(env, BARISTA_SAYISI, KAHVE_SURELERI, add_log, add_queue)
    env.process(musteri_olusturucu(env, dukkan, add_wait))
    env.run(until=SIMULASYON_SURESI)

    # UI Güncellemeleri - Animasyon Etkisi
    with st.spinner("Simülasyon çalışıyor ve sonuçlar ekrana basılıyor..."):
        current_logs = []

        # Logları 20 adımda yansıtacak şekilde bölüyoruz
        chunk_size = max(1, len(sim_logs) // 20)

        for i in range(0, len(sim_logs), chunk_size):
            chunk = sim_logs[i:i+chunk_size]
            current_logs.extend(chunk)

            # Logları en yeni üstte olacak şekilde tekst alanında göster
            log_text = "\n".join(current_logs[::-1])
            with log_placeholder.container():
                st.code(log_text, language="markdown")

            # Grafikler için veriyi bul ve çiz (Adım Adım Ekleme)
            progress_ratio = min(1.0, (i + chunk_size + 1) / len(sim_logs))

            if sim_queue:
                current_q_len = int(progress_ratio * len(sim_queue))
                df_q = pd.DataFrame(sim_queue[:current_q_len])
                if not df_q.empty:
                    fig_q = px.area(df_q, x="Zaman", y="Uzunluk", title="Kuyruk Uzunluğu Zaman İçinde",
                                    labels={"Zaman": "Zaman (dk)", "Uzunluk": "Kuyruk Uzunluğu"})
                    fig_q.update_layout(height=300)
                    chart_placeholder.plotly_chart(fig_q, use_container_width=True, key=f"q_anim_{i}")

            if sim_waits:
                current_w_len = int(progress_ratio * len(sim_waits))
                df_w = pd.DataFrame(sim_waits[:current_w_len])
                if not df_w.empty:
                    fig_w = px.bar(df_w, x="Zaman", y="Bekleme Süresi", title="Bekleme Süreleri",
                                   labels={"Zaman": "Zaman (dk)", "Bekleme Süresi": "Bekleme Süresi (dk)"})
                    fig_w.update_layout(height=300)
                    wait_chart_placeholder.plotly_chart(fig_w, use_container_width=True, key=f"w_anim_{i}")

            # Dashboard'un canlı görünmesi için kullanıcının seçeceği hızda bekle
            time.sleep(CANLI_HIZ)

    # Animasyon sonunda eksik parça kalmaması için son bir yansıtma yapılır
    log_text = "\n".join(sim_logs[::-1])
    with log_placeholder.container():
        st.code(log_text, language="markdown")
    if sim_queue:
        df_q = pd.DataFrame(sim_queue)
        fig_q = px.area(df_q, x="Zaman", y="Uzunluk", title="Kuyruk Uzunluğu Zaman İçinde",
                        labels={"Zaman": "Zaman (dk)", "Uzunluk": "Kuyruk Uzunluğu"})
        fig_q.update_layout(height=300)
        chart_placeholder.plotly_chart(fig_q, use_container_width=True, key="q_final")
    if sim_waits:
        df_w = pd.DataFrame(sim_waits)
        fig_w = px.bar(df_w, x="Zaman", y="Bekleme Süresi", title="Bekleme Süreleri",
                       labels={"Zaman": "Zaman (dk)", "Bekleme Süresi": "Bekleme Süresi (dk)"})
        fig_w.update_layout(height=300)
        wait_chart_placeholder.plotly_chart(fig_w, use_container_width=True, key="w_final")

    # Detaylı Grafikler Tabı
    if sim_waits:
        df_waits = pd.DataFrame(sim_waits)
        fig_hist = px.histogram(df_waits, x="Bekleme Süresi", nbins=20, title="Bekleme Süresi Dağılımı",
                                labels={"Bekleme Süresi": "Bekleme Süresi (dk)", "count": "Müşteri Sayısı"})
        fig_hist.update_layout(height=400)
        detailed_chart_placeholder.plotly_chart(fig_hist, use_container_width=True, key="hist_final")

    st.success("✅ Simülasyon Tamamlandı!")

    # Simülasyon Özeti Çıktısı
    if sim_waits:
        df_final = pd.DataFrame(sim_waits)
        with report_placeholder.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📊 Simülasyon Özeti")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            col_stat1.metric("Toplam Hizmet Alan", len(df_final))
            col_stat2.metric("Ortalama Bekleme Süresi", f"{df_final['Bekleme Süresi'].mean():.2f} dk")
            col_stat3.metric("Maksimum Bekleme Süresi", f"{df_final['Bekleme Süresi'].max():.2f} dk")
            col_stat4.metric("Medyan Bekleme Süresi", f"{df_final['Bekleme Süresi'].median():.2f} dk")
            st.markdown('</div>', unsafe_allow_html=True)

            # Detaylı İstatistikler
            st.subheader("🔍 Detaylı İstatistikler")
            st.dataframe(df_final.describe().round(2))
    else:
        st.warning("Bu simülasyon ayarlarında hiç müşteri gelmedi.")
