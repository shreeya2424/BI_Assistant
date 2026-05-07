import streamlit as st
import pandas as pd

from column_mapper import ColumnMapper

# Custom Functions
from functions import (
    clean_uploaded_data,
    validate_data,
    normalize_column,
    generate_insights,
    predict_next_week
)

# Charts
from charts import (
    create_sales_trend_chart,
    create_top_products_chart,
    create_forecast_chart
)


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Shop BI Assistant",
    layout="wide"
)


# =====================================================
# LOAD COLUMN MAPPER
# =====================================================

@st.cache_resource
def load_mapper():

    return ColumnMapper()


mapper = load_mapper()


# =====================================================
# SESSION STATE
# =====================================================

if 'data' not in st.session_state:

    st.session_state.data = None

if 'data_source' not in st.session_state:

    st.session_state.data_source = None


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🏪 Shop BI Assistant")

st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=['csv']
)


# =====================================================
# FILE PROCESSING
# =====================================================

if uploaded_file is not None:

    try:

        # Try reading CSV using different encodings
        try:

            df = pd.read_csv(
                uploaded_file,
                encoding='utf-8'
            )

        except UnicodeDecodeError:

            df = pd.read_csv(
                uploaded_file,
                encoding='latin-1'
            )

        except:

            df = pd.read_csv(
                uploaded_file,
                encoding='ISO-8859-1'
            )

        st.sidebar.success(
            "✅ File uploaded successfully"
        )

        # =====================================================
        # FILE INFORMATION
        # =====================================================

        with st.sidebar.expander(
            "📊 File Information",
            expanded=True
        ):

            st.write(
                f"Rows: {df.shape[0]}"
            )

            st.write(
                f"Columns: {len(df.columns)}"
            )

            st.write(
                df.columns.tolist()
            )

        # =====================================================
        # COLUMN MAPPING
        # =====================================================

        column_mapping = (
            mapper.map_columns(df.columns)
        )

        df.rename(
            columns=column_mapping,
            inplace=True
        )

        st.sidebar.write(
            "🔄 Column Mapping Applied"
        )

        for original, mapped in column_mapping.items():

            st.sidebar.write(
                f"{original} → {mapped}"
            )

        # =====================================================
        # COLUMN NORMALIZATION
        # =====================================================

        df.columns = [

            normalize_column(col)

            for col in df.columns
        ]

        st.sidebar.write(
            "✅ Final Columns"
        )

        st.sidebar.write(
            df.columns.tolist()
        )

        # =====================================================
        # DATA VALIDATION
        # =====================================================

        errors = validate_data(df)

        if errors:

            st.sidebar.error(
                "⚠️ Validation Failed"
            )

            for error in errors:

                st.sidebar.write(
                    f"- {error}"
                )

            st.warning("""
❌ Your uploaded dataset is missing required columns.

Required Columns:
- Date
- Product
- Quantity
- Price
- Total
""")

            st.stop()

        # =====================================================
        # DATA CLEANING
        # =====================================================

        cleaned_data = clean_uploaded_data(df)

        st.session_state.data = cleaned_data

        st.session_state.data_source = (
            "Uploaded CSV"
        )

    except Exception as e:

        st.sidebar.error(
            f"❌ Error reading file: {e}"
        )

else:

    # Stop app if no file uploaded
    if st.session_state.data is None:

        st.info(
            "⬅️ Upload a CSV file from sidebar to begin"
        )

        st.stop()


# =====================================================
# LOAD DATA
# =====================================================

data = st.session_state.data


# =====================================================
# CALCULATE KPI METRICS
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
# RESULTS DICTIONARY
# =====================================================

results = {

    "metrics": {

        "total_revenue": float(total_revenue),

        "total_transactions": int(total_txns),

        "avg_sale": float(avg_txn),

        "top_product": best_product,

        "date_start": str(data["Date"].min()),

        "date_end": str(data["Date"].max())
    }
}


# =====================================================
# MAIN DASHBOARD
# =====================================================

st.title("🏪 Shop BI Assistant")

st.markdown(
    "Upload business data and generate insights"
)

st.markdown("---")


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

# Sales Trend Chart
with col1:

    sales_chart = (
        create_sales_trend_chart(data)
    )

    st.plotly_chart(
        sales_chart,
        use_container_width=True
    )

# Top Products Chart
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
# BUSINESS INSIGHTS
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
# SALES FORECAST
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