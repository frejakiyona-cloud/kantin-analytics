import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kantin Ceria Nusantara — Analytics",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hero header */
.hero {
    background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 60%, #38BDF8 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.hero h1 { font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.hero p  { font-size: 0.95rem; margin: 0.4rem 0 0; opacity: 0.85; }

/* KPI cards */
.kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.kpi-card {
    flex: 1; min-width: 150px;
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-value { font-size: 1.6rem; font-weight: 800; color: #1B3A6B; line-height: 1.2; font-family: 'Space Mono', monospace; }
.kpi-sub   { font-size: 0.75rem; color: #64748B; margin-top: 0.2rem; }

/* Section headers */
.section-head {
    font-size: 1.05rem; font-weight: 700; color: #1B3A6B;
    border-left: 4px solid #2563EB;
    padding-left: 0.7rem;
    margin: 1.8rem 0 0.8rem;
}

/* Upload zone */
.upload-hint {
    text-align: center; color: #64748B;
    font-size: 0.9rem; padding: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] { background: #F8FAFF; }
</style>
""", unsafe_allow_html=True)

# ── Colour palette (matches BINUS DigiBattle branding) ───────────────────────
BLUE   = "#2563EB"
NAVY   = "#1B3A6B"
GOLD   = "#F59E0B"
SKY    = "#38BDF8"
TEAL   = "#0D9488"
CORAL  = "#F43F5E"
PURPLE = "#7C3AED"
GREEN  = "#16A34A"
MENU_COLORS = [BLUE, GOLD, TEAL, CORAL, PURPLE, GREEN]

MENU_PRICE = {
    "nasi_goreng_sold": 15000,
    "ayam_geprek_sold": 18000,
    "mie_goreng_sold":  12000,
    "bakso_sold":       14000,
    "snack_sold":        5000,
    "drinks_sold":       6000,
}
MENU_LABEL = {
    "nasi_goreng_sold": "Nasi Goreng",
    "ayam_geprek_sold": "Ayam Geprek",
    "mie_goreng_sold":  "Mie Goreng",
    "bakso_sold":       "Bakso",
    "snack_sold":       "Snack",
    "drinks_sold":      "Minuman",
}
DAY_ORDER = ["Senin","Selasa","Rabu","Kamis","Jumat"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_idr(x):
    return f"Rp {x:,.0f}".replace(",",".")

def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    # normalise day_of_week just in case
    if "day_of_week" in df.columns:
        df["day_of_week"] = df["day_of_week"].str.strip().str.capitalize()
    return df

def plotly_defaults(fig, height=350):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Plus Jakarta Sans", size=12, color="#1E293B"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#F1F5F9", linecolor="#E2E8F0")
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Binus_University_logo.svg/320px-Binus_University_logo.svg.png", width=130)
    st.markdown("### 📊 DigiBattle — Business Analytics")
    st.markdown("**Kantin Ceria Nusantara**  \nJan – Mar 2024 · 90 hari sekolah")
    st.divider()

    uploaded = st.file_uploader(
        "Upload dataset CSV",
        type=["csv"],
        help="File: kantin_pre_elimination_dataset.csv"
    )

    if uploaded:
        st.success("✅ Dataset berhasil di-upload!")
        st.caption(f"File: `{uploaded.name}`")
        st.divider()
        st.markdown("**Filter**")
        # placeholder — will be populated after load

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🍜 Kantin Ceria Nusantara</h1>
  <p>Business Analytics Dashboard · DigiBattle 2024 · BINUS University School of Information Systems</p>
</div>
""", unsafe_allow_html=True)

if not uploaded:
    st.markdown("""
    <div class="upload-hint">
        <h3 style="color:#1B3A6B;">Upload dataset CSV untuk mulai analisis</h3>
        <p>Gunakan sidebar kiri → <b>Upload dataset CSV</b></p>
        <p style="font-size:0.82rem;color:#94A3B8;">
            File yang dibutuhkan: <code>kantin_pre_elimination_dataset.csv</code><br>
            90 baris × 15 kolom · Periode Januari – Maret 2024
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load ──────────────────────────────────────────────────────────────────────
df = load_data(uploaded)

# Sidebar filters (after load)
with st.sidebar:
    months = sorted(df["month"].unique())
    month_labels = {1:"Januari", 2:"Februari", 3:"Maret"}
    sel_months = st.multiselect(
        "Bulan", options=months,
        default=months,
        format_func=lambda x: month_labels.get(x, str(x))
    )
    weather_opts = df["weather"].unique().tolist() if "weather" in df.columns else []
    sel_weather = st.multiselect("Kondisi Cuaca", options=weather_opts, default=weather_opts)

mask = df["month"].isin(sel_months)
if weather_opts:
    mask &= df["weather"].isin(sel_weather)
df_f = df[mask].copy()

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_rev  = df_f["total_revenue_idr"].sum()
avg_rev    = df_f["total_revenue_idr"].mean()
total_cust = df_f["total_customers"].sum()
avg_queue  = df_f["avg_queue_time_minutes"].mean()
total_run  = df_f["stock_runout_events"].sum()
best_day_row = df_f.loc[df_f["total_revenue_idr"].idxmax()]

menu_cols = list(MENU_PRICE.keys())
menu_totals = {c: df_f[c].sum() for c in menu_cols if c in df_f.columns}
top_menu = MENU_LABEL[max(menu_totals, key=menu_totals.get)] if menu_totals else "—"

st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
kpis = [
    ("Total Pendapatan", fmt_idr(total_rev), f"Rata-rata {fmt_idr(avg_rev)}/hari"),
    ("Total Pelanggan",  f"{total_cust:,}".replace(",","."), f"Rata-rata {df_f['total_customers'].mean():.0f}/hari"),
    ("Rata-rata Antrian", f"{avg_queue:.1f} mnt", "Per hari sekolah"),
    ("Stock Runout",    str(int(total_run)), "Total kejadian kehabisan stok"),
    ("Menu Terlaris",   top_menu, "Selama periode analisis"),
    ("Hari Terbaik",    best_day_row["date"].strftime("%d %b") if "date" in best_day_row else "—",
                        fmt_idr(best_day_row["total_revenue_idr"])),
]
cols = st.columns(len(kpis))
for col, (label, val, sub) in zip(cols, kpis):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Task 1 — Eksplorasi Data",
    "💰 Task 2 — Pendapatan",
    "🍱 Task 3 — Menu",
    "⚙️ Task 4 — Operasional",
    "🌦️ Task 5 — Cuaca",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Eksplorasi Data
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-head">Statistik Deskriptif</div>', unsafe_allow_html=True)
    num_cols = ["total_customers","total_transactions","total_revenue_idr",
                "stock_runout_events","avg_queue_time_minutes"] + menu_cols
    num_cols = [c for c in num_cols if c in df_f.columns]
    desc = df_f[num_cols].describe().T[["mean","std","min","50%","max"]]
    desc.columns = ["Mean","Std Dev","Min","Median","Max"]
    desc.index = [MENU_LABEL.get(i, i.replace("_"," ").title()) for i in desc.index]
    st.dataframe(desc.style.format("{:,.1f}"), use_container_width=True)

    st.markdown('<div class="section-head">Distribusi Pendapatan Harian & Waktu Antrian</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df_f, x="total_revenue_idr", nbins=20,
                           color_discrete_sequence=[BLUE],
                           title="Distribusi Total Pendapatan Harian")
        fig.update_traces(marker_line_width=0.5, marker_line_color="white")
        fig.update_xaxes(title="Pendapatan (IDR)")
        fig.update_yaxes(title="Frekuensi")
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)
        st.caption("💡 Distribusi pendapatan cenderung simetris/normal dengan ekor kanan — menunjukkan beberapa hari luar biasa tinggi (hari acara sekolah / Jumat).")

    with c2:
        fig = px.histogram(df_f, x="avg_queue_time_minutes", nbins=20,
                           color_discrete_sequence=[GOLD],
                           title="Distribusi Rata-rata Waktu Antrian")
        fig.update_traces(marker_line_width=0.5, marker_line_color="white")
        fig.update_xaxes(title="Waktu Antrian (menit)")
        fig.update_yaxes(title="Frekuensi")
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)
        st.caption("💡 Waktu antrian cenderung right-skewed — sebagian besar hari antrian wajar, namun ada lonjakan ekstrem di hari ramai.")

    st.markdown('<div class="section-head">Pendapatan Bulanan</div>', unsafe_allow_html=True)
    monthly = df_f.groupby("month_name")["total_revenue_idr"].sum().reset_index()
    month_order = ["January","February","March"]
    monthly["month_name"] = pd.Categorical(monthly["month_name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values("month_name")
    fig = px.bar(monthly, x="month_name", y="total_revenue_idr",
                 color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                 text=monthly["total_revenue_idr"].apply(lambda x: fmt_idr(x)),
                 title="Total Pendapatan per Bulan")
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="Bulan")
    fig.update_yaxes(title="Total Pendapatan (IDR)")
    st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)

    st.markdown('<div class="section-head">Proporsi Cuaca & Acara Sekolah</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if "weather" in df_f.columns:
            w_cnt = df_f["weather"].value_counts().reset_index()
            fig = px.pie(w_cnt, names="weather", values="count",
                         color_discrete_sequence=[SKY, BLUE, NAVY],
                         title="Proporsi Kondisi Cuaca",
                         hole=0.45)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)
    with c2:
        if "school_event" in df_f.columns:
            e_cnt = df_f["school_event"].map({1:"Ada Acara",0:"Tidak Ada Acara"}).value_counts().reset_index()
            fig = px.pie(e_cnt, names="school_event", values="count",
                         color_discrete_sequence=[GOLD, TEAL],
                         title="Hari dengan Acara Sekolah",
                         hole=0.45)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Pendapatan
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-head">Grafik Pendapatan Harian (90 Hari)</div>', unsafe_allow_html=True)

    df_sorted = df_f.sort_values("date")
    top5    = df_sorted.nlargest(5, "total_revenue_idr")
    bottom5 = df_sorted.nsmallest(5, "total_revenue_idr")
    events  = df_sorted[df_sorted["school_event"] == 1] if "school_event" in df_sorted.columns else pd.DataFrame()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["date"], y=df_sorted["total_revenue_idr"],
        mode="lines", name="Pendapatan Harian",
        line=dict(color=BLUE, width=1.8),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=top5["date"], y=top5["total_revenue_idr"],
        mode="markers+text", name="Top 5",
        marker=dict(color=GREEN, size=10, symbol="star"),
        text=top5["date"].dt.strftime("%d/%m"), textposition="top center",
        textfont=dict(size=9)
    ))
    fig.add_trace(go.Scatter(
        x=bottom5["date"], y=bottom5["total_revenue_idr"],
        mode="markers+text", name="Bottom 5",
        marker=dict(color=CORAL, size=10, symbol="triangle-down"),
        text=bottom5["date"].dt.strftime("%d/%m"), textposition="bottom center",
        textfont=dict(size=9)
    ))
    if not events.empty:
        fig.add_trace(go.Scatter(
            x=events["date"], y=events["total_revenue_idr"],
            mode="markers", name="Acara Sekolah",
            marker=dict(color=GOLD, size=8, symbol="diamond", line=dict(width=1, color="white"))
        ))
    fig.update_xaxes(title="Tanggal")
    fig.update_yaxes(title="Pendapatan (IDR)")
    st.plotly_chart(plotly_defaults(fig, 380), use_container_width=True)
    st.caption("💡 Puncak pendapatan terlihat di hari dengan acara sekolah. Titik terendah umumnya terjadi di awal minggu (Senin) atau hari hujan deras.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Rata-rata Pendapatan per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns:
            day_avg = df_f.groupby("day_of_week")["total_revenue_idr"].mean().reindex(DAY_ORDER).reset_index()
            fig = px.bar(day_avg, x="day_of_week", y="total_revenue_idr",
                         color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                         text=day_avg["total_revenue_idr"].apply(lambda x: fmt_idr(x)),
                         title="Rata-rata Pendapatan per Hari")
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Rata-rata Pendapatan (IDR)")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

    with c2:
        st.markdown('<div class="section-head">Pendapatan: Acara vs Non-Acara</div>', unsafe_allow_html=True)
        if "school_event" in df_f.columns:
            df_f["event_label"] = df_f["school_event"].map({1:"Ada Acara",0:"Tidak Ada Acara"})
            fig = px.box(df_f, x="event_label", y="total_revenue_idr",
                         color="event_label",
                         color_discrete_map={"Ada Acara": GOLD, "Tidak Ada Acara": BLUE},
                         title="Distribusi Pendapatan: Acara vs Non-Acara",
                         points="all")
            fig.update_xaxes(title="")
            fig.update_yaxes(title="Pendapatan (IDR)")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

    st.markdown('<div class="section-head">Pendapatan Mingguan</div>', unsafe_allow_html=True)
    weekly = df_f.groupby("week")["total_revenue_idr"].sum().reset_index()
    fig = px.bar(weekly, x="week", y="total_revenue_idr",
                 color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                 title="Total Pendapatan per Minggu")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="Minggu ke-")
    fig.update_yaxes(title="Total Pendapatan (IDR)")
    best_wk  = weekly.loc[weekly["total_revenue_idr"].idxmax(), "week"]
    worst_wk = weekly.loc[weekly["total_revenue_idr"].idxmin(), "week"]
    st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)
    st.caption(f"💡 Minggu terbaik: Minggu ke-**{best_wk}** · Minggu terendah: Minggu ke-**{worst_wk}**")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Menu
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    valid_menus = [c for c in menu_cols if c in df_f.columns]
    menu_sum    = {c: df_f[c].sum() for c in valid_menus}
    menu_rev    = {c: df_f[c].sum() * MENU_PRICE[c] for c in valid_menus}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Total Terjual per Menu</div>', unsafe_allow_html=True)
        df_menu = pd.DataFrame({"menu": [MENU_LABEL[c] for c in valid_menus],
                                "terjual": [menu_sum[c] for c in valid_menus]}).sort_values("terjual", ascending=True)
        fig = px.bar(df_menu, x="terjual", y="menu", orientation="h",
                     color="terjual", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                     text="terjual", title="Total Porsi Terjual (90 Hari)")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(title="")
        fig.update_xaxes(title="Jumlah Porsi")
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

    with c2:
        st.markdown('<div class="section-head">Estimasi Kontribusi Pendapatan per Menu</div>', unsafe_allow_html=True)
        df_rev = pd.DataFrame({"menu": [MENU_LABEL[c] for c in valid_menus],
                                "rev":  [menu_rev[c] for c in valid_menus]})
        fig = px.pie(df_rev, names="menu", values="rev",
                     color_discrete_sequence=MENU_COLORS,
                     title="Proporsi Pendapatan per Menu", hole=0.4)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)
        st.caption("💡 Ayam Geprek paling mahal (Rp 18.000), jadi meski bukan paling laris secara volume, kontribusi pendapatannya besar.")

    st.markdown('<div class="section-head">Tren Penjualan Bulanan per Menu</div>', unsafe_allow_html=True)
    df_trend = df_f.groupby("month_name")[valid_menus].sum().reset_index()
    df_trend_melt = df_trend.melt(id_vars="month_name", var_name="menu", value_name="terjual")
    df_trend_melt["menu"] = df_trend_melt["menu"].map(MENU_LABEL)
    df_trend_melt["month_name"] = pd.Categorical(df_trend_melt["month_name"], categories=["January","February","March"], ordered=True)
    df_trend_melt = df_trend_melt.sort_values("month_name")
    fig = px.line(df_trend_melt, x="month_name", y="terjual", color="menu",
                  markers=True, color_discrete_sequence=MENU_COLORS,
                  title="Tren Penjualan Bulanan per Menu")
    fig.update_xaxes(title="Bulan")
    fig.update_yaxes(title="Jumlah Terjual")
    st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Ayam Geprek vs Stock Runout (Scatter + Korelasi)</div>', unsafe_allow_html=True)
        if "ayam_geprek_sold" in df_f.columns and "stock_runout_events" in df_f.columns:
            corr = df_f["ayam_geprek_sold"].corr(df_f["stock_runout_events"])
            fig = px.scatter(df_f, x="ayam_geprek_sold", y="stock_runout_events",
                             trendline="ols", color_discrete_sequence=[CORAL],
                             title=f"Ayam Geprek Terjual vs Stock Runout (r = {corr:.2f})")
            fig.update_xaxes(title="Ayam Geprek Terjual")
            fig.update_yaxes(title="Stock Runout Events")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)
            st.caption(f"💡 Korelasi r = **{corr:.2f}** — {'Positif kuat: semakin banyak Ayam Geprek terjual, semakin sering stok habis.' if corr > 0.5 else 'Korelasi moderat/lemah.'}")

    with c2:
        st.markdown('<div class="section-head">Rata-rata Penjualan: Acara vs Non-Acara</div>', unsafe_allow_html=True)
        if "school_event" in df_f.columns:
            ev_menu = df_f.groupby("school_event")[valid_menus].mean().T.reset_index()
            ev_menu.columns = ["menu","Non-Acara","Ada Acara"] if 0 in ev_menu.columns else ev_menu.columns
            ev_menu["menu"] = ev_menu["menu"].map(MENU_LABEL)
            fig = go.Figure()
            fig.add_bar(name="Non-Acara",  x=ev_menu["menu"], y=ev_menu.iloc[:,1], marker_color=BLUE)
            fig.add_bar(name="Ada Acara",  x=ev_menu["menu"], y=ev_menu.iloc[:,2], marker_color=GOLD)
            fig.update_layout(barmode="group", title="Rata-rata Penjualan Menu: Acara vs Non-Acara")
            fig.update_xaxes(title="Menu")
            fig.update_yaxes(title="Rata-rata Porsi/Hari")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Operasional
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Box Plot Waktu Antrian per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns:
            df_day = df_f[df_f["day_of_week"].isin(DAY_ORDER)]
            fig = px.box(df_day, x="day_of_week", y="avg_queue_time_minutes",
                         category_orders={"day_of_week": DAY_ORDER},
                         color="day_of_week",
                         color_discrete_sequence=MENU_COLORS,
                         title="Distribusi Waktu Antrian per Hari",
                         points="all")
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Waktu Antrian (menit)")
            st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

    with c2:
        st.markdown('<div class="section-head">Pelanggan vs Waktu Antrian</div>', unsafe_allow_html=True)
        fig = px.scatter(df_f, x="total_customers", y="avg_queue_time_minutes",
                         trendline="ols", color_discrete_sequence=[TEAL],
                         title="Total Pelanggan vs Rata-rata Waktu Antrian")
        # Mark 10-minute threshold
        fig.add_hline(y=10, line_dash="dash", line_color=CORAL,
                      annotation_text="10 menit", annotation_position="top right")
        fig.update_xaxes(title="Total Pelanggan")
        fig.update_yaxes(title="Waktu Antrian (menit)")
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)
        st.caption("💡 Garis merah = batas 10 menit. Perhatikan di berapa pelanggan antrian mulai melewati batas ini.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Stock Runout per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns and "stock_runout_events" in df_f.columns:
            runout_day = df_f.groupby("day_of_week")["stock_runout_events"].sum().reindex(DAY_ORDER).reset_index()
            fig = px.bar(runout_day, x="day_of_week", y="stock_runout_events",
                         color="stock_runout_events", color_continuous_scale=["#FEF9C3","#DC2626"],
                         text="stock_runout_events",
                         title="Total Stock Runout per Hari")
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Jumlah Kejadian")
            st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)

    with c2:
        st.markdown('<div class="section-head">Stock Runout per Kondisi Cuaca</div>', unsafe_allow_html=True)
        if "weather" in df_f.columns and "stock_runout_events" in df_f.columns:
            runout_wx = df_f.groupby("weather")["stock_runout_events"].mean().reset_index()
            fig = px.bar(runout_wx, x="weather", y="stock_runout_events",
                         color="weather", color_discrete_sequence=[SKY, BLUE, NAVY],
                         text=runout_wx["stock_runout_events"].round(2),
                         title="Rata-rata Stock Runout per Cuaca")
            fig.update_traces(textposition="outside")
            fig.update_xaxes(title="Cuaca")
            fig.update_yaxes(title="Rata-rata Kejadian/Hari")
            st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)

    st.markdown('<div class="section-head">Estimasi Pendapatan Hilang akibat Stock Runout</div>', unsafe_allow_html=True)
    avg_txn = df_f["total_revenue_idr"].mean() / df_f["total_transactions"].mean() if "total_transactions" in df_f.columns else 12000
    lost_per_event = 15 * avg_txn
    df_f["lost_revenue"] = df_f["stock_runout_events"] * lost_per_event
    total_lost = df_f["lost_revenue"].sum()

    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Rata-rata Nilai Transaksi", fmt_idr(avg_txn))
    kc2.metric("Lost Revenue per Kejadian", fmt_idr(lost_per_event), help="Asumsi: 15 penjualan hilang × nilai rata-rata")
    kc3.metric("Total Estimasi Lost Revenue", fmt_idr(total_lost))

    fig = px.area(df_f.sort_values("date"), x="date", y="lost_revenue",
                  color_discrete_sequence=[CORAL],
                  title="Estimasi Pendapatan Hilang per Hari (Stock Runout)")
    fig.update_xaxes(title="Tanggal")
    fig.update_yaxes(title="Pendapatan Hilang (IDR)")
    st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Cuaca
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    if "weather" not in df_f.columns:
        st.info("Kolom 'weather' tidak ditemukan di dataset.")
    else:
        st.markdown('<div class="section-head">Perbandingan Metrik Utama per Cuaca</div>', unsafe_allow_html=True)
        wx_table = df_f.groupby("weather").agg(
            Hari=("date","count"),
            Rata_Pendapatan=("total_revenue_idr","mean"),
            Rata_Pelanggan=("total_customers","mean"),
            Rata_Antrian=("avg_queue_time_minutes","mean"),
            Rata_Runout=("stock_runout_events","mean"),
        ).reset_index()
        wx_table.columns = ["Cuaca","Hari","Avg Pendapatan","Avg Pelanggan","Avg Antrian (mnt)","Avg Runout"]
        wx_table["Avg Pendapatan"] = wx_table["Avg Pendapatan"].apply(fmt_idr)
        wx_table["Avg Pelanggan"]  = wx_table["Avg Pelanggan"].round(1)
        wx_table["Avg Antrian (mnt)"] = wx_table["Avg Antrian (mnt)"].round(2)
        wx_table["Avg Runout"]     = wx_table["Avg Runout"].round(2)
        st.dataframe(wx_table, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-head">Pendapatan per Cuaca & Hari</div>', unsafe_allow_html=True)
            if "day_of_week" in df_f.columns:
                wx_day = df_f[df_f["day_of_week"].isin(DAY_ORDER)].groupby(
                    ["day_of_week","weather"])["total_revenue_idr"].mean().reset_index()
                fig = px.bar(wx_day, x="day_of_week", y="total_revenue_idr",
                             color="weather",
                             barmode="group",
                             category_orders={"day_of_week": DAY_ORDER},
                             color_discrete_sequence=[SKY, BLUE, NAVY],
                             title="Rata-rata Pendapatan per Hari × Cuaca")
                fig.update_xaxes(title="Hari")
                fig.update_yaxes(title="Rata-rata Pendapatan (IDR)")
                st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

        with c2:
            st.markdown('<div class="section-head">Penjualan Minuman: Hujan vs Cerah</div>', unsafe_allow_html=True)
            if "drinks_sold" in df_f.columns:
                drinks_wx = df_f.groupby("weather")["drinks_sold"].mean().reset_index()
                fig = px.bar(drinks_wx, x="weather", y="drinks_sold",
                             color="weather",
                             color_discrete_sequence=[SKY, BLUE, NAVY],
                             text=drinks_wx["drinks_sold"].round(1),
                             title="Rata-rata Minuman Terjual per Kondisi Cuaca")
                fig.update_traces(textposition="outside")
                fig.update_xaxes(title="Cuaca")
                fig.update_yaxes(title="Rata-rata Minuman Terjual/Hari")
                st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

        st.markdown('<div class="section-head">Scatter: Cuaca & Pelanggan</div>', unsafe_allow_html=True)
        fig = px.scatter(df_f, x="total_customers", y="total_revenue_idr",
                         color="weather",
                         color_discrete_sequence=[SKY, BLUE, NAVY],
                         size="avg_queue_time_minutes",
                         hover_data=["date","day_of_week"],
                         title="Pelanggan vs Pendapatan (warna = cuaca, ukuran = waktu antrian)")
        fig.update_xaxes(title="Total Pelanggan")
        fig.update_yaxes(title="Total Pendapatan (IDR)")
        st.plotly_chart(plotly_defaults(fig, 380), use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("📊 Kantin Ceria Nusantara Analytics · DigiBattle 2024 · Built for BINUS Business Analytics Case Study")
