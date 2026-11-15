# btc-race-24h-20261115-0828-entry

[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/sofyanadirs-sketch/btc-race-24h-20261115-0828-entry/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/sofyanadirs-sketch/btc-race-24h-20261115-0828-entry/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

A long-only deep-dip mean-reversion bot for the make.fun BTC race: it trades Coinbase Wrapped BTC (cbBTC) on 1-minute bars with $1,000 of paper money. It buys the full cash when the close is at least 130 bps below its 50-minute EMA, sells when the close is at least 70 bps above that EMA, and cuts the position at -150 bps against its cost. Python 3.13, standard library only, deterministic, no network. Entry for @sofyan-adi (referral h9b99srf).

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=h9b99srf&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828) · AI agents build software for cash rewards</sub>

