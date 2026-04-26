import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import (
    simulate_gbm_paths,
    monte_carlo_option_price,
    black_scholes_price,
    bs_greeks,
    mc_convergence,
    implied_vol_surface,
)

st.set_page_config(page_title="MC Options Pricer", layout="wide", initial_sidebar_state="expanded")

# colours
BG      = "#0e1117"
SURFACE = "#161b27"
CARD    = "#1e2537"
ACCENT  = "#00d4ff"
ACCENT2 = "#ff6b6b"
GREEN   = "#00f5a0"
MUTED   = "#b0b8c8"   # brighter than before
TEXT    = "#ffffff"   # pure white for max contrast

PLOTLY_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(color=TEXT, family="IBM Plex Mono, monospace", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="#2e3a50", zerolinecolor="#2e3a50", tickfont=dict(size=12, color=TEXT), title_font=dict(size=13, color=TEXT)),
    yaxis=dict(gridcolor="#2e3a50", zerolinecolor="#2e3a50", tickfont=dict(size=12, color=TEXT), title_font=dict(size=13, color=TEXT)),
)

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@300;500;700&display=swap');
  html, body, [class*="css"] {{
      background-color: {BG}; color: {TEXT}; font-family: 'Space Grotesk', sans-serif; font-size: 15px;
  }}
  .block-container {{ padding: 1.5rem 2rem; max-width: 1600px; }}

  /* sidebar — brighter labels and bigger text */
  section[data-testid="stSidebar"] {{ background: {SURFACE}; border-right: 1px solid #2e3a50; }}
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] div {{ color: {TEXT} !important; font-size: 14px !important; }}
  section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
  section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {{ color: {MUTED} !important; font-size: 13px !important; }}

  /* metric cards */
  .metric-card {{
      background: {CARD}; border: 1px solid #2e3a50; border-radius: 12px;
      padding: 1rem 1.2rem; text-align: center;
  }}
  .metric-label {{ color: {MUTED}; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }}
  .metric-value {{ color: {ACCENT}; font-size: 1.6rem; font-family: 'IBM Plex Mono', monospace; font-weight: 600; }}
  .metric-sub   {{ color: {MUTED}; font-size: 0.8rem; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }}

  /* section headers */
  .section-header {{
      font-size: 0.8rem; letter-spacing: 0.15em; text-transform: uppercase;
      color: {ACCENT}; border-bottom: 1px solid #2e3a50; padding-bottom: 0.4rem; margin: 1.5rem 0 1rem;
  }}

  /* greek pills */
  .greek-pill {{
      display: inline-block; background: #252d3d; border-radius: 8px;
      padding: 0.6rem 1rem; margin: 0.3rem; font-family: 'IBM Plex Mono', monospace;
  }}
  .greek-name {{ color: {MUTED}; font-size: 0.78rem; letter-spacing: 0.1em; }}
  .greek-val  {{ color: {TEXT}; font-size: 1.15rem; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


# sidebar
with st.sidebar:
    st.markdown(f"<div style='color:{ACCENT};font-family:IBM Plex Mono;font-size:1.1rem;font-weight:600;letter-spacing:0.1em;margin-bottom:1rem'>⬡ MC PRICER</div>", unsafe_allow_html=True)

    st.markdown("**Underlying**")
    S0    = st.slider("Spot Price (S₀)",          50.0, 200.0, 100.0, 1.0)
    K     = st.slider("Strike Price (K)",          50.0, 200.0, 100.0, 1.0)

    st.markdown("**Model Parameters**")
    sigma = st.slider("Volatility (σ)",            0.05,  1.00,  0.20, 0.01, format="%.2f")
    r     = st.slider("Risk-free Rate (r)",        0.00,  0.15,  0.05, 0.005, format="%.3f")
    T     = st.slider("Time to Maturity (T, yrs)", 0.1,   3.0,   1.0,  0.05)

    st.markdown("**Simulation**")
    n_paths = st.select_slider("Paths", options=[500, 1000, 2000, 5000, 10000], value=2000)
    steps   = st.slider("Steps", 50, 504, 252, 1)
    seed    = st.number_input("Random Seed", 0, 9999, 42, 1)

    option_type = st.radio("Option Type", ["call", "put"], horizontal=True)
    run_btn = st.button("▶  RUN SIMULATION", use_container_width=True, type="primary")


if "results" not in st.session_state:
    st.session_state.results = None

if run_btn or st.session_state.results is None:
    with st.spinner("Simulating paths…"):
        t, paths = simulate_gbm_paths(S0, r, sigma, T, steps, n_paths, seed=int(seed))

    mc_price, mc_se, mc_lo, mc_hi = monte_carlo_option_price(paths, K, r, T, option_type)
    bs_price = black_scholes_price(S0, K, r, sigma, T, option_type)
    greeks   = bs_greeks(S0, K, r, sigma, T, option_type)
    ns, conv_prices, conv_lo, conv_hi = mc_convergence(paths, K, r, T, option_type)

    strikes    = np.linspace(S0 * 0.6, S0 * 1.4, 30)
    maturities = np.linspace(0.1, 3.0, 20)
    vol_surf   = implied_vol_surface(S0, r, strikes, maturities)

    st.session_state.results = dict(
        t=t, paths=paths,
        mc_price=mc_price, mc_se=mc_se, mc_lo=mc_lo, mc_hi=mc_hi,
        bs_price=bs_price, greeks=greeks,
        ns=ns, conv_prices=conv_prices, conv_lo=conv_lo, conv_hi=conv_hi,
        strikes=strikes, maturities=maturities, vol_surf=vol_surf,
        S0=S0, K=K, r=r, sigma=sigma, T=T, option_type=option_type, n_paths=n_paths,
    )

res = st.session_state.results

# header
st.markdown(
    f"<h1 style='font-family:IBM Plex Mono;font-size:1.4rem;font-weight:600;"
    f"letter-spacing:0.08em;color:{TEXT};margin-bottom:0.2rem'>"
    f"Monte Carlo Options Pricing Dashboard</h1>"
    f"<div style='color:{MUTED};font-size:0.8rem;margin-bottom:1.2rem'>"
    f"S₀={res['S0']} · K={res['K']} · σ={res['sigma']} · r={res['r']} · T={res['T']}yr · "
    f"{res['n_paths']:,} paths · {res['option_type'].upper()}</div>",
    unsafe_allow_html=True,
)

# price cards
diff      = res["mc_price"] - res["bs_price"]
diff_sign = "+" if diff >= 0 else ""

c1, c2, c3, c4 = st.columns(4)
for col, label, val, sub in [
    (c1, "MC Price",  f"{res['mc_price']:.4f}", f"±{1.96*res['mc_se']:.4f} (95% CI)"),
    (c2, "BS Price",  f"{res['bs_price']:.4f}", "Analytical benchmark"),
    (c3, "MC − BS",   f"{diff_sign}{diff:.4f}", "Pricing error"),
    (c4, "Std Error", f"{res['mc_se']:.5f}",    f"{res['n_paths']:,} paths"),
]:
    col.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{val}</div>"
        f"<div class='metric-sub'>{sub}</div>"
        f"</div>", unsafe_allow_html=True,
    )

# greeks
st.markdown("<div class='section-header'>Option Greeks (Black-Scholes)</div>", unsafe_allow_html=True)

greek_meta = {
    "Delta": ("Δ", "Price sensitivity to S"),
    "Gamma": ("Γ", "Delta sensitivity to S"),
    "Vega":  ("ν", "Price / 1% vol move"),
    "Theta": ("Θ", "Price / calendar day"),
    "Rho":   ("ρ", "Price / 1% rate move"),
}
for col, (name, (sym, desc)) in zip(st.columns(5), greek_meta.items()):
    val = res["greeks"][name]
    col.markdown(
        f"<div class='greek-pill'>"
        f"<div class='greek-name'>{sym} {name}</div>"
        f"<div class='greek-val'>{val:+.4f}</div>"
        f"<div style='color:{MUTED};font-size:0.62rem;margin-top:2px'>{desc}</div>"
        f"</div>", unsafe_allow_html=True,
    )

# GBM paths + payoff distribution
st.markdown("<div class='section-header'>Simulation</div>", unsafe_allow_html=True)
r1c1, r1c2 = st.columns([3, 2])

with r1c1:
    n_show = min(80, res["n_paths"])
    fig_paths = go.Figure()

    for i in range(n_show):
        itm = res["paths"][i, -1] >= res["K"] if res["option_type"] == "call" else res["paths"][i, -1] <= res["K"]
        color = "rgba(0,212,255,0.12)" if itm else "rgba(255,107,107,0.10)"
        fig_paths.add_trace(go.Scatter(
            x=res["t"], y=res["paths"][i],
            mode="lines", line=dict(width=0.7, color=color),
            showlegend=False, hoverinfo="skip",
        ))

    fig_paths.add_hline(y=res["K"], line_dash="dash", line_color=ACCENT2, line_width=1.5,
                        annotation_text=f"K = {res['K']}", annotation_font_color=ACCENT2)

    mean_path = np.mean(res["paths"], axis=0)
    fig_paths.add_trace(go.Scatter(
        x=res["t"], y=mean_path, mode="lines", name="Mean path",
        line=dict(color=GREEN, width=2),
    ))

    fig_paths.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"GBM Paths ({n_show} shown, {res['n_paths']:,} simulated)", font_size=13),
        xaxis_title="Time (years)", yaxis_title="Stock Price",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
        height=380,
    )
    st.plotly_chart(fig_paths, use_container_width=True)

