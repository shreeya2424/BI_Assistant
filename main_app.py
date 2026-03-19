import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from column_mapper import ColumnMapper

st.set_page_config(page_title="Shop BI Assistant", layout="wide")


# ================== DATA CLEANING ==================
def clean_uploaded_data(df):
    """Clean uploaded CSV data"""
    st.subheader("📋 Data Cleaning Process")

    # Display original info
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Original Data:**")
        st.write(f"- Rows: {df.shape[0]}")
        st.write(f"- Columns: {df.shape[1]}")
        st.write(f"- Missing Values: {df.isnull().sum().sum()}")
        st.write(f"- Duplicate Rows: {df.duplicated().sum()}")

    df_cleaned = df.copy()
    df_cleaned.drop_duplicates(inplace=True)

    for col in df_cleaned.columns:
        if df_cleaned[col].dtype in ['int64', 'float64']:
            df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
        else:
            mode_value = df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else "Unknown"
            df_cleaned[col].fillna(mode_value, inplace=True)

    if 'Date' in df_cleaned.columns:
        df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')

        # remove rows with invalid or missing dates
        df_cleaned = df_cleaned.dropna(subset=['Date'])

        # standardize format
        df_cleaned['Date'] = df_cleaned['Date'].dt.strftime('%Y-%m-%d')


    with col2:
        st.write("**After Cleaning:**")
        st.write(f"- Rows: {df_cleaned.shape[0]}")
        st.write(f"- Columns: {df_cleaned.shape[1]}")
        st.write(f"- Missing Values: {df_cleaned.isnull().sum().sum()}")
        st.write(f"- Duplicate Rows: {df_cleaned.duplicated().sum()}")

    st.success("✅ Data cleaning completed successfully!")

    with st.expander("View Cleaned Data Preview"):
        st.dataframe(df_cleaned.head(20), use_container_width=True)

    st.markdown("---")
    return df_cleaned


