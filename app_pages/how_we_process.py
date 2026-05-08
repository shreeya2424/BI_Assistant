# pages/how_we_process_data.py

import streamlit as st

def show_how_we_process():
#    st.set_page_config(page_title="How We Process Data", page_icon="⚙️")

    st.title("⚙️ How We Process Your Data")

    st.markdown("""
    We designed this app to make business data simple and easy to understand — even if you are not from a technical background.

    Here’s a quick look at what happens behind the scenes after you upload your CSV file.
    """)

    # STEP 1
    st.subheader("1️⃣ Uploading Your File")

    st.markdown("""
    When you upload a CSV file, the app reads your data and checks the columns available.

    Example:
    - Product names
    - Sales amount
    - Date
    - Quantity
    - Customer details
    """)

    with st.expander("See small code example"):
        st.code("""
    df = pd.read_csv(uploaded_file)
    """, language="python")

    # STEP 2
    st.subheader("2️⃣ Cleaning the Data")

    st.markdown("""
    Real-world business data is often messy.

    So the app automatically:
    - Removes empty rows
    - Fixes missing values
    - Converts dates into proper format
    - Removes duplicate entries
    - Makes numbers usable for calculations

    This helps create accurate dashboards and reports.
    """)

    with st.expander("See small code example"):
        st.code("""
    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    """, language="python")

    # STEP 3
    st.subheader("3️⃣ Calculating Business Insights")

    st.markdown("""
    After cleaning, the app calculates useful business information like:
    - Total Revenue
    - Average Sales
    - Top Selling Products
    - Number of Transactions
    - Sales Trends

    These calculations power the dashboard visuals.
    """)

    with st.expander("See small code example"):
        st.code("""
    total_revenue = df["Sales"].sum()
    avg_sale = df["Sales"].mean()
    top_product = df.groupby("Product")["Sales"].sum().idxmax()
    """, language="python")

    # STEP 4
    st.subheader("4️⃣ Creating Dashboard Visuals")

    st.markdown("""
    The processed data is then converted into:
    - Charts
    - Graphs
    - KPIs
    - Trend Analysis

    This makes business performance easier to understand at a glance.
    """)

    with st.expander("See small code example"):
        st.code("""
    st.line_chart(monthly_sales)
    st.bar_chart(product_sales)
    """, language="python")

    # STEP 5
    st.subheader("5️⃣ AI Chatbot Analysis")

    st.markdown("""
    The chatbot uses the cleaned data and calculated insights to answer questions like:
    - "Which product sold the most?"
    - "What was the highest revenue month?"
    - "Show sales trends"

    Instead of manually checking spreadsheets, users can simply ask questions in normal language.
    """)

    with st.expander("See small code example"):
        st.code("""
    response = chatbot.ask(user_question, cleaned_data)
    """, language="python")

    st.divider()

    st.success("✨ Goal of the project: Turn raw business data into simple insights")