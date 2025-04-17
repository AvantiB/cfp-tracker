import streamlit as st
import pandas as pd

st.set_page_config(page_title="CFP Tracker", layout="wide")
st.title("Call for Proposals (CFP) Tracker")

@st.cache_data
def load_data():
    df = pd.read_csv("grants_database.csv")

    # Remove columns that are all null
    df = df.dropna(axis=1, how='all')

    # Add clickable program_id if source_url exists
    if "source_url" in df.columns:
        df["program_id"] = df.apply(lambda row: f"[{row['program_id']}]({row['source_url']})", axis=1)

    return df

df = load_data()
# 🔍 Search bar
search_query = st.text_input("Search keywords (title, agency, or keywords):").lower()

if search_query:
    df = df[df.apply(lambda row: search_query in str(row["program_name"]).lower() or
                                      search_query in str(row["agency_name"]).lower() or
                                      search_query in str(row["keywords"]).lower(), axis=1)]

# Columns to display in the main table
table_columns = [
    "program_id", "program_name", "agency_name", "start_date", "end_date",
    "genAI_relevance", "NLP_relevance", "CV_relevance"
]

# Only show columns that exist in the dataframe
display_columns = [col for col in table_columns if col in df.columns]

# Display summary table
st.subheader("CFP Listings")
st.dataframe(df[display_columns], use_container_width=True, hide_index=True)

# Expandable details section
st.markdown("---")
st.subheader("CFP Details")

for _, row in df.iterrows():
    with st.expander(f"{row.get('program_name', '')}"):
        st.markdown(f"**Program ID:** {row.get('program_id', '')}")
        st.markdown(f"**Program Name:** {row.get('program_name', '')}")
        st.markdown(f"**Agency Name:** {row.get('agency_name', '')}")
        st.markdown(f"**Summary:** {row.get('proposal_summary', '')}")
        st.markdown(f"**Program Areas:** {row.get('program_areas', '')}")
        st.markdown(f"**Research Areas:** {row.get('research_areas', '')}")
        st.markdown(f"**Award Info:** {row.get('award_info', '')}")
        st.markdown(f"**Submission Format:** {row.get('submission_format', '')}")
        st.markdown(f"**Contact:** {row.get('contact', '')}")
        if "source_url" in row:
            st.markdown(f"**Link:** [View full details]({row['source_url']})")