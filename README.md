# Polyalpha Suite: Quantitative Prediction Market Toolkit

Polyalpha Suite is a dual-module financial dashboard designed for Polymarket participants. It combines modern portfolio theory with information-theoretic divergence scanning to identify mispriced "Laggard" markets.

---

### 1. Modules

**A. Portfolio Optimizer (Strategic)**
Uses a Mean-Variance Optimization approach to calculate the ideal allocation across multiple correlated markets.
* **Input:** Estimated Edge, Market Correlations, and Risk Aversion.
* **Output:** Precise dollar-amount bets based on your global bankroll.

**B. Divergence Pro Scanner (Tactical)**
Uses Shannon Entropy and Kullback-Leibler Divergence to spot information gaps between a "Lead" market (efficient) and a "Laggard" market (slow).

---

### 2. The Mathematics of Divergence

To identify an opportunity, the suite calculates the "Information Distance" between two related markets.

**A. Shannon Entropy ($H$)**
Measures the uncertainty or "noise" in the Lead market. If entropy is high, the market is a toss-up; if low, the outcome is nearly certain.
$$H(P) = - \sum_{i} p_i \log_2(p_i)$$

**B. KL Divergence ($D_{KL}$)**
Measures how much the Laggard distribution ($Q$) differs from the Lead distribution ($P$). This represents the "Information Gap."
$$D_{KL}(P \parallel Q) = \sum_{i} p_i \log_2 \left( \frac{p_i}{q_i} \right)$$

**C. Confidence Score**
Scales the Gap by the certainty of the Lead. The tool recommends trading only if the Lead is certain and the Gap is large.
$$\text{Confidence} = D_{KL} \times (1 - H)$$

**D. Risk-Adjusted Kelly Sizing**
The bet size is determined by a Quarter-Kelly (25%) multiplier, further reduced by the Certainty Factor $(1-H)$ to prevent over-betting on noisy signals.
$$\text{Bet} = \min(\text{Bankroll} \times f^* \times 0.25 \times (1-H), \text{Liquidity})$$

---

### 3. Essential Trading Rules

* **The 'Intuitive Link' Rule:** Only scan markets that are logically tethered (e.g., GOP Senate Control vs. GOP win in Ohio).
* **The Lead Efficiency Rule:** We assume the Lead Market is higher-volume and more efficient. If Lead Entropy is $> 0.70$, the signal is likely just noise.
* **The Liquidity Brake:** Never exceed the Recommended Bet. Buying more than the available liquidity creates Slippage, which erodes your mathematical edge.

---

### 4. Best Times to Scan (Strategy)

Information divergence is most profitable during high-velocity events where news breaks faster than traders can update every sub-market:

* **Live Events:** Political debates or election nights. The "Main" outcome moves instantly, but "Local" markets often lag by minutes.
* **Economic Releases:** When data like the CPI or Fed rates are released, look for divergence between Global indices (Lead) and niche contracts (Laggard).
* **Court Rulings:** Fast-breaking legal news hits the primary event first; secondary markets often take longer to price in the verdict.

---

### 5. Setup & Installation

1.  **Clone the repo:**
    `git clone https://github.com/yourusername/Polyalpha-Suite.git`

2.  **Install dependencies:**
    `pip install streamlit numpy pandas scipy plotly`

3.  **Run the app:**
    `streamlit run app.py`
