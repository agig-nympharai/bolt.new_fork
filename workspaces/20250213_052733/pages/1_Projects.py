import streamlit as st

st.set_page_config(
    page_title="My Portfolio | Projects",
    page_icon="🚀",
    layout="wide"
)

st.header("🚀 Projects")

# Function to create project card
def project_card(title, description, technologies, link):
    with st.container():
        st.markdown(f"### {title}")
        st.markdown(description)
        st.markdown(f"**Technologies:** {technologies}")
        st.markdown(f"[View Project]({link})")
        st.markdown("---")

# Project 1
project_card(
    "Data Analytics Dashboard",
    "A comprehensive dashboard for visualizing business metrics and KPIs.",
    "Python, Streamlit, Pandas, Plotly",
    "https://github.com/username/project1"
)

# Project 2
project_card(
    "E-commerce Platform",
    "Full-stack e-commerce solution with payment integration.",
    "React, Django, PostgreSQL, Stripe",
    "https://github.com/username/project2"
)

# Project 3
project_card(
    "Machine Learning Model API",
    "REST API serving predictions from a trained ML model.",
    "FastAPI, scikit-learn, Docker",
    "https://github.com/username/project3"
)