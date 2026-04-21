import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Bond inputs
face_value = 1000
coupon_rate = 0.05
years_to_maturity = 10
current_yield = 0.04

# Generate cash flows
coupon_payment = face_value * coupon_rate
cash_flows = []

for year in range(1, years_to_maturity + 1):
    if year == years_to_maturity:
        cash_flows.append(coupon_payment + face_value)
    else:
        cash_flows.append(coupon_payment)

# Calculate bond price
bond_price = 0

for year in range(1, years_to_maturity + 1):
    bond_price += cash_flows[year - 1] / (1 + current_yield) ** year

print(f'Bond Price: ${bond_price:.2f}')

# Calculate duration
duration = 0

for year in range(1, years_to_maturity + 1):
    pv_cash_flow = cash_flows[year - 1] / (1 + current_yield) ** year
    duration += (year * pv_cash_flow) / bond_price

print(f'Duration: {duration:.2f} years')

#Calculate convexity
convexity = 0
for year in range(1, years_to_maturity + 1):
    pv_cash_flow = cash_flows[year - 1] / (1 + current_yield) ** year
    convexity += pv_cash_flow * year * (year + 1)

convexity = (convexity / (bond_price * (1 + current_yield) ** 2 * 100)) * 100

print(f'Convexity: {convexity:.2f}')

# Simulate rate shocks
rate_up = current_yield + 0.01
rate_down = current_yield - 0.01

price_up = sum(cash_flows[y - 1] / (1 + rate_up) ** y for y in range(1, years_to_maturity + 1))
price_down = sum(cash_flows[y - 1] / (1 + rate_down) ** y for y in range(1, years_to_maturity +1))

change_up = ((price_up - bond_price) / bond_price) * 100
change_down = ((price_down - bond_price) / bond_price) * 100

print(f'Price if rates +1%: ${price_up:.2f} ({change_up:.2f}%)')
print(f'Price if rates -1%: ${price_down:.2f} ({change_down:.2f}%)')

# Calculate DV01 (dollar value of 1 basis point)
dv01 = (price_down - price_up) / 2
print(f'DV01: ${dv01:.2f} (price change per 1bp move)')

# Trade idea
if duration > 7 and current_yield < 0.05:
    bond_trade = 'Reduce long duration exposure'
    bond_rationale = f'Duration of {duration:.1f} years mean high rate sensitivity. A 1% rate rises loses ${abs(price_up - bond_price):.2f}. Consider shortening duration.'
elif duration > 7 and current_yield >= 0.05:
    bond_trade = 'long duration - rates likely to fall'
    bond_rationale = f'High duration ({duration:.1f} years) with elevated yields. If rates fall 1%, bond gains ${abs(price_down - bond_price):.2f}. Attractive entry point.'
else:
    bond_trade = 'Neutral duration positioning'
    bond_rationale = f'Duration of {duration:.1f} years is moderate. DV01 of ${dv01:.2f} - manageable rate risk.'

print(f'\n--- TRADE IDEA ---')
print(f'Trade: {bond_trade}')
print(f'Rationale: {bond_rationale}')
print(f'Convexity Advantage: Bond gains ${abs(price_down - bond_price):.2f} if rates fall 1% vs loses ${abs(price_up - bond_price):.2f} if rates rise 1%')

# Build plotly dashboard
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Bond Price vs Interest Rate', 'Rate Shock Analysis')
)

# Chart 1 - Price across different yields
yields_range = [i/100 for i in range(1, 11)]
prices_range = []

for y in yields_range:
    p = sum(cash_flows[yr -1] / (1 + y) ** yr for yr in range(1, years_to_maturity + 1))
    prices_range.append(p)

fig.add_trace(
    go.Scatter(
        x=[y * 100 for y in yields_range],
        y=prices_range,
        mode='lines+markers',
        line=dict(color='#185FA5', width=3),
        marker=dict(size=6),
        name='Bond Price'
    ),
    row=1, col=1
)

#Chart 2 - Rate shock bar chart
fig.add_trace(
    go.Bar(
        x=['-1% Rate Shock', 'Current Price', '+1% Rate Shock'],
        y=[price_down, bond_price, price_up],
        marker_color=['#1D9E75', '#185FA5', '#E24B4A'],
        text=[f'${price_down:.2f}', f'${bond_price:.2f}', f'${price_up:.2f}'],
        textposition='outside'
    ),
    row=1, col=2
)

fig.update_layout(
    title=dict(
        text=f'Bond Pricing Dashboard | Price: <b>${bond_price:.2f}</b> | Duration: <b>{duration:.2f}yr</b> | Convexity: <b>{convexity:.2f}</b> | DV01: <b>${dv01:.2f}</b> | Trade: <b>{bond_trade}</b>',
        font=dict(size=13)
    ),
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500
)

fig.update_xaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
fig.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')

fig.update_xaxes(title_text='Yield (%)', row=1, col=1)
fig.update_yaxes(title_text='Price ($)', row=1, col=1)
fig.update_yaxes(title_text='Price ($)', row=1, col=2)

fig.write_html('/Users/manishv/Desktop/Python_Finance_Projects/bond_dashboard.html')
print('Dashboard saved! Open bond_dashboard.html in your browser.')