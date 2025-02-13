import streamlit as st

st.set_page_config(
    page_title="My Portfolio | CV",
    page_icon="👨‍💻",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stHeader {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.header("👨‍💻 Curriculum Vitae")

# Professional Summary
st.subheader("Professional Summary")
st.write("""
    Experienced professional with a strong background in software development and 
    data science. Passionate about creating efficient solutions and learning new technologies.
""")

# Experience
st.subheader("Work Experience")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Senior Developer | Tech Corp")
    st.markdown("* Led development of cloud-based solutions")
    st.markdown("* Managed team of 5 developers")
    st.markdown("* Implemented CI/CD pipelines")

with col2:
    st.markdown("2020 - Present")

# Education
st.subheader("Education")
st.markdown("#### Master of Computer Science")
st.markdown("University of Technology | 2018-2020")

# Skills
st.subheader("Skills")
cols = st.columns(3)

with cols[0]:
    st.markdown("**Programming Languages**")
    st.markdown("- Python\n- JavaScript\n- Java")

with cols[1]:
    st.markdown("**Frameworks**")
    st.markdown("- React\n- Django\n- Flask")

with cols[2]:
    st.markdown("**Tools & Technologies**")
    st.markdown("- Docker\n- AWS\n- Git")

# Contact Information
st.subheader("Contact Information")
st.markdown("📧 email@example.com")
st.markdown("🔗 [LinkedIn Profile](https://linkedin.com)")
st.markdown("🐙 [GitHub Profile](https://github.com)")