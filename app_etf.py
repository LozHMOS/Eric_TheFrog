"""
DevPro – Underground Development Productivity Suite
Lean mining methodology for continuous improvement in underground coal development.
All benchmark data derived from real-world PIE (Process Improvement Event) programmes.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="DevPro | Development Productivity Suite",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background-color:#0d1117}
[data-testid="stSidebar"]{background-color:#161b22!important;border-right:1px solid #30363d}
section[data-testid="stSidebar"]>div{background-color:#161b22!important}
.block-container{padding-top:1.4rem;padding-bottom:2rem}
h1{color:#f0a500!important;font-weight:900!important;letter-spacing:-0.02em}
h2{color:#e5a200!important;font-weight:700!important}
h3{color:#d4a017!important;font-weight:600!important}
p,li{color:#c9d1d9!important}
label,.stMarkdown p{color:#c9d1d9!important}
div[data-testid="stMetric"]{background:#1c2128;border-radius:8px;border:1px solid #30363d;padding:1rem!important}
div[data-testid="stMetric"] label{color:#8b949e!important;font-size:0.72rem!important;text-transform:uppercase;letter-spacing:0.05em}
div[data-testid="stMetricValue"]{color:#f0a500!important;font-weight:800!important}
div[data-testid="stMetricDelta"]{font-size:0.78rem!important}
.stButton>button{background:linear-gradient(135deg,#f0a500,#d97706)!important;color:#0d1117!important;font-weight:700!important;border:none!important;border-radius:6px!important;padding:0.45rem 1.4rem!important}
.stButton>button:hover{opacity:0.88!important}
.stTextInput input,.stNumberInput input,.stTextArea textarea,div[data-baseweb="select"]>div{background-color:#1c2128!important;color:#c9d1d9!important;border:1px solid #30363d!important;border-radius:6px!important}
div[data-testid="stDataFrame"]{border-radius:8px}
.stTabs [data-baseweb="tab-list"]{background-color:#161b22!important;border-bottom:1px solid #30363d}
.stTabs [data-baseweb="tab"]{color:#8b949e!important;background:transparent!important}
.stTabs [aria-selected="true"]{color:#f0a500!important;border-bottom:2px solid #f0a500!important}
.streamlit-expanderHeader{background-color:#1c2128!important;color:#c9d1d9!important}
.streamlit-expanderContent{background-color:#161b22!important}
hr{border-color:#30363d!important}
#MainMenu,footer,header{visibility:hidden}
</style>
""", unsafe_allow_html=True)

COAL_PRICE_DEFAULT = 220
TONNES_PER_METRE   = 35
LW_DAILY_PROD_T    = 12000
SHIFTS_PER_DAY     = 2
CUT_HOURS          = 9.5
AMBER  = "#f0a500"; GREEN="#10b981"; RED="#ef4444"
BLUE   = "#3b82f6"; ORANGE="#f97316"; PURPLE="#8b5cf6"; GREY="#6b7280"

