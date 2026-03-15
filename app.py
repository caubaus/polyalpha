import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

# --- 1. RESET LOGIC ---
def reset_callback():
    for key in st.session_state.keys():
        if any(key.startswith(prefix) for prefix in ["name_", "edge_", "corr_"]):
            if "name" in key: st.session_state[key] = ""
            elif "edge" in key: st.session_state[key] = 0.00
            elif "corr" in key: st.session_state[key] = 0.0

# --- 2. SIDEBAR ---
st.sidebar.header("⚙️ Strategy Settings")
num_markets = st.sidebar.number_input("Number of Markets", 2, 10, 3)
bankroll = st.sidebar.number_input("Total Bankroll ($)", 100, 1000000, 10000)
risk_penalty = st.sidebar.slider("Risk Aversion", 0.0, 1.0, 0.1)
st.sidebar.button("🗑️ Clear All Inputs", on_click=reset_callback, use_container_width=True)

st.title("Portfolio Optimizer")

# --- 3. THE INTERACTIVE GRID ---
col_name, col_edge, col_corr = st.columns([1, 1, 2])

market_names = []
market_edges = []

with col_name:
    st.subheader("1. Markets")
    st.caption("Event Names")
    for i in range(num_markets):
        n = st.text_input(f"Market {i+1}", placeholder=f"Event {i+1}", key=f"name_{i}")
        market_names.append(n if n else f"M{i+1}")

with col_edge:
    st.subheader("2. Your Edge")
    st.caption("Expected Profit %")
    for i in range(num_markets):
        e_val = st.slider(f"Edge: {market_names[i]}", -0.50, 0.50, 0.00, 0.01, key=f"edge_{i}")
        market_edges.append(e_val)

with col_corr:
    st.subheader("3. Correlations (-1 to 1)")
    st.caption("How markets move together")
    corr_matrix = np.eye(num_markets)
    
    pairs = []
    for i in range(num_markets):
        for j in range(i + 1, num_markets):
            pairs.append((i, j))
    
    sub_cols = st.columns(2 if num_markets < 5 else 3)
    
    for idx, (i, j) in enumerate(pairs):
        with sub_cols[idx % len(sub_cols)]:
            c_val = st.slider(f"{market_names[i]} / {market_names[j]}", -1.0, 1.0, 0.0, 0.1, key=f"corr_{i}_{j}")
            corr_matrix[i, j] = c_val
            corr_matrix[j, i] = c_val

# --- 4. OPTIMIZATION ENGINE ---
edges = np.array(market_edges)
portfolio = np.array([1/num_markets] * num_markets)

if np.any(edges != 0):
    for k in range(100):
        gradient = edges - (risk_penalty * np.dot(corr_matrix, portfolio))
        best_market_index = np.argmax(gradient)
        gamma = 2 / (k + 2)
        target = np.zeros(num_markets)
        target[best_market_index] = 1.0
        portfolio = (1 - gamma) * portfolio + gamma * target

# --- 5. VISUAL OUTPUTS ---
st.divider()
res_col, graph_col = st.columns([1, 1.2])

with res_col:
    st.subheader("Optimal Allocation")
    results_df = pd.DataFrame({
        "Market": market_names,
        "Allocation": (portfolio * 100).round(2),
        "Bet ($)": (portfolio * bankroll).round(2)
    })
    st.table(results_df.style.format({"Bet ($)": "${:,.2f}", "Allocation": "{:.2f}%"}))

with graph_col:
    st.subheader("Allocation Radar")
    radar_r = list(results_df["Allocation"])
    radar_theta = list(results_df["Market"])
    radar_r.append(radar_r[0])
    radar_theta.append(radar_theta[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=radar_r, theta=radar_theta, fill='toself', line_color='#008080'))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                tickfont=dict(color="#90EE90", size=10) 
            ),
            bgcolor="rgba(0,0,0,0)"
        ), 
        showlegend=False, 
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
