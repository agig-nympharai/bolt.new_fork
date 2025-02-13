import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="My Portfolio | Blog",
    page_icon="📝",
    layout="wide"
)

st.header("📝 Blog Posts")

# Function to create blog post
def blog_post(title, date, summary, content):
    with st.expander(f"{title} - {date}"):
        st.markdown(f"**{summary}**")
        st.markdown("---")
        st.markdown(content)

# Blog posts
blog_post(
    "Getting Started with Streamlit",
    "March 15, 2024",
    "A beginner's guide to building web apps with Streamlit",
    """
    Streamlit is an amazing framework for building data applications quickly.
    In this post, we'll explore the basics of creating interactive web applications
    using Streamlit...
    
    ### Key Points
    * Easy to learn
    * Python-based
    * Great for data applications
    
    [Read more...](https://example.com/blog1)
    """
)

blog_post(
    "Machine Learning Project Structure",
    "March 10, 2024",
    "Best practices for organizing ML projects",
    """
    Organizing machine learning projects can be challenging. Here's my approach to
    structuring ML projects for better maintainability and collaboration...
    
    ### Project Structure
    * data/
    * models/
    * notebooks/
    * src/
    
    [Read more...](https://example.com/blog2)
    """
)

# Add new blog post form
st.sidebar.header("Admin Section")
with st.sidebar.form("new_post"):
    st.write("Add New Blog Post")
    title = st.text_input("Title")
    summary = st.text_area("Summary")
    content = st.text_area("Content")
    submitted = st.form_submit_button("Post")
    
    if submitted:
        st.success("Blog post added successfully!")