import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import entropy

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Polyalpha Suite", layout="wide")

# --- 2. GLOBAL SIDEBAR ---
st.sidebar.header("Global Control")
bankroll = st.sidebar.number_input("Total Bankroll ($)", 100, 1000000, 10000, step=100)

def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

st.sidebar.divider()
st.sidebar.button("Clear All Inputs", on_click=reset_all, use_container_width=True)
st.sidebar.caption("Clears all market names, sliders, and calculations in both tabs.")

# --- 3. HELPER FUNCTIONS ---

def create_dynamic_gauge(label, value, max_val):
    """Minimal dark-themed gauges"""
    is_entropy = "Entropy" in label
    
    if is_entropy:
        color = "#00cc96" if value < 0.4 else "#f39c12" if value < 0.7 else "#ef553b"
    else:
        threshold = max_val * 0.3
        color = "#ef553b" if value < threshold else "#00cc96"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': label, 'font': {'size': 18, 'color': 'white'}},
        number = {'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': 'gray'},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)", 
            'borderwidth': 1,
            'bordercolor': "gray",
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=240, 
        margin=dict(l=30, r=30, t=50, b=20)
    )
    return fig

# --- 4. MAIN NAVIGATION ---
tab1, tab2 = st.tabs(["Optimal Allocation", "Divergence Scanner"])

