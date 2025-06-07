import streamlit as st
import pandas as pd
from lead_utils import load_model_and_preprocessor, score_leads
from database import insert_leads, fetch_leads_with_scores, create_table

create_table()
model, preprocessor = load_model_and_preprocessor()

st.title("♦ Lead Scoring Tool")

menu = st.sidebar.selectbox("Navigation", ["Home", "Raw Leads", "Scored Leads"])

if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = None

if menu == "Home":
    st.subheader("Upload your leads CSV")

    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            df.index = df.index + 1  # Start index from 1
            st.session_state["raw_data"] = df  # Save to session state
            st.write("Uploaded Data Preview", df.head())

            if st.button("Score Leads"):
                try:
                    df_scored = score_leads(df, model, preprocessor)
                    insert_leads(df_scored)
                    st.success("✅ Leads scored and saved to database successfully!")
                    st.dataframe(
                        df_scored[["Company", "Lead Score"]].sort_values(
                            by="Lead Score", ascending=False
                        ) 
                    ) 
                except Exception as e:
                    st.error(f"❌ Error during scoring or saving: {e}")

        except Exception as e:
            st.error(f"❌ Error reading CSV file: {e}")

elif menu == "Raw Leads":
    st.subheader("📋 Raw Leads (Uploaded CSV)")

    if st.session_state["raw_data"] is not None:
        st.dataframe(st.session_state["raw_data"])
    else:
        st.info("No CSV uploaded yet. Please upload a CSV in Home tab.")

elif menu == "Scored Leads":
    st.subheader("🏆 Scored Leads (High to Low)")
    try:
        df_scored = fetch_leads_with_scores()
        if df_scored.empty:
            st.info("No scored leads found in the database.")
        else:
            # st.dataframe(df_scored.style.highlight_max(axis=0, color="lightgreen"))
            st.dataframe(df_scored.style.highlight_max(axis=0))
    except Exception as e:
        st.error(f"❌ Error fetching scored leads: {e}")
