import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Development Productivity Toolkit",
    page_icon="📐",
    layout="wide"
)

# Initialise session state
if "ideas" not in st.session_state:
    st.session_state.ideas = []
if "golden_data" not in st.session_state:
    st.session_state.golden_data = pd.DataFrame(columns=["Date", "Crew", "Bolting_Pattern", "Instantaneous_Rate_m_h", "Metres_Cut"])
if "pillar_history" not in st.session_state:
    st.session_state.pillar_history = pd.DataFrame({
        "Pillar": ["P1", "P2", "P3", "P4"],
        "Shifts_Actual": [24, 21, 17, 19],
        "Shifts_Forecast": [26, 22, 20, 21],
        "Metres_Actual": [210, 235, 255, 240]
    })

st.title("Underground Development Productivity Toolkit")
st.markdown("**A practical bolt-on application to help development teams identify, test and sustain process improvements.**")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select module",
    [
        "Home",
        "Diagnostic Scanner",
        "Golden Meter Builder",
        "Pillar Cycle Simulator",
        "Live Takt Planner",
        "Performance Dashboard",
        "Idea Bank & Action Tracker",
        "Future PIE Generator"
    ]
)

if page == "Home":
    st.header("Welcome to the Development Productivity Toolkit")
    st.markdown("""
    This application demonstrates how development teams can systematically improve panel performance through operator-led Process Improvement Events, 
    detailed time-and-motion analysis and visual performance tracking.
    
    **Key benefits shown in the demonstration:**
    - Faster identification of recurring losses
    - Repeatable best-practice standards (Golden Meter)
    - Realistic pillar-cycle forecasting
    - Immediate visual feedback to crews
    - Sustained ownership of improvements by the operators themselves
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Typical instantaneous cut rate (green roof)", "3.5 – 4.5 m/h", "↑ 30 %")
    with col2:
        st.metric("Achievable pillar cycle reduction", "15 – 30 %", "↓ 5–7 shifts")
    with col3:
        st.metric("Weekly advance target (green roof)", "220 – 235 m", "↑ 25 %")
    
    st.info("Use the sidebar to explore each module. All data is saved in your current session.")

elif page == "Diagnostic Scanner":
    st.header("Diagnostic Scanner")
    st.markdown("Quickly identify and prioritise improvement opportunities using a structured brainstorming approach.")
    
    focus_area = st.selectbox("Focus area", [
        "Pillar cycle time", "Instantaneous cut rate", "Manning & crew balance",
        "Ventilation & parallel process work", "Belt & outbye downtime", "Roof support density"
    ])
    
    issues = st.text_area("List the main recurring issues you observe in this area (one per line)")
    
    if st.button("Generate prioritised opportunities"):
        if issues:
            st.success("Diagnostic complete – opportunities ranked by impact and ease of implementation")
            st.dataframe(pd.DataFrame({
                "Opportunity": ["Reduce external downtime", "Optimise manning to 7 operators + 2 trades", "Implement parallel process work in second heading"],
                "Estimated gain (m/shift)": [4.5, 3.0, 2.8],
                "Ease": ["High", "Medium", "High"],
                "Priority": ["1", "2", "3"]
            }))
        else:
            st.warning("Please enter at least one issue.")

elif page == "Golden Meter Builder":
    st.header("Golden Meter Builder")
    st.markdown("Build and validate the optimum 15-minute cycle for one metre of advance.")
    
    st.subheader("Standard sequence (green roof – 8-bolt pattern)")
    cols = st.columns(4)
    with cols[0]:
        stone_cut = st.number_input("Stone cutting (min)", value=4.0, step=0.1)
    with cols[1]:
        bolting = st.number_input("Roof & rib bolting (min)", value=4.0, step=0.1)
    with cols[2]:
        underpass = st.number_input("Underpass cut (min)", value=2.0, step=0.1)
    with cols[3]:
        adjustment = st.number_input("Adjustment & supplies (min)", value=1.0, step=0.1)
    
    total_min = stone_cut + bolting + underpass + adjustment
    rate = 60 / total_min if total_min > 0 else 0
    
    st.metric("Calculated instantaneous cut rate", f"{rate:.1f} m/h", help="Target range 3.5 – 4.5 m/h")
    
    if st.button("Save this Golden Meter observation"):
        new_row = pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Crew": ["Demo Crew"],
            "Bolting_Pattern": ["8-bolt"],
            "Instantaneous_Rate_m_h": [round(rate, 1)],
            "Metres_Cut": [25]
        })
        st.session_state.golden_data = pd.concat([st.session_state.golden_data, new_row], ignore_index=True)
        st.success("Observation saved")

    st.subheader("Historical Golden Meter results")
    st.dataframe(st.session_state.golden_data)

elif page == "Pillar Cycle Simulator":
    st.header("Pillar Cycle Simulator")
    st.markdown("Test different configurations and instantly see the effect on pillar completion time.")
    
    col1, col2 = st.columns(2)
    with col1:
        operators = st.slider("Operators on Continuous Miner", 3, 7, 5)
        trades = st.slider("Trades", 2, 3, 2)
        fans = st.radio("Number of fans", [1, 2], horizontal=True)
    with col2:
        bolting_pattern = st.selectbox("Bolting pattern", ["6-bolt green", "8-bolt green", "8-bolt + mega-bolts"])
        external_downtime_pct = st.slider("External downtime (%)", 0, 40, 15)
    
    base_shifts = 22
    adjustment = (7 - operators) * 2 + (1 - fans) * 4 + external_downtime_pct / 5
    estimated_shifts = max(14, int(base_shifts + adjustment))
    
    st.metric("Estimated pillar cycle (shifts)", estimated_shifts, 
              f"{22 - estimated_shifts} shift improvement vs baseline" if estimated_shifts < 22 else "No improvement yet")
    
    fig = go.Figure(go.Bar(x=["Current config", "Optimised config"], y=[22, estimated_shifts], marker_color=["#d62728", "#2ca02c"]))
    st.plotly_chart(fig, use_container_width=True)

elif page == "Live Takt Planner":
    st.header("Live Takt Planner (15-minute intervals)")
    st.markdown("Visual weekly plan showing expected metres, maintenance windows and process work.")
    
    dates = pd.date_range(datetime.now(), periods=7, freq="D")
    takt = pd.DataFrame({
        "Shift": ["A/S", "N/S"] * 7,
        "Date": np.repeat(dates.strftime("%d %b"), 2),
        "Planned metres": [22, 23, 21, 24, 20, 25, 23, 22, 24, 21, 23, 22, 20, 24],
        "Actual metres": [None] * 14,
        "Notes": ["Maintenance", "", "", "Mega-bolts", "", "", "", "", "", "", "", "", "", ""]
    })
    edited = st.data_editor(takt, num_rows="fixed", use_container_width=True)
    st.button("Save updated Takt Plan")

elif page == "Performance Dashboard":
    st.header("Performance Dashboard")
    
    st.subheader("14-shift rolling performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.pillar_history["Pillar"], 
                           y=st.session_state.pillar_history["Metres_Actual"], 
                           mode="lines+markers", name="Actual metres", line=dict(color="#2ca02c")))
    fig.add_trace(go.Scatter(x=st.session_state.pillar_history["Pillar"], 
                           y=[220]*4, mode="lines", name="PIE target", line=dict(dash="dash", color="#1f77b4")))
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Pillar history")
    st.dataframe(st.session_state.pillar_history)

elif page == "Idea Bank & Action Tracker":
    st.header("Idea Bank & Action Tracker")
    
    with st.form("new_idea"):
        idea_text = st.text_input("New improvement idea")
        owner = st.text_input("Owner (crew member)")
        submitted = st.form_submit_button("Add idea")
        if submitted and idea_text:
            st.session_state.ideas.append({
                "Idea": idea_text,
                "Owner": owner,
                "Status": "Open",
                "Date": datetime.now().strftime("%Y-%m-%d")
            })
    
    if st.session_state.ideas:
        df_ideas = pd.DataFrame(st.session_state.ideas)
        st.data_editor(df_ideas, use_container_width=True)
    else:
        st.info("No ideas yet – add your first improvement suggestion above.")

elif page == "Future PIE Generator":
    st.header("Future PIE Generator")
    st.markdown("Suggested next Process Improvement Events based on current panel performance gaps.")
    
    suggestions = [
        {"PIE": "Panel Advances & Premium Panel configuration", "Expected benefit": "Reduce pillar cycle by 1–2 shifts"},
        {"PIE": "Maintenance optimisation (on-condition vs scheduled)", "Expected benefit": "Reduce unplanned equipment downtime"},
        {"PIE": "Roster & hot-seat change optimisation", "Expected benefit": "Increase available operating time"},
        {"PIE": "Belt system uptime improvement", "Expected benefit": "Reduce external downtime to <5 %"}
    ]
    st.dataframe(pd.DataFrame(suggestions), use_container_width=True)
    
    st.success("Run the one-week diagnostic session with the senior team to select the highest-value PIEs for the next wave.")

st.sidebar.markdown("---")
st.sidebar.caption("Demonstration version – fully functional for training and proof-of-concept purposes.")
