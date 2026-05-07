import streamlit as st
import pandas as pd

from column_mapper import ColumnMapper


from chatbot.chat_engine import ChatEngine

st.set_page_config(page_title="Shop BI Assistant", layout="wide")

# Functions
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
# LOAD ML COLUMN MAPPER
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

        # Read uploaded file
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

        # File info
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
        # VALIDATION
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

            st.stop()

        # =====================================================
        # CLEANING
        # =====================================================

        cleaned_data = clean_uploaded_data(df)

        st.session_state.data = cleaned_data

        st.session_state.data_source = (
            "Uploaded CSV"
        )

    except Exception as e:

        st.sidebar.error(
            f"❌ Error: {e}"
        )

else:

    if st.session_state.data is None:

        st.info(
            "⬅️ Upload a CSV file to begin"
        )

        st.stop()


# =====================================================
# MAIN DASHBOARD
# =====================================================

data = st.session_state.data

st.title("🏪 Shop BI Assistant")

st.markdown(
    "Upload business data and generate insights"
)

st.markdown("---")


# =====================================================
# KPI METRICS
# =====================================================

st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_revenue = data['Total'].sum()

transactions = len(data)

top_product = (
    data.groupby('Product')['Total']
    .sum()
    .idxmax()
)

average_sale = data['Total'].mean()

col1.metric(
    "Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Transactions",
    transactions
)

col3.metric(
    "Top Product",
    top_product
)

col4.metric(
    "Average Sale",
    f"₹{average_sale:.0f}"
)

st.markdown("---")


# =====================================================
# SALES ANALYSIS
# =====================================================

st.subheader("📈 Sales Analysis")

col1, col2 = st.columns(2)

with col1:

    sales_chart = (
        create_sales_trend_chart(data)
    )

    st.plotly_chart(
        sales_chart,
        use_container_width=True
    )

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


# Forecast
st.subheader("🔮 Sales Forecast (Next 7 Days)")
predictions, model, daily_df = predict_next_week(data)

results = {
    "metrics": {
        "total_revenue": float(total_revenue),
        "total_transactions": int(total_txns),
        "avg_sale": float(avg_txn),
        "top_product": best_product,
        "date_start": str(data["Date"].min()),
        "date_end": str(data["Date"].max())
    },
    "insights": insights,
    "forecast": predictions
}


if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = ChatEngine()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
hist_data = daily_df[['date', 'Total']].tail(14).copy()
hist_data.columns = ['Date', 'Sales']
hist_data['Type'] = 'Actual'


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

# Forecast table
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


st.markdown("---")
st.subheader("💬 Ask Questions About Your Data")

# Show chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_question = st.chat_input("Ask about revenue, products, trends, dates...")

if user_question:
    # Store user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    # Get assistant response (STRUCTURED ENGINE ONLY)
    assistant_reply = st.session_state.chat_engine.answer_question(
        question=user_question,
        results=results,
        data=data
    )

    # Store assistant response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

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