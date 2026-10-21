import streamlit as st

st.set_page_config(
    page_title="Calculator for MOAs",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# SESSION STATE
# ==============================

if "selected_app" not in st.session_state:
    st.session_state.selected_app = "home"


# ==============================
# STYLE
# ==============================

st.markdown("""
<style>
    .stApp {
        background-color: #F7F8F0;
    }

    h1, h2, h3 {
        color: #355E3B;
    }

    .hero {
        background: linear-gradient(135deg, #DCE9D5, #F5EBDD);
        padding: 35px;
        border-radius: 22px;
        text-align: center;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        color: #536B54;
    }

    .app-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE7D8;
        padding: 25px;
        border-radius: 20px;
        min-height: 220px;
        box-shadow: 0 4px 12px rgba(50, 80, 50, 0.06);
    }

    .app-card h3 {
        margin-top: 0;
    }

    .app-card p {
        color: #59665A;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #71816F;
        margin-top: 40px;
        font-size: 13px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 48px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==============================
# HOME PAGE
# ==============================

if st.session_state.selected_app == "home":

    st.markdown("""
    <div class="hero">
        <h1>💚 Calculator for MOAs</h1>
        <p>Turn Data Into Dream</p>
        <p>Your little home for statistical analysis ✨</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;'>Choose Your Experience 🌷</h2>",
        unsafe_allow_html=True
    )

    st.write(
        "<p style='text-align:center;'>"
        "Pilih aplikasi yang sesuai dengan kebutuhanmu."
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    left, right = st.columns(2, gap="large")

    with left:

        st.markdown("""
        <div class="app-card">
            <h3>💚 MOA Classic</h3>
            <p>
                Simple, sweet, and easy to use!<br><br>
                📊 Statistik deskriptif<br>
                📈 Histogram dan boxplot<br>
                📥 Download hasil statistik<br><br>
                Cocok untuk analisis data sederhana.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "💚 Open MOA Classic",
            key="open_classic",
            type="primary"
        ):
            st.session_state.selected_app = "classic"
            st.rerun()

    with right:

        st.markdown("""
        <div class="app-card">
            <h3>📊 MOA Statistics</h3>
            <p>
                Explore your data more deeply!<br><br>
                📋 Statistik deskriptif lengkap<br>
                🔗 Analisis korelasi<br>
                📉 Regresi linear sederhana<br>
                📥 Download CSV dan Excel<br><br>
                Cocok untuk analisis statistik lanjutan.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "📊 Open MOA Statistics",
            key="open_statistics",
            type="primary"
        ):
            st.session_state.selected_app = "statistics"
            st.rerun()

    st.markdown("""
    <div class="footer">
        Made with 💚 for curious minds and MOAs everywhere.
    </div>
    """, unsafe_allow_html=True)


# ==============================
# CLASSIC APP
# ==============================

elif st.session_state.selected_app == "classic":

    if st.button("← Back to Home"):
        st.session_state.selected_app = "home"
        st.rerun()

    st.divider()

    # Menampilkan aplikasi klasik.
    # File app.py harus diubah menjadi modul
    # yang memiliki fungsi run_app().

    import app

    app.run_app()


# ==============================
# STATISTICS APP
# ==============================

elif st.session_state.selected_app == "statistics":

    if st.button("← Back to Home"):
        st.session_state.selected_app = "home"
        st.rerun()

    st.divider()

    # Menampilkan aplikasi statistik lanjutan.
    # File app2.py harus diubah menjadi modul
    # yang memiliki fungsi run_app().

    import app2

    app2.run_app()