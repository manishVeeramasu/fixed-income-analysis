# Fixed Income & Cross-Asset Analysis

I built 3 python projects to learn how rates, bonds, and credit markets actually work. 
Each one pulls real market data and tries to answer one question: what trade do you put on and why?

## Projects

### 1. Yield Curve Analyzer
Pulls live Treasury yield data from the Fed and tracks the shape of the yield curve over time.

It tracks the 2Y, 5Y, 10Y, and 30Y yields, calculates the 10Y-2Y spread, and figures out 
what regime we're in — steepening, flattening, normal, or inverted. From there it outputs 
a trade idea and a recession probability signal. Additionally I built an interactive Plotly dashboard to visualize it.

Current signal: Steepening at 0.55% → Long 2Y / Short 10Y

### 2. Bond Pricing & Duration Model
Models how a bond is priced and how much it moves when rates change.

This project prices the bond by discounting all future cash flows, then calculates duration, convexity, 
and DV01. It runs rate shock simulations at +100 and -100 basis points to show how 
much you gain or lose. The convexity section was the most interesting part to build, as 
it shows why bonds gain more when rates fall than they lose when rates rise.

### 3. Cross-Asset Credit Signal Engine
Tracks investment grade and high yield credit spreads and turns them into actionable signals.

It pulls ICE BofA IG and HY spread data from FRED, calculates z-scores, and classifies 
the current credit environment. It then crosses it with NASDAQ and 10Y yield data to find 
correlations and detect divergences between credit and equity markets.

The backtest result that surprised me most: when HY spreads exceed +1 standard deviation, 
the NASDAQ returned an average of +6.4% over the next 30 days with a 79% win rate across 
141 signals since 2020. Wide spreads are actually a contrarian buy signal.

## Setup

pip install fredapi pandas plotly numpy

Get a free FRED API key at https://fred.stlouisfed.org/ and swap it into each file.
