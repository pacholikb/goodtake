import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.title("GL Pricing Calculator")

st.sidebar.header("Take Rate Configurations")

# Input projected gross revenue
months = 36
gross_revenue = st.sidebar.number_input("Monthly Gross Revenue", min_value=0, value=6000)
gross_revenue = [gross_revenue]*months

# Static take rate
with st.sidebar.expander("Scenario #1"):
    static_take_rate = st.number_input("Static Take Rate (%)", min_value=0, max_value=100, value=20)

# Take rate configurations
with st.sidebar.expander("Scenario #2"):
    stepped_take_rates = st.text_area("Take Rates for each period.", value="30,20,15", key="stepped_take_rates")
    take_rate_periods = st.text_area("Periods for each take rate.", value="3,12", key="take_rate_periods")

# Take rate configurations for Scenario 3
with st.sidebar.expander("Scenario #3"):
    stepped_take_rates_2 = st.text_area("Take Rates for each period.", value="35,25,15", key="stepped_take_rates_2")
    take_rate_periods_2 = st.text_area("Periods for each take rate.", value="3,12", key="take_rate_periods_2")

# Parsing input values
stepped_take_rates = list(map(float, stepped_take_rates.split(',')))
take_rate_periods = list(map(int, take_rate_periods.split(',')))

# Parsing input values for Scenario 3
stepped_take_rates_2 = list(map(float, stepped_take_rates_2.split(',')))
take_rate_periods_2 = list(map(int, take_rate_periods_2.split(',')))

# Add remaining periods to take_rate_periods
remaining_periods = months - sum(take_rate_periods)
take_rate_periods.append(remaining_periods)

# Add remaining periods to take_rate_periods for Scenario 3
remaining_periods_2 = months - sum(take_rate_periods_2)
take_rate_periods_2.append(remaining_periods_2)

# Generate take rate for each month
def generate_stepped_take_rate(take_rates, periods, months):
    take_rate = []
    period_cumsum = np.cumsum(periods)
    for month in range(1, months+1):
        for idx, period in enumerate(period_cumsum):
            if month <= period:
                take_rate.append(take_rates[idx])
                break
    return take_rate

stepped_take_rate = generate_stepped_take_rate(stepped_take_rates, take_rate_periods, months)
stepped_take_rate_2 = generate_stepped_take_rate(stepped_take_rates_2, take_rate_periods_2, months) # Scenario 3

# Data Preparation
data = {
    "Month": list(range(1, months+1)),
    "Gross Revenue": gross_revenue,
    "Static Take Rate (%)": [static_take_rate] * months,
    "Stepped Take Rate (%)": stepped_take_rate,
    "Stepped Take Rate #2 (%)": stepped_take_rate_2, # Scenario 3
}

df = pd.DataFrame(data)
df["Net Revenue (Static)"] = df["Gross Revenue"] * (df["Static Take Rate (%)"] / 100)
df["Net Revenue (Stepped)"] = df["Gross Revenue"] * (df["Stepped Take Rate (%)"] / 100)
df["Net Revenue (Stepped #2)"] = df["Gross Revenue"] * (df["Stepped Take Rate #2 (%)"] / 100) # Scenario 3

# Plotly Graphs
tab1, tab2 = st.tabs(["Area", "Bar"])

with tab1:
    fig2 = go.Figure()

    # Cumulative Area Chart for Net Revenue Comparison
    fig2.add_trace(go.Scatter(
        x=df["Month"],
        y=df["Net Revenue (Static)"].cumsum(),
        fill='tozeroy',
        name='Scenario #1',
        marker_color='#008e82'
    ))
    fig2.add_trace(go.Scatter(
        x=df["Month"],
        y=df["Net Revenue (Stepped)"].cumsum(),
        fill='tozeroy',
        name='Scenario #2',
        marker_color='black'
    ))
    fig2.add_trace(go.Scatter(
        x=df["Month"],
        y=df["Net Revenue (Stepped #2)"].cumsum(),
        fill='tozeroy',
        name='Scenario #3',
        marker_color='#d3d3d3'
    ))

    fig2.update_layout(
        title='Cumulative Net Revenue Comparison',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Cumulative Net Revenue',
            titlefont_size=16,
            tickfont_size=12,
        ),
        showlegend=True
    )

    st.plotly_chart(fig2)

with tab2:
    fig = go.Figure()

    # Grouped Bar Chart for Net Revenue Comparison
    fig.add_trace(go.Bar(
        x=df["Month"],
        y=df["Net Revenue (Static)"],
        name='Scenario #1 - (20%)',
        marker_color='#008e82'
    ))
    fig.add_trace(go.Bar(
        x=df["Month"],
        y=df["Net Revenue (Stepped)"],
        name='Scenario #2 - (30%,20%,10%)',
        marker_color='black'
    ))
    fig.add_trace(go.Bar(
        x=df["Month"],
        y=df["Net Revenue (Stepped #2)"],
        name='Scenario #3 - (35%,25%,15%)',
        marker_color='#ff7f0e' # Different color for Scenario 3
    ))

    fig.update_layout(
        barmode='group',
        title='Net Revenue Comparison',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Net Revenue',
            titlefont_size=16,
            tickfont_size=12,
        ),
        showlegend=True
    )

    st.plotly_chart(fig)

# Summary Table
summary_data = {
    "": ["Net Revenue", "3 Months", "6 Months", "12 Months", "24 Months", "36 Months"],
    "Scenario 1": ["", 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 3]["Net Revenue (Static)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 6]["Net Revenue (Static)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 12]["Net Revenue (Static)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 24]["Net Revenue (Static)"]))),
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 36]["Net Revenue (Static)"])))],
    "Scenario 2": ["", 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 3]["Net Revenue (Stepped)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 6]["Net Revenue (Stepped)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 12]["Net Revenue (Stepped)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 24]["Net Revenue (Stepped)"]))),
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 36]["Net Revenue (Stepped)"])))],
    "Scenario 3": ["", 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 3]["Net Revenue (Stepped #2)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 6]["Net Revenue (Stepped #2)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 12]["Net Revenue (Stepped #2)"]))), 
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 24]["Net Revenue (Stepped #2)"]))),
                   "${:,.2f}".format(round(sum(df[df["Month"] <= 36]["Net Revenue (Stepped #2)"])))],
}
summary_df = pd.DataFrame(summary_data)

# Remove index
summary_df.set_index('', inplace=True)

st.dataframe(summary_df)

