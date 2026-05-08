# pages/discover_more.py

import streamlit as st
import requests
from datetime import datetime

# ---------------- PAGE HEADER ---------------- #

def show_discover():
    st.title("📰 Discover More")
    st.markdown(
        "Stay updated with the latest business, startup, finance, and AI news."
    )

    st.divider()

    # ---------------- API CONFIG ---------------- #

    API_KEY = "543a109185f241e0b928e6a56e39ce54"

    # Example using NewsAPI
    API_URL = (
        f"https://newsapi.org/v2/top-headlines?"
        #f"country=in&"
        f"category=business&"
        f"language=en&"
        f"pageSize=10&"
        f"apiKey={API_KEY}"
    )

    # ---------------- FETCH NEWS ---------------- #

    @st.cache_data(ttl=1800)
    def get_news():
        try:
            response = requests.get(API_URL)

            if response.status_code == 200:
                data = response.json()

                if data["status"] == "ok":
                    return data["articles"]

            return []

        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return []


    articles = get_news()

    # ---------------- DISPLAY NEWS ---------------- #

    if not articles:
        st.warning("No news available right now.")
    else:

        for idx, article in enumerate(articles[:10]):

            title = article.get("title", "No Title")
            description = article.get("description", "No description available.")
            image = article.get("urlToImage")
            news_url = article.get("url")
            source = article.get("source", {}).get("name", "Unknown")
            published = article.get("publishedAt", "")

            # Format date
            try:
                published = datetime.strptime(
                    published,
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%d %b %Y • %I:%M %p")
            except:
                published = "Unknown Date"

            # ---------------- NEWS CARD ---------------- #

            with st.container():

                st.markdown(
                    """
                    <div style="
                        background-color:#111827;
                        padding:20px;
                        border-radius:18px;
                        margin-bottom:25px;
                        border:1px solid #1f2937;
                    ">
                    """,
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns([1, 2])

                with col1:
                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        st.image(
                            "https://via.placeholder.com/400x250?text=No+Image",
                            use_container_width=True
                        )

                with col2:

                    st.markdown(
                        f"""
                        <h3 style="margin-bottom:10px;">
                            {title}
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )

                    st.caption(f"🕒 {published}   |   🏢 {source}")

                    st.write(description)

                    st.link_button(
                        "Read Full Article ↗",
                        news_url,
                        use_container_width=False
                    )

                st.markdown("</div>", unsafe_allow_html=True)