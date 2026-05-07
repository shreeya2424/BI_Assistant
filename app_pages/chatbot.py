# =========================
# pages/chatbot.py
# =========================

import streamlit as st
import pandas as pd
import requests
import json


# =====================================================
# OPENROUTER CONFIG
# =====================================================

API_KEY = "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"

OPENROUTER_API_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

SELECTED_MODEL = (
    "nvidia/nemotron-3-super-120b-a12b:free"
)

MODEL_LABEL = (
    "NVIDIA Nemotron 3 Super 120B"
)

MAX_ROWS_FOR_CONTEXT = 200


# =====================================================
# SESSION STATE
# =====================================================

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "business_context" not in st.session_state:
    st.session_state.business_context = ""

if "chatbot_enabled" not in st.session_state:
    st.session_state.chatbot_enabled = False


# =====================================================
# BUILD DATASET CONTEXT
# =====================================================

def build_dataset_context(data):

    preview = (
        data.head(MAX_ROWS_FOR_CONTEXT)
        .to_csv(index=False)
    )

    shape_info = (
        f"Dataset Shape: "
        f"{data.shape[0]} rows x "
        f"{data.shape[1]} columns\n\n"
    )

    columns_info = (
        "Columns:\n"
        + "\n".join(data.columns.tolist())
        + "\n\n"
    )

    dtypes_info = (
        "Column Types:\n"
        + data.dtypes.to_string()
        + "\n\n"
    )

    return (
        shape_info
        + columns_info
        + dtypes_info
        + "Dataset Preview:\n"
        + preview
    )


# =====================================================
# SYSTEM PROMPT
# =====================================================

def build_system_prompt(data, business_context):

    dataset_context = build_dataset_context(data)

    prompt = f"""
You are an advanced business intelligence assistant.

The user has uploaded business data.

Your job:
- Analyze business performance
- Answer questions about sales, revenue, products, trends, forecasting
- Give useful business recommendations
- Explain insights clearly
- Use business context when answering

BUSINESS CONTEXT:
{business_context}

DATASET CONTEXT:
{dataset_context}

Rules:
- Be accurate
- Be concise but useful
- Use the uploaded dataset
- If data is insufficient, clearly say so
- Give actionable business insights
"""

    return prompt


# =====================================================
# OPENROUTER API CALL
# =====================================================

def call_openrouter(messages, system_prompt):

    headers = {

        "Authorization": f"Bearer {API_KEY}",

        "Content-Type": "application/json",

        "HTTP-Referer": "http://localhost:8501",

        "X-Title": "Shop BI Assistant"
    }

    payload = {

        "model": SELECTED_MODEL,

        "messages": [
            {
                "role": "system",
                "content": system_prompt
            }
        ] + messages,

        "temperature": 0.3,

        "max_tokens": 1200
    }

    response = requests.post(

        OPENROUTER_API_URL,

        headers=headers,

        json=payload
    )

    return response


# =====================================================
# CHATBOT PAGE
# =====================================================

def show_chatbot():

    st.title("🤖 AI Business Assistant")

    st.markdown(
        "Chat with your business data"
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
    # BUSINESS CONTEXT INPUT
    # =====================================================

    st.subheader("🏢 Business Context")

    st.markdown("""
Describe the business so the AI can give
better and more relevant answers.

Examples:
- We are a grocery store chain
- We sell electronics online
- We are a seasonal fashion business
- Our target audience is college students
""")

    business_context = st.text_area(

        "Enter business context",

        value=st.session_state.business_context,

        height=150,

        placeholder=(
            "Example: We are a bakery business "
            "with 3 branches in Pune..."
        )
    )

    # =====================================================
    # LOAD CHATBOT BUTTON
    # =====================================================

    if st.button("🚀 Load AI Assistant"):

        if business_context.strip() == "":

            st.warning(
                "Please enter business context first"
            )

            return

        st.session_state.business_context = (
            business_context
        )

        st.session_state.chatbot_enabled = True

        st.success(
            "✅ AI Assistant Loaded"
        )

    st.markdown("---")

    # =====================================================
    # CHATBOT
    # =====================================================

    if not st.session_state.chatbot_enabled:

        st.info(
            "Enter business context and "
            "click 'Load AI Assistant'"
        )

        return

    # =====================================================
    # DATASET INFO
    # =====================================================

    st.caption(
        f"""
Dataset:
{data.shape[0]} rows × {data.shape[1]} columns
"""
    )

    st.caption(
        f"Model: {MODEL_LABEL}"
    )

    st.markdown("---")

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    for msg in st.session_state.chat_messages:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # =====================================================
    # CHAT INPUT
    # =====================================================

    user_prompt = st.chat_input(
        "Ask about your business data..."
    )

    if user_prompt:

        # Store user message
        st.session_state.chat_messages.append({

            "role": "user",

            "content": user_prompt
        })

        with st.chat_message("user"):

            st.markdown(user_prompt)

        # =====================================================
        # GENERATE RESPONSE
        # =====================================================

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing business data..."
            ):

                try:

                    system_prompt = (
                        build_system_prompt(
                            data,
                            st.session_state.business_context
                        )
                    )

                    response = call_openrouter(

                        st.session_state.chat_messages,

                        system_prompt
                    )

                    if response.status_code != 200:

                        st.error(
                            f"API Error: "
                            f"{response.status_code}"
                        )

                        return

                    result = response.json()

                    assistant_reply = result[
                        "choices"
                    ][0]["message"]["content"]

                    st.markdown(
                        assistant_reply
                    )

                    # Save assistant message
                    st.session_state.chat_messages.append({

                        "role": "assistant",

                        "content": assistant_reply
                    })

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )