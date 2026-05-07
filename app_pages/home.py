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
# HOME PAGE
# =====================================================

def show_home():

    st.title("🏠 Home")

    st.markdown(
        "Upload and prepare your business dataset"
    )

    st.markdown("---")

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=['csv']
    )

    # =====================================================
    # FILE PROCESSING
    # =====================================================

    if uploaded_file is not None:

        try:

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

            st.success(
                "✅ File uploaded successfully"
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
            # COLUMN NORMALIZATION
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

                return

            # =====================================================
            # DATA CLEANING
            # =====================================================

            cleaned_data = clean_uploaded_data(df)

            st.session_state.data = cleaned_data

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