# --- TAB 1: PORTFOLIO OPTIMIZER ---
with tab1:
    st.title("Portfolio Optimizer")
    
    with st.expander("Optimizer Settings", expanded=True):
        c1, c2 = st.columns(2)
        num_markets = c1.number_input("Number of Markets", 2, 10, 3)
        risk_penalty = c2.slider("Risk Aversion", 0.0, 1.0, 0.1)

    st.header("Portfolio Inputs")
    col_name, col_edge, col_corr = st.columns([1, 1, 2])
    market_names, market_edges = [], []

    with col_name:
        st.subheader("1. Markets")
        for i in range(num_markets):
            n = st.text_input(f"Market {i+1}", placeholder=f"Event {i+1}", key=f"name_{i}")
            market_names.append(n if n else f"M{i+1}")

    with col_edge:
        st.subheader("2. Your Edge")
        for i in range(num_markets):
            e_val = st.slider(f"Edge: {market_names[i]}", -0.50, 0.50, 0.00, 0.01, key=f"edge_{i}")
            market_edges.append(e_val)

    with col_corr:
        st.subheader("3. Correlations")
        corr_matrix = np.eye(num_markets)
        pairs = [(i, j) for i in range(num_markets) for j in range(i + 1, num_markets)]
        sub_cols = st.columns(3)
        for idx, (i, j) in enumerate(pairs):
            with sub_cols[idx % 3]:
                c_val = st.slider(f"{market_names[i]}/{market_names[j]}", -1.0, 1.0, 0.0, 0.1, key=f"corr_{i}_{j}")
                corr_matrix[i, j] = corr_matrix[j, i] = c_val

    # Optimization Engine
    edges = np.array(market_edges)
    portfolio = np.array([1/num_markets] * num_markets)
    if np.any(edges != 0):
        for k in range(100):
            gradient = edges - (risk_penalty * np.dot(corr_matrix, portfolio))
            portfolio = (1 - (2/(k+2))) * portfolio + (2/(k+2)) * (np.eye(num_markets)[np.argmax(gradient)])

    st.divider()
    res_col, graph_col = st.columns([1, 1.2])
    with res_col:
        st.subheader("Allocation Summary")
        results_df = pd.DataFrame({
            "Market": market_names, 
            "Allocation": (portfolio * 100).round(2), 
            "Bet ($)": (portfolio * bankroll).round(2)
        })
        st.table(results_df.style.format({"Bet ($)": "${:,.2f}", "Allocation": "{:.2f}%"}))

    with graph_col:
        r_val = list(results_df["Allocation"]) + [results_df["Allocation"][0]]
        t_val = list(results_df["Market"]) + [results_df["Market"][0]]
        fig = go.Figure(data=[go.Scatterpolar(
            r=r_val, 
            theta=t_val, 
            fill='toself', 
            line_color='#00cc96',
            fillcolor='rgba(0, 204, 150, 0.1)'
        )])
        fig.update_layout(
            title={'text': "Portfolio Concentration Radar", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'color': 'white'}},
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100], 
                    tickfont={'color': '#00cc96'},
                    gridcolor='rgba(255,255,255,0.05)' # Faint dark grid
                ),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont={'color': 'white'})
            ),
            showlegend=False, 
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: DIVERGENCE SCANNER ---
with tab2:
    st.header("Divergence Scanner")
    
    with st.expander("Manual Market Inputs", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            lead_n = st.text_input("Lead Market Name", placeholder="e.g., GOP Senate", key="l_name")
            p1 = st.slider("Lead Price (Probability)", 0.01, 0.99, 0.50, 0.01)
        with col2:
            lag_n = st.text_input("Laggard Market Name", placeholder="e.g., PA Senate", key="g_name")
            p2 = st.slider("Laggard Price (Probability)", 0.01, 0.99, 0.50, 0.01)
            liq_lag = st.number_input("Laggard Liquidity ($)", 0, 1000000, 1000, step=100)

    # Math Logic
    h_lead = entropy([p1, 1-p1], base=2)
    kl_div = entropy([p1, 1-p1], [p2, 1-p2], base=2)
    conf = kl_div * (1 - h_lead)
    
    # Kelly Sizing Logic
    edge = p1 - p2
    if edge > 0:
        odds = (1 - p2) / p2
        kelly_f = edge / odds
        raw_kelly_bet = kelly_f * bankroll * 0.25 * (1 - h_lead)
        rec_bet = min(raw_kelly_bet, liq_lag)
    else:
        raw_kelly_bet = 0
        rec_bet = 0

    # UI Gauges
    st.divider()
    g1, g2, g3 = st.columns(3)
    g1.plotly_chart(create_dynamic_gauge("Lead Entropy (Noise)", h_lead, 1.0), use_container_width=True)
    g2.plotly_chart(create_dynamic_gauge("KL-Gap (Divergence)", kl_div, 0.5), use_container_width=True)
    g3.plotly_chart(create_dynamic_gauge("Confidence Score", conf, 0.2), use_container_width=True)

    # Verdict
    st.divider()
    v1, v2 = st.columns(2)
    with v1:
        st.subheader("Analysis")
        if conf > 0.04:
            st.success(f"Opportunity: {lead_n} shows high divergence.")
        else:
            st.info("Markets are effectively in sync.")
            
    with v2:
        st.subheader("Action Plan")
        if rec_bet > 0:
            st.metric("Recommended Bet", f"${rec_bet:,.2f}")
            st.caption(f"Risk Note: This bet uses a 25% Fractional Kelly multiplier, further reduced by a { (1-h_lead)*100 :.1f}% Certainty Factor.")
            
            if raw_kelly_bet > liq_lag:
                st.error(f"Slippage Warning: Optimal bet is ${raw_kelly_bet:,.2f}, but liquidity is only ${liq_lag:,.2f}.")
        else:
            st.write("Hold. No trade recommended.")

    # --- TRADING RULES & LIQUIDITY GUIDE ---
    st.divider()
    with st.expander("📜 Essential Trading Rules & Liquidity Guide"):
        st.markdown(f"""
        ### 1. How to find Laggard Liquidity
        To get the correct **Liquidity ($)** value for this tool:
        1. Open the **{lag_n if lag_n else 'Laggard'}** market on Polymarket.
        2. Look at the **Order Book** (usually on the right or bottom).
        3. Find the **'Asks'** (the SELL orders for YES).
        4. Look at the **Depth** at the best price. 
           * *Example:* If there are 1,000 shares at \$0.52, your liquidity is **$520**.
        
        

        ### 2. The 'Intuitive Link' Rule
        Only scan markets that move on the same information (e.g., GOP Senate vs. GOP House). Unrelated markets will show "False Positive" gaps.

        ### 3. The Lead Efficiency Rule
        If **Lead Entropy** is Red (> 0.7), the Lead is just guessing. Even a large price gap is likely meaningless noise.

        ### 4. Slippage Protection
        If the **Slippage Warning** appears, it means your theoretical "edge" is larger than the market can handle. Do not exceed the **Recommended Bet**, or you will become the one moving the market price!
        """)