# ================== VALIDATION ==================
def validate_data(df):
    """Validate CSV data - strict format checking"""
    errors = []
    required = ['Date', 'Product', 'Quantity', 'Price', 'Total']

    missing_cols = [col for col in required if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        errors.append(f"Found columns: {', '.join(df.columns.tolist())}")

    if df.empty:
        errors.append("CSV file is empty")

    if 'Quantity' in df.columns and (df['Quantity'] < 0).any():
        errors.append("Found negative quantities")

    if 'Price' in df.columns and (df['Price'] < 0).any():
        errors.append("Found negative prices")

    # Return errors and column mapping
    column_mapping = {col: col for col in df.columns}
    return errors, column_mapping


# ================== INSIGHTS ==================
def generate_insights(data):
    """Generate all insights with explanations"""
    insights = []

    total_revenue = data['Total'].sum()
    total_txns = len(data)
    avg_txn = total_revenue / total_txns
    days = (pd.to_datetime(data['Date']).max() - pd.to_datetime(data['Date']).min()).days + 1
    avg_daily = total_revenue / days

    insights.append({
        'title': f"Total Revenue: ₹{total_revenue:,.0f}",
        'explanation': f"""
**OVERALL PERFORMANCE**
- Period: {data['Date'].min()} to {data['Date'].max()} ({days} days)
- Total Revenue: ₹{total_revenue:,.0f}
- Average per Day: ₹{avg_daily:,.0f}
- Total Transactions: {total_txns}
- Average per Transaction: ₹{avg_txn:.0f}
"""
    })

    product_revenue = data.groupby('Product')['Total'].sum()
    best = product_revenue.idxmax()
    revenue = product_revenue[best]
    total_rev = product_revenue.sum()
    pct = (revenue / total_rev) * 100

    insights.append({
        'title': f"Top Product: {best} ({pct:.0f}% of revenue)",
        'explanation': f"""
**TOP SELLING PRODUCT: {best}**
- {best} Revenue: ₹{revenue:,.0f}
- Total Revenue: ₹{total_rev:,.0f}
- Percentage: {pct:.1f}%
"""
    })

    data_copy = data.copy()
    data_copy['DayOfWeek'] = pd.to_datetime(data_copy['Date']).dt.day_name()
    day_sales = data_copy.groupby('DayOfWeek')['Total'].sum()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_sales = day_sales.reindex(day_order)

    best_day = day_sales.idxmax()
    avg_sales = day_sales.mean()
    diff_pct = ((day_sales[best_day] - avg_sales) / avg_sales) * 100

    insights.append({
        'title': f"Best Sales Day: {best_day} ({diff_pct:+.0f}% vs average)",
        'explanation': f"""
**DAY-OF-WEEK PATTERNS**
- Best Day: {best_day}
- Weekly Average: ₹{avg_sales:,.0f}
"""
    })

    return insights


# ================== FORECASTING ==================
def predict_next_week(data):
    """Predict sales for next 7 days"""
    daily_df = data.groupby('Date')['Total'].sum().reset_index()
    daily_df['date'] = pd.to_datetime(daily_df['Date'])
    daily_df['day_num'] = range(len(daily_df))

    X = daily_df[['day_num']].values
    y = daily_df['Total'].values

    model = LinearRegression()
    model.fit(X, y)

    daily_df['DayOfWeek'] = daily_df['date'].dt.dayofweek
    day_multipliers = daily_df.groupby('DayOfWeek')['Total'].mean() / daily_df['Total'].mean()

    predictions = []
    last_day_num = daily_df['day_num'].max()
    last_date = daily_df['date'].max()

    for i in range(1, 8):
        future_day = last_day_num + i
        future_date = last_date + timedelta(days=i)
        future_dow = future_date.weekday()
        base_pred = model.predict([[future_day]])[0]
        adjusted = base_pred * day_multipliers[future_dow]
        predictions.append({
            'date': future_date,
            'day': future_date.strftime('%a'),
            'predicted': max(0, adjusted)
        })

    return predictions, model, daily_df


# ================== SIDEBAR ==================

@st.cache_resource
def load_mapper():
    return ColumnMapper()

mapper = load_mapper()

st.sidebar.title("Shop BI Assistant")
st.sidebar.markdown("---")

if 'data' not in st.session_state:
    st.session_state.data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = None

st.sidebar.subheader("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV (Date, Product, Quantity, Price, Total)", type=['csv'])

if uploaded_file is not None:
    try:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='latin-1')
        except:
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

        st.sidebar.success("✅ File uploaded!")
        with st.sidebar.expander("📊 File Info", expanded=True):
            st.write(f"**Columns Found:** {', '.join(df.columns)}")
            st.write(f"**Total Rows:** {df.shape[0]}")

        # ================== COLUMN MAPPING ==================

        column_mapping = mapper.map_columns(df.columns)

        # Rename columns using ML predictions
        df.rename(columns=column_mapping, inplace=True)

        st.sidebar.write("🔄 Column Mapping Applied:")
        for original, mapped in column_mapping.items():
            st.sidebar.write(f"{original} → {mapped}")
            
        # ================== STANDARDIZATION ==================

        def normalize_column(col):
            col = col.strip().lower()

            if "date" in col:
                return "Date"

            elif any(word in col for word in ["product", "item", "name"]):
                return "Product"

            elif any(word in col for word in ["qty", "quantity", "amount", "count", "units"]):
                return "Quantity"

            elif any(word in col for word in ["price", "rate", "cost"]):
                return "Price"

            elif any(word in col for word in ["total", "revenue", "sales"]):
                return "Total"

            return col

        df.columns = [normalize_column(col) for col in df.columns]

        st.sidebar.write("✅ Final Columns:", df.columns.tolist())

        # ================== VALIDATION ==================
        errors, _ = validate_data(df)

        if errors:
            st.sidebar.error("⚠️ Data Validation Failed:")
            for error in errors:
                st.sidebar.write(f"- {error}")
            st.sidebar.info("💡 Required columns: Date, Product, Quantity, Price, Total")
            st.warning(
                "❌ Your uploaded file is missing one or more required columns.\n"
                "Please modify your dataset to include the following columns before uploading:\n\n"
                "- **Date** (in YYYY-MM-DD format)\n"
                "- **Product** (product name or ID)\n"
                "- **Quantity** (number of units sold)\n"
                "- **Price** (per unit)\n"
                "- **Total** (total sales = Quantity × Price)\n\n"
                "💡 Tip: Even if some values are missing or inconsistent, the cleaner will handle them automatically — "
                "just make sure all these columns exist in your file."
            )
            st.stop()
        else:
            st.session_state.data = clean_uploaded_data(df)
            st.session_state.data_source = "Uploaded CSV"
            st.sidebar.success("✅ Data loaded successfully!")

    except Exception as e:
        st.sidebar.error(f"❌ Error reading file: {e}")
