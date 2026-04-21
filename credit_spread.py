from fredapi import Fred
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Connect to FRED
fred = Fred(api_key='f90652d998912491885a363ee0750235')

# Pull credit spread data
# ICE BofA Investment Grade spread
# ICE BofA High Yield spread
ig_spread = fred.get_series('BAMLC0A0CM', observation_start='2020-01-01')
hy_spread = fred.get_series('BAMLH0A0HYM2', observation_start='2020-01-01')

# Combine into one table and clean
df = pd.DataFrame({'IG': ig_spread, 'HY': hy_spread})
df = df.dropna()

# Calculate the HY-IG ratio (risk appetite indicator)
df['HY_IG_Ratio'] = df['HY'] / df['IG']
df['Spread'] = df['HY'] - df['IG']
latest_spread = df['Spread'].iloc[-1]

# Get latest value
latest_ig = df['IG'].iloc[-1]
latest_hy = df['HY'].iloc[-1]
latest_ratio = df['HY_IG_Ratio'].iloc[-1]

# Historical averages 
avg_ig = df['IG'].mean()
avg_hy = df['HY'].mean()

# Identify current environment
if latest_ig < avg_ig and latest_hy < avg_hy:
    environment = 'Risk-On - spreads tight, markets calm'
elif latest_ig > avg_ig and latest_hy > avg_hy:
    environment = 'Risk-Off - spreads wide, markets stressed'
else: 
    environment = 'Mixed signals - monitor closely'

print(f'Latest IG Spread: {latest_ig:.2f} bps')
print(f'Latest HY Spread: {latest_hy:.2f} bps')
print(f'HY/IG Ratio: {latest_ratio:.2f}x')
print(f'Environment: {environment}')

# Calculate z-scores
ig_zscore = (latest_ig - avg_ig) / df['IG'].std()
hy_zscore = (latest_hy - avg_hy) / df['HY'].std()
spread_zscore = (latest_spread - df['Spread'].mean()) / df['Spread'].std()

print(f'IG z-score: {ig_zscore:.2f}')
print(f'HY z-score: {hy_zscore:.2f}')
print(f'Spread Z-Score: {spread_zscore:.2f}')

# Pull cross-asset data
spy = fred.get_series('NASDAQCOM', observation_start='2020-01-01')
treasury_10y = fred.get_series('DGS10', observation_start='2020-01-01')

# Align all data to same dates
cross = pd.DataFrame({
    'IG': df['IG'],
    'HY': df['HY'],
    'equity': spy,
    '10Y': treasury_10y
}).dropna()

# Calculate correlations
ig_spy_corr = cross['IG'].corr(cross['equity'])
hy_spy_corr = cross['HY'].corr(cross['equity'])
hy_10y_corr = cross['HY'].corr(cross['10Y'])

print(f'\n--- CROSS-ASSET CORRELATIONS ---')
print(f'HY Spreads vs S&P 500: {hy_spy_corr:.2f}')
print(f'IG Spreads vs S&P 500: {ig_spy_corr:.2f}')
print(f'HY Spreads vs 10Y Yield: {hy_10y_corr:.2f}')

# Backtest - what happens 30 days after signal
cross['HY_zscore'] = (cross['HY'] - cross['HY'].mean()) / cross['HY'].std()
cross['SPY_fwd30'] = cross['equity'].pct_change(30).shift(-30) * 100

risk_on_signals = cross[cross['HY_zscore'] < -1.0]['SPY_fwd30'].dropna()
neutral_signals = cross[(cross['HY_zscore'] >= -1.0) & (cross['HY_zscore'] <= 1.0)]['SPY_fwd30'].dropna()
risk_off_signals = cross[cross['HY_zscore'] > 1.0]['SPY_fwd30'].dropna()

risk_on = risk_on_signals.mean()
neutral = neutral_signals.mean()
risk_off = risk_off_signals.mean()

risk_on_winrate = (risk_on_signals > 0).sum() / len(risk_on_signals) * 100
risk_on_worst = risk_on_signals.min()
risk_on_count = len(risk_on_signals)

risk_off_winrate = (risk_off_signals > 0).sum() / len(risk_off_signals) * 100
risk_off_worst = risk_off_signals.min()
risk_off_count = len(risk_off_signals)

print(f'\n--- BACKTEST: NASDAQ RETURNS 30 DAYS AFTER SIGNAL ---')
print(f'When HY spreads tight (Risk-On signal):')
print(f'  Avg Return: {risk_on:.1f}% | Win Rate: {risk_on_winrate:.0f}% | Worst: {risk_on_worst:.1f}% | Signals: {risk_on_count}')
print(f'When HY spreads neutral:')
print(f'  Avg Return: {neutral:.1f}%')
print(f'When HY spreads wide (Risk-Off signal):')
print(f'  Avg Return: {risk_off:.1f}% | Win Rate: {risk_off_winrate:.0f}% | Worst: {risk_off_worst:.1f}% | Signals: {risk_off_count}')

# Key insight
print(f'\n--- KEY INSIGHT ---')
print(f'When HY spreads exceed +1.0σ, NASDAQ returns averaged {risk_off:.1f}% over the next 30 days.')
print(f'Win rate: {risk_off_winrate:.0f}% across {risk_off_count} signals - consistent with mean reversion in risk premia.')
print(f'Implication: Wide credit spreads are a contrarian buy signal for equities.')

