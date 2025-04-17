import streamlit as st
import pandas as pd

st.set_page_config(page_title="CFP Tracker", layout="wide")
st.title("Call for Proposals (CFP) Tracker")

@st.cache_data
def load_data():
    df = pd.read_csv("grants_database.csv")
    df = df.dropna(axis=1, how='all')
    # Create clickable links
    if "source_url" in df.columns:
        df["program_id_display"] = df.apply(
            lambda row: f"[{row['program_id']}]({row['source_url']})" if pd.notna(row.get("source_url")) else row["program_id"],
            axis=1
        )
    return df

df = load_data()

# Filter
search_query = st.text_input("Search CFPs by keyword (program name, agency, or keywords):").lower()
if search_query:
    df = df[df.apply(lambda row: search_query in str(row.get("program_name", "")).lower() or
                                  search_query in str(row.get("agency_name", "")).lower() or
                                  search_query in str(row.get("keywords", "")).lower(), axis=1)]

# Display listings
st.subheader("CFP Listings")
df_display = df.copy()
if "program_id_display" in df_display.columns:
    df_display["program_id"] = df_display["program_id_display"]
display_columns = [
    "program_id", "program_name", "agency_name", "start_date", "end_date",
    "genAI_relevance", "NLP_relevance", "CV_relevance"
]
display_columns = [col for col in display_columns if col in df_display.columns]
st.markdown(df_display[display_columns].to_markdown(index=False), unsafe_allow_html=True)

# Program selection
st.subheader("Select a Program to View Details")
selected_program = st.selectbox("Choose a program:", df["program_name"].unique())

# Show selected details
selected_row = df[df["program_name"] == selected_program].iloc[0]
st.markdown("### CFP Details")
st.markdown(f"**Program ID:** [{selected_row.get('program_id', '')}]({selected_row.get('source_url', '')})")
st.markdown(f"**Program Name:** {selected_row.get('program_name', '')}")
st.markdown(f"**Agency Name:** {selected_row.get('agency_name', '')}")
st.markdown(f"**Summary:** {selected_row.get('proposal_summary', '')}")
st.markdown(f"**Program Areas:** {selected_row.get('program_areas', '')}")
st.markdown(f"**Research Areas:** {selected_row.get('research_areas', '')}")
st.markdown(f"**Award Info:** {selected_row.get('award_info', '')}")
st.markdown(f"**Submission Format:** {selected_row.get('submission_format', '')}")
st.markdown(f"**Contact:** {selected_row.get('contact', '')}")