with r1c2:
    S_T = res["paths"][:, -1]
    payoffs = np.maximum(S_T - res["K"], 0) if res["option_type"] == "call" else np.maximum(res["K"] - S_T, 0)

    otm_frac = np.mean(payoffs == 0) * 100
    itm_frac = 100 - otm_frac

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=payoffs[payoffs == 0], name=f"OTM ({otm_frac:.1f}%)",
        marker_color=ACCENT2, opacity=0.7, xbins=dict(start=0, end=1, size=1),
    ))
    itm_payoffs = payoffs[payoffs > 0]
    if len(itm_payoffs):
        fig_hist.add_trace(go.Histogram(
            x=itm_payoffs, name=f"ITM ({itm_frac:.1f}%)",
            marker_color=ACCENT, opacity=0.75, nbinsx=60,
        ))
    fig_hist.add_vline(x=np.mean(payoffs), line_dash="dot", line_color=GREEN, line_width=2,
                       annotation_text=f"E[payoff]={np.mean(payoffs):.2f}", annotation_font_color=GREEN)

    fig_hist.update_layout(
        **PLOTLY_LAYOUT, barmode="overlay",
        title=dict(text="Payoff Distribution at Expiry", font_size=13),
        xaxis_title="Payoff", yaxis_title="Count",
        legend=dict(x=0.6, y=0.99, bgcolor="rgba(0,0,0,0)"),
        height=380,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# convergence + greeks bar
st.markdown("<div class='section-header'>Analytics</div>", unsafe_allow_html=True)
r2c1, r2c2 = st.columns([3, 2])

with r2c1:
    fig_conv = go.Figure()

    # shaded CI band
    fig_conv.add_trace(go.Scatter(
        x=np.concatenate([res["ns"], res["ns"][::-1]]),
        y=np.concatenate([res["conv_hi"], res["conv_lo"][::-1]]),
        fill="toself", fillcolor="rgba(0,212,255,0.1)",
        line=dict(color="rgba(0,0,0,0)"), name="95% CI", hoverinfo="skip",
    ))
    fig_conv.add_trace(go.Scatter(
        x=res["ns"], y=res["conv_prices"], mode="lines", name="MC Price",
        line=dict(color=ACCENT, width=2),
    ))
    fig_conv.add_hline(y=res["bs_price"], line_dash="dash", line_color=GREEN, line_width=1.5,
                       annotation_text=f"BS = {res['bs_price']:.4f}", annotation_font_color=GREEN)

    fig_conv.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Price Convergence vs. Number of Paths", font_size=13),
        xaxis_title="Number of Paths", yaxis_title="Option Price",
        xaxis_type="log", legend=dict(x=0.6, y=0.99, bgcolor="rgba(0,0,0,0)"),
        height=360,
    )
    st.plotly_chart(fig_conv, use_container_width=True)

