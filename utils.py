import numpy as np
from scipy.stats import norm


def simulate_gbm_paths(S0, r, sigma, T, steps, n_paths, seed=42):
    np.random.seed(seed)
    dt = T / steps
    Z = np.random.standard_normal((n_paths, steps))
    increments = (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
    log_paths = np.cumsum(increments, axis=1)
    log_paths = np.hstack([np.zeros((n_paths, 1)), log_paths])
    paths = S0 * np.exp(log_paths)
    t = np.linspace(0, T, steps + 1)
    return t, paths


def monte_carlo_option_price(paths, K, r, T, option_type="call"):
    S_T = paths[:, -1]
    if option_type == "call":
        payoffs = np.maximum(S_T - K, 0)
    else:
        payoffs = np.maximum(K - S_T, 0)
    disc = np.exp(-r * T)
    price = disc * np.mean(payoffs)
    se = disc * np.std(payoffs) / np.sqrt(len(payoffs))
    ci_low = price - 1.96 * se
    ci_high = price + 1.96 * se
    return price, se, ci_low, ci_high


def mc_convergence(paths, K, r, T, option_type="call", n_points=50):
    # price at increasing path counts to show convergence
    n_total = paths.shape[0]
    ns = np.unique(np.geomspace(10, n_total, n_points).astype(int))
    prices, lows, highs = [], [], []
    for n in ns:
        p, se, lo, hi = monte_carlo_option_price(paths[:n], K, r, T, option_type)
        prices.append(p)
        lows.append(lo)
        highs.append(hi)
    return ns, np.array(prices), np.array(lows), np.array(highs)


def _d1_d2(S, K, r, sigma, T):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def black_scholes_price(S, K, r, sigma, T, option_type="call"):
    d1, d2 = _d1_d2(S, K, r, sigma, T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def bs_greeks(S, K, r, sigma, T, option_type="call"):
    d1, d2 = _d1_d2(S, K, r, sigma, T)
    sign = 1 if option_type == "call" else -1

    delta = sign * norm.cdf(sign * d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega  = S * norm.pdf(d1) * np.sqrt(T) / 100      # per 1% vol move
    theta = (
        -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        - sign * r * K * np.exp(-r * T) * norm.cdf(sign * d2)
    ) / 365                                            # per calendar day
    rho = sign * K * T * np.exp(-r * T) * norm.cdf(sign * d2) / 100  # per 1% rate move

    return {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho}


def implied_vol_surface(S, r, strikes, maturities, vol_base=0.20):
    # synthetic surface — real version would invert market prices
    surface = np.zeros((len(maturities), len(strikes)))
    for i, T in enumerate(maturities):
        for j, K in enumerate(strikes):
            moneyness = np.log(K / S)
            skew  = -0.15 * moneyness
            smile =  0.10 * moneyness ** 2
            term  =  0.05 * (1 - np.exp(-T))
            surface[i, j] = vol_base + skew + smile + term
    return np.clip(surface, 0.01, 2.0)
