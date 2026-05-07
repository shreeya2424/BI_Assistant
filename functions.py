import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import timedelta


# =====================================================
# DATA CLEANING
# =====================================================

def clean_uploaded_data(df):

    st.subheader("📋 Data Cleaning Process")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Original Data:**")
        st.write(f"- Rows: {df.shape[0]}")
        st.write(f"- Columns: {df.shape[1]}")
        st.write(f"- Missing Values: {df.isnull().sum().sum()}")
        st.write(f"- Duplicate Rows: {df.duplicated().sum()}")

    df_cleaned = df.copy()

    # Remove duplicates
    df_cleaned.drop_duplicates(inplace=True)

    # Fill missing values
    for col in df_cleaned.columns:

        if df_cleaned[col].dtype in ['int64', 'float64']:

            df_cleaned[col].fillna(
                df_cleaned[col].mean(),
                inplace=True
            )

        else:

            mode_value = (
                df_cleaned[col].mode()[0]
                if not df_cleaned[col].mode().empty
                else "Unknown"
            )

            df_cleaned[col].fillna(
                mode_value,
                inplace=True
            )

    # Date cleaning
    if 'Date' in df_cleaned.columns:

        df_cleaned['Date'] = pd.to_datetime(
            df_cleaned['Date'],
            errors='coerce'
        )

        # Remove invalid dates
        df_cleaned = df_cleaned.dropna(
            subset=['Date']
        )

        # Standardize date format
        df_cleaned['Date'] = (
            df_cleaned['Date']
            .dt.strftime('%Y-%m-%d')
        )

    with col2:

        st.write("**After Cleaning:**")
        st.write(f"- Rows: {df_cleaned.shape[0]}")
        st.write(f"- Columns: {df_cleaned.shape[1]}")
        st.write(f"- Missing Values: {df_cleaned.isnull().sum().sum()}")
        st.write(f"- Duplicate Rows: {df_cleaned.duplicated().sum()}")

    st.success("✅ Data cleaning completed!")

    with st.expander("View Cleaned Data"):

        st.dataframe(
            df_cleaned.head(20),
            use_container_width=True
        )

    st.markdown("---")

    return df_cleaned


# =====================================================
# DATA VALIDATION
# =====================================================

def validate_data(df):

    errors = []

    required_columns = [
        'Date',
        'Product',
        'Quantity',
        'Price',
        'Total'
    ]

    # Missing columns
    missing_columns = [

        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        errors.append(
            f"Missing required columns: "
            f"{', '.join(missing_columns)}"
        )

    # Empty file
    if df.empty:
        errors.append("Uploaded file is empty")

    # Negative quantity
    if 'Quantity' in df.columns:

        if (df['Quantity'] < 0).any():

            errors.append(
                "Negative quantities found"
            )

    # Negative price
    if 'Price' in df.columns:

        if (df['Price'] < 0).any():

            errors.append(
                "Negative prices found"
            )

    return errors


# =====================================================
# COLUMN NORMALIZATION
# =====================================================

def normalize_column(col):

    col = col.strip().lower()

    if "date" in col:
        return "Date"

    elif any(word in col for word in [
        "product",
        "item",
        "name"
    ]):
        return "Product"

    elif any(word in col for word in [
        "qty",
        "quantity",
        "count",
        "units",
        "amount"
    ]):
        return "Quantity"

    elif any(word in col for word in [
        "price",
        "rate",
        "cost"
    ]):
        return "Price"

    elif any(word in col for word in [
        "sales",
        "total",
        "revenue"
    ]):
        return "Total"

    return col


# =====================================================
# INSIGHTS GENERATION
# =====================================================

def generate_insights(data):

    insights = []

    total_revenue = data['Total'].sum()

    total_transactions = len(data)

    average_sale = (
        total_revenue / total_transactions
    )

    # Total revenue insight
    insights.append({

        'title': f"Total Revenue: ₹{total_revenue:,.0f}",

        'explanation': f"""
### Overall Business Performance

- Total Revenue: ₹{total_revenue:,.0f}
- Transactions: {total_transactions}
- Average Sale: ₹{average_sale:.0f}
"""
    })

    # Top product insight
    product_sales = (
        data.groupby('Product')['Total']
        .sum()
    )

    best_product = product_sales.idxmax()

    best_product_sales = (
        product_sales.max()
    )

    percentage = (
        best_product_sales
        / product_sales.sum()
    ) * 100

    insights.append({

        'title': (
            f"Top Product: {best_product}"
        ),

        'explanation': f"""
### Best Performing Product

- Product: {best_product}
- Revenue: ₹{best_product_sales:,.0f}
- Revenue Share: {percentage:.1f}%
"""
    })

    return insights


# =====================================================
# FORECASTING
# =====================================================

def predict_next_week(data):

    daily_df = (
        data.groupby('Date')['Total']
        .sum()
        .reset_index()
    )

    daily_df['date'] = pd.to_datetime(
        daily_df['Date']
    )

    daily_df['day_num'] = range(
        len(daily_df)
    )

    X = daily_df[['day_num']].values

    y = daily_df['Total'].values

    # Train model
    model = LinearRegression()

    model.fit(X, y)

    # Day patterns
    daily_df['DayOfWeek'] = (
        daily_df['date'].dt.dayofweek
    )

    day_multipliers = (
        daily_df.groupby('DayOfWeek')['Total']
        .mean()
        / daily_df['Total'].mean()
    )

    predictions = []

    last_day_num = daily_df['day_num'].max()

    last_date = daily_df['date'].max()

    # Predict next 7 days
    for i in range(1, 8):

        future_day = last_day_num + i

        future_date = (
            last_date + timedelta(days=i)
        )

        future_dow = (
            future_date.weekday()
        )

        base_prediction = (
            model.predict([[future_day]])[0]
        )

        adjusted_prediction = (
            base_prediction
            * day_multipliers[future_dow]
        )

        predictions.append({

            'date': future_date,

            'day': future_date.strftime('%a'),

            'predicted': max(
                0,
                adjusted_prediction
            )
        })

    return predictions, model, daily_df