else:
    if st.session_state.data is None:
        st.info("⬅️ Please upload a CSV file from the sidebar to begin analysis")
        st.stop()

data = st.session_state.data

# ================== MAIN CONTENT ==================
st.title("🏪 Shop BI Assistant")
st.markdown("Analyze your sales data and get actionable insights")
st.markdown("---")

# Key Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
total_revenue = data['Total'].sum()
total_txns = len(data)
best_product = data.groupby('Product')['Total'].sum().idxmax()
avg_txn = data['Total'].mean()

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Transactions", f"{total_txns}")
col3.metric("Top Product", best_product)
col4.metric("Avg Sale", f"₹{avg_txn:.0f}")

st.markdown("---")

# Sales Analysis
st.subheader("📈 Sales Analysis")
col1, col2 = st.columns(2)

with col1:
    st.write("**Sales Over Time**")
    daily_sales = data.groupby('Date')['Total'].sum().reset_index()
    fig1 = px.line(daily_sales, x='Date', y='Total', labels={'Total': 'Revenue (₹)', 'Date': 'Date'}, template='plotly_white')
    fig1.update_traces(line_color='#1f77b4', line_width=2)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.write("**Top 5 Products**")
    top_products = data.groupby('Product')['Total'].sum().nlargest(5).reset_index()
    fig2 = px.bar(top_products, x='Product', y='Total', labels={'Total': 'Revenue (₹)', 'Product': 'Product'}, template='plotly_white')
    fig2.update_traces(marker_color='#ff7f0e')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Insights
st.subheader("💡 Key Insights & Explanations")  

insights = generate_insights(data)
for i, insight in enumerate(insights):
    with st.expander(f"{i+1}. {insight['title']}", expanded=(i == 0)):
        st.markdown(insight['explanation'])

st.markdown("---")

# Forecast
st.subheader("🔮 Sales Forecast (Next 7 Days)")
predictions, model, daily_df = predict_next_week(data)
hist_data = daily_df[['date', 'Total']].tail(14).copy()
hist_data.columns = ['Date', 'Sales']
hist_data['Type'] = 'Actual'

forecast_data = pd.DataFrame([{'Date': p['date'], 'Sales': p['predicted'], 'Type': 'Forecast'} for p in predictions])
combined = pd.concat([hist_data, forecast_data], ignore_index=True)

fig_forecast = px.line(
    combined,
    x='Date',
    y='Sales',
    color='Type',
    labels={'Sales': 'Revenue (₹)'},
    template='plotly_white',
    color_discrete_map={'Actual': '#1f77b4', 'Forecast': '#ff7f0e'}
)
st.plotly_chart(fig_forecast, use_container_width=True)

forecast_table = pd.DataFrame([
    {'Date': p['date'].strftime('%d %b'), 'Day': p['day'], 'Predicted Sales': f"₹{p['predicted']:,.0f}"}
    for p in predictions
])
st.dataframe(forecast_table, use_container_width=True, hide_index=True)

with st.expander("How We Predict (Click to expand)"):
    st.markdown(f"""
**PREDICTION METHOD: Linear Regression + Day Patterns**
- Analyzed {len(daily_df)} days of data
- Linear Regression trend: ₹{model.coef_[0]:+.0f} per day
- Adjusted by day-of-week multipliers
""")

# Raw Data
with st.expander("📄 View Raw Data"):
    st.write(f"Showing rows of {len(data)} total transactions:")
    st.dataframe(data.head(50), use_container_width=True)
