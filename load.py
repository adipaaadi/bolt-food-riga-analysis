import json
import pandas as pd
import re

# ---------- 1. Load raw JSON ----------
with open('result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data['messages'])
print(f"Raw messages: {len(df)}")

# ---------- 2. Keep only real messages ----------
df = df[df['type'] == 'message'].copy()
print(f"After dropping service messages: {len(df)}")

# ---------- 3. Flatten the mixed text field ----------
def flatten_text(t):
    if isinstance(t, str):
        return t
    if isinstance(t, list):
        parts = []
        for chunk in t:
            if isinstance(chunk, str):
                parts.append(chunk)
            elif isinstance(chunk, dict) and 'text' in chunk:
                parts.append(chunk['text'])
        return ''.join(parts)
    return ''

df['text_clean'] = df['text'].apply(flatten_text)

# ---------- 4. Remove bot commands and clean whitespace ----------
def strip_bot_commands(s):
    # remove /command tokens
    s = re.sub(r'/\w+', '', s)
    # collapse multiple spaces and newlines
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

df['text_clean'] = df['text_clean'].apply(strip_bot_commands)

# ---------- 5. Drop empty messages ----------
df = df[df['text_clean'].str.len() > 0].copy()
print(f"After dropping empty: {len(df)}")

# ---------- 6. Parse dates ----------
df['date'] = pd.to_datetime(df['date'])
df['date_unixtime'] = pd.to_numeric(df['date_unixtime'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['hour'] = df['date'].dt.hour
df['weekday'] = df['date'].dt.day_name()
df['year_month'] = df['date'].dt.to_period('M').astype(str)

# ---------- 7. Language flags ----------
# crude but effective: check for Latvian, English, Russian characters/markers
df['has_lv'] = df['text_clean'].str.contains(r'[āēīūōķļņģčšž]', case=False, regex=True)
df['has_ru'] = df['text_clean'].str.contains(r'[а-яА-Я]', regex=True)
df['has_en'] = df['text_clean'].str.contains(r'\b(the|and|for|you|your|with|from)\b', case=False, regex=True)

# ---------- 8. Save ----------
output_cols = ['id', 'date', 'year', 'month', 'day', 'hour', 'weekday', 'year_month',
               'text_clean', 'has_lv', 'has_ru', 'has_en']
df[output_cols].to_csv('bfriga_clean.csv', index=False, encoding='utf-8')
print("Saved bfriga_clean.csv")
print(df[['date', 'text_clean']].head())