import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="WISN Family Medicine Planner", page_icon="🩺", layout="wide")

DATA_PATH = Path(__file__).parent / "RF_F4_forecast_2569_2573_strata.csv.gz"
HEALTH_NEEDS = ["Acute", "Chronic", "Prevention"]
HEALTH_TH = {"Acute": "บริการเฉียบพลัน (Acute)", "Chronic": "บริการโรคเรื้อรัง (Chronic)", "Prevention": "บริการส่งเสริมสุขภาพและป้องกันโรค (Prevention)"}
HEALTH_SHORT = {"Acute": "เฉียบพลัน", "Chronic": "โรคเรื้อรัง", "Prevention": "ส่งเสริม/ป้องกัน"}
HEALTH_COLOR = {"Acute": "#E07A5F", "Chronic": "#3D5A80", "Prevention": "#2A9D8F"}
HOS_TH = {1: "หน่วยบริการปฐมภูมิ", 2: "โรงพยาบาลชุมชน", 3: "โรงพยาบาลทั่วไป", 4: "โรงพยาบาลศูนย์", 5: "โรงพยาบาลมหาวิทยาลัย", 6: "โรงพยาบาลและสถานพยาบาลอื่น ๆ"}
DEFAULTS = {"std_Acute": 6.55, "std_Chronic": 6.55, "std_Prevention": 6.55, "awt": 1680.0, "unmet": 0.0}
FONT = "IBM Plex Sans Thai"

# ---------------------------------------------------------------- styles
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&display=swap');

:root {{
  --ink: #0F2A3D; --muted: #5B6B79; --line: #E3E9EE;
  --brand: #0E6E6E; --brand-2: #14918F; --soft: #F3F7F9;
}}
html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
.stApp [data-baseweb="select"] div, .stApp [data-baseweb="tab"], .stApp table, .stApp th, .stApp td,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"] {{
  font-family: '{FONT}', 'Sarabun', sans-serif !important;
}}
[data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}

.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1320px; }}

