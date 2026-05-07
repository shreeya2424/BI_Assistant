import plotly.express as px
import pandas as pd


# =====================================================
# SALES OVER TIME CHART
# =====================================================

def create_sales_trend_chart(data):
    """
    Creates line chart for sales over time.
    """

    daily_sales = (
        data.groupby('Date')['Total']
        .sum()
        .reset_index()
    )

    fig = px.line(
        daily_sales,
        x='Date',
        y='Total',
        labels={
            'Date': 'Date',
            'Total': 'Revenue (₹)'
        },
        template='plotly_white'
    )

    fig.update_traces(
        line_width=3
    )

    return fig


# =====================================================
# TOP PRODUCTS CHART
# =====================================================

def create_top_products_chart(data, top_n=5):
    """
    Creates bar chart for top selling products.
    """

    top_products = (
        data.groupby('Product')['Total']
        .sum()
        .nlargest(top_n)
        .reset_index()
    )

    fig = px.bar(
        top_products,
        x='Product',
        y='Total',
        labels={
            'Product': 'Product',
            'Total': 'Revenue (₹)'
        },
        template='plotly_white'
    )

    return fig


# =====================================================
# FORECAST CHART
# =====================================================

def create_forecast_chart(daily_df, predictions):
    """
    Creates forecast visualization chart.
    """

    # Historical data
    historical = (
        daily_df[['date', 'Total']]
        .tail(14)
        .copy()
    )

    historical.columns = ['Date', 'Sales']

    historical['Type'] = 'Actual'

    # Forecast data
    forecast_df = pd.DataFrame([

        {
            'Date': p['date'],
            'Sales': p['predicted'],
            'Type': 'Forecast'
        }

        for p in predictions
    ])

    # Combine both
    combined = pd.concat(
        [historical, forecast_df],
        ignore_index=True
    )

    fig = px.line(
        combined,
        x='Date',
        y='Sales',
        color='Type',
        labels={
            'Sales': 'Revenue (₹)'
        },
        template='plotly_white'
    )

    return fig