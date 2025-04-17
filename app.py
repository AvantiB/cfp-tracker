import streamlit as st
import pandas as pd

st.set_page_config(page_title="CFP Tracker", layout="wide")
st.title("Call for Proposals (CFP) Tracker")

@st.cache_data
def load_data():
    return pd.read_csv("grants_database.csv")

df = load_data()
# 🔍 Search bar
search_query = st.text_input("Search keywords (title, agency, or keywords):").lower()

if search_query:
    df = df[df.apply(lambda row: search_query in str(row["program_name"]).lower() or
                                      search_query in str(row["agency_name"]).lower() or
                                      search_query in str(row["keywords"]).lower(), axis=1)]
else:
    df = load_data()

# Create clickable links for program_id
if "source_url" in df.columns:
    df["program_id"] = df.apply(lambda row: f"[{row['program_id']}]({row['source_url']})", axis=1)

# Preview table
st.subheader("CFP Listings")
st.dataframe(
    df[["program_id", "program_name", "agency_name", "start_date", "end_date"]],
    use_container_width=True,
    hide_index=True
)

# Detailed expandable summaries
st.markdown("---")
st.subheader("CFP Details")

for _, row in df.iterrows():
    with st.expander(f"{row['program_name']} ({row['program_id']})"):
        st.markdown(f"**Agency:** {row['agency_name']}")
        st.markdown(f"**Start Date:** {row['start_date']}")
        st.markdown(f"**End Date:** {row['end_date']}")
        st.markdown(f"**Keywords:** {row['keywords']}")
        st.markdown(f"**Program Areas:** {row.get('program_areas', '')}")
        st.markdown(f"**Research Areas:** {row.get('research_areas', '')}")
        st.markdown(f"**Submission Format:** {row.get('submission_format', '')}")
        st.markdown(f"**Contact:** {row.get('contact', '')}")
        if "source_url" in row:
            st.markdown(f"**Link:** [View full details]({row['source_url']})")
        st.markdown("**Summary:**")
        st.write(row["summary"])
