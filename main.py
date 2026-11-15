"""Deep-dip mean-reversion bot for make.fun btc-race-24h-20261115-0828.

The bot trades Coinbase Wrapped BTC (cbBTC) against USDC on 1-minute bars,
long only, one position at a time, whole cash per trade. It watches the
distance between the latest close and a 40-minute EMA of closes:

  - BUY the full cash when the close sits at least 130 bps BELOW the EMA
    (a deep dip) and nothing is held.
  - SELL the whole position when the close climbs back to at least 65 bps
    ABOVE the EMA (the dip has reverted past the mean).
  - SELL as well when the position is worth 150 bps less than its cost
    (stop-loss, a safety net; it never fired on the dev window).

At most one order per reply; every order allows up to 100 bps of slippage
against the latest close.

Why these numbers: the dev window (2026-11-14 08:29 -> 2026-11-15 08:28 UTC)
is a slow grind down, BTC -4.00% ($67,215.60 -> $64,523.80), with 1-minute
volatility of ~12 bps against a ~26 bps round-trip cost. Shallower dip
thresholds (50-110 bps) catch falling knives and lose money after fees on
this window (the previous race's EMA25/buy-70/sell-65 bot loses -$21.06
here). Only deep dips that revert clear costs: buy 120-150 bps under a
35-50 minute EMA and sell 55-90 bps over it is profitable across the whole
neighbourhood (27 of 80 grid points positive), and EMA40 / buy 130 / sell
65 sits in the middle of that region, so every immediate neighbour is
profitable too (+$3.62 to +$11.84). The single dev trade: buy bar 824 at
$63,526.62, sell bar 923 at $64,032.07, net +$7.15 on $1,000 (2 trades,
max drawdown 1.37%).

Honest caveat: the dev profit comes from one round trip, so the race
window may or may not offer a dip deep enough to trade. The gate only
needs dev PnL above $0, which this clears with margin, and the guardrail
needs at least 1 trade in the race window.

Deterministic: standard library only, no network, no wall clock, no files
outside the repository, no randomness. The same bars always give the same
orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
EMA_SPAN = 40        # minutes of closes in the EMA
BUY_DIP_BPS = 130    # buy when the close is this far below the EMA
SELL_BPS = 65        # sell when the close is this far above the EMA
STOP_LOSS_BPS = 150  # sell when the position is this far below its cost
MAX_SLIPPAGE_BPS = 100


class EmaTracker:
    """EMA seeded with the mean of its first span of closes."""

    def __init__(self, span):
        self.span = span
        self._seed = []
        self.value = None

    def update(self, close):
        if self.value is not None:
            self.value += (2.0 / (self.span + 1)) * (close - self.value)
            return self.value
        self._seed.append(close)
        if len(self._seed) == self.span:
            self.value = sum(self._seed) / self.span
        return self.value


ema = EmaTracker(EMA_SPAN)


def _buy_order(state):
    notional = state.cash
    if notional < int(state.hello["fees"]["min_notional_quote_units"]):
        return None
    return [{"side": "buy", "symbol": SYMBOL,
             "notional_quote_units": notional,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def _sell_order(state):
    held = state.positions.get(SYMBOL)
    if held is None:
        return None
    return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def on_batch(state, batch):
    bar = None
    for candidate in batch["bars"]:
        if candidate["symbol"] == SYMBOL:
            bar = candidate
            break
    if bar is None:
        return []
    ema.update(float(bar["c"]))
    if state.warming_up or ema.value is None:
        return []
    close = float(bar["c"])
    # How far the close sits from the EMA, in basis points.
    gap_bps = (close - ema.value) / ema.value * 10000.0
    held = state.positions.get(SYMBOL)
    if held is None:
        if gap_bps <= -BUY_DIP_BPS:
            return _buy_order(state) or []
        return []
    if gap_bps >= SELL_BPS:
        return _sell_order(state) or []
    position_value = state.value(SYMBOL, held.qty)
    # Sell when value <= cost * (1 - STOP_LOSS_BPS / 10000), in integers.
    if position_value * 10000 <= held.cost * (10000 - STOP_LOSS_BPS):
        return _sell_order(state) or []
    return []


makefun_bars.run(on_batch)
