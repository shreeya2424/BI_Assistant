# =========================
# pages/home.py
# =========================

import streamlit as st
import pandas as pd

from column_mapper import ColumnMapper

from functions import (
    clean_uploaded_data,
    validate_data,
    normalize_column
)


# =====================================================
# LOAD COLUMN MAPPER
# =====================================================

@st.cache_resource
def load_mapper():

    return ColumnMapper()


mapper = load_mapper()


# =====================================================
# RESET APPLICATION STATE
# =====================================================

def reset_app_state():

    st.session_state.data = None

    st.session_state.data_source = None

    # Reset chatbot
    st.session_state.business_context = ""

    st.session_state.chat_messages = []

    st.session_state.chatbot_enabled = False


# =====================================================
# PROCESS FILE
# =====================================================

def process_uploaded_file(uploaded_file):

    # Try different encodings
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

    # =====================================================
    # FILE INFO
    # =====================================================

    with st.expander(
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

    st.subheader(
        "🔄 Column Mapping"
    )

    for original, mapped in column_mapping.items():

        st.write(
            f"{original} → {mapped}"
        )

    # =====================================================
    # NORMALIZE COLUMNS
    # =====================================================

    df.columns = [

        normalize_column(col)

        for col in df.columns
    ]

    st.subheader(
        "✅ Final Columns"
    )

    st.write(
        df.columns.tolist()
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    errors = validate_data(df)

    if errors:

        st.error(
            "⚠️ Validation Failed"
        )

        for error in errors:

            st.write(
                f"- {error}"
            )

        st.warning("""
Required Columns:
- Date
- Product
- Quantity
- Price
- Total
""")

        return None

    # =====================================================
    # CLEAN DATA
    # =====================================================

    cleaned_data = clean_uploaded_data(df)

    return cleaned_data


# =====================================================
# HOME PAGE
# =====================================================

def show_home():

    st.title("🏠 Home")

    st.markdown(
        "Upload and prepare your business dataset"
    )

    st.markdown("---")

    # =====================================================
    # EXISTING DATASET
    # =====================================================

    if st.session_state.data is not None:

        data = st.session_state.data

        st.success(
            "✅ Dataset already loaded"
        )

        col1, col2 = st.columns([1, 1])

        # =====================================================
        # REPLACE DATASET BUTTON
        # =====================================================

        with col1:

            if st.button(
                "🔄 Add New Data"
            ):

                reset_app_state()

                st.rerun()

        # =====================================================
        # DATASET INFO
        # =====================================================

        with col2:

            st.info(
                f"""
Rows: {data.shape[0]}
Columns: {data.shape[1]}
"""
            )

        # =====================================================
        # PREVIEW
        # =====================================================

        st.subheader(
            "📄 Current Cleaned Dataset"
        )

        st.dataframe(
            data.head(20),
            use_container_width=True
        )

        return

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    uploaded_file = st.file_uploader(

        "Upload CSV File",

        type=['csv']
    )

    # =====================================================
    # PROCESS FILE
    # =====================================================

    if uploaded_file is not None:

        try:

            cleaned_data = process_uploaded_file(
                uploaded_file
            )

            if cleaned_data is None:

                return

            # Save data
            st.session_state.data = (
                cleaned_data
            )

            st.session_state.data_source = (
                "Uploaded CSV"
            )

            st.success(
                "✅ Data cleaned and saved successfully"
            )

            # =====================================================
            # DATA PREVIEW
            # =====================================================

            st.subheader(
                "📄 Cleaned Data Preview"
            )

            st.dataframe(
                cleaned_data.head(20),
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"❌ Error reading file: {e}"
            )

    else:

        st.info(
            "Upload a CSV file to begin"
        )