/* Hero */
.hero {{
  background: linear-gradient(120deg, #0B4F5C 0%, #0E6E6E 55%, #1A8F7E 100%);
  border-radius: 18px; padding: 26px 30px 22px; color: #fff; margin-bottom: 18px;
  box-shadow: 0 10px 30px -18px rgba(11,79,92,.7); position: relative; overflow: hidden;
}}
.hero::after {{
  content: ""; position: absolute; right: -60px; top: -60px; width: 240px; height: 240px;
  border-radius: 50%; background: rgba(255,255,255,.07);
}}
.hero .eyebrow {{ font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; opacity: .8; margin: 0 0 6px; }}
.hero h1 {{ color: #fff !important; font-size: 1.65rem; font-weight: 600; line-height: 1.35; margin: 0 0 4px; padding: 0; }}
.hero .sub {{ opacity: .85; font-size: .95rem; margin: 0 0 14px; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.chip {{
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.22);
  border-radius: 999px; padding: 4px 12px; font-size: .82rem; white-space: nowrap;
}}
.chip b {{ font-weight: 600; }}

/* KPI cards */
.kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin-bottom: 14px; }}
@media (max-width: 900px) {{ .kpis {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
.kpi {{
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px;
  box-shadow: 0 1px 2px rgba(15,42,61,.04);
}}
.kpi .lbl {{ color: var(--muted); font-size: .84rem; margin-bottom: 6px; }}
.kpi .val {{ color: var(--ink); font-size: 1.6rem; font-weight: 600; line-height: 1.2; }}
.kpi .unit {{ font-size: .85rem; font-weight: 400; color: var(--muted); margin-left: 4px; }}
.kpi .note {{ color: var(--muted); font-size: .76rem; margin-top: 6px; }}
.kpi.accent {{ background: linear-gradient(135deg, #0E6E6E, #14918F); border: none; }}
.kpi.accent .lbl, .kpi.accent .unit, .kpi.accent .note {{ color: rgba(255,255,255,.82); }}
.kpi.accent .val {{ color: #fff; font-size: 1.9rem; }}

/* Formula strip */
.formula {{
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
  background: var(--soft); border: 1px dashed #C9D6DE; border-radius: 12px;
  padding: 10px 14px; font-size: .86rem; color: var(--ink); margin-bottom: 8px;
}}
.formula .t {{ background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 3px 9px; }}
.formula .op {{ color: var(--muted); font-weight: 600; }}
.formula .res {{ background: var(--brand); color: #fff; border-radius: 8px; padding: 3px 10px; font-weight: 600; }}
.disclaimer {{ color: var(--muted); font-size: .8rem; margin: 2px 0 18px; }}

/* Section title */
.sec {{ font-size: 1.02rem; font-weight: 600; color: var(--ink); margin: 6px 0 2px; }}
.sec-sub {{ font-size: .82rem; color: var(--muted); margin-bottom: 8px; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid var(--line); }}
.stTabs [data-baseweb="tab"] {{ padding: 8px 14px; border-radius: 10px 10px 0 0; }}
.stTabs [aria-selected="true"] {{ background: var(--soft); }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: #F6F9FA; border-right: 1px solid var(--line); }}
.side-h {{
  display: flex; align-items: center; gap: 8px; font-weight: 600; color: var(--ink);
  font-size: .95rem; margin: 10px 0 6px;
}}
.side-h .n {{
  width: 22px; height: 22px; border-radius: 50%; background: var(--brand); color: #fff;
  display: inline-flex; align-items: center; justify-content: center; font-size: .75rem;
}}
.brand {{ display: flex; align-items: center; gap: 10px; margin: -6px 0 6px; }}
.brand .logo {{
  width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg,#0E6E6E,#1A8F7E);
  color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}}
.brand .name {{ font-weight: 600; color: var(--ink); line-height: 1.2; }}
.brand .tag {{ font-size: .75rem; color: var(--muted); }}

/* Expander + download */
[data-testid="stExpander"] details {{ border-radius: 12px; border-color: var(--line); background: #fff; }}
.foot {{ text-align: center; color: var(--muted); font-size: .78rem; margin-top: 26px; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, compression="gzip")
    expected = {"health_need", "province", "hos_type", "sex", "age_group", "cci", "year", "pred_rate", "Population", "จำนวนการใช้บริการ"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"ไม่พบคอลัมน์ที่จำเป็น: {', '.join(missing)}")
    df["hos_type"] = pd.to_numeric(df["hos_type"], errors="coerce").astype("Int64")
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
    df["จำนวนการใช้บริการ"] = pd.to_numeric(df["จำนวนการใช้บริการ"], errors="coerce").fillna(0)
    df["pred_rate"] = pd.to_numeric(df["pred_rate"], errors="coerce").fillna(0)
    return df


def age_key(a):
    try:
        return int(str(a).split("-")[0].replace("+", ""))
    except ValueError:
        return 999


try:
    data = load_data()
except Exception as e:
    st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
    st.info("วางไฟล์ RF_F4_forecast_2569_2573_strata.csv.gz ไว้ในโฟลเดอร์เดียวกับ app.py")
    st.stop()

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reset_params():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("""<div class="brand"><div class="logo">🩺</div>
      <div><div class="name">WISN Planner</div><div class="tag">Family Medicine workforce</div></div></div>""",
                unsafe_allow_html=True)

    st.markdown('<div class="side-h"><span class="n">1</span>ขอบเขตการวิเคราะห์</div>', unsafe_allow_html=True)
    years = sorted(data.year.unique().tolist())
    year = st.segmented_control("ปี พ.ศ.", years, default=years[0], selection_mode="single")
    if year is None:
        year = years[0]
    provinces = ["ทุกจังหวัด"] + sorted(data.province.dropna().unique().tolist())
    province = st.selectbox("จังหวัด", provinces)
    hos_options = ["ทุกประเภท"] + sorted(data.hos_type.dropna().astype(int).unique().tolist())
    hos_pick = st.selectbox("ประเภทหน่วยบริการ", hos_options,
                            format_func=lambda x: x if x == "ทุกประเภท" else f"{x} — {HOS_TH.get(x, '')}")
    needs = st.pills("Health Need", HEALTH_NEEDS, default=HEALTH_NEEDS, selection_mode="multi",
                     format_func=lambda n: f"{n} · {HEALTH_SHORT[n]}")

    st.markdown('<div class="side-h"><span class="n">2</span>พารามิเตอร์ WISN</div>', unsafe_allow_html=True)
    st.caption("ค่าเริ่มต้นเป็นสมมติฐานตัวอย่างจากกรอบการศึกษานี้ สามารถปรับเพื่อวิเคราะห์สถานการณ์ได้")
    standard = {}
    with st.expander("เวลามาตรฐาน (นาที/ครั้ง)", expanded=True):
        for n in HEALTH_NEEDS:
            standard[n] = st.number_input(f"{n} · {HEALTH_SHORT[n]}", min_value=0.0, max_value=240.0,
                                          step=0.25, key=f"std_{n}")
    awt = st.number_input("AWT (ชั่วโมง/คน/ปี)", min_value=1.0, max_value=3000.0, step=24.0, key="awt",
                          help="Available Working Time: เวลาทำงานที่ใช้ได้จริงต่อแพทย์ 1 คนต่อปี")
    unmet_pct = st.slider("ปรับเพิ่ม Unmet Need (%)", min_value=0.0, max_value=300.0, step=0.5, key="unmet",
                          help="ตั้งต้น 0% เพื่อแสดงค่าตามจำนวนบริการพยากรณ์ หากมีหลักฐานรองรับจึงค่อยปรับ")
    st.caption("การปรับ Unmet Need เป็น scenario ไม่ใช่ค่าที่ระบบยืนยันว่าเหมาะกับทุกกลุ่มบริการ")
    st.button("↺ คืนค่าเริ่มต้น", on_click=reset_params, use_container_width=True)


# ---------------------------------------------------------------- calc
def apply_filters(frame):
    out = frame[frame.health_need.isin(needs)]
    if province != "ทุกจังหวัด":
        out = out[out.province == province]
    if hos_pick != "ทุกประเภท":
        out = out[out.hos_type == hos_pick]
    return out


def add_calc(frame):
    frame = frame.copy()
    frame["ปริมาณบริการฐาน (ครั้ง)"] = frame["จำนวนการใช้บริการ"]
    frame["ปริมาณบริการหลังปรับ (ครั้ง)"] = frame["จำนวนการใช้บริการ"] * (1 + unmet_pct / 100)
    frame["เวลามาตรฐาน (นาที/ครั้ง)"] = frame.health_need.map(standard)
    frame["ภาระงาน (ชั่วโมง)"] = frame["ปริมาณบริการหลังปรับ (ครั้ง)"] * frame["เวลามาตรฐาน (นาที/ครั้ง)"] / 60
    frame["ความต้องการกำลังคน (FTE)"] = frame["ภาระงาน (ชั่วโมง)"] / awt
    return frame


scoped = apply_filters(data)
df = scoped[scoped.year == year]

if not needs:
    st.warning("กรุณาเลือก Health Need อย่างน้อย 1 กลุ่มที่แถบด้านซ้าย")
    st.stop()
if df.empty:
    st.warning("ไม่มีข้อมูลตรงกับตัวเลือกนี้")
    st.stop()

df = add_calc(df)
df["Health Need"] = df.health_need.map(HEALTH_TH)
df["ประเภทหน่วยบริการ"] = df.hos_type.astype(int).map(HOS_TH)

volume = df["ปริมาณบริการหลังปรับ (ครั้ง)"].sum()
workhours = df["ภาระงาน (ชั่วโมง)"].sum()
fte = df["ความต้องการกำลังคน (FTE)"].sum()
basevol = df["ปริมาณบริการฐาน (ครั้ง)"].sum()
avg_std = workhours * 60 / volume if volume else 0

# ---------------------------------------------------------------- header
hos_label = "ทุกประเภทหน่วยบริการ" if hos_pick == "ทุกประเภท" else HOS_TH.get(hos_pick, str(hos_pick))
need_label = "ครบ 3 กลุ่ม" if len(needs) == 3 else ", ".join(HEALTH_SHORT[n] for n in needs)
st.markdown(f"""
<div class="hero">
  <p class="eyebrow">Forecast-based workload estimation · WISN-inspired</p>
  <h1>เครื่องมือประมาณความต้องการกำลังคนแพทย์เวชศาสตร์ครอบครัว</h1>
  <p class="sub">ประมาณภาระงานและ FTE จากจำนวนบริการพยากรณ์ ปี พ.ศ. {years[0]}–{years[-1]}</p>
  <div class="chips">
    <span class="chip">ปี <b>{year}</b></span>
    <span class="chip">จังหวัด <b>{province}</b></span>
    <span class="chip">หน่วยบริการ <b>{hos_label}</b></span>
    <span class="chip">Health Need <b>{need_label}</b></span>
    <span class="chip">Unmet Need <b>+{unmet_pct:g}%</b></span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpis">
  <div class="kpi"><div class="lbl">ปริมาณบริการพยากรณ์</div>
    <div class="val">{basevol:,.0f}<span class="unit">ครั้ง</span></div><div class="note">ฐานจากไฟล์ผลพยากรณ์</div></div>
  <div class="kpi"><div class="lbl">บริการหลังปรับ scenario</div>
    <div class="val">{volume:,.0f}<span class="unit">ครั้ง</span></div><div class="note">รวม Unmet Need +{unmet_pct:g}%</div></div>
  <div class="kpi"><div class="lbl">ภาระงาน</div>
    <div class="val">{workhours:,.0f}<span class="unit">ชั่วโมง</span></div><div class="note">เวลามาตรฐานเฉลี่ย {avg_std:,.2f} นาที/ครั้ง</div></div>
  <div class="kpi accent"><div class="lbl">ความต้องการกำลังคน</div>
    <div class="val">{fte:,.2f}<span class="unit">FTE</span></div><div class="note">AWT {awt:,.0f} ชั่วโมง/คน/ปี</div></div>
</div>
<div class="formula">
  <span class="t">{volume:,.0f} ครั้ง</span><span class="op">×</span>
  <span class="t">{avg_std:,.2f} นาที</span><span class="op">÷ 60 =</span>
  <span class="t">{workhours:,.0f} ชม.</span><span class="op">÷</span>
  <span class="t">AWT {awt:,.0f}</span><span class="op">=</span>
  <span class="res">{fte:,.2f} FTE</span>
</div>
<div class="disclaimer">ℹ️ FTE คำนวณจากบริการที่เลือก × เวลามาตรฐาน ÷ 60 ÷ AWT และปรับ Unmet Need ตามค่าที่ผู้ใช้ระบุ
ไม่ใช่จำนวนแพทย์ที่ขาดแคลนหรือจำนวนที่ควรบรรจุทันที</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- charts
def chart_cfg(c, height):
    return (c.properties(height=height)
            .configure(font=FONT)
            .configure_view(strokeWidth=0)
            .configure_axis(labelFontSize=12, titleFontSize=12, labelColor="#5B6B79", titleColor="#5B6B79",
                            gridColor="#EEF2F5", domainColor="#D5DEE5", tickColor="#D5DEE5")
            .configure_legend(labelFontSize=12, titleFontSize=12, orient="top"))


need_scale = alt.Scale(domain=[HEALTH_SHORT[n] for n in HEALTH_NEEDS],
                       range=[HEALTH_COLOR[n] for n in HEALTH_NEEDS])

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Health Need", "🏥 หน่วยบริการ", "📈 แนวโน้ม 5 ปี", "👥 กลุ่มอายุ / จังหวัด", "📄 รายละเอียด / ส่งออก"])

with tab1:
    summary = df.groupby("health_need", as_index=False).agg(
        service_base=("ปริมาณบริการฐาน (ครั้ง)", "sum"),
        service_adjusted=("ปริมาณบริการหลังปรับ (ครั้ง)", "sum"),
        workload_hours=("ภาระงาน (ชั่วโมง)", "sum"),
        FTE=("ความต้องการกำลังคน (FTE)", "sum"))
    summary["Health Need"] = summary.health_need.map(HEALTH_TH)
    summary["กลุ่ม"] = summary.health_need.map(HEALTH_SHORT)
    summary["สัดส่วน FTE"] = summary.FTE / summary.FTE.sum()

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown('<div class="sec">FTE แยกตาม Health Need</div><div class="sec-sub">สัดส่วนความต้องการกำลังคนในขอบเขตที่เลือก</div>', unsafe_allow_html=True)
        base = alt.Chart(summary).encode(
            y=alt.Y("กลุ่ม:N", sort="-x", title=None),
            x=alt.X("FTE:Q", title="FTE", scale=alt.Scale(domain=[0, float(summary.FTE.max()) * 1.35 or 1])),
            tooltip=[alt.Tooltip("Health Need:N"), alt.Tooltip("FTE:Q", format=",.2f"),
                     alt.Tooltip("สัดส่วน FTE:Q", format=".1%"), alt.Tooltip("workload_hours:Q", title="ภาระงาน (ชม.)", format=",.0f")])
        bars = base.mark_bar(cornerRadiusEnd=6, size=34).encode(color=alt.Color("กลุ่ม:N", scale=need_scale, legend=None))
        labels = base.mark_text(align="left", dx=6, fontSize=12, color="#0F2A3D").encode(
            text=alt.Text("label:N")).transform_calculate(label="format(datum.FTE, ',.2f') + '  (' + format(datum['สัดส่วน FTE'], '.0%') + ')'")
        st.altair_chart(chart_cfg(bars + labels, 70 * len(summary) + 30), use_container_width=True)
    with right:
        st.markdown('<div class="sec">ตารางสรุป</div><div class="sec-sub">บริการ ภาระงาน และ FTE</div>', unsafe_allow_html=True)
        st.dataframe(summary[["Health Need", "service_base", "service_adjusted", "workload_hours", "FTE", "สัดส่วน FTE"]].rename(columns={
            "service_base": "บริการฐาน (ครั้ง)", "service_adjusted": "บริการหลังปรับ (ครั้ง)", "workload_hours": "ภาระงาน (ชั่วโมง)"}).style.format({
            "บริการฐาน (ครั้ง)": "{:,.0f}", "บริการหลังปรับ (ครั้ง)": "{:,.0f}", "ภาระงาน (ชั่วโมง)": "{:,.1f}", "FTE": "{:,.3f}", "สัดส่วน FTE": "{:.1%}"}),
            use_container_width=True, hide_index=True)

with tab2:
    s2 = df.groupby("ประเภทหน่วยบริการ", as_index=False).agg(
        visits=("ปริมาณบริการฐาน (ครั้ง)", "sum"), workload=("ภาระงาน (ชั่วโมง)", "sum"), FTE=("ความต้องการกำลังคน (FTE)", "sum"))
    s2 = s2.sort_values("FTE", ascending=False)
    s2_need = df.assign(กลุ่ม=df.health_need.map(HEALTH_SHORT)).groupby(["ประเภทหน่วยบริการ", "กลุ่ม"], as_index=False)["ความต้องการกำลังคน (FTE)"].sum()

    st.markdown('<div class="sec">FTE แยกตามประเภทหน่วยบริการ</div><div class="sec-sub">แท่งซ้อนตาม Health Need · เรียงจากมากไปน้อย</div>', unsafe_allow_html=True)
    c2 = alt.Chart(s2_need).mark_bar(cornerRadiusEnd=4, size=26).encode(
        y=alt.Y("ประเภทหน่วยบริการ:N", sort=s2["ประเภทหน่วยบริการ"].tolist(), title=None, axis=alt.Axis(labelLimit=260)),
        x=alt.X("ความต้องการกำลังคน (FTE):Q", title="FTE", stack="zero"),
        color=alt.Color("กลุ่ม:N", scale=need_scale, title="Health Need"),
        tooltip=["ประเภทหน่วยบริการ:N", "กลุ่ม:N", alt.Tooltip("ความต้องการกำลังคน (FTE):Q", format=",.2f")])
    st.altair_chart(chart_cfg(c2, 48 * len(s2) + 40), use_container_width=True)
    st.dataframe(s2.rename(columns={"visits": "บริการฐาน (ครั้ง)", "workload": "ภาระงาน (ชั่วโมง)"}).style.format(
        {"บริการฐาน (ครั้ง)": "{:,.0f}", "ภาระงาน (ชั่วโมง)": "{:,.1f}", "FTE": "{:,.3f}"}),
        use_container_width=True, hide_index=True)

with tab3:
    trend = add_calc(scoped)
    trend["กลุ่ม"] = trend.health_need.map(HEALTH_SHORT)
    t_need = trend.groupby(["year", "กลุ่ม"], as_index=False)["ความต้องการกำลังคน (FTE)"].sum()
    t_tot = trend.groupby("year", as_index=False)["ความต้องการกำลังคน (FTE)"].sum()
    t_tot["selected"] = t_tot.year == year

    st.markdown(f'<div class="sec">แนวโน้มความต้องการกำลังคน พ.ศ. {years[0]}–{years[-1]}</div><div class="sec-sub">ใช้ตัวกรองและพารามิเตอร์ชุดเดียวกัน · แท่งเข้มคือปีที่เลือก</div>', unsafe_allow_html=True)
    tl, tr = st.columns([1, 1], gap="large")
    with tl:
        tb = alt.Chart(t_tot).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=46).encode(
            x=alt.X("year:O", title="ปี พ.ศ.", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("ความต้องการกำลังคน (FTE):Q", title="FTE รวม"),
            color=alt.condition("datum.selected", alt.value("#0E6E6E"), alt.value("#A9CFCB")),
            tooltip=[alt.Tooltip("year:O", title="ปี"), alt.Tooltip("ความต้องการกำลังคน (FTE):Q", title="FTE", format=",.2f")])
        tt = tb.mark_text(dy=-8, fontSize=12, color="#0F2A3D").encode(
            text=alt.Text("ความต้องการกำลังคน (FTE):Q", format=",.1f"), color=alt.value("#0F2A3D"))
        st.altair_chart(chart_cfg(tb + tt, 320), use_container_width=True)
    with tr:
        tln = alt.Chart(t_need).mark_line(point=alt.OverlayMarkDef(size=60, filled=True), strokeWidth=2.5).encode(
            x=alt.X("year:O", title="ปี พ.ศ.", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("ความต้องการกำลังคน (FTE):Q", title="FTE", scale=alt.Scale(zero=False)),
            color=alt.Color("กลุ่ม:N", scale=need_scale, title="Health Need"),
            tooltip=[alt.Tooltip("year:O", title="ปี"), "กลุ่ม:N", alt.Tooltip("ความต้องการกำลังคน (FTE):Q", title="FTE", format=",.2f")])
        st.altair_chart(chart_cfg(tln, 320), use_container_width=True)
    first, last = t_tot.iloc[0]["ความต้องการกำลังคน (FTE)"], t_tot.iloc[-1]["ความต้องการกำลังคน (FTE)"]
    if first:
        st.caption(f"การเปลี่ยนแปลง {years[0]} → {years[-1]}: {last - first:+,.2f} FTE ({(last / first - 1):+.1%})")

with tab4:
    ag = df.assign(กลุ่ม=df.health_need.map(HEALTH_SHORT)).groupby(["age_group", "กลุ่ม"], as_index=False)["ความต้องการกำลังคน (FTE)"].sum()
    age_order = sorted(ag.age_group.unique().tolist(), key=age_key)
    st.markdown('<div class="sec">FTE แยกตามกลุ่มอายุ</div><div class="sec-sub">แท่งซ้อนตาม Health Need</div>', unsafe_allow_html=True)
    ca = alt.Chart(ag).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("age_group:N", sort=age_order, title="กลุ่มอายุ (ปี)", axis=alt.Axis(labelAngle=-40)),
        y=alt.Y("ความต้องการกำลังคน (FTE):Q", title="FTE", stack="zero"),
        color=alt.Color("กลุ่ม:N", scale=need_scale, title="Health Need"),
        tooltip=[alt.Tooltip("age_group:N", title="กลุ่มอายุ"), "กลุ่ม:N", alt.Tooltip("ความต้องการกำลังคน (FTE):Q", title="FTE", format=",.2f")])
    st.altair_chart(chart_cfg(ca, 320), use_container_width=True)

    if province == "ทุกจังหวัด":
        pv = df.groupby("province", as_index=False)["ความต้องการกำลังคน (FTE)"].sum().sort_values("ความต้องการกำลังคน (FTE)", ascending=False)
        top_n = st.slider("จำนวนจังหวัดที่แสดง", 5, len(pv), min(15, len(pv)))
        pv_top = pv.head(top_n)
        st.markdown(f'<div class="sec">{top_n} จังหวัดที่มี FTE สูงสุด</div><div class="sec-sub">ปี {year} · ตามตัวกรองปัจจุบัน</div>', unsafe_allow_html=True)
        cp = alt.Chart(pv_top).mark_bar(cornerRadiusEnd=4, color="#14918F").encode(
            y=alt.Y("province:N", sort="-x", title=None),
            x=alt.X("ความต้องการกำลังคน (FTE):Q", title="FTE"),
            tooltip=[alt.Tooltip("province:N", title="จังหวัด"), alt.Tooltip("ความต้องการกำลังคน (FTE):Q", title="FTE", format=",.2f")])
        st.altair_chart(chart_cfg(cp, 24 * top_n + 40), use_container_width=True)
    else:
        st.caption("เลือก “ทุกจังหวัด” ที่แถบด้านซ้ายเพื่อดูการเปรียบเทียบรายจังหวัด")

with tab5:
    showcols = ["year", "province", "hos_type", "ประเภทหน่วยบริการ", "health_need", "sex", "age_group", "cci", "pred_rate", "Population",
                "ปริมาณบริการฐาน (ครั้ง)", "ปริมาณบริการหลังปรับ (ครั้ง)", "เวลามาตรฐาน (นาที/ครั้ง)", "ภาระงาน (ชั่วโมง)", "ความต้องการกำลังคน (FTE)"]
    out = df[showcols].copy()
    d1, d2 = st.columns([3, 1])
    d1.markdown(f'<div class="sec">ข้อมูลระดับ strata</div><div class="sec-sub">{len(out):,} แถว · ปี {year}</div>', unsafe_allow_html=True)
    d2.download_button("⬇️ ดาวน์โหลด CSV", data=out.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"WISN_FTE_{year}.csv", mime="text/csv", use_container_width=True, type="primary")
    st.dataframe(out.rename(columns={"year": "ปี", "province": "จังหวัด", "hos_type": "รหัสประเภทหน่วยบริการ", "health_need": "Health Need",
                                     "sex": "รหัสเพศ", "age_group": "กลุ่มอายุ", "cci": "CCI", "pred_rate": "อัตราพยากรณ์ต้นทาง"}),
                 use_container_width=True, height=460, hide_index=True)

st.write("")
with st.expander("📘 คำอธิบายสูตรและข้อควรระวัง"):
    st.markdown("""
**สูตรหลัก**

- บริการหลังปรับ = จำนวนบริการพยากรณ์ × (1 + Unmet Need/100)
- ภาระงาน (ชั่วโมง) = บริการหลังปรับ × เวลามาตรฐาน (นาที/ครั้ง) ÷ 60
- ความต้องการกำลังคน (FTE) = ภาระงาน (ชั่วโมง) ÷ AWT (ชั่วโมง/คน/ปี)

**ข้อควรระวัง**
1. ผลิตภัณฑ์นี้ใช้จำนวนบริการจากไฟล์ผลพยากรณ์เป็นฐาน ไม่ได้ฝึกหรือรัน Random Forest ใหม่
2. ผลรวม FTE จะเปลี่ยนตามตัวกรอง พารามิเตอร์ และขอบเขตบริการที่เลือก
3. AWT 1,680 ชั่วโมง/ปี และเวลามาตรฐาน 6.55 นาที/ครั้ง เป็นค่าตั้งต้นของการศึกษา ควรทบทวนความเหมาะสมก่อนใช้จริง
4. การคำนวณราย Health Need ใช้เวลามาตรฐานเดียวกันเป็นค่าเริ่มต้นเท่านั้น สามารถปรับแยกหมวดเมื่อมีหลักฐานรองรับ
5. ไม่ควรนำผลต่างระหว่าง FTE กับจำนวนแพทย์มาเรียกว่าการขาดแคลน หากยังไม่มีข้อมูลกำลังคนจริงและนิยามหน่วยงานที่เปรียบเทียบตรงกัน
6. ตรวจสอบความหมายของ pred_rate และ Population กับแหล่งสร้างไฟล์ก่อนนำไปอ้างอิงเชิงนโยบาย โดยไม่ควรรวมคอลัมน์ Population ข้าม strata เพราะประชากรอาจถูกทำซ้ำในแต่ละมิติ
""")
st.markdown('<div class="foot">Prototype สำหรับการวิจัย/ทดสอบการคำนวณ ไม่ใช่ระบบปฏิบัติการหรือคำแนะนำการจัดสรรกำลังคน</div>', unsafe_allow_html=True)