with r2c2:
    greeks_df = pd.DataFrame({"Greek": list(res["greeks"].keys()), "Value": list(res["greeks"].values())})
    colors = [GREEN if v >= 0 else ACCENT2 for v in greeks_df["Value"]]

    fig_greeks = go.Figure(go.Bar(
        x=greeks_df["Greek"], y=greeks_df["Value"],
        marker_color=colors,
        text=[f"{v:+.4f}" for v in greeks_df["Value"]],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=11),
    ))
    fig_greeks.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Greeks (normalised units)", font_size=13),
        yaxis_title="Value", height=360, showlegend=False,
    )
    st.plotly_chart(fig_greeks, use_container_width=True)

# vol surface
st.markdown("<div class='section-header'>Implied Volatility Surface</div>", unsafe_allow_html=True)

fig_surf = go.Figure(go.Surface(
    z=res["vol_surf"] * 100, x=res["strikes"], y=res["maturities"],
    colorscale=[[0.0, "#0a1628"], [0.2, "#003d6b"], [0.4, "#0070a8"],
                [0.6, ACCENT], [0.8, "#00f5a0"], [1.0, "#ffffff"]],
    contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="#fff", project_z=True)),
    opacity=0.9,
    colorbar=dict(title="IV (%)", tickfont=dict(color=TEXT, family="IBM Plex Mono"), thickness=12),
))

