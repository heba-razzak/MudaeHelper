"""
Mudae JSON to CSV Converter (Only tested for `$topku` so far)

This script processes JSON files from Mudae and converts them into CSV format.

For `$top`
- Extracts rank, character, series, and kakera count.

Process Flow
1. Loads JSON data
2. Cleans and processes the text
3. Extracts relevant columns
4. Saves the structured data as a CSV file
"""

import os
import json
import pandas as pd
import re

# 🔹 List all JSON files
json_files = [f for f in os.listdir("data") if f.endswith(".json")]
filenames_df = pd.DataFrame(json_files, columns=["filename"])

# view json files in data folder
filenames_df

# Choose file to convert to csv
json_filename = json_files[0]  # Change this to pick a specific file
json_path = os.path.join("data", json_filename)

# Load JSON data
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Convert to DataFrame
df = pd.DataFrame(data)


# Extracts the command type (e.g., "top", "im")
category = json_filename.split("_")[0]

# Expand description by splitting on newlines and creating new rows
df = df.assign(description=df['description'].str.split('\n')).explode('description')
df = df.reset_index(drop=True)

# Step 1: Remove zero-width spaces & trim whitespace
df['description'] = df['description'].str.replace("\u200b", "", regex=False).str.strip()

# Step 2: Drop rows where 'description' is now empty
df = df[df['description'] != ""]

def split_top_desc(text):
    parts = re.split(r"\*\* \- | \- \*\* | · \*\*", text)  # Split using delimiters
    parts = [p.replace("**", "").strip() for p in parts]  # Clean extra "**" and whitespace
    # Ensure parts has at least 4 elements
    while len(parts) < 4:
        parts.append(None)
    return parts

df['description'] = df['description'].apply(split_top_desc)

if category.startswith("top"):
    # Convert 'description' list column into separate DataFrame columns
    df[['rank', 'character', 'series', 'kakera']] = pd.DataFrame(df['description'].tolist(), index=df.index)
    
    # Clean 'rank' column
    df['rank'] = df['rank'].astype(str).str.replace("#", "", regex=False).astype("Int64")

    # Clean 'kakera' column
    df['kakera'] = df['kakera'].astype(str).str.replace(" ka", "", regex=False).astype("Int64")

# Function to extract page numbers using `re.search()`
def extract_page_info(page_text):
    if isinstance(page_text, str):  # Ensure it's a string
        match = re.search(r"(\d+) / (\d+)", page_text)
        if match:
            return pd.Series([int(match.group(1)), int(match.group(2))])
    return pd.Series([None, None])  # Return None if no match

# Extract page number and total_pages
df[['pg', 'maxpg']] = df['page'].apply(extract_page_info)

# Drop the original 'description' column
df.drop(columns=['description', 'page', 'channel', 'guild', 'timestamp'], inplace=True)

# Save CSV
df.to_csv(json_path.replace(".json", ".csv"), index=False, encoding="utf-8")