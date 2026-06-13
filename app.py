import streamlit as st
import requests
import pandas as pd

# -----------------------------------
# CONFIG
# -----------------------------------
API_KEY = "a3f417b116fa4104b3c547e8ee9d32e1"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("News Filters")

countries = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp"
}

country_name = st.sidebar.selectbox(
    "Select Country",
    list(countries.keys())
)

country = countries[country_name]

category = st.sidebar.selectbox(
    "Select Topic",
    [
        "general",
        "business",
        "entertainment",
        "health",
        "science",
        "sports",
        "technology"
    ]
)

article_count = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=50,
    value=15
)

keyword = st.sidebar.text_input(
    "Search Keyword",
    placeholder="e.g. AI, Tesla, Cricket"
)

search_btn = st.sidebar.button("Fetch News")

# -----------------------------------
# FETCH NEWS FUNCTION
# -----------------------------------
@st.cache_data(ttl=300)
def get_news(country, category, page_size, keyword):
    params = {
        "apiKey": API_KEY,
        "country": country,
        "category": category,
        "pageSize": page_size
    }

    if keyword:
        params["q"] = keyword

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()

    return {
        "status": "error",
        "message": f"API Error: {response.status_code}"
    }

# -----------------------------------
# HEADER
# -----------------------------------
st.title("📰 Advanced News Dashboard")
st.markdown(
    "Filter news by country, topic, article count, and keywords."
)

# -----------------------------------
# LOAD NEWS
# -----------------------------------
if search_btn:

    with st.spinner("Fetching latest news..."):
        data = get_news(
            country,
            category,
            article_count,
            keyword
        )

    if data["status"] == "ok":

        articles = data.get("articles", [])

        st.success(f"Found {len(articles)} articles")

        if len(articles) == 0:
            st.warning("No articles found.")
        else:

            for article in articles:

                with st.container():

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        if article.get("urlToImage"):
                            st.image(
                                article["urlToImage"],
                                use_container_width=True
                            )

                    with col2:
                        st.subheader(article.get("title", "No Title"))

                        st.caption(
                            f"Source: {article['source']['name']}"
                        )

                        if article.get("publishedAt"):
                            st.write(
                                f"Published: {article['publishedAt']}"
                            )

                        if article.get("description"):
                            st.write(article["description"])

                        st.link_button(
                            "Read Full Article",
                            article["url"]
                        )

                    st.divider()

    else:
        st.error(data.get("message", "Something went wrong"))

# -----------------------------------
# OPTIONAL ANALYTICS
# -----------------------------------
st.markdown("---")
st.subheader("📊 News Analytics")

if search_btn and data["status"] == "ok":

    articles = data.get("articles", [])

    if articles:

        sources = [
            article["source"]["name"]
            for article in articles
        ]

        df = pd.DataFrame(
            sources,
            columns=["Source"]
        )

        source_counts = (
            df["Source"]
            .value_counts()
            .reset_index()
        )

        source_counts.columns = [
            "Source",
            "Count"
        ]

        st.bar_chart(
            source_counts.set_index("Source")
        )
