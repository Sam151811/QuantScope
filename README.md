# QuantScope

Streamlit dashboard for pricing European options via Monte Carlo simulation. Compares results against Black-Scholes, visualises GBM paths, Greeks, payoff distributions, convergence with confidence intervals, a 3D implied vol surface and a delta heatmap. Supports up to 10,000 simulated paths with live parameter controls.

---

## Features

- **Monte Carlo pricing** — simulate up to 10,000 GBM paths and price European calls or puts
- **Black-Scholes benchmark** — compare MC price against the analytical solution in real time
- **Greeks** — delta, gamma, vega, theta, and rho with normalised units
- **Convergence plot** — see the MC price narrow toward BS as path count increases, with 95% CI band
- **Payoff distribution** — histogram splitting ITM vs OTM paths at expiry
- **3D implied vol surface** — synthetic skew and term structure across strike and maturity space
- **Delta heatmap** — delta across the full spot x volatility grid with crosshairs at current params
- **Live controls** — sliders for spot, strike, volatility, rate, maturity, path count, and seed

## Project Structure

```
quantscope/
├── app.py        # Streamlit app and all chart logic
├── utils.py      # GBM simulation, BS pricer, Greeks, MC engine
└── README.md
```

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/yourname/quantscope.git
cd quantscope
```

**2. Install dependencies**
```bash
pip install streamlit plotly scipy numpy pandas
```

**3. Run the app**
```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

> On Windows, if `streamlit` is not recognised, use `python -m streamlit run app.py` instead.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Spot Price | 100 | Current underlying price |
| Strike Price | 100 | Option strike |
| Volatility | 0.20 | Annualised vol |
| Risk-free Rate | 0.05 | Continuously compounded rate |
| Time to Maturity | 1.0 yr | Time until expiry |
| Paths | 2000 | Number of MC paths |
| Steps | 252 | Time steps per path (daily = 252) |

## Notes

- The implied vol surface is synthetic and uses a parametric skew and term structure model. A production version would invert observed market prices to extract implied vols.
- All Greeks are computed analytically via Black-Scholes. Vega is per 1% vol move, theta per calendar day, rho per 1% rate move.

## Dependencies

- [Streamlit](https://streamlit.io)
- [Plotly](https://plotly.com/python)
- [NumPy](https://numpy.org)
- [SciPy](https://scipy.org)
- [Pandas](https://pandas.pydata.org)