# Detect credit/equity divergence
latest_equity = cross['equity'].iloc[-1]
prev_equity = cross['equity'].iloc[20]
equity_change = ((latest_equity - prev_equity) / prev_equity) * 100

latest_hy_recent = cross['HY'].iloc[-1]
prev_hy_recent = cross['HY'].iloc[-20]
hy_change = latest_hy_recent - prev_hy_recent

if hy_change > 0.1 and equity_change > 0:
    divergence = 'DIVERGENCE DETECTED: Credit stress not priced into equities'
    divergence_trade = 'Long equities / Short HY credit as hedge'
elif hy_change > 0.1 and equity_change < 0:
    divergence = 'Credit and equities both signaling stress - risk-off confirmed'
    divergence_trade = 'Long IG / Short HY - reduce equotuy exposure'
else:
    divergence = 'No divergence - credit and equities aligned'
    divergence_trade = 'No divergence trade required'

print(f'\n--- DIVERGENCE SIGNAL ---')
print(f'HY Spread Change(20 days): {hy_change:.2f}%')
print(f'Equity Change (20 days): {equity_change:.1f}%')
print(f'Signal: {divergence}')
print(f'Trade: {divergence_trade}')

# Generate signal and trade idea
if hy_zscore > 1.5:
    signal = 'Risk-Off'
    confidence = 'High'
    trade = 'Long IG Credit / Short HY Credit'
    rationale = f'HY spreads at +{hy_zscore:.1f}σ -historically mean reverts. Favor quality.'
elif hy_zscore > 0.5:
    signal = 'Caution'
    confidence = 'Medium'
    trade = 'Reduce HY exposure / Add IG'
    rationale = f'HY spreads elevated at +{hy_zscore:.1f}σ - watch for further widening.'
elif hy_zscore < 1.0:
    signal = 'Risk-On'
    confidence = 'Medium'
    trade = 'Long HY Credit / Reduce cash'
    rationale = f'HY spreads tight at {hy_zscore:.1f}σ - risk appetite strong, carry trade favored'
else: 
    signal = 'Neutral'
    confidence = 'Low'
    trade = 'Hold current positioning'
    rationale = f'Spreads near historical average - no strong directional signal.'

print(f'\n--- SIGNAL ENGINE ---')
print(f'Signal: {signal}')
print(f'Confidence: {confidence}')
print(f'Trade: {trade}')
print(f'Rationale: {rationale}')

# Build plotly dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'IG vs HY Credit Spreads Since 2020',
        'HY/IG Ratio - Risk Appetite Indicator',
        'Cross-Asset: NASDAQ vs HY Spread',
        'Backtest: NASDAQ Returns After Signal'
    ),
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)

# Chart 1 - IG and HY spreads over time
fig.add_trace(
    go.Scatter(
        x=df.index, y=df['IG'],
        mode='lines', name='IG Spread',
        line=dict(color='#185FA5', width=2)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=df.index, y=df['HY'],
        mode='lines', name='HY Spread',
        line=dict(color='#E24B4A', width=2)
    ),
    row=1, col=1
)

# Chart 2 - HY/IG ratio
fig.add_trace(
    go.Scatter(
        x=df.index, y=df['HY_IG_Ratio'],
        mode='lines', name='HY/IG Ratio',
        line=dict(color='#EF9F27', width=2),
        fill='tozeroy',
        fillcolor='rgba(239, 159, 39, 0.1)'
    ),
    row=1, col=2
)

# Chart 3 - NASDAQ vs HY spread
fig.add_trace(
    go.Scatter(
        x=cross.index, y=cross['equity'],
        mode='lines', name='NASDAQ',
        line=dict(color='#1D9E75', width=2)
    ),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(
        x=cross.index, y=cross['HY'],
        mode='lines', name='HY Spread (overlay)',
        line=dict(color='#E24B4A', width=1.5, dash='dot'),
        yaxis='y3'
    ),
    row=2, col=1
)

# Chart 4 - Backtest bar chart
fig.add_trace(
    go.Bar(
        x=['Risk-On (tight)', 'Neutral', 'Risk-Off (wide)'],
        y=[risk_on, neutral, risk_off],
        marker_color=['#E24B4A', '#EF9F27', '#1D9E75'],
        text=[f'{risk_on:.1f}%', f'{neutral:.1f}%', f'{risk_off:.1f}%'],
        textposition='outside',
        name='Fwd 30D Return'
    ),
    row=2, col=2
)

fig.update_layout(
    title=dict(
        text=f'Cross-Asset Signal Engine | Signal: <b>{signal}</b> | Trade: <b>{trade}</b> | HY Z-score: <b>{hy_zscore:.2f}σ</b> | Environment: <b>{environment}</b>',
        font=dict(size=12)
    ),
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=800
)

fig.update_xaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
fig.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')

fig.write_html('/Users/manishv/Desktop/Python_Finance_Projects/credit_spread_dashboard.html')
print('Dashboard saved! Open credit_spread_dashboard.html in your browser.')