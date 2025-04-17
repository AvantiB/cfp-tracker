import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import os
import time
import re
import openai
import pandas as pd
import json
from schema import json_schema

print("🚀 Starting CFP Tracker...")

# Base URL for the search results
BASE_SEARCH_URL = "https://simpler.grants.gov/search?sortby=postedDateDesc&page={}"

# Headers to mimic a browser
HEADERS = {'User-Agent': 'Mozilla/5.0'}

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("BASE_URL")


client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url
)

def get_response (text, json_schema):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that extracts structured data from Call For Proposal(CFP) text.
                    Your job is to perform the following tasks: 
                    1. Summarize the proposal in 25-30 words
                    2. Extract 10 keywords based on the focus of the proposal
                    3. Identify 5 key research areas that this proposal is most relevant to
                    4. Fill in additional fields as per the schema provided. Ensure the extracted values are accurate, concise, and formatted as strings (or lists where applicable)

                    Return only the JSON object that adheres to the provided schema. Do not include any explanation, commentary, or markdown formatting.
                    """,
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": json_schema,
        }
    )
    completion_text =[choice.message.content for choice in response.choices][0]
    return completion_text

def append_to_database(json_string: str, link: str, database_file: str = "grants_database.csv"):
    try:
        data = json.loads(json_string)
        new_entries = data.get("results", [])
        if not new_entries:
            print("No results found in the JSON.")
            return

        # Convert new data to DataFrame
        df_new = pd.DataFrame(new_entries)

        # Load existing database if it exists
        if os.path.exists(database_file):
            df_existing = pd.read_csv(database_file, dtype=str)

            for _, new_row in df_new.iterrows():
                new_row["source_url"] = link
                # Define match condition
                condition = (
                    (df_existing["program_id"] == new_row["program_id"]) &
                    (df_existing["program_name"] == new_row["program_name"]) &
                    (df_existing["agency_name"] == new_row["agency_name"])
                )

                # Check for existing matching record
                if df_existing[condition].empty:
                    # No match found, append new record
                    df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                    print(f"Added new record: {new_row['program_id']}")
                else:
                    # Matching record found, check for date differences
                    existing_row = df_existing[condition].iloc[0]
                    if (existing_row["start_date"] != new_row["start_date"] or
                        existing_row["end_date"] != new_row["end_date"]):
                        # Remove old entry and replace with new one
                        df_existing = df_existing[~condition]
                        df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                        print(f"Updated record: {new_row['program_id']}")
                    else:
                        # Same dates, skip
                        print(f"No changes detected for: {new_row['program_id']}, skipping.")
        else:
            # No existing file, write new one
            df_new["source_url"] = link
            df_existing = df_new
            print("Database created with initial records.")

        # Save the updated data
        df_existing.dropna(axis=1, how='all', inplace=True)
        df_existing.to_csv(database_file, index=False)

    except Exception as e:
        print(f"Error while appending to database: {e}")


def get_opportunity_links(page_number):
    url = BASE_SEARCH_URL.format(page_number)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/opportunity/'):
            full_url = f"https://simpler.grants.gov{href}"
            if full_url not in links:
                links.append(full_url)
    return links


def extract_summary(soup):
    # Find the "Funding opportunity" header or section
    funding_header = soup.find(
        lambda tag: tag.name in ['h2', 'h3'] and "funding opportunity" in tag.get_text(strip=True).lower())
    if not funding_header:
        return ""

    # Search forward through siblings for the word "Summary"
    current = funding_header.find_next()
    while current:
        text = current.get_text(strip=True).lower() if current else ""
        if "summary" in text and len(text) < 100:
            # Assume the next sibling is the actual summary
            next_content = current.find_next_sibling()
            if next_content:
                summary_text = next_content.get_text(strip=True)
                if len(summary_text) > 50:
                    return summary_text
        current = current.find_next_sibling()
    return ""


def download_and_read_pdfs(soup):
    documents_section = soup.find('h2', string='Documents')
    if not documents_section:
        return None

    text_blocks = []
    for link in documents_section.find_all_next('a', href=True):
        href = link['href']
        if href.lower().endswith('.pdf'):
            pdf_url = href if href.startswith("http") else f"https://simpler.grants.gov{href}"
            pdf_filename = pdf_url.split('/')[-1]

            # Download PDF
            response = requests.get(pdf_url)
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)

            try:
                with open(pdf_filename, 'rb') as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            text_blocks.append(text.strip())
            except Exception as e:
                print(f"PDF read error: {e}")
            finally:
                os.remove(pdf_filename)

        # Stop if we hit another section
        if link.find_previous('h2') != documents_section:
            break

    return "\n\n".join(text_blocks) if text_blocks else ""


def check_additional_info_link(soup):
    info_section = soup.find('h2', string='Link to additional information')
    if info_section:
        link_tag = info_section.find_next('a', href=True)
        if link_tag:
            url = link_tag['href']
            if not url.startswith("http"):
                url = f"https://simpler.grants.gov{url}"
            print(f"\nVisiting additional info: {url}")
            try:
                response = requests.get(url, headers=HEADERS)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.get_text(separator='\n', strip=True)
            except Exception as e:
                print(f"Failed to fetch additional info link: {e}")
    return ""


def process_opportunity(url):
    print(f"\n=== Processing: {url} ===")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find("h1")
        program_name = title_tag.get_text(strip=True) if title_tag else ""
        exclusion_keywords = [
            "early career",
            "young investigator",
            "new investigator",
            "early-stage investigator",
            "early-stage researcher"
        ]
        if any(keyword in program_name.lower() for keyword in exclusion_keywords):
            print(f"Skipped (title indicates early career award): {program_name}")
            return ""  # Skip this entry

        summary = extract_summary(soup)
        # print(f"\nSummary:\n{summary}")

        pdf_text = download_and_read_pdfs(soup)
        if pdf_text:
            return summary + "\n\n" + pdf_text

        link_text = check_additional_info_link(soup)
        if link_text:
            return summary + "\n\n" + link_text
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return ""

def main():
    for page in range(1, 10):
        print(f"\n=== PAGE {page} ===")
        try:
            links = get_opportunity_links(page)
            for link in links:
                cfp_text = process_opportunity(link)
                if cfp_text:
                    try:
                        response = get_response (cfp_text, json_schema)  # returns JSON string
                        append_to_database(response, link = link)
                    except openai.OpenAIError as e:
                        print(f"OpenAI error for {link}: {e}")
                time.sleep(1)
        except Exception as e:
            print(f"Error on page {page}: {e}")

if __name__ == "__main__":
    main()
