from pathlib import Path
import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="MedGuard | Medication Safety",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "drug_pairs_processed.csv"
FILTERED_FILE = "drug_pairs_filtered.csv"

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root { --ink:#102d3b; --muted:#5c7c8b; --teal:#087f83; --teal2:#0caaa8;
        --ice:#eaf8f9; --line:#cfe7e9; }
.stApp {
  background:
    radial-gradient(ellipse at 84% 7%, rgba(130,228,229,.40), transparent 27%),
    radial-gradient(ellipse at 55% 30%, rgba(221,248,249,.75), transparent 38%),
    linear-gradient(135deg,#f8ffff 0%,#edf8f9 53%,#e7f5f6 100%);
  color:var(--ink); font-family:'DM Sans',sans-serif;
}
[data-testid="stHeader"] {background:rgba(240,251,251,.78);}
.block-container {padding-top:1.2rem; padding-bottom:2.3rem; max-width:1500px;}
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#f2fbfb,#e4f4f5);
  border-right:1px solid #d5e9ea;
}
[data-testid="stSidebar"] * {color:#153846;}
.brand {font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;line-height:1.1;color:#102d3b;}
.brand-sub {font-size:.88rem;color:#63818d;line-height:1.5;margin-top:5px;}
.side-note {margin-top:25px;padding:18px 16px;border:1px solid #cfe9eb;border-radius:20px;
 background:linear-gradient(145deg,rgba(183,239,240,.68),rgba(255,255,255,.76));}
.side-note h3 {font-family:'Playfair Display',serif;color:#123746;font-size:1.3rem;margin:14px 0 8px;}
.side-note p {font-size:.9rem;color:#5d7c89;margin:0;line-height:1.55;}
.eyebrow {font-size:.73rem;letter-spacing:.24em;text-transform:uppercase;font-weight:700;color:#147f85;}
.hero {position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.95);border-radius:30px;
 padding:34px 36px 30px;min-height:325px;
 background:linear-gradient(110deg,rgba(255,255,255,.91) 0%,rgba(240,252,252,.87) 52%,rgba(180,239,239,.55) 100%);
 box-shadow:0 16px 50px rgba(27,104,115,.08);}
.hero h1 {font-family:'Playfair Display',serif;font-size:clamp(2.3rem,4vw,4.25rem);
 line-height:.99;letter-spacing:-.04em;color:#102735;margin:13px 0 18px;max-width:700px;}
.hero p {font-size:1.05rem;line-height:1.6;color:#5b7988;max-width:660px;margin-bottom:22px;}
.hero-art {position:absolute;right:1.8%;top:0%;width:39%;height:100%;pointer-events:none;opacity:.99;}
.hero-art svg {width:100%;height:100%;filter:drop-shadow(0 16px 22px rgba(0,110,130,.19));}
.metric-row {display:flex;gap:28px;flex-wrap:wrap;position:relative;z-index:1;}
.metric {display:flex;align-items:center;gap:11px;min-width:150px;}
.metric-icon {width:48px;height:48px;border-radius:50%;display:grid;place-items:center;
 background:rgba(177,233,235,.55);font-size:1.35rem;}
.metric b {display:block;font-size:1.08rem;color:#153543;}
.metric small {color:#688592;font-size:.83rem;}
.panel {border:1px solid rgba(255,255,255,.95);border-radius:26px;background:rgba(255,255,255,.77);
 box-shadow:0 10px 36px rgba(32,109,119,.055);padding:24px 25px;margin-top:18px;}
.panel-title {font-family:'Playfair Display',serif;color:#123542;font-size:1.7rem;font-weight:600;margin:0;}
.panel-sub {color:#688592;margin-top:3px;font-size:.91rem;}
.pill-note {padding:12px 15px;border:1px solid #d5ebed;background:rgba(239,250,250,.95);
 border-radius:15px;color:#416977;font-size:.83rem;line-height:1.45;}
.field-label {font-weight:700;color:#153846;font-size:.92rem;margin:0 0 7px;}
div[data-baseweb="select"] > div {
  background:#fff !important; border:1px solid #c8e1e5 !important; border-radius:14px !important;
  min-height:52px !important; box-shadow:0 3px 10px rgba(17,94,109,.04) !important;
}
/* Selected medicine: target Streamlit/BaseWeb's actual value and input nodes */
div[data-baseweb="select"] > div {
  background:#ffffff !important;
  border:1px solid #b9dce1 !important;
  border-radius:14px !important;
}
/* Force contrast on Streamlit's select widget value, input and icons */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
  background-color:#ffffff !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div {
  color:#123746 !important;
  -webkit-text-fill-color:#123746 !important;
  opacity:1 !important;
  text-shadow:none !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder {
  color:#587987 !important;
  -webkit-text-fill-color:#587987 !important;
  opacity:1 !important;
}
div[data-baseweb="select"] [role="combobox"],
div[data-baseweb="select"] [role="combobox"] *,
div[data-baseweb="select"] input,
div[data-baseweb="select"] input + div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] p {
  color:#123746 !important;
  -webkit-text-fill-color:#123746 !important;
  opacity:1 !important;
  text-shadow:none !important;
}
div[data-baseweb="select"] input::placeholder {
  color:#587987 !important;
  -webkit-text-fill-color:#587987 !important;
  opacity:1 !important;
}
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[role="listbox"],
ul[role="listbox"] {
  background-color:#ffffff !important;
  color:#173643 !important;
  -webkit-text-fill-color:#173643 !important;
}
li[role="option"], div[role="option"] {
  background-color:#ffffff !important;
  color:#173643 !important;
  -webkit-text-fill-color:#173643 !important;
  opacity:1 !important;
}
li[role="option"]:hover, div[role="option"]:hover {
  background-color:#dff5f5 !important;
  color:#103742 !important;
  -webkit-text-fill-color:#103742 !important;
}
button[kind="primary"] {background:linear-gradient(110deg,#087c80,#00565b)!important;color:white!important;
 border:0!important;border-radius:15px!important;min-height:52px!important;font-weight:700!important;}
button[kind="primary"] p {color:#fff!important;}
.stat-card {height:100%;min-height:125px;border:1px solid #dceff0;border-radius:20px;
 background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(238,250,250,.85));padding:17px 18px;}
.stat-label {font-size:.78rem;color:#688592;font-weight:700;text-transform:uppercase;letter-spacing:.06em;}
.stat-value {font-family:'Playfair Display',serif;font-size:2rem;font-weight:600;color:#123542;line-height:1.2;margin:6px 0;}
.stat-detail {font-size:.82rem;color:#688592;line-height:1.4;}
.warning {background:#fff5dc;border:1px solid #f4e0a9;border-radius:14px;padding:13px 16px;
 color:#684a13;font-size:.86rem;line-height:1.5;}
.info-box {background:#e9f6fb;border:1px solid #cde8f2;border-radius:14px;padding:14px 16px;
 color:#21566c;font-size:.89rem;line-height:1.55;}
.footer {text-align:center;color:#77949f;font-size:.78rem;padding:24px 8px 4px;}
hr {border-color:#dcebed;}
@media (max-width: 850px) {
 .hero {padding:25px 22px;}
 .hero-art {opacity:.2;width:62%;right:-9%;}
 .panel {padding:19px 16px;}
 .hero h1 {font-size:2.5rem;}
}
</style>
""", unsafe_allow_html=True)

# A custom, crisp glass-capsule illustration (pure SVG; no external image dependency)
capsule_svg = """
<svg viewBox="0 0 520 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Translucent crystal capsule illustration">
 <defs>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
   <stop offset="0" stop-color="#ffffff" stop-opacity=".96"/>
   <stop offset=".28" stop-color="#c9ffff" stop-opacity=".72"/>
   <stop offset=".53" stop-color="#39c5d1" stop-opacity=".57"/>
   <stop offset=".78" stop-color="#f7ffff" stop-opacity=".83"/>
   <stop offset="1" stop-color="#5ddbe0" stop-opacity=".72"/>
  </linearGradient>
  <linearGradient id="inner" x1="0" y1="0" x2="1" y2="1">
   <stop offset="0" stop-color="#ffffff" stop-opacity=".98"/>
   <stop offset=".45" stop-color="#7ae5eb" stop-opacity=".88"/>
   <stop offset="1" stop-color="#0c879b" stop-opacity=".9"/>
  </linearGradient>
  <radialGradient id="shine"><stop stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#bafcff" stop-opacity="0"/></radialGradient>
  <filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
  <clipPath id="pillclip"><rect x="143" y="73" width="250" height="116" rx="58" transform="rotate(-43 268 131)"/></clipPath>
 </defs>
 <circle cx="343" cy="165" r="135" fill="#7de7eb" opacity=".16" filter="url(#blur)"/>
 <g opacity=".78" stroke="#fff" stroke-width="2" fill="url(#glass)">
  <circle cx="100" cy="76" r="19"/><circle cx="432" cy="75" r="12"/><circle cx="435" cy="276" r="17"/>
  <circle cx="133" cy="290" r="9"/><circle cx="392" cy="45" r="5"/>
 </g>
 <g transform="rotate(-43 268 131)">
   <rect x="143" y="73" width="250" height="116" rx="58" fill="#72dce3" opacity=".28" filter="url(#blur)"/>
   <rect x="143" y="73" width="250" height="116" rx="58" fill="url(#glass)" stroke="#fff" stroke-width="5"/>
   <rect x="152" y="82" width="232" height="98" rx="49" fill="none" stroke="#8cebf0" stroke-width="2.2"/>
   <g clip-path="url(#pillclip)">
    <rect x="260" y="67" width="143" height="130" fill="url(#inner)" opacity=".88"/>
    <path d="M267 75 C296 100 296 159 267 186" fill="none" stroke="#f4ffff" stroke-width="4" opacity=".85"/>
    <g fill="#e8ffff" opacity=".82">
     <circle cx="301" cy="105" r="4"/><circle cx="334" cy="92" r="3"/><circle cx="356" cy="129" r="5"/>
     <circle cx="314" cy="151" r="3"/><circle cx="370" cy="156" r="3"/><circle cx="344" cy="111" r="2"/>
     <circle cx="291" cy="134" r="2.5"/><circle cx="331" cy="171" r="4"/>
    </g>
   </g>
   <path d="M169 98 Q218 72 253 91" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" opacity=".94"/>
   <path d="M166 114 Q180 92 202 89" stroke="#fff" stroke-width="2.5" stroke-linecap="round" fill="none" opacity=".8"/>
   <ellipse cx="221" cy="91" rx="42" ry="8" fill="#fff" opacity=".2"/>
 </g>
 <g fill="url(#shine)"><circle cx="412" cy="218" r="42"/><circle cx="110" cy="195" r="25"/></g>
 <path d="M400 95l5 12 12 5-12 5-5 12-5-12-12-5 12-5z" fill="#fff" opacity=".95"/>
 <path d="M103 226l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="#fff" opacity=".9"/>
</svg>
"""

# ---------- Load data ----------
@st.cache_data
def load_data():
    source = DATA_FILE if Path(DATA_FILE).exists() else FILTERED_FILE
    if not Path(source).exists():
        return None, source
    frame = pd.read_csv(source)
    required = {"drug1", "drug2", "report_count", "serious_count", "serious_ratio"}
    if not required.issubset(frame.columns):
        return None, source
    frame = frame.dropna(subset=list(required)).copy()
    frame["drug1"] = frame["drug1"].astype(str).str.strip()
    frame["drug2"] = frame["drug2"].astype(str).str.strip()
    frame["report_count"] = pd.to_numeric(frame["report_count"], errors="coerce")
    frame["serious_count"] = pd.to_numeric(frame["serious_count"], errors="coerce")
    frame["serious_ratio"] = pd.to_numeric(frame["serious_ratio"], errors="coerce")
    frame = frame.dropna(subset=["report_count", "serious_count", "serious_ratio"])
    frame = frame[(frame["report_count"] > 0) & frame["serious_ratio"].between(0,1)]
    frame["key"] = frame.apply(
        lambda r: tuple(sorted((r["drug1"].casefold(), r["drug2"].casefold()))), axis=1
    )
    frame = frame.drop_duplicates("key")
    return frame, source

data, source_name = load_data()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div style="font-size:2.2rem;margin-bottom:5px">💊</div><div class="brand">MedGuard</div><div class="brand-sub">Medication Safety<br>Assessment System</div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("NAVIGATION", ["Home", "Drug Pair Explorer", "About Data", "Methodology", "Team", "Disclaimer"], label_visibility="collapsed")
    st.markdown("""
    <div class="side-note">
      <div style="font-size:1.9rem">✧ ◌</div>
      <h3>Data-Driven<br>Medication Awareness</h3>
      <p>Exploring real-world reporting patterns for research awareness.</p>
    </div>
    <div style="margin-top:20px;color:#7a98a2;font-size:.78rem">v1.0 &nbsp; | &nbsp; Research Prototype</div>
    """, unsafe_allow_html=True)

if data is None:
    st.error(f"Could not load a compatible CSV. Put {DATA_FILE} (preferred) or {FILTERED_FILE} in the same folder as app.py.")
    st.stop()

medicines = sorted(set(data["drug1"].tolist()) | set(data["drug2"].tolist()), key=str.casefold)
total_pairs = len(data)
filtered_count = None
if Path(FILTERED_FILE).exists():
    try:
        filtered_count = len(pd.read_csv(FILTERED_FILE))
    except Exception:
        pass
report_total = 20000  # current prototype source report count

def stat_card(label, value, detail):
    return f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div class="stat-detail">{detail}</div></div>'

# ---------- Pages ----------
if page in ("Home", "Drug Pair Explorer"):
    st.markdown(f"""
    <section class="hero">
      <div class="hero-art">{capsule_svg}</div>
      <div style="position:relative;z-index:2;max-width:760px">
        <div class="eyebrow">FAERS-BASED ANALYSIS</div>
        <h1>Medication Safety<br>Assessment System</h1>
        <p>Explore real-world drug-pair reporting statistics from FAERS-derived data.<br>
        A research prototype for educational awareness.</p>
        <div class="metric-row">
          <div class="metric"><div class="metric-icon">▤</div><div><b>{report_total:,}</b><small>Source Reports</small></div></div>
          <div class="metric"><div class="metric-icon">⌘</div><div><b>{total_pairs:,}</b><small>Observed Drug Pairs</small></div></div>
          <div class="metric"><div class="metric-icon">◉</div><div><b>openFDA / FAERS</b><small>Data Source</small></div></div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    head1, head2 = st.columns([3,1.05], vertical_alignment="center")
    with head1:
        st.markdown('<div style="font-size:1.85rem">💊 <span class="panel-title">Drug Pair Explorer</span></div><div class="panel-sub">Select two medicines to view reporting statistics from FAERS-derived reports.</div>', unsafe_allow_html=True)
    with head2:
        st.markdown('<div class="pill-note">ⓘ &nbsp; Reporting data only.<br>&nbsp;&nbsp;&nbsp;&nbsp;Not a clinical safety assessment.</div>', unsafe_allow_html=True)

    a, swapcol, b, action = st.columns([1.15,.18,1.15,.82], vertical_alignment="bottom")
    # Searchable medicine selectors with clear initial state.
    # Widget values are controlled by Streamlit itself; avoid assigning
    # st.session_state[key] and index simultaneously.

    if st.session_state.pop("pending_swap", False):
        old_a = st.session_state.get("med_a")
        old_b = st.session_state.get("med_b")
        st.session_state["med_a"] = old_b
        st.session_state["med_b"] = old_a

    with a:
        st.markdown('<div class="field-label">💊 &nbsp; Select Medicine A</div>', unsafe_allow_html=True)
        med_a = st.selectbox(
            "Select Medicine A",
            medicines,
            index=None,
            placeholder="Search and select a medicine...",
            key="med_a",
            label_visibility="collapsed",
        )
    with swapcol:
        st.markdown("<div style='height:11px'></div>", unsafe_allow_html=True)
        swap_clicked = st.button("↔", help="Swap medicines", use_container_width=True)
    with b:
        st.markdown('<div class="field-label">💊 &nbsp; Select Medicine B</div>', unsafe_allow_html=True)
        med_b = st.selectbox(
            "Select Medicine B",
            medicines,
            index=None,
            placeholder="Search and select a medicine...",
            key="med_b",
            label_visibility="collapsed",
        )
    with action:
        st.markdown("<div style='height:11px'></div>", unsafe_allow_html=True)
        check = st.button("⌕  Check Pair Statistics", type="primary", use_container_width=True)
        

    if swap_clicked:
        if med_a and med_b:
            st.session_state["pending_swap"] = True
            st.session_state.pop("last_pair", None)
            st.rerun()
        else:
            st.warning("Select both medicines before swapping.")



    if check:
        if not med_a or not med_b:
            st.warning("Please select both medicines first.")
        else:
            st.session_state["last_pair"] = (med_a, med_b)
    selected = st.session_state.get("last_pair")
    if selected:
        left, right = selected
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Observed Reporting Statistics</div><div class="panel-sub">Pair-level reporting summary for the selected medicines.</div><div style="height:13px"></div>', unsafe_allow_html=True)
        if left.casefold() == right.casefold():
            st.markdown("""
            <div style="
                background-color: #FFF4CC;
                color: #663C00;
                border: 1px solid #E6B800;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: 600;
            ">
                Please select two different medicines.
            </div>
            """, unsafe_allow_html=True)
        else:
            key = tuple(sorted((left.casefold(), right.casefold())))
            match = data[data["key"] == key]
            if match.empty:
                st.markdown('<div class="info-box">This exact combination is not present in the current dataset. Missing data does not mean that the combination is safe.</div>', unsafe_allow_html=True)
            else:
                rec = match.iloc[0]
                count = int(rec["report_count"])
                serious = int(rec["serious_count"])
                ratio = float(rec["serious_ratio"]) * 100
                c1,c2,c3,c4 = st.columns([1,1,1,1.18])
                with c1: st.markdown(stat_card("Reports mentioning both",f"{count:,}","Reports containing both medicine names"),unsafe_allow_html=True)
                with c2: st.markdown(stat_card("Reports marked serious",f"{serious:,}","Reports with serious flag"),unsafe_allow_html=True)
                with c3: st.markdown(stat_card("Serious-report proportion",f"{ratio:.1f}%","Serious reports ÷ reports mentioning pair"),unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<div class="stat-card"><div class="stat-label">Selected pair</div><div style="font-weight:700;color:#123542;margin:9px 0;line-height:1.4">{html.escape(left)}<br><span style="color:#07888b">+</span><br>{html.escape(right)}</div><div class="stat-detail">Observed in this dataset</div></div>',unsafe_allow_html=True)
                st.markdown('<div style="height:12px"></div><div class="warning"><b>⚠ Reporting statistics are not a clinical safety assessment.</b> This proportion is not the probability of harm, interaction strength, or causal evidence. Consult a doctor or pharmacist before starting, stopping, or combining medicines.</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="panel"><div class="panel-title">Observed Reporting Statistics</div><div class="panel-sub">Choose two medicines above, then select <b>Check Pair Statistics</b> to view the pair summary.</div></div>',unsafe_allow_html=True)

    fcount = f"{filtered_count:,}" if filtered_count is not None else "—"
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(stat_card("Data source","openFDA / FAERS","Adverse-event reports"),unsafe_allow_html=True)
    with c2: st.markdown(stat_card("Total reports",f"{report_total:,}","Individual reports processed"),unsafe_allow_html=True)
    with c3: st.markdown(stat_card("Observed drug pairs",f"{total_pairs:,}","Co-reported pairs in processed data"),unsafe_allow_html=True)
    with c4: st.markdown(stat_card("Filtered dataset",fcount,"Pairs with 5 or more reports"),unsafe_allow_html=True)

elif page == "About Data":
    st.markdown('<div class="panel"><div class="eyebrow">DATA OVERVIEW</div><div class="panel-title">About the dataset</div><div class="panel-sub">What the numbers represent—and what they do not.</div><hr></div>',unsafe_allow_html=True)
    st.write(f"**Loaded file:** `{source_name}`")
    st.write(f"**Rows in loaded pair table:** {len(data):,}")
    st.write(f"**Distinct medicine names:** {len(medicines):,}")
    st.markdown('<div class="info-box">The table contains medicine pairs co-mentioned in adverse-event reports. Co-reporting alone does not establish that the medicines interacted or caused an event.</div>',unsafe_allow_html=True)
    st.write("Medicine-name matching is based on the text available in the dataset. Brand names, salt forms, spelling variants, and strengths may be represented separately.")

elif page == "Methodology":
    st.markdown('<div class="panel"><div class="eyebrow">METHOD</div><div class="panel-title">How pair statistics are produced</div><hr>1. Load FAERS-derived reports collected through openFDA.<br><br>2. Extract medicine names from each report and standardize text casing/whitespace.<br><br>3. Generate unordered medicine pairs within each report.<br><br>4. Count reports mentioning each pair and count those marked serious.<br><br>5. Calculate serious-report proportion = serious_count ÷ report_count.</div>',unsafe_allow_html=True)
    st.markdown('<div class="warning"><b>Interpretation limit:</b> Report frequency and seriousness flags are descriptive reporting measures—not verified drug-interaction labels, incidence rates, or a clinical prediction.</div>',unsafe_allow_html=True)

elif page == "Team":
    st.markdown('<div class="panel"><div class="eyebrow">PROJECT TEAM</div><div class="panel-title">Built for research awareness</div><hr><b>Diya Mehlawat</b> — Project coordination<br><br><b>Devansh Mishra</b> — Application development<br><br><b>Shivam Tiwari</b> — Model / analysis<br><br><b>Kritika Gupta</b> — Data processing<br><br><b>Project Guide:</b> Dr. Tejasvee Bisen<br><b>Project ID:</b> PT170</div>',unsafe_allow_html=True)

elif page == "Disclaimer":
    st.markdown('<div class="panel"><div class="eyebrow">PLEASE READ</div><div class="panel-title">Research prototype disclaimer</div><hr>This application summarizes FAERS-derived adverse-event reporting data for educational and research awareness only.<br><br>• Reports can be biased, incomplete, duplicated, or influenced by reporting patterns.<br>• Co-occurrence does not prove causation or a drug-drug interaction.<br>• Absence of a pair from this dataset does not mean the combination is safe.<br>• Serious-report proportion is not the probability of harm.<br>• This application does not provide diagnosis, treatment advice, or clinical safety clearance.<br><br><b>Always consult a qualified doctor or pharmacist about medication decisions.</b></div>',unsafe_allow_html=True)

st.markdown('<div class="footer">MedGuard · Medication Safety Assessment System &nbsp; | &nbsp; Research Prototype · FAERS-derived reporting analysis</div>',unsafe_allow_html=True)
 
