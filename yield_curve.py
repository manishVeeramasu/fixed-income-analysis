from fredapi import Fred
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Connect to FRED using your API key
fred = Fred(api_key='f90652d998912491885a363ee0750235')

# Define the Treasury yields we want to pull
maturities = {
    '2Y': 'DGS2',
    '5Y': 'DGS5',
    '10Y': 'DGS10',
    '30Y': 'DGS30'
}

# Pull the last 2 years of yield data from FRED
yields = {}
for name, code in maturities.items():
    yields[name] = fred.get_series(code, observation_start='2024-01-01')

# Combine all yields into one table and clean it
df = pd.DataFrame(yields)
df = df.dropna()

# Calculate the 10Y-2Y spread over time
df['Spread'] = df['10Y'] - df['2Y']
latest_spread = df['Spread'].iloc[-1]

# Identify the regime and generate trade idea
if latest_spread > 0.5:
    regime = 'Steepening'
    trade = 'Long 2Y / Short 10Y'
    rationale = 'Steepening curve favors short end. Long 2Y captures higher carry, short 10Y hedges duration risk.'
    recession_prob = 'Low - steepening typically signals economic recovery expectations.'
elif latest_spread > 0:
    regime = 'Normal'
    trade = 'Neutral - monitor for steepening or flattening signals'
    rationale = 'Curve near normal shape. No strong directional trade.'
    recession_prob = 'Low to moderate - normal curve consistent with stable growth.'
elif latest_spread > -0.5:
    regime = 'Flattening'
    trade = 'Long 10Y / Short 2Y'
    rationale = 'Flattening signals slowing growth. Long duration outperforms as rates fall long end.'
    recession_prob = 'Moderate - flattening historically precedes inversion by 6-12 months.'
else:
    regime = 'Inverted'
    trade = 'Long 30Y Treasuries / Reduce risk assets'
    rationale = 'Inversion has preceded every US recession since 1955. Flight to safety trade.'
    recession_prob = 'High - yield curve inversion is the most reliable recession indicator historically.'

print(f'Regime: {regime}')
print(f'10Y-2Y Spread: {latest_spread:.2f}%')
print(f'Trade: {trade}')
print(f'Rationale: {rationale}')
print(f'Recession Probability Signal: {recession_prob}')

# Color the spread bars by regime
bar_colors = []
for val in df['Spread']:
    if val > 0.5:
        bar_colors.append('#1D9E75')
    elif val > 0:
        bar_colors.append('#378ADD')
    elif val > -0.5:
        bar_colors.append('#EF9F27')
    else:
        bar_colors.append('#E24B4A')

# Latest yields for curve chart
latest = df.iloc[-1][['2Y', '5Y', '10Y', '30Y']]
maturities_list = [2, 5, 10, 30]

# Build dashboard with 2 charts side by side
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('US Treasury Yield Curve — Today', '10Y–2Y Spread — Last 2 Years')
)

# Chart 1 — Yield Curve
fig.add_trace(
    go.Scatter(
        x=maturities_list,
        y=latest.values.tolist(),
        mode='lines+markers',
        line=dict(color='#185FA5', width=3),
        marker=dict(size=8, color='#185FA5'),
        fill='tozeroy',
        fillcolor='rgba(55,138,221,0.08)',
        name='Yield Curve'
    ),
    row=1, col=1
)

# Chart 2 — Spread over time
fig.add_trace(
    go.Bar(
        x=df.index,
        y=df['Spread'],
        marker_color=bar_colors,
        name='10Y-2Y Spread'
    ),
    row=1, col=2
)

# Layout styling
fig.update_layout(
    title=dict(
        text=f'Yield Curve Dashboard — Regime: <b>{regime}</b> | Trade: <b>{trade}</b> | Spread: <b>{latest_spread:.2f}%</b> | 2Y: <b>{latest["2Y"]:.2f}%</b> | 10Y: <b>{latest["10Y"]:.2f}%</b>',
        font=dict(size=14)
    ),
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#444'),
    height=500
)

fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.15)')
fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.15)', ticksuffix='%')

fig.update_xaxes(
    tickvals=maturities_list,
    ticktext=['2Y', '5Y', '10Y', '30Y'],
    row=1, col=1
)

# Save as interactive HTML file
fig.write_html('/Users/manishv/Documents/yield_curve_dashboard.html')
print(f'Dashboard saved! Open yield_curve_dashboard.html in your browser.')