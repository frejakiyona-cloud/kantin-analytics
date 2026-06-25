import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
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
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 60%, #38BDF8 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; color: white;
}
.hero h1 { font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.hero p  { font-size: 0.95rem; margin: 0.4rem 0 0; opacity: 0.85; }

.kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.kpi-card {
    flex: 1; min-width: 150px; background: white;
    border: 1px solid #E2E8F0; border-radius: 12px;
    padding: 1.1rem 1.3rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-value { font-size: 1.6rem; font-weight: 800; color: #1B3A6B; line-height: 1.2; font-family: 'Space Mono', monospace; }
.kpi-sub   { font-size: 0.75rem; color: #64748B; margin-top: 0.2rem; }

.section-head {
    font-size: 1.05rem; font-weight: 700; color: #1B3A6B;
    border-left: 4px solid #2563EB; padding-left: 0.7rem; margin: 1.8rem 0 0.8rem;
}

.insight-box {
    background: #F0F7FF; border-left: 4px solid #2563EB;
    border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem;
    margin-top: 0.5rem; margin-bottom: 1rem;
}
.insight-box p { margin: 0; font-size: 0.88rem; color: #1E3A5F; line-height: 1.6; }
.insight-box strong { color: #1B3A6B; }

.insight-warn {
    background: #FFF7ED; border-left: 4px solid #F59E0B;
    border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem;
    margin-top: 0.5rem; margin-bottom: 1rem;
}
.insight-warn p { margin: 0; font-size: 0.88rem; color: #78350F; line-height: 1.6; }

.insight-ok {
    background: #F0FDF4; border-left: 4px solid #16A34A;
    border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem;
    margin-top: 0.5rem; margin-bottom: 1rem;
}
.insight-ok p { margin: 0; font-size: 0.88rem; color: #14532D; line-height: 1.6; }

.upload-hint { text-align: center; color: #64748B; font-size: 0.9rem; padding: 1rem; }
section[data-testid="stSidebar"] { background: #F8FAFF; }
</style>
""", unsafe_allow_html=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE   = "#2563EB"; NAVY = "#1B3A6B"; GOLD = "#F59E0B"
SKY    = "#38BDF8"; TEAL = "#0D9488"; CORAL = "#F43F5E"
PURPLE = "#7C3AED"; GREEN = "#16A34A"
MENU_COLORS = [BLUE, GOLD, TEAL, CORAL, PURPLE, GREEN]

MENU_PRICE = {
    "nasi_goreng_sold": 15000, "ayam_geprek_sold": 18000,
    "mie_goreng_sold":  12000, "bakso_sold":       14000,
    "snack_sold":        5000, "drinks_sold":       6000,
}
MENU_LABEL = {
    "nasi_goreng_sold": "Nasi Goreng", "ayam_geprek_sold": "Ayam Geprek",
    "mie_goreng_sold":  "Mie Goreng",  "bakso_sold":       "Bakso",
    "snack_sold":       "Snack",        "drinks_sold":      "Minuman",
}
DAY_ORDER = ["Senin","Selasa","Rabu","Kamis","Jumat"]
MONTH_ORDER = ["January","February","March","April","May"]
MONTH_ID    = {1:"Januari",2:"Februari",3:"Maret",4:"April",5:"Mei"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_idr(x):
    return f"Rp {x:,.0f}".replace(",",".")

def insight(text, kind="blue"):
    cls = {"blue":"insight-box","warn":"insight-warn","ok":"insight-ok"}.get(kind,"insight-box")
    st.markdown(f'<div class="{cls}"><p>📊 {text}</p></div>', unsafe_allow_html=True)

def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    if "day_of_week" in df.columns:
        df["day_of_week"] = df["day_of_week"].str.strip().str.capitalize()
    return df

def plotly_defaults(fig, height=350):
    fig.update_layout(
        height=height, plot_bgcolor="white", paper_bgcolor="white",
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
    st.markdown("**Kantin Ceria Nusantara**  \nJan – Mei 2024 · 90 hari sekolah")
    st.divider()
    uploaded = st.file_uploader("Upload dataset CSV", type=["csv"],
                                help="File: kantin_pre_elimination_dataset.csv")
    if uploaded:
        st.success("✅ Dataset berhasil di-upload!")
        st.caption(f"File: `{uploaded.name}`")
        st.divider()
        st.markdown("**Filter**")

# ── Hero ──────────────────────────────────────────────────────────────────────
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
            File: <code>kantin_pre_elimination_dataset.csv</code><br>
            90 baris × 15 kolom · Periode Januari – Mei 2024
        </p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Load & Filter ─────────────────────────────────────────────────────────────
df = load_data(uploaded)

with st.sidebar:
    months = sorted(df["month"].unique())
    sel_months = st.multiselect("Bulan", options=months, default=months,
                                format_func=lambda x: MONTH_ID.get(x, str(x)))
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

menu_cols   = list(MENU_PRICE.keys())
menu_totals = {c: df_f[c].sum() for c in menu_cols if c in df_f.columns}
top_menu    = MENU_LABEL[max(menu_totals, key=menu_totals.get)] if menu_totals else "—"

st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
kpis = [
    ("Total Pendapatan",   fmt_idr(total_rev),          f"Rata-rata {fmt_idr(avg_rev)}/hari"),
    ("Total Pelanggan",    f"{total_cust:,}".replace(",","."), f"Rata-rata {df_f['total_customers'].mean():.0f}/hari"),
    ("Rata-rata Antrian",  f"{avg_queue:.1f} mnt",       "Per hari sekolah"),
    ("Stock Runout",       str(int(total_run)),           "Total kejadian kehabisan stok"),
    ("Menu Terlaris",      top_menu,                      "Selama periode analisis"),
    ("Hari Terbaik",       best_day_row["date"].strftime("%d %b"),
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
# TAB 1
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

    rev_mean = df_f["total_revenue_idr"].mean()
    rev_std  = df_f["total_revenue_idr"].std()
    rev_cv   = rev_std / rev_mean * 100
    q_mean   = df_f["avg_queue_time_minutes"].mean()
    q_max    = df_f["avg_queue_time_minutes"].max()
    insight(
        f"Rata-rata pendapatan harian adalah <strong>{fmt_idr(rev_mean)}</strong> dengan standar deviasi "
        f"<strong>{fmt_idr(rev_std)}</strong> (CV = {rev_cv:.1f}%). Angka CV {'di bawah 20% — pendapatan relatif stabil' if rev_cv < 20 else 'cukup tinggi — ada variasi besar antar hari'}. "
        f"Waktu antrian rata-rata <strong>{q_mean:.1f} menit</strong>, namun pernah mencapai puncak <strong>{q_max:.1f} menit</strong> — "
        f"menunjukkan ada hari-hari dengan beban sangat tinggi yang perlu diantisipasi.",
        "blue"
    )

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
        skew_rev = df_f["total_revenue_idr"].skew()
        shape = "right-skewed (ekor ke kanan)" if skew_rev > 0.5 else ("left-skewed" if skew_rev < -0.5 else "mendekati normal/simetris")
        insight(
            f"Distribusi pendapatan bersifat <strong>{shape}</strong> (skewness = {skew_rev:.2f}). "
            f"{'Ini berarti sebagian besar hari memiliki pendapatan di bawah rata-rata, namun ada beberapa hari istimewa dengan pendapatan sangat tinggi — kemungkinan hari acara sekolah atau hari Jumat.' if skew_rev > 0.5 else 'Pendapatan terdistribusi cukup merata di sekitar nilai rata-rata.'}",
            "blue"
        )
    with c2:
        fig = px.histogram(df_f, x="avg_queue_time_minutes", nbins=20,
                           color_discrete_sequence=[GOLD],
                           title="Distribusi Rata-rata Waktu Antrian")
        fig.update_traces(marker_line_width=0.5, marker_line_color="white")
        fig.update_xaxes(title="Waktu Antrian (menit)")
        fig.update_yaxes(title="Frekuensi")
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)
        skew_q = df_f["avg_queue_time_minutes"].skew()
        pct_over10 = (df_f["avg_queue_time_minutes"] > 10).mean() * 100
        insight(
            f"Distribusi waktu antrian bersifat <strong>{'right-skewed' if skew_q > 0.5 else 'relatif simetris'}</strong> (skewness = {skew_q:.2f}). "
            f"Sebanyak <strong>{pct_over10:.1f}%</strong> hari memiliki antrian rata-rata lebih dari 10 menit — "
            f"{'proporsi yang signifikan dan perlu penanganan operasional segera.' if pct_over10 > 20 else 'masih dalam batas yang dapat ditoleransi.'}",
            "warn" if pct_over10 > 20 else "blue"
        )

    st.markdown('<div class="section-head">Pendapatan Bulanan</div>', unsafe_allow_html=True)
    monthly = df_f.groupby("month_name")["total_revenue_idr"].sum().reset_index()
    monthly["month_name"] = pd.Categorical(monthly["month_name"], categories=MONTH_ORDER, ordered=True)
    monthly = monthly.sort_values("month_name")
    fig = px.bar(monthly, x="month_name", y="total_revenue_idr",
                 color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                 text=monthly["total_revenue_idr"].apply(fmt_idr),
                 title="Total Pendapatan per Bulan")
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="Bulan")
    fig.update_yaxes(title="Total Pendapatan (IDR)")
    st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)

    if len(monthly) > 0:
        best_month  = monthly.loc[monthly["total_revenue_idr"].idxmax(), "month_name"]
        worst_month = monthly.loc[monthly["total_revenue_idr"].idxmin(), "month_name"]
        best_val    = monthly["total_revenue_idr"].max()
        worst_val   = monthly["total_revenue_idr"].min()
        gap_pct     = (best_val - worst_val) / worst_val * 100
        insight(
            f"Bulan dengan pendapatan tertinggi adalah <strong>{best_month}</strong> ({fmt_idr(best_val)}), "
            f"sedangkan bulan terendah adalah <strong>{worst_month}</strong> ({fmt_idr(worst_val)}). "
            f"Selisihnya sebesar <strong>{gap_pct:.1f}%</strong> — perbedaan ini perlu diinvestigasi lebih lanjut, "
            f"misalnya apakah berkaitan dengan jumlah hari sekolah aktif, acara khusus, atau musim ujian.",
            "blue"
        )

    st.markdown('<div class="section-head">Proporsi Cuaca & Acara Sekolah</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if "weather" in df_f.columns:
            w_cnt = df_f["weather"].value_counts().reset_index()
            fig = px.pie(w_cnt, names="weather", values="count",
                         color_discrete_sequence=[SKY, BLUE, NAVY],
                         title="Proporsi Kondisi Cuaca", hole=0.45)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)
            dom_weather = w_cnt.iloc[0]["weather"]
            dom_pct     = w_cnt.iloc[0]["count"] / w_cnt["count"].sum() * 100
            insight(
                f"Kondisi cuaca yang paling sering terjadi adalah <strong>{dom_weather}</strong> ({dom_pct:.1f}% hari). "
                f"{'Kondisi cuaca hujan yang cukup sering bisa memengaruhi jumlah pelanggan dan pola pembelian — analisis dampaknya ada di Tab 5.' if 'Hujan' in w_cnt['weather'].values else 'Cuaca dominan cerah atau berawan mendukung kehadiran pelanggan yang konsisten.'}",
                "blue"
            )
    with c2:
        if "school_event" in df_f.columns:
            e_cnt = df_f["school_event"].map({1:"Ada Acara",0:"Tidak Ada Acara"}).value_counts().reset_index()
            fig = px.pie(e_cnt, names="school_event", values="count",
                         color_discrete_sequence=[GOLD, TEAL],
                         title="Hari dengan Acara Sekolah", hole=0.45)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)
            event_days = df_f["school_event"].sum()
            event_pct  = event_days / len(df_f) * 100
            avg_rev_event    = df_f[df_f["school_event"]==1]["total_revenue_idr"].mean() if event_days > 0 else 0
            avg_rev_noevent  = df_f[df_f["school_event"]==0]["total_revenue_idr"].mean()
            insight(
                f"Terdapat <strong>{int(event_days)} hari ({event_pct:.1f}%)</strong> dengan acara sekolah. "
                f"{'Rata-rata pendapatan pada hari acara (' + fmt_idr(avg_rev_event) + ') vs hari biasa (' + fmt_idr(avg_rev_noevent) + ') — lihat Tab 2 untuk analisis lengkapnya.' if event_days > 0 else 'Tidak ada hari acara dalam filter ini.'}",
                "ok" if avg_rev_event > avg_rev_noevent else "blue"
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-head">Grafik Pendapatan Harian (90 Hari)</div>', unsafe_allow_html=True)
    df_sorted = df_f.sort_values("date")
    top5      = df_sorted.nlargest(5, "total_revenue_idr")
    bottom5   = df_sorted.nsmallest(5, "total_revenue_idr")
    events    = df_sorted[df_sorted["school_event"]==1] if "school_event" in df_sorted.columns else pd.DataFrame()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["date"], y=df_sorted["total_revenue_idr"],
        mode="lines", name="Pendapatan Harian",
        line=dict(color=BLUE, width=1.8),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=top5["date"], y=top5["total_revenue_idr"],
        mode="markers+text", name="Top 5 ⭐",
        marker=dict(color=GREEN, size=10, symbol="star"),
        text=top5["date"].dt.strftime("%d/%m"), textposition="top center",
        textfont=dict(size=9)
    ))
    fig.add_trace(go.Scatter(
        x=bottom5["date"], y=bottom5["total_revenue_idr"],
        mode="markers+text", name="Bottom 5 ▼",
        marker=dict(color=CORAL, size=10, symbol="triangle-down"),
        text=bottom5["date"].dt.strftime("%d/%m"), textposition="bottom center",
        textfont=dict(size=9)
    ))
    if not events.empty:
        fig.add_trace(go.Scatter(
            x=events["date"], y=events["total_revenue_idr"],
            mode="markers", name="Acara Sekolah ◆",
            marker=dict(color=GOLD, size=8, symbol="diamond", line=dict(width=1, color="white"))
        ))
    fig.update_xaxes(title="Tanggal")
    fig.update_yaxes(title="Pendapatan (IDR)")
    st.plotly_chart(plotly_defaults(fig, 380), use_container_width=True)

    top5_dates  = ", ".join(top5["date"].dt.strftime("%d %b").tolist())
    bot5_dates  = ", ".join(bottom5["date"].dt.strftime("%d %b").tolist())
    top5_event  = top5["school_event"].sum() if "school_event" in top5.columns else 0
    insight(
        f"Lima hari dengan pendapatan tertinggi jatuh pada: <strong>{top5_dates}</strong>. "
        f"{'Dari 5 hari terbaik ini, ' + str(int(top5_event)) + ' di antaranya adalah hari acara sekolah — mengonfirmasi bahwa acara sekolah menjadi pendorong utama lonjakan pendapatan.' if top5_event > 0 else ''} "
        f"Sebaliknya, 5 hari terendah ({bot5_dates}) perlu dievaluasi — kemungkinan bersamaan dengan hari hujan deras atau awal minggu dengan kehadiran rendah.",
        "blue"
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Rata-rata Pendapatan per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns:
            day_avg = df_f.groupby("day_of_week")["total_revenue_idr"].mean().reindex(DAY_ORDER).reset_index()
            fig = px.bar(day_avg, x="day_of_week", y="total_revenue_idr",
                         color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                         text=day_avg["total_revenue_idr"].apply(fmt_idr),
                         title="Rata-rata Pendapatan per Hari")
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Rata-rata Pendapatan (IDR)")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

            best_day  = day_avg.loc[day_avg["total_revenue_idr"].idxmax(), "day_of_week"]
            worst_day = day_avg.loc[day_avg["total_revenue_idr"].idxmin(), "day_of_week"]
            best_d_val  = day_avg["total_revenue_idr"].max()
            worst_d_val = day_avg["total_revenue_idr"].min()
            gap_d = (best_d_val - worst_d_val) / worst_d_val * 100
            insight(
                f"<strong>{best_day}</strong> adalah hari dengan rata-rata pendapatan tertinggi ({fmt_idr(best_d_val)}), "
                f"sedangkan <strong>{worst_day}</strong> terendah ({fmt_idr(worst_d_val)}). "
                f"Selisih antar hari mencapai <strong>{gap_d:.1f}%</strong>. "
                f"Kantin sebaiknya menyiapkan stok lebih banyak dan personel tambahan pada hari {best_day}.",
                "ok"
            )

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

            avg_e  = df_f[df_f["school_event"]==1]["total_revenue_idr"].mean()
            avg_ne = df_f[df_f["school_event"]==0]["total_revenue_idr"].mean()
            uplift = (avg_e - avg_ne) / avg_ne * 100 if avg_ne > 0 else 0
            kind   = "ok" if uplift > 0 else "warn"
            insight(
                f"Hari dengan acara sekolah menghasilkan rata-rata <strong>{fmt_idr(avg_e)}</strong>, "
                f"{'lebih tinggi' if uplift > 0 else 'lebih rendah'} <strong>{abs(uplift):.1f}%</strong> "
                f"dibanding hari biasa ({fmt_idr(avg_ne)}). "
                f"{'Ini menunjukkan acara sekolah secara konsisten mendorong lebih banyak transaksi — jadikan sebagai momen persiapan ekstra.' if uplift > 0 else 'Perlu ditelusuri mengapa acara sekolah tidak meningkatkan pendapatan.'}",
                kind
            )

    st.markdown('<div class="section-head">Pendapatan Mingguan</div>', unsafe_allow_html=True)
    weekly   = df_f.groupby("week")["total_revenue_idr"].sum().reset_index()
    fig = px.bar(weekly, x="week", y="total_revenue_idr",
                 color="total_revenue_idr", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                 title="Total Pendapatan per Minggu")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="Minggu ke-")
    fig.update_yaxes(title="Total Pendapatan (IDR)")
    best_wk  = weekly.loc[weekly["total_revenue_idr"].idxmax(), "week"]
    worst_wk = weekly.loc[weekly["total_revenue_idr"].idxmin(), "week"]
    best_wv  = weekly["total_revenue_idr"].max()
    worst_wv = weekly["total_revenue_idr"].min()
    st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)
    insight(
        f"Minggu ke-<strong>{best_wk}</strong> adalah minggu paling produktif ({fmt_idr(best_wv)}), "
        f"sementara minggu ke-<strong>{worst_wk}</strong> paling rendah ({fmt_idr(worst_wv)}). "
        f"Perlu dicek: apakah minggu terendah bersamaan dengan banyak hari libur, ujian, atau cuaca buruk? "
        f"Data ini bisa digunakan untuk merencanankan pembelian bahan baku secara mingguan.",
        "blue"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    valid_menus = [c for c in menu_cols if c in df_f.columns]
    menu_sum    = {c: df_f[c].sum() for c in valid_menus}
    menu_rev    = {c: df_f[c].sum() * MENU_PRICE[c] for c in valid_menus}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Total Terjual per Menu</div>', unsafe_allow_html=True)
        df_menu = pd.DataFrame({"menu": [MENU_LABEL[c] for c in valid_menus],
                                "terjual": [menu_sum[c] for c in valid_menus],
                                "col": valid_menus}).sort_values("terjual", ascending=True)
        fig = px.bar(df_menu, x="terjual", y="menu", orientation="h",
                     color="terjual", color_continuous_scale=["#BFDBFE","#1B3A6B"],
                     text="terjual", title="Total Porsi Terjual")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(title="")
        fig.update_xaxes(title="Jumlah Porsi")
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

        sorted_menus = sorted(menu_sum, key=menu_sum.get, reverse=True)
        top_m  = MENU_LABEL[sorted_menus[0]]
        top_v  = menu_sum[sorted_menus[0]]
        last_m = MENU_LABEL[sorted_menus[-1]]
        last_v = menu_sum[sorted_menus[-1]]
        ratio  = top_v / last_v if last_v > 0 else 0
        insight(
            f"Menu paling laris adalah <strong>{top_m}</strong> dengan total <strong>{top_v:,} porsi</strong>. "
            f"Perbandingan dengan menu paling sedikit terjual (<strong>{last_m}</strong>, {last_v:,} porsi) "
            f"mencapai <strong>{ratio:.1f}x</strong>. "
            f"Kantin perlu memastikan stok {top_m} selalu tersedia, terutama di hari-hari ramai.",
            "blue"
        )

    with c2:
        st.markdown('<div class="section-head">Estimasi Kontribusi Pendapatan per Menu</div>', unsafe_allow_html=True)
        df_rev_chart = pd.DataFrame({"menu": [MENU_LABEL[c] for c in valid_menus],
                                     "rev":  [menu_rev[c] for c in valid_menus]})
        fig = px.pie(df_rev_chart, names="menu", values="rev",
                     color_discrete_sequence=MENU_COLORS,
                     title="Proporsi Pendapatan per Menu", hole=0.4)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

        top_rev_col  = max(menu_rev, key=menu_rev.get)
        top_rev_name = MENU_LABEL[top_rev_col]
        top_rev_pct  = menu_rev[top_rev_col] / sum(menu_rev.values()) * 100
        is_same = top_rev_col == sorted_menus[0]
        insight(
            f"Kontributor pendapatan terbesar adalah <strong>{top_rev_name}</strong> ({top_rev_pct:.1f}% dari total). "
            f"{'Menu terlaris dari segi volume sekaligus terbesar kontribusi pendapatannya — posisi strategis yang harus dipertahankan.' if is_same else f'Menariknya, menu terlaris dari segi volume ({MENU_LABEL[sorted_menus[0]]}) berbeda dengan kontributor pendapatan terbesar ({top_rev_name}) — harga per unit yang lebih tinggi membuat perbedaan signifikan.'}",
            "ok"
        )

    st.markdown('<div class="section-head">Tren Penjualan Bulanan per Menu</div>', unsafe_allow_html=True)
    df_trend = df_f.groupby("month_name")[valid_menus].sum().reset_index()
    df_trend_melt = df_trend.melt(id_vars="month_name", var_name="menu", value_name="terjual")
    df_trend_melt["menu"] = df_trend_melt["menu"].map(MENU_LABEL)
    df_trend_melt["month_name"] = pd.Categorical(df_trend_melt["month_name"], categories=MONTH_ORDER, ordered=True)
    df_trend_melt = df_trend_melt.sort_values("month_name")
    fig = px.line(df_trend_melt, x="month_name", y="terjual", color="menu",
                  markers=True, color_discrete_sequence=MENU_COLORS,
                  title="Tren Penjualan Bulanan per Menu")
    fig.update_xaxes(title="Bulan")
    fig.update_yaxes(title="Jumlah Terjual")
    st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

    # Identify trend per menu
    if len(df_trend) >= 2:
        trends = {}
        for c in valid_menus:
            vals = df_trend[c].values
            if len(vals) >= 2:
                slope = np.polyfit(range(len(vals)), vals, 1)[0]
                cv    = vals.std() / vals.mean() * 100 if vals.mean() > 0 else 0
                trends[c] = (slope, cv)
        if trends:
            most_stable   = MENU_LABEL[min(trends, key=lambda k: trends[k][1])]
            most_increase = MENU_LABEL[max(trends, key=lambda k: trends[k][0])]
            most_decrease = MENU_LABEL[min(trends, key=lambda k: trends[k][0])]
            insight(
                f"Menu paling <strong>stabil</strong> sepanjang periode: <strong>{most_stable}</strong> (variasi antar bulan paling kecil). "
                f"Menu dengan tren <strong>meningkat</strong>: <strong>{most_increase}</strong>. "
                f"Menu dengan tren <strong>menurun</strong>: <strong>{most_decrease}</strong> — perlu evaluasi apakah ada masalah ketersediaan atau preferensi pelanggan yang berubah.",
                "blue"
            )

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

            if corr > 0.6:
                corr_desc = "korelasi positif kuat"
                corr_msg  = f"Semakin banyak Ayam Geprek terjual, semakin sering terjadi kehabisan stok. Ini mengindikasikan bahwa stok Ayam Geprek sering tidak mencukupi di hari-hari permintaan tinggi."
                kind = "warn"
            elif corr > 0.3:
                corr_desc = "korelasi positif moderat"
                corr_msg  = "Ada kecenderungan bahwa hari dengan penjualan Ayam Geprek tinggi lebih rawan kehabisan stok, meski tidak selalu."
                kind = "blue"
            elif corr < -0.3:
                corr_desc = "korelasi negatif"
                corr_msg  = "Semakin banyak Ayam Geprek terjual, justru lebih sedikit stock runout — kemungkinan stok sudah dipersiapkan lebih baik di hari ramai."
                kind = "ok"
            else:
                corr_desc = "korelasi lemah/tidak signifikan"
                corr_msg  = "Penjualan Ayam Geprek tidak berkorelasi kuat dengan kejadian kehabisan stok — stock runout lebih dipengaruhi faktor lain."
                kind = "blue"
            insight(
                f"Nilai korelasi r = <strong>{corr:.2f}</strong> menunjukkan <strong>{corr_desc}</strong>. "
                f"{corr_msg}",
                kind
            )

    with c2:
        st.markdown('<div class="section-head">Rata-rata Penjualan: Acara vs Non-Acara</div>', unsafe_allow_html=True)
        if "school_event" in df_f.columns:
            ev_menu = df_f.groupby("school_event")[valid_menus].mean().T.reset_index()
            ev_menu.columns = ["menu"] + [f"group_{c}" for c in ev_menu.columns[1:]]
            ev_menu["menu"] = ev_menu["menu"].map(MENU_LABEL)
            cols_grp = ev_menu.columns[1:]
            fig = go.Figure()
            colors_pair = [BLUE, GOLD]
            labels = ["Tidak Ada Acara", "Ada Acara"]
            for i, (col, lbl, clr) in enumerate(zip(cols_grp, labels, colors_pair)):
                fig.add_bar(name=lbl, x=ev_menu["menu"], y=ev_menu[col], marker_color=clr)
            fig.update_layout(barmode="group", title="Rata-rata Penjualan Menu: Acara vs Non-Acara")
            fig.update_xaxes(title="Menu")
            fig.update_yaxes(title="Rata-rata Porsi/Hari")
            st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

            # Find menus that spike most on event days
            if len(cols_grp) == 2:
                ev_menu["diff"] = ev_menu[cols_grp[1]] - ev_menu[cols_grp[0]]
                spike_menu = ev_menu.loc[ev_menu["diff"].idxmax(), "menu"]
                spike_val  = ev_menu["diff"].max()
                insight(
                    f"Pada hari acara sekolah, penjualan <strong>{spike_menu}</strong> mengalami peningkatan terbesar "
                    f"(+{spike_val:.1f} porsi/hari). Kantin sebaiknya memprioritaskan persiapan menu ini di hari-hari acara. "
                    f"Secara umum, hari acara mendorong kenaikan di hampir semua menu, bukan hanya satu kategori.",
                    "ok"
                )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Box Plot Waktu Antrian per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns:
            df_day = df_f[df_f["day_of_week"].isin(DAY_ORDER)]
            fig = px.box(df_day, x="day_of_week", y="avg_queue_time_minutes",
                         category_orders={"day_of_week": DAY_ORDER},
                         color="day_of_week", color_discrete_sequence=MENU_COLORS,
                         title="Distribusi Waktu Antrian per Hari", points="all")
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Waktu Antrian (menit)")
            st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

            day_q = df_day.groupby("day_of_week")["avg_queue_time_minutes"].agg(["median","std"]).reindex(DAY_ORDER)
            longest_q_day = day_q["median"].idxmax()
            most_var_day  = day_q["std"].idxmax()
            insight(
                f"Median waktu antrian terlama terjadi pada hari <strong>{longest_q_day}</strong> "
                f"({day_q.loc[longest_q_day,'median']:.1f} menit). "
                f"Variasi antrian terbesar ada di hari <strong>{most_var_day}</strong> — "
                f"artinya di hari ini antrean sangat tidak konsisten, ada kalanya cepat dan ada kalanya sangat panjang. "
                f"Tambahan kasir atau sistem pre-order bisa membantu menstabilkan kondisi ini.",
                "warn"
            )

    with c2:
        st.markdown('<div class="section-head">Pelanggan vs Waktu Antrian</div>', unsafe_allow_html=True)
        fig = px.scatter(df_f, x="total_customers", y="avg_queue_time_minutes",
                         trendline="ols", color_discrete_sequence=[TEAL],
                         title="Total Pelanggan vs Rata-rata Waktu Antrian")
        fig.add_hline(y=10, line_dash="dash", line_color=CORAL,
                      annotation_text="Batas 10 menit", annotation_position="top right")
        fig.update_xaxes(title="Total Pelanggan")
        fig.update_yaxes(title="Waktu Antrian (menit)")
        st.plotly_chart(plotly_defaults(fig, 340), use_container_width=True)

        corr_cq = df_f["total_customers"].corr(df_f["avg_queue_time_minutes"])
        # Estimate threshold: find customers where queue ~ 10 min from regression
        try:
            from numpy.polynomial.polynomial import polyfit as npfit
            coef = np.polyfit(df_f["total_customers"], df_f["avg_queue_time_minutes"], 1)
            thresh_cust = (10 - coef[1]) / coef[0] if coef[0] != 0 else None
        except Exception:
            thresh_cust = None
        thresh_txt = f"Antrian mulai melewati 10 menit saat pelanggan mencapai sekitar <strong>{thresh_cust:.0f} orang</strong>. " if thresh_cust and thresh_cust > 0 else ""
        insight(
            f"Korelasi antara jumlah pelanggan dan waktu antrian: r = <strong>{corr_cq:.2f}</strong> "
            f"({'positif — semakin ramai, semakin panjang antrian' if corr_cq > 0.3 else 'lemah — waktu antrian tidak semata-mata tergantung jumlah pelanggan'}). "
            f"{thresh_txt}"
            f"Kantin perlu menyiapkan protokol khusus saat kehadiran melebihi angka tersebut.",
            "warn" if corr_cq > 0.4 else "blue"
        )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Stock Runout per Hari</div>', unsafe_allow_html=True)
        if "day_of_week" in df_f.columns and "stock_runout_events" in df_f.columns:
            runout_day = df_f.groupby("day_of_week")["stock_runout_events"].sum().reindex(DAY_ORDER).reset_index()
            fig = px.bar(runout_day, x="day_of_week", y="stock_runout_events",
                         color="stock_runout_events", color_continuous_scale=["#FEF9C3","#DC2626"],
                         text="stock_runout_events", title="Total Stock Runout per Hari")
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title="Hari")
            fig.update_yaxes(title="Jumlah Kejadian")
            st.plotly_chart(plotly_defaults(fig, 300), use_container_width=True)

            worst_runout_day = runout_day.loc[runout_day["stock_runout_events"].idxmax(), "day_of_week"]
            worst_runout_val = runout_day["stock_runout_events"].max()
            insight(
                f"Hari <strong>{worst_runout_day}</strong> paling sering mengalami kehabisan stok "
                f"(total <strong>{int(worst_runout_val)} kejadian</strong> selama periode ini). "
                f"Ini adalah sinyal jelas bahwa pembelian bahan baku harus dinaikkan khusus untuk hari tersebut. "
                f"Evaluasi juga apakah hari ini bersamaan dengan hari-hari ramai atau acara sekolah.",
                "warn"
            )

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

            max_wx = runout_wx.loc[runout_wx["stock_runout_events"].idxmax(), "weather"]
            min_wx = runout_wx.loc[runout_wx["stock_runout_events"].idxmin(), "weather"]
            max_v  = runout_wx["stock_runout_events"].max()
            min_v  = runout_wx["stock_runout_events"].min()
            insight(
                f"Cuaca <strong>{max_wx}</strong> memiliki rata-rata stock runout tertinggi ({max_v:.2f}/hari), "
                f"dibanding cuaca <strong>{min_wx}</strong> ({min_v:.2f}/hari). "
                f"{'Cuaca hujan menurunkan kehadiran tapi tidak selalu menurunkan stock runout — kemungkinan karena stok juga dikurangi di hari hujan.' if 'Hujan' in max_wx else 'Cuaca cerah membawa lebih banyak pelanggan sehingga stok lebih cepat habis — perlu persiapan ekstra di hari cerah.'}",
                "blue"
            )

    st.markdown('<div class="section-head">Estimasi Pendapatan Hilang akibat Stock Runout</div>', unsafe_allow_html=True)
    avg_txn = (df_f["total_revenue_idr"].mean() / df_f["total_transactions"].mean()
               if "total_transactions" in df_f.columns else 12000)
    lost_per_event = 15 * avg_txn
    df_f["lost_revenue"] = df_f["stock_runout_events"] * lost_per_event
    total_lost = df_f["lost_revenue"].sum()

    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Rata-rata Nilai Transaksi", fmt_idr(avg_txn))
    kc2.metric("Lost Revenue per Kejadian", fmt_idr(lost_per_event),
               help="Asumsi: 15 penjualan hilang × nilai rata-rata")
    kc3.metric("Total Estimasi Lost Revenue", fmt_idr(total_lost))

    fig = px.area(df_f.sort_values("date"), x="date", y="lost_revenue",
                  color_discrete_sequence=[CORAL],
                  title="Estimasi Pendapatan Hilang per Hari (Stock Runout)")
    fig.update_xaxes(title="Tanggal")
    fig.update_yaxes(title="Pendapatan Hilang (IDR)")
    st.plotly_chart(plotly_defaults(fig, 280), use_container_width=True)

    lost_pct = total_lost / total_rev * 100 if total_rev > 0 else 0
    insight(
        f"Total estimasi pendapatan yang hilang akibat kehabisan stok selama periode ini mencapai "
        f"<strong>{fmt_idr(total_lost)}</strong> — setara dengan <strong>{lost_pct:.1f}%</strong> dari total pendapatan aktual. "
        f"{'Angka ini cukup signifikan.' if lost_pct > 5 else 'Angka ini relatif kecil.'} "
        f"Dengan perencanaan stok yang lebih baik menggunakan data ini, sebagian besar kerugian tersebut seharusnya bisa dicegah.",
        "warn" if lost_pct > 5 else "ok"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    if "weather" not in df_f.columns:
        st.info("Kolom 'weather' tidak ditemukan di dataset.")
    else:
        st.markdown('<div class="section-head">Perbandingan Metrik Utama per Cuaca</div>', unsafe_allow_html=True)
        wx_agg = df_f.groupby("weather").agg(
            Hari=("date","count"),
            Avg_Rev=("total_revenue_idr","mean"),
            Avg_Cust=("total_customers","mean"),
            Avg_Queue=("avg_queue_time_minutes","mean"),
            Avg_Runout=("stock_runout_events","mean"),
        ).reset_index()
        wx_display = wx_agg.copy()
        wx_display.columns = ["Cuaca","Hari","Avg Pendapatan","Avg Pelanggan","Avg Antrian (mnt)","Avg Runout"]
        wx_display["Avg Pendapatan"] = wx_display["Avg Pendapatan"].apply(fmt_idr)
        wx_display["Avg Pelanggan"]  = wx_display["Avg Pelanggan"].round(1)
        wx_display["Avg Antrian (mnt)"] = wx_display["Avg Antrian (mnt)"].round(2)
        wx_display["Avg Runout"]     = wx_display["Avg Runout"].round(2)
        st.dataframe(wx_display, use_container_width=True, hide_index=True)

        best_wx  = wx_agg.loc[wx_agg["Avg_Rev"].idxmax(), "weather"]
        worst_wx = wx_agg.loc[wx_agg["Avg_Rev"].idxmin(), "weather"]
        best_wv  = wx_agg["Avg_Rev"].max()
        worst_wv = wx_agg["Avg_Rev"].min()
        diff_wx  = (best_wv - worst_wv) / worst_wv * 100 if worst_wv > 0 else 0
        insight(
            f"Cuaca <strong>{best_wx}</strong> menghasilkan rata-rata pendapatan tertinggi ({fmt_idr(best_wv)}), "
            f"sedangkan <strong>{worst_wx}</strong> paling rendah ({fmt_idr(worst_wv)}). "
            f"Selisihnya <strong>{diff_wx:.1f}%</strong> — cuaca menjadi faktor eksternal yang perlu diantisipasi dalam perencanaan stok harian.",
            "blue"
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-head">Pendapatan per Cuaca & Hari</div>', unsafe_allow_html=True)
            if "day_of_week" in df_f.columns:
                wx_day = (df_f[df_f["day_of_week"].isin(DAY_ORDER)]
                          .groupby(["day_of_week","weather"])["total_revenue_idr"].mean().reset_index())
                fig = px.bar(wx_day, x="day_of_week", y="total_revenue_idr",
                             color="weather", barmode="group",
                             category_orders={"day_of_week": DAY_ORDER},
                             color_discrete_sequence=[SKY, BLUE, NAVY],
                             title="Rata-rata Pendapatan per Hari × Cuaca")
                fig.update_xaxes(title="Hari")
                fig.update_yaxes(title="Rata-rata Pendapatan (IDR)")
                st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

                # Find day-weather combo with highest revenue
                best_combo = wx_day.loc[wx_day["total_revenue_idr"].idxmax()]
                insight(
                    f"Kombinasi terbaik adalah <strong>{best_combo['day_of_week']} + cuaca {best_combo['weather']}</strong> "
                    f"dengan rata-rata {fmt_idr(best_combo['total_revenue_idr'])}. "
                    f"Pada kondisi ini, kantin harus benar-benar siap — stok penuh dan personel lengkap.",
                    "ok"
                )

        with c2:
            st.markdown('<div class="section-head">Penjualan Minuman: Hujan vs Cerah</div>', unsafe_allow_html=True)
            if "drinks_sold" in df_f.columns:
                drinks_wx = df_f.groupby("weather")["drinks_sold"].mean().reset_index()
                fig = px.bar(drinks_wx, x="weather", y="drinks_sold",
                             color="weather", color_discrete_sequence=[SKY, BLUE, NAVY],
                             text=drinks_wx["drinks_sold"].round(1),
                             title="Rata-rata Minuman Terjual per Kondisi Cuaca")
                fig.update_traces(textposition="outside")
                fig.update_xaxes(title="Cuaca")
                fig.update_yaxes(title="Rata-rata Minuman Terjual/Hari")
                st.plotly_chart(plotly_defaults(fig, 320), use_container_width=True)

                if "Cerah" in drinks_wx["weather"].values and "Hujan" in drinks_wx["weather"].values:
                    cerah_val = drinks_wx[drinks_wx["weather"]=="Cerah"]["drinks_sold"].values[0]
                    hujan_val = drinks_wx[drinks_wx["weather"]=="Hujan"]["drinks_sold"].values[0]
                    higher = "Cerah" if cerah_val > hujan_val else "Hujan"
                    diff_d = abs(cerah_val - hujan_val)
                    insight(
                        f"Penjualan minuman lebih tinggi di hari <strong>{higher}</strong> "
                        f"(selisih {diff_d:.1f} gelas/hari dibanding kondisi lainnya). "
                        f"{'Cuaca panas mendorong konsumsi minuman lebih banyak — kantin bisa menyiapkan lebih banyak minuman di hari cerah.' if higher == 'Cerah' else 'Hari hujan justru mendorong konsumsi minuman hangat — pertimbangkan menambah varian minuman hangat.'}",
                        "blue"
                    )
                else:
                    insight("Bandingkan data cuaca Cerah dan Hujan untuk melihat pola penjualan minuman.", "blue")

        st.markdown('<div class="section-head">Scatter: Pelanggan vs Pendapatan per Cuaca</div>', unsafe_allow_html=True)
        fig = px.scatter(df_f, x="total_customers", y="total_revenue_idr",
                         color="weather", color_discrete_sequence=[SKY, BLUE, NAVY],
                         size="avg_queue_time_minutes",
                         hover_data=["date","day_of_week"],
                         title="Pelanggan vs Pendapatan (warna = cuaca · ukuran titik = waktu antrian)")
        fig.update_xaxes(title="Total Pelanggan")
        fig.update_yaxes(title="Total Pendapatan (IDR)")
        st.plotly_chart(plotly_defaults(fig, 380), use_container_width=True)
        insight(
            f"Scatter ini menggabungkan tiga dimensi sekaligus: jumlah pelanggan, pendapatan, dan waktu antrian (ukuran titik). "
            f"Titik besar yang berada di kanan atas menunjukkan hari-hari dengan banyak pelanggan, pendapatan tinggi, sekaligus antrian panjang — "
            f"ini adalah hari yang paling kritis secara operasional dan perlu persiapan ekstra.",
            "blue"
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("📊 Kantin Ceria Nusantara Analytics · DigiBattle 2024 · Built for BINUS Business Analytics Case Study")
