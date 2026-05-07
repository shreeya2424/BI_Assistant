# =========================
# pages/dashboard.py
# =========================

import streamlit as st
import pandas as pd

from functions import (
    generate_insights,
    predict_next_week
)

from charts import (
    create_sales_trend_chart,
    create_top_products_chart,
    create_forecast_chart
)


# =====================================================
# DASHBOARD PAGE
# =====================================================

def show_dashboard():

    st.title("📊 Dashboard")

    st.markdown(
        "Business analytics and forecasting"
    )

    st.markdown("---")

    # =====================================================
    # CHECK DATA
    # =====================================================

    if st.session_state.data is None:

        st.warning(
            "⚠️ Please upload data first from Home page"
        )

        return

    data = st.session_state.data

    # =====================================================
    # KPI METRICS
    # =====================================================

    total_revenue = data['Total'].sum()

    total_txns = len(data)

    avg_txn = data['Total'].mean()

    best_product = (
        data.groupby('Product')['Total']
        .sum()
        .idxmax()
    )

    # =====================================================
    # KPI SECTION
    # =====================================================

    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenue",
        f"₹{total_revenue:,.0f}"
    )

    col2.metric(
        "Transactions",
        total_txns
    )

    col3.metric(
        "Top Product",
        best_product
    )

    col4.metric(
        "Average Sale",
        f"₹{avg_txn:.0f}"
    )

    st.markdown("---")

    # =====================================================
    # SALES ANALYSIS
    # =====================================================

    st.subheader("📈 Sales Analysis")

    col1, col2 = st.columns(2)

    # Sales Trend
    with col1:

        sales_chart = (
            create_sales_trend_chart(data)
        )

        st.plotly_chart(
            sales_chart,
            use_container_width=True
        )

    # Top Products
    with col2:

        product_chart = (
            create_top_products_chart(data)
        )

        st.plotly_chart(
            product_chart,
            use_container_width=True
        )

    st.markdown("---")

    # =====================================================
    # INSIGHTS
    # =====================================================

    st.subheader("💡 Business Insights")

    insights = generate_insights(data)

    for i, insight in enumerate(insights):

        with st.expander(
            f"{i+1}. {insight['title']}",
            expanded=(i == 0)
        ):

            st.markdown(
                insight['explanation']
            )

    st.markdown("---")

    # =====================================================
    # FORECAST
    # =====================================================

    st.subheader("🔮 Sales Forecast")

    predictions, model, daily_df = (
        predict_next_week(data)
    )

    forecast_chart = create_forecast_chart(
        daily_df,
        predictions
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True
    )

    # =====================================================
    # FORECAST TABLE
    # =====================================================

    forecast_table = pd.DataFrame([

        {
            'Date': p['date'].strftime('%d %b'),

            'Day': p['day'],

            'Predicted Sales': (
                f"₹{p['predicted']:,.0f}"
            )
        }

        for p in predictions
    ])

    st.dataframe(
        forecast_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # =====================================================
    # RAW DATA
    # =====================================================

    with st.expander("📄 View Raw Data"):

        st.dataframe(
            data.head(50),
            use_container_width=True
        )