import streamlit as st
import pandas as pd

st.title("Smart Business Assistant Prototype")

# File upload
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.write("### Column Names:")
        st.write(list(df.columns))

        st.write("### Preview of Data:")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")
