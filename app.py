import streamlit as st
import pandas as pd
from lead_utils import load_model_and_preprocessor, score_leads
from database import insert_leads, fetch_leads, fetch_leads_with_scores
from database import create_table
create_table()

# Load model and preprocessor
model, preprocessor = load_model_and_preprocessor()

st.title("🧠 Lead Scoring Tool")

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", ["Home", "Raw Leads", "Scored Leads"])

# Home Tab: Upload and Score Leads
if menu == "Home":
    st.subheader("Upload your leads CSV")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        df = pd.read_csv(uploaded)
        st.write("Uploaded Data", df.head())

        if st.button("Score Leads"):
            try:
                df_scored = score_leads(df, model, preprocessor)
                insert_leads(df_scored)
                st.success("✅ Leads scored and stored successfully!")
                st.dataframe(df_scored[["Company", "Lead Score"]].sort_values(by="Lead Score", ascending=False))
            except Exception as e:
                st.error(f"❌ Error while scoring leads: {e}")

# Raw Leads Tab
elif menu == "Raw Leads":
    st.subheader("📋 Leads without Scores")
    df_raw = fetch_leads(raw_only=True)
    st.dataframe(df_raw)

# Scored Leads Tab
elif menu == "Scored Leads":
    st.subheader("🏆 Scored Leads (High to Low)")
    df_scored = fetch_leads_with_scores()
    st.dataframe(df_scored.style.highlight_max(axis=0, color="lightgreen"))