# mark where current params sit on the surface
fig_surf.add_trace(go.Scatter3d(
    x=[res["K"]], y=[res["T"]], z=[res["sigma"] * 100],
    mode="markers+text", marker=dict(size=8, color=ACCENT2, symbol="diamond"),
    text=["Current"], textfont=dict(color=ACCENT2), name="Current params",
))

fig_surf.update_layout(
    paper_bgcolor=SURFACE, font=dict(color=TEXT, family="IBM Plex Mono", size=13),
    scene=dict(
        xaxis=dict(title="Strike",        gridcolor="#252d3d", backgroundcolor=SURFACE),
        yaxis=dict(title="Maturity (yrs)", gridcolor="#252d3d", backgroundcolor=SURFACE),
        zaxis=dict(title="IV (%)",         gridcolor="#252d3d", backgroundcolor=SURFACE),
        bgcolor=SURFACE,
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    title=dict(text="Implied Volatility Surface (synthetic skew + term structure)", font_size=13),
    height=500, legend=dict(bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_surf, use_container_width=True)

# delta heatmap across spot × vol space
st.markdown("<div class='section-header'>Delta Sensitivity Heatmap  (S × σ)</div>", unsafe_allow_html=True)

spot_range  = np.linspace(S0 * 0.6, S0 * 1.4, 40)
sigma_range = np.linspace(0.05, 0.80, 40)
delta_grid  = np.zeros((len(sigma_range), len(spot_range)))

for i, sv in enumerate(sigma_range):
    for j, sp in enumerate(spot_range):
        delta_grid[i, j] = bs_greeks(sp, res["K"], res["r"], sv, res["T"], res["option_type"])["Delta"]

fig_heat = go.Figure(go.Heatmap(
    z=delta_grid, x=np.round(spot_range, 1), y=np.round(sigma_range, 2),
    colorscale=[[0.0, ACCENT2], [0.5, "#1a2540"], [1.0, GREEN]],
    colorbar=dict(title="Δ", tickfont=dict(color=TEXT, family="IBM Plex Mono"), thickness=12),
    zsmooth="best",
))

# crosshair at current S0 and sigma
fig_heat.add_shape(type="line", x0=S0, x1=S0, y0=sigma_range[0], y1=sigma_range[-1],
                   line=dict(color=ACCENT, width=1.5, dash="dot"))
fig_heat.add_shape(type="line", x0=spot_range[0], x1=spot_range[-1], y0=sigma, y1=sigma,
                   line=dict(color=ACCENT, width=1.5, dash="dot"))

fig_heat.update_layout(
    **PLOTLY_LAYOUT, xaxis_title="Spot Price", yaxis_title="Volatility (σ)", height=380,
)
st.plotly_chart(fig_heat, use_container_width=True)

# footer
st.markdown(
    f"<div style='color:{MUTED};font-size:0.68rem;font-family:IBM Plex Mono;text-align:center;"
    f"border-top:1px solid #252d3d;padding-top:0.8rem;margin-top:1rem'>"
    f"Black-Scholes · GBM · Monte Carlo · {res['n_paths']:,} paths · seed {int(seed)}"
    f"</div>",
    unsafe_allow_html=True,
)