PLOT_BASE = dict(
    paper_bgcolor="#1c2128", plot_bgcolor="#1c2128",
    font=dict(color="#c9d1d9", size=12),
    xaxis=dict(gridcolor="#2d3748", linecolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#2d3748", linecolor="#30363d", zerolinecolor="#30363d"),
    legend=dict(bgcolor="#1c2128", bordercolor="#30363d", borderwidth=1),
    margin=dict(l=50, r=20, t=45, b=45)
)

# ── session state ─────────────────────────────────────────────────────────────
def _default_pillar_history():
    return pd.DataFrame({
        "Pillar":          ["1-2","3-4","5-6","7-8","9-10","11-12","12-13"],
        "Roof Condition":  ["High Clay","High Clay","Green","Green","Green","High Clay","High Clay"],
        "Actual (shfts)":  [32,30,26,24,17,23,22],
        "Forecast (shfts)":[27,27,22,20,16,24,21],
        "Metres":          [165,175,210,225,235,190,200],
        "Ops Manning":     [4,4,5,5,5,6,5],
        "Belt DT %":       [28,25,20,18,15,22,29],
        "Period":          ["M1","M1","M2","M2","M3","M4","M4"],
    })

def _default_shift_log():
    np.random.seed(42)
    rows=[]
    base=datetime(2024,1,1)
    m_act={
        "A":{"8-bolt green":[20,24,23,21,25,22,23],"8-bolt+mega":[14,15,13,14,16]},
        "B":{"8-bolt green":[21,22,20,23,22,21,24],"8-bolt+mega":[14,13,15,14,13]},
        "C":{"8-bolt green":[22,23,24,20,25,23,22],"8-bolt+mega":[15,16,14,15,16]},
        "D":{"8-bolt green":[17,19,17,14,18,16,17],"8-bolt+mega":[12,11,13,12,11]},
    }
    crews=["A","B","C","D"]
    idx={c:{p:0 for p in["8-bolt green","8-bolt+mega"]}for c in crews}
    for i in range(28):
        d=base+timedelta(days=i//2)
        sh="A/S"if i%2==0 else"N/S"
        cr=crews[i%4]
        pt="8-bolt green"if i<20 else"8-bolt+mega"
        ci=idx[cr][pt]%len(m_act[cr][pt])
        ac=m_act[cr][pt][ci]; idx[cr][pt]+=1
        rows.append({"Date":d.strftime("%d %b"),"Shift":sh,"Crew":cr,"Pattern":pt,
            "Target (m)":22 if pt=="8-bolt green" else 14,"Actual (m)":ac,
            "Belt DT(min)":int(np.random.randint(10,35)),"Power DT(min)":int(np.random.randint(0,25)),
            "SC DT(min)":int(np.random.randint(0,20)),"CM DT(min)":int(np.random.randint(0,20)),"Notes":""})
    return pd.DataFrame(rows)

def _default_ideas():
    return [
        {"Idea":"Trial 6-bolt pattern in green roof conditions","Owner":"Crew A","PIE Link":"Golden Meter","Expected Gain (m/shift)":3.0,"Status":"In Progress","Priority":"High","Date":"2024-01-05"},
        {"Idea":"Add second fan to enable parallel D-heading process work","Owner":"Crew C","PIE Link":"Pillar Cycle","Expected Gain (m/shift)":2.5,"Status":"Open","Priority":"High","Date":"2024-01-08"},
        {"Idea":"Pre-stage bolt pods and mesh before every shift","Owner":"Crew B","PIE Link":"Golden Meter","Expected Gain (m/shift)":1.5,"Status":"Complete","Priority":"Medium","Date":"2024-01-03"},
        {"Idea":"Surface delegate to conduct drift runner pre-starts","Owner":"Crew D","PIE Link":"Roster/TTFC","Expected Gain (m/shift)":1.0,"Status":"Complete","Priority":"Medium","Date":"2023-12-20"},
        {"Idea":"Dedicated LHD for inbye supplies during straight runs","Owner":"Crew A","PIE Link":"Manning","Expected Gain (m/shift)":2.0,"Status":"Open","Priority":"High","Date":"2024-01-10"},
    ]

for k,v in {
    "ideas":_default_ideas(),
    "golden_data":pd.DataFrame(columns=["Date","Crew","Bolting Pattern","Rate (m/hr)","Metres Cut","Notes"]),
    "pillar_history":_default_pillar_history(),
    "shift_log":_default_shift_log(),
    "coal_price":COAL_PRICE_DEFAULT,
    "takt_data":None,
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ── helpers ───────────────────────────────────────────────────────────────────
def kpi_card(label,value,delta=None,delta_up=True,accent=AMBER):
    arrow="▲"if delta_up else"▼"
    dc=GREEN if delta_up else RED
    dh=(f'<div style="font-size:0.78rem;color:{dc};margin-top:0.2rem">{arrow} {delta}</div>')if delta else""
    return(f'<div style="background:#1c2128;border:1px solid #30363d;border-left:4px solid {accent};'
           f'border-radius:8px;padding:0.9rem 1.1rem;height:100%">'
           f'<div style="font-size:0.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.06em;font-weight:600">{label}</div>'
           f'<div style="font-size:1.8rem;font-weight:900;color:{accent};line-height:1.15;margin-top:0.2rem">{value}</div>{dh}</div>')

def banner(msg,kind="info"):
    cfg={"info":(f"background:#0c1a2e;border-left:4px solid {BLUE};color:#93c5fd","ℹ️"),
         "warning":(f"background:#451a03;border-left:4px solid {ORANGE};color:#fed7aa","⚠️"),
         "success":(f"background:#052e16;border-left:4px solid {GREEN};color:#bbf7d0","✅"),
         "danger":(f"background:#450a0a;border-left:4px solid {RED};color:#fecaca","🚨")}
    s,ic=cfg.get(kind,cfg["info"])
    return f'<div style="{s};border-radius:6px;padding:0.7rem 1rem;margin:0.4rem 0;font-size:0.88rem">{ic} {msg}</div>'

def slbl(text):
    st.markdown(f'<p style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#6b7280;border-bottom:1px solid #30363d;padding-bottom:0.3rem;margin:1.1rem 0 0.6rem 0">{text}</p>',unsafe_allow_html=True)

def aplayout(fig,title="",height=320,leg_h=False):
    kw=dict(**PLOT_BASE,title=title,height=height)
    if leg_h:kw["legend"]=dict(**PLOT_BASE["legend"],orientation="h",y=-0.2)
    fig.update_layout(**kw);return fig

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:0.8rem 0 0.4rem 0"><div style="font-size:1.65rem;font-weight:900;background:linear-gradient(90deg,#f0a500,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent">⛏ DevPro</div><div style="font-size:0.65rem;color:#6b7280;letter-spacing:0.1em;margin-top:-0.2rem">DEVELOPMENT PRODUCTIVITY SUITE</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    page=st.radio("nav",label_visibility="collapsed",options=[
        "🏠  Executive Overview","🔍  Diagnostic Scanner","🏅  Golden Meter Builder",
        "🔄  Pillar Cycle Simulator","📅  Live Takt Planner","📊  Performance Dashboard",
        "⏱️  Downtime Loss Analyser","💡  Idea Bank & Action Tracker","🚀  Future PIE Generator"])
    st.markdown("---")
    slbl("Global Settings")
    st.session_state.coal_price=st.number_input("HCC Price (AUD/t)",value=int(st.session_state.coal_price),step=5,help="Hard coking coal reference price")
    lw_float=st.number_input("Current LW Float (days)",value=95,step=1,help="Development days ahead of the longwall — below 60 is critical")
    st.markdown("---")
    if lw_float<60:    st.markdown(banner(f"LW float CRITICAL — {lw_float} days!","danger"),unsafe_allow_html=True)
    elif lw_float<90:  st.markdown(banner(f"LW float at risk — {lw_float} days","warning"),unsafe_allow_html=True)
    else:              st.markdown(banner(f"LW float healthy — {lw_float} days","success"),unsafe_allow_html=True)
    st.markdown("---")
    st.caption("DevPro v2.0 · Lean Mining Methodology · Benchmarks from real-world PIE programmes")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if "Executive Overview" in page:
    st.markdown("# ⛏ Underground Development Productivity Suite")
    st.markdown('<p style="color:#8b949e;font-size:1rem;margin-top:-0.7rem">Operator-led continuous improvement &nbsp;·&nbsp; Lean mining methodology &nbsp;·&nbsp; Real-time panel intelligence</p>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2,c3,c4,c5=st.columns(5)
    lw_rev=LW_DAILY_PROD_T*st.session_state.coal_price/1e6
    for col,args in zip([c1,c2,c3,c4,c5],[
        ("Best Instantaneous Rate","4.5 m/hr","6-bolt green roof",True,AMBER),
        ("Best Pillar Cycle","17 shifts","vs 32-shift baseline",True,GREEN),
        ("Target Weekly Advance","235 m","14 shifts · green conditions",True,BLUE),
        ("Belt DT Target","→ < 5%","from 20–30% of cut time",True,ORANGE),
        ("LW Daily Revenue",f"${lw_rev:.1f}M","at stake without dev metres",True,PURPLE)]):
        with col: st.markdown(kpi_card(*args),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    L,R=st.columns([3,2],gap="large")
    with L:
        slbl("What One Wave of PIEs Delivers — Proven Results")
        df_r=pd.DataFrame({
            "Metric":["Pillar cycle — green roof","Pillar cycle — high clay","Cut rate (8-bolt)","Cut rate (6-bolt)","Weekly metres — green","Weekly metres — high clay","Belt downtime","Operators on CM"],
            "Baseline":["24 shifts","32 shifts","2.0–2.5 m/hr","—","~140 m","~100 m","20–30 %","3–4"],
            "Post-PIE":["17–20 shifts","22 shifts","2.8–4.0 m/hr","3.5–4.5 m/hr","220–235 m","170–185 m","< 5 % target","5–7"],
            "Uplift":["↑ 25–30 %","↑ 31 %","↑ 40–60 %","New standard","↑ 57–68 %","↑ 70–85 %","PIE in progress","Critical enabler"]})
        def _cu(v):
            if "↑" in str(v): return"color:#10b981;font-weight:bold"
            if "progress" in str(v): return"color:#f59e0b"
            if "standard" in str(v): return"color:#3b82f6;font-weight:bold"
            return""
        st.dataframe(df_r.style.applymap(_cu,subset=["Uplift"]),use_container_width=True,hide_index=True)
        st.markdown("<br>",unsafe_allow_html=True)
        slbl("The Four-Step PIE Cycle")
        steps=[("1️⃣","DIAGNOSE","Structured brainstorm with operators. Rank top 5–10 loss drivers."),
               ("2️⃣","PIE EVENT","2–4 day intensive with frontline operators — time & motion, data, solutions."),
               ("3️⃣","IMPLEMENT","Operators own the change. Trial in real shifts. Measure the result."),
               ("4️⃣","SUSTAIN","Live dashboard tracks adherence. Idea bank feeds the next wave.")]
        cols4=st.columns(4)
        for col,(ic,tt,ds) in zip(cols4,steps):
            with col:
                st.markdown(f'<div style="background:#1c2128;border:1px solid #30363d;border-top:3px solid {AMBER};border-radius:8px;padding:0.8rem;text-align:center;min-height:140px"><div style="font-size:1.4rem">{ic}</div><div style="font-size:0.68rem;font-weight:800;color:{AMBER};letter-spacing:0.1em;margin:0.3rem 0">{tt}</div><div style="font-size:0.75rem;color:#9ca3af;line-height:1.4">{ds}</div></div>',unsafe_allow_html=True)
    with R:
        slbl("Pillar Cycle Improvement Trajectory")
        months=["Month 1","Month 2","Month 3","Month 4","Month 5*","Month 6*"]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=months,y=[27,20,18,21,18,17],mode="lines",name="Forecast",line=dict(color=GREY,dash="dash"),opacity=0.7))
        fig.add_trace(go.Scatter(x=months,y=[32,24,20,22,18,15],mode="lines+markers",name="Actuals",line=dict(color=AMBER,width=3),marker=dict(size=9,color=AMBER,line=dict(width=2,color="#0d1117"))))
        fig.add_trace(go.Scatter(x=months,y=[None,None,16,14,14,14],mode="lines+markers",name="PIE Target",line=dict(color=GREEN,dash="dot",width=2),marker=dict(size=8,color=GREEN),connectgaps=False))
        fig.add_hrect(y0=14,y1=16,fillcolor=GREEN,opacity=0.05,line_width=0)
        fig.add_annotation(x="Month 6*",y=14.5,text="Target zone",font=dict(color=GREEN,size=10),showarrow=False,xanchor="right")
        fig.update_yaxes(range=[10,36],title="Shifts per pillar")
        aplayout(fig,"Monthly avg pillar cycle",height=280,leg_h=True)
        st.plotly_chart(fig,use_container_width=True)
        slbl("Financial Impact Calculator")
        extra_m=st.slider("Additional metres/week from improvements",0,150,80,help="Baseline ~140 m/wk · PIE target ~235 m/wk (+95 m)")
        t_per_m=st.slider("Estimated tonnes per metre of advance",20,60,35)
        extra_t=extra_m*t_per_m*52; extra_r=extra_t*st.session_state.coal_price/1e6
        fc1,fc2=st.columns(2)
        with fc1: st.markdown(kpi_card("Extra Tonnes/Year",f"{extra_t/1000:.0f}kt",f"{extra_m}m/wk · {t_per_m}t/m",True,GREEN),unsafe_allow_html=True)
        with fc2: st.markdown(kpi_card("Revenue Uplift/Year",f"${extra_r:.1f}M",f"@ ${st.session_state.coal_price}/t HCC",True,AMBER),unsafe_allow_html=True)
        st.markdown(banner(f"Every additional {extra_m} m/week of advance directly extends LW float by ~{extra_m/14:.1f} days/week — reducing exposure to a ${lw_rev:.1f}M/day LW stoppage.","success"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DIAGNOSTIC SCANNER
# ══════════════════════════════════════════════════════════════════════════════
elif "Diagnostic Scanner" in page:
    st.markdown("# 🔍 Diagnostic Scanner")
    st.markdown('<p style="color:#8b949e">Identify, rank and prioritise improvement opportunities — the essential first step of any PIE programme.</p>',unsafe_allow_html=True)
    st.markdown("---")
    L,R=st.columns([2,3],gap="large")
    with L:
        slbl("Configure Your Diagnostic")
        focus=st.selectbox("Primary focus area",["All loss categories","Belt system & outbye infrastructure","Pillar cycle time & panel planning","Instantaneous cut rate (Golden Meter)","Manning & crew balance","Ventilation & parallel process work","Equipment reliability & maintenance","Roof support density & bolting patterns","Roster, TTFC & operating time recovery","Skills, tickets & crew capability"])
        slbl("Record Observed Issues (one per line)")
        issues=st.text_area("obs",height=110,placeholder="e.g.\nBelt trips 3–4 times per shift\nOnly 1 fan — D-heading idle\nCrew drops to 3 ops on CM during crib",label_visibility="collapsed")
        slbl("Observed Downtime Split (% available cut time)")
        belt_dt=st.slider("Belt system",0,40,25)
        power_dt=st.slider("Panel power / electrical",0,20,8)
        sc_dt=st.slider("S/C trips",0,15,6)
        cm_dt=st.slider("CM maintenance",0,20,7)
        other_dt=st.slider("Other delays",0,15,5)
        total_dt=belt_dt+power_dt+sc_dt+cm_dt+other_dt
        if total_dt>50:   st.markdown(banner(f"Total downtime: {total_dt}% — critically high. These losses are costing metres every shift.","danger"),unsafe_allow_html=True)
        elif total_dt>30: st.markdown(banner(f"Total downtime: {total_dt}% — significant improvement opportunity.","warning"),unsafe_allow_html=True)
        st.button("▶ Generate Prioritised Opportunities",use_container_width=True)
    with R:
        slbl("Loss Pareto — Where Are the Metres Going?")
        labels_p=["Belt system","CM / hydraulics","Manning gaps","Power / elec","S/C trips","Other"]
        pct_p=[belt_dt,cm_dt,12,power_dt,sc_dt,other_dt]
        order_p=np.argsort(pct_p)[::-1]
        ls=[labels_p[i] for i in order_p]; ps=[pct_p[i] for i in order_p]
        cum_p=np.cumsum(ps)
        fig2=make_subplots(specs=[[{"secondary_y":True}]])
        fig2.add_trace(go.Bar(x=ls,y=ps,name="% Cut Time Lost",marker_color=[AMBER,RED,ORANGE,BLUE,PURPLE,GREY][:len(ls)],text=[f"{v}%" for v in ps],textposition="outside"),secondary_y=False)
        fig2.add_trace(go.Scatter(x=ls,y=cum_p,name="Cumulative %",mode="lines+markers",line=dict(color=GREEN,width=2),marker=dict(size=7)),secondary_y=True)
        fig2.add_hline(y=80,line_dash="dot",line_color=GREEN,opacity=0.5,annotation_text="80% line",secondary_y=True)
        fig2.update_yaxes(title_text="% of Cut Time",secondary_y=False)
        fig2.update_yaxes(title_text="Cumulative %",secondary_y=True,range=[0,120])
        aplayout(fig2,"Downtime Pareto — all categories",height=300,leg_h=True)
        st.plotly_chart(fig2,use_container_width=True)
        slbl("Ranked Improvement Opportunities")
        belt_m=round(belt_dt/100*CUT_HOURS*3.5,1)
        opps=pd.DataFrame({"Opportunity":["Reduce belt downtime to < 5% of cut time","Optimise crew to 7 ops + 2 trades","Add 2nd fan — enable parallel D-heading","Eliminate pre-start travel via surface delegate","Dedicated LHD for inbye supplies","Challenge bolting pattern in green roof","On-condition maintenance — reduce CM trips"],"Est. Gain (m/shift)":[belt_m,3.0,2.5,1.0,2.0,3.5,1.8],"Ease":["Medium","High","Medium","High","High","Medium","Low"],"PIE Type":["Belt Uptime","Manning","Ventilation","Roster/TTFC","Process Work","Golden Meter","Maintenance"],"Priority":["🔴 1","🔴 2","🟡 3","🟢 4","🟢 5","🟡 6","🔴 7"]}).sort_values("Est. Gain (m/shift)",ascending=False).reset_index(drop=True)
        st.dataframe(opps,use_container_width=True,hide_index=True)
        wk_gain=opps["Est. Gain (m/shift)"].sum()*SHIFTS_PER_DAY*7
        ann_r=wk_gain*52*TONNES_PER_METRE*st.session_state.coal_price/1e6
        st.markdown(banner(f"If all opportunities are captured: +{wk_gain:.0f} m/week · ${ann_r:.1f}M additional annual revenue at ${st.session_state.coal_price}/t.","success"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — GOLDEN METER BUILDER
# ══════════════════════════════════════════════════════════════════════════════
elif "Golden Meter Builder" in page:
    st.markdown("# 🏅 Golden Meter Builder")
    st.markdown('<p style="color:#8b949e">Define, validate and share the optimum 15-minute cutting sequence — the standard every crew aspires to on every metre.</p>',unsafe_allow_html=True)
    st.markdown("---")
    L,R=st.columns([2,3],gap="large")
    with L:
        slbl("Cutting Sequence Parameters")
        pat=st.selectbox("Bolting pattern",["6-bolt green roof","8-bolt green roof","8-bolt green + 2 mega-bolts every 2nd mesh"])
        if "mega" in pat:
            st.markdown(banner("Mega-bolt window: use the extra 10–15 min for bulk supply restocking.","info"),unsafe_allow_html=True)
            sc=st.number_input("Stone cutting (min)",value=4.0,step=0.1,min_value=1.0)
            b1=st.number_input("Roof bolting pass 1 (min)",value=4.0,step=0.1,min_value=1.0)
            up=st.number_input("Underpass cut (min)",value=2.0,step=0.1,min_value=0.5)
            b2=st.number_input("Roof + rib bolt pass 2 (min)",value=4.0,step=0.1,min_value=1.0)
            mb=st.number_input("Mega-bolt drill & bolt (min, per 2nd m)",value=10.0,step=0.5)
            adj=st.number_input("Adjustment / vent / supplies (min)",value=1.5,step=0.1)
            avg_cyc=sc+b1+up+b2+adj+mb/2; bmark=2.7
        elif "6-bolt" in pat:
            sc=st.number_input("Stone cutting (min)",value=3.5,step=0.1,min_value=1.0)
            b1=st.number_input("Roof bolting pass 1 (min)",value=3.5,step=0.1,min_value=1.0)
            up=st.number_input("Underpass cut (min)",value=2.0,step=0.1,min_value=0.5)
            b2=st.number_input("Roof + rib bolt pass 2 (min)",value=3.5,step=0.1,min_value=1.0)
            mb=0.0; adj=st.number_input("Adjustment / vent / supplies (min)",value=1.0,step=0.1)
            avg_cyc=sc+b1+up+b2+adj; bmark=4.0
        else:
            sc=st.number_input("Stone cutting (min)",value=4.0,step=0.1,min_value=1.0)
            b1=st.number_input("Roof bolting pass 1 (min)",value=4.0,step=0.1,min_value=1.0)
            up=st.number_input("Underpass cut (min)",value=2.0,step=0.1,min_value=0.5)
            b2=st.number_input("Roof + rib bolt pass 2 (min)",value=4.0,step=0.1,min_value=1.0)
            mb=0.0; adj=st.number_input("Adjustment / vent / supplies (min)",value=1.0,step=0.1)
            avg_cyc=sc+b1+up+b2+adj; bmark=3.5
        rate=round(60/avg_cyc,2)if avg_cyc>0 else 0
        shift_m=round(rate*CUT_HOURS,1)
        slbl("Calculated Performance")
        m1,m2,m3=st.columns(3)
        m1.metric("Cycle Time",f"{avg_cyc:.1f} min/m")
        m2.metric("Instant Rate",f"{rate:.2f} m/hr",delta=f"{'▲' if rate>=bmark else '▼'} bmark {bmark}")
        m3.metric("Metres/Shift",f"{shift_m:.0f} m")
        if rate>=bmark:
            st.markdown(banner(f"On-target! {rate:.2f} m/hr meets the {pat} benchmark of {bmark} m/hr.","success"),unsafe_allow_html=True)
        else:
            gap=bmark-rate; ml=round(gap*CUT_HOURS,1)
            st.markdown(banner(f"{rate:.2f} m/hr is {gap:.2f} m/hr below benchmark — ~{ml} m/shift left on the table.","warning"),unsafe_allow_html=True)
        if st.button("💾 Save Observation"):
            new=pd.DataFrame({"Date":[datetime.now().strftime("%Y-%m-%d")],"Crew":["—"],"Bolting Pattern":[pat],"Rate (m/hr)":[rate],"Metres Cut":[shift_m],"Notes":[""]})
            st.session_state.golden_data=pd.concat([st.session_state.golden_data,new],ignore_index=True)
            st.success("Observation saved.")
    with R:
        slbl("15-Minute Sequence Visualisation")
        slbls=["Stone cut (3 passes)","Roof bolt pass 1 (2+2)","Underpass cut","Roof + rib bolt pass 2","Adjustment / supplies / vent"]
        svals=[sc,b1,up,b2,adj]
        if mb>0: slbls.append("Mega-bolt drill & bolt (every 2nd m)"); svals.append(mb)
        cols_s=[AMBER,BLUE,GREEN,ORANGE,PURPLE,RED]
        starts=[]; s=0
        for v in svals: starts.append(s); s+=v
        figB=go.Figure()
        for i,(lb,dv,st_) in enumerate(zip(slbls,svals,starts)):
            figB.add_trace(go.Bar(y=["Sequence"],x=[dv],base=st_,name=lb,orientation="h",marker_color=cols_s[i%len(cols_s)],text=f"{dv:.1f}'",textposition="inside",insidetextanchor="middle",hovertemplate=f"<b>{lb}</b><br>{dv:.1f} min<extra></extra>"))
        figB.add_vline(x=15,line_dash="dash",line_color=GREEN,annotation_text="15 min target",annotation_position="top right")
        figB.update_layout(**PLOT_BASE,barmode="stack",height=180,showlegend=False,xaxis_title="Minutes",yaxis=dict(showticklabels=False))
        st.plotly_chart(figB,use_container_width=True)
        slbl("Pattern Benchmark Comparison")
        st.dataframe(pd.DataFrame({"Bolting Pattern":["6-bolt green","8-bolt green","8-bolt + mega-bolt"],"Cycle (min/m)":[13.5,15.0,21.0],"Rate (m/hr)":[4.4,4.0,2.9],"Proj. m/shift":[42,38,28],"14-shift total (m)":[235,220,180],"Condition":["Green roof","Green roof","High clay"]}),use_container_width=True,hide_index=True)
        slbl("Key Success Factors")
        for tt,ds in [("👷 4 operators on CM at all times","A 4th operator delivers +30% cut rate vs 3 operators in identical conditions on the same day."),("🚚 S/C driver anticipation","Must anticipate CM position, stone sequence timing and avoid burying the breaker-feeder."),("🔩 Pre-positioned supplies","Bolt pods, mesh, chemicals and plates staged before the sequence starts — not during it."),("🌬️ Vent line management","Vent extensions planned per metre — managed during the mega-bolt window where applicable.")]:
            with st.expander(tt): st.markdown(f'<p style="color:#c9d1d9;font-size:0.88rem">{ds}</p>',unsafe_allow_html=True)
        slbl("Saved Observations")
        if st.session_state.golden_data.empty: st.markdown(banner("No observations saved yet — use the form on the left.","info"),unsafe_allow_html=True)
        else: st.dataframe(st.session_state.golden_data,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PILLAR CYCLE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Pillar Cycle Simulator" in page:
    st.markdown("# 🔄 Pillar Cycle Simulator")
    st.markdown('<p style="color:#8b949e">Model the effect of manning, equipment, ventilation and downtime on pillar cycle time — before committing resources underground.</p>',unsafe_allow_html=True)
    st.markdown("---")
    L,M,R=st.columns([1.5,1.5,2],gap="large")
    with L:
        slbl("Manning Configuration")
        operators=st.slider("Operators on CM",3,7,5,help="4+ operators gives +30% cut rate vs 3 operators")
        trades=st.slider("Trades per shift",1,3,2)
        hot_seat=st.checkbox("Hot-seat changeover active",value=False)
        st.markdown(banner("Target crew: 7 operators + 2 trades + 1 deputy. The 4th operator on the CM alone delivers +30% instantaneous cut rate.","info"),unsafe_allow_html=True)
    with M:
        slbl("Equipment & Conditions")
        fans=st.radio("Ventilation fans",[1,2],horizontal=True,help="2 fans enables parallel D-heading process work")
        belt_dt=st.slider("Belt downtime (%)",0,40,20,help="Target < 5% — currently 20–30% is typical")
        bolting=st.selectbox("Bolting pattern",["8-bolt green roof","6-bolt green roof","8-bolt + mega-bolts (high clay)"])
        parallel=fans==2 and operators>=6
        if parallel: st.markdown(banner("2 fans + ≥ 6 operators enables parallel D-heading process work — significant cycle reduction.","success"),unsafe_allow_html=True)
        else:         st.markdown(banner("Single fan or under-manned — parallel process work not possible.","warning"),unsafe_allow_html=True)
    base_sh=22
    op_adj=(7-operators)*1.8; fan_adj=(2-fans)*3.5
    dt_adj=max(0,belt_dt-5)*0.18
    bolt_adj={"8-bolt green roof":0,"6-bolt green roof":-2.5,"8-bolt + mega-bolts (high clay)":6.5}[bolting]
    para_adj=-2.0 if parallel else 0; hs_adj=-0.5 if hot_seat else 0
    sim=max(12,round(base_sh+op_adj+fan_adj+dt_adj+bolt_adj+para_adj+hs_adj))
    imp=base_sh-sim
    with R:
        slbl("Simulated Result")
        r1,r2,r3=st.columns(3)
        r1.metric("Pillar Cycle",f"{sim} shifts",delta=f"{imp:+.0f} vs baseline",delta_color="inverse"if imp<0 else"normal")
        ref_m=235 if"mega"not in bolting else 185
        r2.metric("Metres/Pillar",f"~{ref_m} m")
        ann_p=round(52*SHIFTS_PER_DAY*7/sim)
        r3.metric("Pillars/Year",f"~{ann_p}",delta=f"+{max(0,ann_p-round(52*SHIFTS_PER_DAY*7/base_sh))} vs baseline")
        fig3=go.Figure()
        bl=["High Clay\nBaseline","Green\nBaseline","Post-PIE\nPresent","Best\nAchieved","Your\nSimulation","Ultimate\nTarget"]
        bv=[32,24,21,17,sim,14]
        bc=[RED if v>22 else ORANGE if v>17 else GREEN if v<=14 else AMBER for v in bv]
        bc[-2]=BLUE
        fig3.add_trace(go.Bar(x=bl,y=bv,marker_color=bc,text=[str(v) for v in bv],textposition="outside",textfont=dict(color="#c9d1d9",size=13)))
        fig3.add_hline(y=14,line_dash="dot",line_color=GREEN,opacity=0.6,annotation_text="Ultimate target")
        fig3.update_yaxes(range=[0,38],title="Shifts per pillar")
        aplayout(fig3,"Pillar cycle — scenario vs benchmarks",height=290)
        st.plotly_chart(fig3,use_container_width=True)
        slbl("Adjustment Drivers")
        st.dataframe(pd.DataFrame({"Driver":["Operators","Fans","Belt DT","Bolting pattern","Parallel work","Hot-seat"],"Setting":[f"{operators} ops",f"{fans} fan{'s'if fans>1 else''}",f"{belt_dt}%",bolting.replace(" roof",""),"Yes"if parallel else"No","Yes"if hot_seat else"No"],"Shift delta":[f"{op_adj:+.1f}",f"{fan_adj:+.1f}",f"{dt_adj:+.1f}",f"{bolt_adj:+.1f}",f"{para_adj:+.1f}",f"{hs_adj:+.1f}"]}),use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — LIVE TAKT PLANNER
# ══════════════════════════════════════════════════════════════════════════════
elif "Live Takt Planner" in page:
    st.markdown("# 📅 Live Takt Planner")
    st.markdown('<p style="color:#8b949e">Weekly shift-by-shift plan at 15-minute Takt intervals — the shared source of truth for every crew underground.</p>',unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.takt_data is None or st.button("🔄 Reset to this week"):
        today=datetime.now(); mon=today-timedelta(days=today.weekday())
        dates=[mon+timedelta(days=d) for d in range(7)]
        crews_=["A","B","C","D","A","B","C","D","A","B","C","D","A","B"]
        pats_=["8-bolt green"]*10+["8-bolt+mega"]*4; tgts_=[22]*10+[14]*4
        rows_=[]
        for i,d in enumerate(dates):
            for j,sh in enumerate(["A/S","N/S"]):
                idx_=i*2+j
                rows_.append({"Day":d.strftime("%a %d %b"),"Shift":sh,"Crew":crews_[idx_],"Pattern":pats_[idx_],"Target (m)":tgts_[idx_],"Actual (m)":None,"Maint":("✔" if d.weekday() in[1,3] and sh=="A/S" else ""),"Notes":""})
        st.session_state.takt_data=pd.DataFrame(rows_)
    slbl("Shift Plan — Enter Actuals as Each Shift Completes")
    edited=st.data_editor(st.session_state.takt_data,num_rows="fixed",use_container_width=True,column_config={"Actual (m)":st.column_config.NumberColumn("Actual (m)",min_value=0,max_value=50),"Notes":st.column_config.TextColumn("Notes"),"Maint":st.column_config.TextColumn("⚙️",width="small")},hide_index=True)
    st.session_state.takt_data=edited
    if st.button("💾 Save Takt Plan"): st.success("Takt plan saved.")
    st.markdown("<br>",unsafe_allow_html=True)
    LT,RT=st.columns([2,1],gap="large")
    with LT:
        slbl("Cumulative Metres — Actuals vs Target vs PIE Benchmark")
        df_t=st.session_state.takt_data.copy()
        df_t["sn"]=range(1,len(df_t)+1)
        df_t["cum_tgt"]=df_t["Target (m)"].cumsum()
        df_t["cum_pie"]=df_t["Pattern"].map({"8-bolt green":22,"8-bolt+mega":14}).cumsum()
        df_t["cum_act"]=pd.to_numeric(df_t["Actual (m)"],errors="coerce").cumsum()
        figT=go.Figure()
        figT.add_trace(go.Scatter(x=df_t["sn"],y=df_t["cum_tgt"],name="Shift Target",mode="lines",line=dict(color=GREY,dash="dash")))
        figT.add_trace(go.Scatter(x=df_t["sn"],y=df_t["cum_pie"],name="PIE Benchmark",mode="lines",line=dict(color=GREEN,dash="dot",width=2)))
        figT.add_trace(go.Scatter(x=df_t["sn"],y=df_t["cum_act"],name="Actuals",mode="lines+markers",line=dict(color=AMBER,width=3),marker=dict(size=8,color=AMBER)))
        figT.update_xaxes(title="Shift #"); figT.update_yaxes(title="Cumulative metres")
        aplayout(figT,"14-shift rolling cumulative metres",height=290,leg_h=True)
        st.plotly_chart(figT,use_container_width=True)
    with RT:
        slbl("Weekly Summary")
        tt=df_t["Target (m)"].sum(); tp=df_t["Pattern"].map({"8-bolt green":22,"8-bolt+mega":14}).sum()
        ta=pd.to_numeric(df_t["Actual (m)"],errors="coerce").sum()
        st.metric("Weekly Target",f"{tt} m"); st.metric("PIE Benchmark",f"{tp} m")
        if not np.isnan(ta): st.metric("Actual to Date",f"{ta:.0f} m",delta=f"{ta-tt:.0f} m vs target")
        slbl("Takt Parameters")
        takt_r=st.number_input("Takt rate (m/hr)",value=3.5,step=0.1,min_value=1.0)
        tc=round(60/takt_r,1); mps=round(takt_r*CUT_HOURS,0)
        st.metric("Takt cycle time",f"{tc:.1f} min/m"); st.metric("Metres per shift",f"{mps:.0f} m"); st.metric("Metres per week",f"{mps*14:.0f} m")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — PERFORMANCE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif "Performance Dashboard" in page:
    st.markdown("# 📊 Performance Dashboard")
    st.markdown('<p style="color:#8b949e">14-shift rolling actuals · Crew benchmarking · Pillar history · Financial value of the performance gap.</p>',unsafe_allow_html=True)
    st.markdown("---")
    df_sl=st.session_state.shift_log.copy()
    df_sl["Actual (m)"]=pd.to_numeric(df_sl["Actual (m)"],errors="coerce")
    tab1,tab2,tab3=st.tabs(["  📈  Rolling Performance  ","  👥  Crew Benchmarking  ","  🏗️  Pillar History  "])
    with tab1:
        CL,CR=st.columns([3,1],gap="large")
        with CL:
            slbl("14-Shift Rolling Actuals vs Forecast vs PIE Target")
            df_sl["cum_act"]=df_sl["Actual (m)"].cumsum()
            df_sl["cum_tgt"]=df_sl["Target (m)"].cumsum()
            df_sl["cum_pie"]=df_sl["Pattern"].map({"8-bolt green":22,"8-bolt+mega":14}).cumsum()
            figD=go.Figure()
            figD.add_trace(go.Scatter(x=df_sl.index,y=df_sl["cum_tgt"],name="Shift Target",mode="lines",line=dict(color=GREY,dash="dash")))
            figD.add_trace(go.Scatter(x=df_sl.index,y=df_sl["cum_pie"],name="PIE Benchmark",mode="lines",line=dict(color=GREEN,dash="dot",width=2)))
            figD.add_trace(go.Scatter(x=df_sl.index,y=df_sl["cum_act"],name="Actuals",mode="lines+markers",line=dict(color=AMBER,width=3),marker=dict(size=8,color=AMBER,line=dict(width=2,color="#0d1117"))))
            figD.update_xaxes(title="Shift number"); figD.update_yaxes(title="Cumulative metres")
            aplayout(figD,"Cumulative metres — actuals vs forecast vs PIE target",height=320,leg_h=True)
            st.plotly_chart(figD,use_container_width=True)
        with CR:
            slbl("Period KPIs")
            avg_a=df_sl["Actual (m)"].mean(); avg_t=df_sl["Target (m)"].mean()
            best_s=df_sl["Actual (m)"].max(); worst_s=df_sl["Actual (m)"].min()
            pct_ab=(df_sl["Actual (m)"]>=df_sl["Target (m)"]).mean()*100
            st.metric("Avg Metres/Shift",f"{avg_a:.1f} m",delta=f"{avg_a-avg_t:+.1f} vs target")
            st.metric("Best Shift",f"{best_s:.0f} m"); st.metric("Worst Shift",f"{worst_s:.0f} m",delta=f"{worst_s-avg_t:+.0f} vs target",delta_color="inverse")
            st.metric("Shifts ≥ Target",f"{pct_ab:.0f}%")
            slbl("Shift Log (last 10)")
            st.dataframe(df_sl[["Date","Shift","Crew","Pattern","Target (m)","Actual (m)"]].tail(10),use_container_width=True,hide_index=True)
    with tab2:
        slbl("Crew-by-Crew Performance — Green Roof Straight Runs")
        cg=df_sl[df_sl["Pattern"]=="8-bolt green"].copy()
        ca=cg.groupby("Crew")["Actual (m)"].mean().reset_index()
        ca.columns=["Crew","Avg m/Shift"]
        CL2,CR2=st.columns([2,2],gap="large")
        with CL2:
            bc2=[GREEN if v==ca["Avg m/Shift"].max() else RED if v==ca["Avg m/Shift"].min() else AMBER for v in ca["Avg m/Shift"]]
            figC=go.Figure(go.Bar(x=ca["Crew"],y=ca["Avg m/Shift"],marker_color=bc2,text=[f"{v:.1f} m" for v in ca["Avg m/Shift"]],textposition="outside",textfont=dict(color="#c9d1d9",size=13)))
            bv2=ca["Avg m/Shift"].max(); wv2=ca["Avg m/Shift"].min(); gp2=(bv2-wv2)/wv2*100
            figC.add_hline(y=bv2,line_dash="dot",line_color=GREEN,annotation_text=f"Best crew: {bv2:.1f} m",annotation_position="top left")
            figC.update_yaxes(title="Avg metres/shift",range=[0,bv2*1.2])
            aplayout(figC,"Average metres per shift by crew — green roof",height=320)
            st.plotly_chart(figC,use_container_width=True)
        with CR2:
            slbl("Performance Gap Analysis")
            gm_sh=bv2-wv2; gm_wk=gm_sh*SHIFTS_PER_DAY*7; gr_ann=gm_wk*52*TONNES_PER_METRE*st.session_state.coal_price/1e6
            st.metric("Best vs Worst Crew Gap",f"{gp2:.0f}%",help="Real-world gap: ≥30% between crews in identical conditions")
            st.metric("Metres Lost per Shift",f"{gm_sh:.1f} m"); st.metric("Metres Lost per Week",f"{gm_wk:.0f} m"); st.metric("Revenue Gap (annual)",f"${gr_ann:.1f}M")
            st.markdown(banner(f"Closing the best-to-worst crew gap — without changing any equipment — is worth ${gr_ann:.1f}M/year. PIEs reduce this gap by more than half in a single wave.","success"),unsafe_allow_html=True)
            slbl("TTFC Impact")
            ttfc=st.slider("TTFC gap best vs worst crew (minutes)",0,60,30,help="30-min TTFC gap is observed between high and low performing crews")
            ttfc_m=round(ttfc/60*3.5,1)
            st.markdown(banner(f"A {ttfc}-min TTFC disadvantage costs ~{ttfc_m} m/shift before any cutting starts — compounded by the loss of operating rhythm.","warning"),unsafe_allow_html=True)
            slbl("Shift Scatter — All Crews")
            figS=px.strip(df_sl[df_sl["Pattern"]=="8-bolt green"],x="Crew",y="Actual (m)",color="Crew",color_discrete_map={"A":AMBER,"B":BLUE,"C":GREEN,"D":RED},stripmode="overlay",hover_data=["Date","Shift"])
            figS.add_hline(y=22,line_dash="dash",line_color=GREY,opacity=0.6,annotation_text="Target 22 m")
            aplayout(figS,"All shift results by crew (green roof)",height=260)
            st.plotly_chart(figS,use_container_width=True)
    with tab3:
        slbl("Pillar Cycle History")
        df_ph=st.session_state.pillar_history.copy()
        figP=go.Figure()
        figP.add_trace(go.Bar(x=df_ph["Pillar"],y=df_ph["Forecast (shfts)"],name="Forecast",marker_color="#374151",opacity=0.8))
        figP.add_trace(go.Bar(x=df_ph["Pillar"],y=df_ph["Actual (shfts)"],name="Actual",marker_color=[GREEN if a<=f else RED if a>f+3 else AMBER for a,f in zip(df_ph["Actual (shfts)"],df_ph["Forecast (shfts)"])],opacity=0.9))
        figP.add_hline(y=14,line_dash="dot",line_color=GREEN,opacity=0.5,annotation_text="Green target: 14 shifts")
        figP.add_hline(y=18,line_dash="dot",line_color=ORANGE,opacity=0.5,annotation_text="High clay target: 18 shifts")
        figP.update_yaxes(title="Shifts per pillar")
        aplayout(figP,"Pillar cycle — actual vs forecast",height=320,leg_h=True)
        st.plotly_chart(figP,use_container_width=True)
        with st.expander("➕ Log a New Pillar"):
            np1,np2,np3,np4,np5=st.columns(5)
            pn=np1.text_input("Pillar #","14-15"); pc=np2.selectbox("Roof",["Green","High Clay"])
            pa=np3.number_input("Actual shfts",14,40,20); pf=np4.number_input("Forecast shfts",14,40,18); pm=np5.number_input("Metres",100,300,220)
            if st.button("Add Pillar"):
                nr=pd.DataFrame({"Pillar":[pn],"Roof Condition":[pc],"Actual (shfts)":[pa],"Forecast (shfts)":[pf],"Metres":[pm],"Ops Manning":[5],"Belt DT %":[15],"Period":[datetime.now().strftime("%b-%y")]})
                st.session_state.pillar_history=pd.concat([st.session_state.pillar_history,nr],ignore_index=True)
                st.success(f"Pillar {pn} logged.")
        st.dataframe(df_ph,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — DOWNTIME LOSS ANALYSER
# ══════════════════════════════════════════════════════════════════════════════
elif "Downtime Loss Analyser" in page:
    st.markdown("# ⏱️ Downtime Loss Analyser")
    st.markdown('<p style="color:#8b949e">Quantify exactly what each downtime category costs in metres, tonnes and revenue — then target the biggest losses first.</p>',unsafe_allow_html=True)
    st.markdown("---")
    LD,RD=st.columns([2,3],gap="large")
    with LD:
        slbl("Enter Downtime by Category (minutes per shift)")
        belt_min=st.number_input("Belt system stoppages",0,600,120,help="Observed range: 130–225 min/shift at its worst")
        power_min=st.number_input("Panel power / electrical",0,300,30)
        sc_min=st.number_input("S/C trips & resets",0,120,20)
        cm_min=st.number_input("CM maintenance (hydraulics, picks, platform)",0,240,25)
        other_min=st.number_input("Other delays",0,120,15)
        cut_rate=st.number_input("Operational cut rate (m/hr)",2.0,5.0,3.5,step=0.1)
        tot_min=belt_min+power_min+sc_min+cm_min+other_min
        avail_min=CUT_HOURS*60; dt_pct=min(tot_min/avail_min*100,100)
        m_lost=round(tot_min/60*cut_rate,1)
        stop_starts=int(belt_min/30+power_min/30+sc_min/20)
        reramp_m=round(stop_starts*0.4*cut_rate,1); tot_m_lost=m_lost+reramp_m
        slbl("Impact Summary")
        d1,d2=st.columns(2)
        d1.metric("Total DT",f"{tot_min} min",delta=f"{dt_pct:.0f}% of cut time",delta_color="inverse")
        d2.metric("Direct Metres Lost",f"{m_lost} m")
        d1.metric("Re-ramp losses",f"~{reramp_m} m",help="20–40 min ramp-up after every stop-start event")
        d2.metric("Total Metres Lost",f"{tot_m_lost} m")
        wk_ml=tot_m_lost*SHIFTS_PER_DAY*7; ann_rl=wk_ml*52*TONNES_PER_METRE*st.session_state.coal_price/1e6
        if dt_pct>=30:   st.markdown(banner(f"CRITICAL: {dt_pct:.0f}% downtime · ~{wk_ml:.0f} m/week · ~${ann_rl:.1f}M/year. Belt PIE required immediately.","danger"),unsafe_allow_html=True)
        elif dt_pct>=15: st.markdown(banner(f"WARNING: {dt_pct:.0f}% downtime · {wk_ml:.0f} m/week · ${ann_rl:.1f}M/year.","warning"),unsafe_allow_html=True)
        else:            st.markdown(banner(f"Manageable: {dt_pct:.0f}% downtime. Continue targeting < 5%.","info"),unsafe_allow_html=True)
    with RD:
        slbl("Downtime Pareto — Direct Metres Lost")
        cats_d=["Belt system","Panel power","S/C trips","CM maintenance","Other"]
        mins_d=[belt_min,power_min,sc_min,cm_min,other_min]
        ml_d=[round(m/60*cut_rate,1)for m in mins_d]
        ord_d=np.argsort(ml_d)[::-1]
        cs_d=[cats_d[i]for i in ord_d]; mls_d=[ml_d[i]for i in ord_d]
        cum_d=np.cumsum(mls_d)/max(sum(mls_d),0.01)*100
        figDT=make_subplots(specs=[[{"secondary_y":True}]])
        figDT.add_trace(go.Bar(x=cs_d,y=mls_d,marker_color=[AMBER,RED,ORANGE,BLUE,GREY][:len(cs_d)],name="Metres Lost",text=[f"{v:.1f} m"for v in mls_d],textposition="outside"),secondary_y=False)
        figDT.add_trace(go.Scatter(x=cs_d,y=cum_d,mode="lines+markers",name="Cumulative %",line=dict(color=GREEN,width=2),marker=dict(size=7)),secondary_y=True)
        figDT.add_hline(y=80,line_dash="dot",line_color=GREEN,opacity=0.5,secondary_y=True,annotation_text="80% line")
        figDT.update_yaxes(title_text="Metres lost per shift",secondary_y=False)
        figDT.update_yaxes(title_text="Cumulative %",secondary_y=True,range=[0,120])
        aplayout(figDT,"Downtime Pareto — metres lost per category",height=320,leg_h=True)
        st.plotly_chart(figDT,use_container_width=True)
        slbl("Annual Impact vs < 5% Downtime Target")
        tgt_ml=round(avail_min*0.05/60*cut_rate,1); sav=tot_m_lost-tgt_ml
        sav_ann=sav*SHIFTS_PER_DAY*7*52*TONNES_PER_METRE*st.session_state.coal_price/1e6
        figAI=go.Figure(go.Bar(x=["Current","< 5% DT Target"],y=[tot_m_lost,tgt_ml],marker_color=[RED,GREEN],text=[f"{v:.1f} m/shift"for v in[tot_m_lost,tgt_ml]],textposition="outside",textfont=dict(color="#c9d1d9",size=12)))
        aplayout(figAI,"Metres lost per shift — now vs target",height=240)
        st.plotly_chart(figAI,use_container_width=True)
        st.markdown(banner(f"Achieving < 5% belt downtime recovers ~{sav:.1f} m/shift. Over 52 weeks that is worth ${sav_ann:.1f}M — making the belt system the single highest-value PIE target on any development panel.","success"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — IDEA BANK & ACTION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif "Idea Bank" in page:
    st.markdown("# 💡 Idea Bank & Action Tracker")
    st.markdown('<p style="color:#8b949e">Capture every improvement idea from the workforce — assign ownership, link to PIEs, track progress and celebrate wins.</p>',unsafe_allow_html=True)
    st.markdown("---")
    LI,RI=st.columns([2,3],gap="large")
    with LI:
        slbl("Add New Idea")
        with st.form("idea_form",clear_on_submit=True):
            idea_txt=st.text_area("Describe the improvement idea",height=80)
            ci1,ci2=st.columns(2)
            owner_=ci1.text_input("Owner (crew / role)")
            pie_lnk=ci2.selectbox("PIE type",["Golden Meter","Pillar Cycle","Belt Uptime","Manning","Roster/TTFC","Ventilation","Maintenance","Roof Support","Process Work","Other"])
            ci3,ci4=st.columns(2)
            exp_g=ci3.number_input("Gain (m/shift)",0.0,20.0,1.5,0.5)
            pri_=ci4.selectbox("Priority",["High","Medium","Low"])
            submitted=st.form_submit_button("➕ Add to Idea Bank")
            if submitted and idea_txt:
                st.session_state.ideas.append({"Idea":idea_txt,"Owner":owner_,"PIE Link":pie_lnk,"Expected Gain (m/shift)":exp_g,"Status":"Open","Priority":pri_,"Date":datetime.now().strftime("%Y-%m-%d")})
                st.success("Idea added!")
        slbl("Bank Summary")
        if st.session_state.ideas:
            df_id=pd.DataFrame(st.session_state.ideas)
            oc=(df_id["Status"]=="Open").sum(); pc=(df_id["Status"]=="In Progress").sum(); dc=(df_id["Status"]=="Complete").sum()
            tg=df_id["Expected Gain (m/shift)"].sum()
            s1,s2=st.columns(2)
            s1.metric("Open",f"{oc}"); s2.metric("In Progress",f"{pc}")
            s1.metric("Complete",f"{dc}"); s2.metric("Total Expected Gain",f"{tg:.1f} m/shift")
            bp=df_id.groupby("PIE Link")["Expected Gain (m/shift)"].sum().reset_index()
            bp.columns=["PIE Type","Gain (m/shift)"]
            figIB=go.Figure(go.Bar(x=bp["PIE Type"],y=bp["Gain (m/shift)"],marker_color=AMBER,text=[f"{v:.1f}"for v in bp["Gain (m/shift)"]],textposition="outside"))
            aplayout(figIB,"Expected gain by PIE type (m/shift)",height=220)
            st.plotly_chart(figIB,use_container_width=True)
    with RI:
        if st.session_state.ideas:
            slbl("All Ideas — Click to Update Status")
            df_show=pd.DataFrame(st.session_state.ideas)
            edited_id=st.data_editor(df_show,num_rows="fixed",use_container_width=True,column_config={"Status":st.column_config.SelectboxColumn("Status",options=["Open","In Progress","Complete","On Hold"]),"Priority":st.column_config.SelectboxColumn("Priority",options=["High","Medium","Low"]),"Expected Gain (m/shift)":st.column_config.NumberColumn("Gain (m/shift)",min_value=0.0,max_value=20.0,step=0.5)},hide_index=True)
            st.session_state.ideas=edited_id.to_dict("records")
            slbl("Status Distribution")
            sc_=pd.DataFrame(st.session_state.ideas)["Status"].value_counts()
            figPi=go.Figure(go.Pie(labels=sc_.index,values=sc_.values,hole=0.55,marker_colors=[GREEN,AMBER,ORANGE,GREY]))
            figPi.update_traces(textfont_size=12)
            aplayout(figPi,"",height=220)
            st.plotly_chart(figPi,use_container_width=True)
        else:
            st.markdown(banner("No ideas yet — add your first improvement suggestion on the left.","info"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — FUTURE PIE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Future PIE Generator" in page:
    st.markdown("# 🚀 Future PIE Generator")
    st.markdown('<p style="color:#8b949e">Prioritise your next wave of Process Improvement Events by impact, ease and strategic fit — then build your 3–6 month roadmap.</p>',unsafe_allow_html=True)
    st.markdown("---")
    pie_bl=pd.DataFrame({
        "PIE Subject":["Belt system uptime improvement","Panel advances & premium panel configuration","Optimise manning to 7 ops + 2 trades + 1 deputy","Add second fan — parallel D-heading process work","Roster optimisation & hot-seat changeover","Bolting pattern review (green & high clay conditions)","Maintenance scheduling — on-condition vs scheduled (TPM)","Panel standards & Lean 5S discipline","Miner driver ticket availability & skills uplift","Systematic D-heading process work scheduling","Recruitment & skills retention practices"],
        "Category":["Infrastructure","Panel Planning","Manning","Ventilation","Roster","Support","Maintenance","Standards","Capability","Process Work","HR"],
        "Impact (1-10)":[10,8,9,7,6,8,7,5,6,7,4],
        "Ease (1-10)":[4,6,8,5,6,7,5,8,4,6,3],
        "Est. Gain (m/shift)":[6.5,3.5,3.0,2.5,1.5,3.0,2.0,1.0,1.5,2.5,0.8],
        "Duration (days)":[4,4,2,3,2,3,4,2,3,3,2],
        "Wave":["Wave 2","Wave 2","Wave 1 ✔","Wave 2","Wave 2","Wave 1 ✔","Wave 2","Wave 3","Wave 3","Wave 2","Wave 3"],
    })
    LP,RP=st.columns([3,2],gap="large")
    with LP:
        slbl("PIE Priority Matrix — Impact vs Ease (bubble size = metres gained/shift)")
        wave_c={"Wave 1 ✔":GREEN,"Wave 2":AMBER,"Wave 3":GREY}
        figM=go.Figure()
        for wave,grp in pie_bl.groupby("Wave"):
            figM.add_trace(go.Scatter(x=grp["Ease (1-10)"],y=grp["Impact (1-10)"],mode="markers+text",name=wave,
                text=grp["PIE Subject"].apply(lambda s:s[:22]+"…"if len(s)>22 else s),
                textposition="top center",textfont=dict(size=9,color="#c9d1d9"),
                marker=dict(size=grp["Est. Gain (m/shift)"]*7,color=wave_c.get(wave,AMBER),opacity=0.8,line=dict(width=1,color="#0d1117"))))
        figM.add_vline(x=5.5,line_dash="dot",line_color="#374151",opacity=0.6)
        figM.add_hline(y=5.5,line_dash="dot",line_color="#374151",opacity=0.6)
        for txt,xp,yp,col in [("Do First →",8,9.5,GREEN),("Plan Carefully",2,9.5,ORANGE),("Quick Wins",8,1.5,BLUE),("Deprioritise",2,1.5,GREY)]:
            figM.add_annotation(x=xp,y=yp,text=txt,font=dict(color=col,size=10),showarrow=False)
        figM.update_xaxes(range=[0,11],title="Ease of Implementation →")
        figM.update_yaxes(range=[0,11],title="Business Impact ↑")
        aplayout(figM,"PIE Priority Matrix",height=430,leg_h=True)
        st.plotly_chart(figM,use_container_width=True)
    with RP:
        slbl("PIE Backlog")
        st.dataframe(pie_bl[["PIE Subject","Category","Impact (1-10)","Ease (1-10)","Est. Gain (m/shift)","Wave"]],use_container_width=True,hide_index=True)
        slbl("Wave 2 Forecast Outcome")
        w2=pie_bl[pie_bl["Wave"]=="Wave 2"]
        tg_w2=w2["Est. Gain (m/shift)"].sum(); wk_w2=tg_w2*SHIFTS_PER_DAY*7
        rev_w2=wk_w2*52*TONNES_PER_METRE*st.session_state.coal_price/1e6
        ww1,ww2=st.columns(2)
        ww1.metric("Wave 2 PIEs",f"{len(w2)}"); ww2.metric("Combined gain",f"{tg_w2:.1f} m/shift")
        ww1.metric("Weekly metres uplift",f"{wk_w2:.0f} m/wk"); ww2.metric("Annual revenue potential",f"${rev_w2:.1f}M")
        st.markdown(banner(f"A focused Wave 2 targeting {len(w2)} PIEs could deliver up to {tg_w2:.1f} additional metres per shift — worth ${rev_w2:.1f}M/year at current HCC prices.","success"),unsafe_allow_html=True)
        slbl("Senior Team Diagnostic — Recommended Before Wave 2")
        st.markdown('<div style="background:#1c2128;border:1px solid #30363d;border-radius:8px;padding:1rem;font-size:0.85rem;color:#c9d1d9;line-height:1.6"><b style="color:#f0a500">One focused session (~1 hr/day for one week) with the management team:</b><br><br>• Brainstorm generates 50–70 candidate improvement projects<br>• Cluster and score by impact vs available budget<br>• Agree on top 5–10 projects for the wave — shared ownership from day one<br>• Process legitimises priorities and drives the "one direction" commitment<br><br><b style="color:#10b981">The diagnostic is what makes PIEs stick — it is not optional.</b></div>',unsafe_allow_html=True)
