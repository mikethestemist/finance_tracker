import csv
import json
import os
import re
from pathlib import Path

# Base directory of the script
BASE_DIR = Path(__file__).resolve().parent

# --- UPDATED PATHS TO POINT TO THE DATA FOLDER ---
DATA_FILE = BASE_DIR / 'data' / 'transaction_reports.json'
STORAGE_FILE = BASE_DIR / 'data' / 'register.csv'


def clean_text(value):
    return re.sub(r'\s+', ' ', value or '').strip()


def extract_amount(body):
    patterns = [
        r'(?:Debit|Credit)\s+Amount\s*[:\-]?\s*([N₦$]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'\b(?:Debit|Credit)\s+Amount\s*[:\-]?\s*([\d,\.]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return clean_text(match.group(1)).replace('N', '').replace('₦', '').replace('$', '').replace(',', '')
    return ''


def extract_balance(body):
    match = re.search(r'Account\s+Balance\s*[:\-]?\s*([N₦$]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', body, re.IGNORECASE)
    if match:
        return clean_text(match.group(1)).replace('N', '').replace('₦', '').replace('$', '').replace(',', '')
    return ''


def extract_description(body):
    match = re.search(r' Narration\s*[:\-]?\s*(.+?)(?:\r?\n|$)', body, re.IGNORECASE)
    if match:
        return clean_text(match.group(1))

    match = re.search(r'Transaction\s+Details\s*(.+)', body, re.IGNORECASE)
    if match:
        return clean_text(match.close(1)) if hasattr(match, 'close') else clean_text(match.group(1))

    return ''


def extract_date(body, fallback=''):
    patterns = [
        r'Date\s*&\s*Time\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]{3},\s*\d{4}\s*\|\s*\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM))',
        r'\b(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2})\b',
        r'\b(\d{1,2}\s+[A-Za-z]{3},\s*\d{4})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
    return fallback


def extract_time(body, fallback=''):
    match = re.search(r'(\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM))', body, re.IGNORECASE)
    if match:
        return clean_text(match.group(1))
    return fallback


def extract_alert_type(subject, body):
    if 'debit' in subject.lower() or 'debit' in body.lower():
        return 'Debit'
    if 'credit' in subject.lower() or 'credit' in body.lower():
        return 'Credit'
    return 'Unknown'


# --- NEW: RULE-BASED TRANSACTIONS CATEGORIZER ---
def categorize_transaction(alert_type, subject, description, body):
    if alert_type == 'Credit':
        return 'Income'
        
    # Combine fields to check comprehensively
    text_blob = f"{subject} {description} {body}".lower()
    
    # 1. Food Rules
    food_keywords = ['restaurant', 'eatery', 'food', 'chowdeck', 'bolt food', 'supermarket', 'buka', 'kitchen', 'canteen', 'groceries', 'fastfood']
    if any(kw in text_blob for kw in food_keywords):
        return 'Food'
        
    # 2. Airtime & Data Rules
    telecom_keywords = ['data purchase', 'dtp|', 'airtime', 'mtn', 'airtel', 'glo', '9mobile', 'vended', 'phone number']
    if any(kw in text_blob for kw in telecom_keywords):
        return 'Airtime/Data'
        
    # 3. Transport Rules
    transport_keywords = ['bolt', 'uber', 'indrive', 'ride', 'transport', 'fuel', 'filling station', 'uber trip', 'railway']
    if any(kw in text_blob for kw in transport_keywords):
        return 'Transport'
        
    # 4. Personal Rules (Subscriptions, self-transfers, shopping etc.)
    personal_keywords = ['netflix', 'spotify', 'apple', 'gym', 'personal', 'salon', 'barber', 'clothing', 'store', 'atm cash']
    if any(kw in text_blob for kw in personal_keywords):
        return 'Personal'
        
    # 5. Default Fallback
    return 'Other'


def load_reports(data_file=DATA_FILE):
    if not data_file.exists():
        return []
    with open(data_file, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def process_reports(reports):
    rows = []
    for report in reports:
        body = report.get('body', '')
        subject = report.get('subject', '')
        date = report.get('date', '')
        
        alert_type = extract_alert_type(subject, body)
        description = extract_description(body)
        
        # Determine category dynamically
        category = categorize_transaction(alert_type, subject, description, body)
        
        row = [
            subject,
            alert_type,
            extract_amount(body),
            extract_balance(body),
            description,
            category,  # Added to row structure
            extract_time(body),
            extract_date(body, date),
        ]
        rows.append(row)
    return rows


def save_register(rows):
    # Ensure the data directory exists before trying to write to it
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists and if it has content safely
    file_exists = STORAGE_FILE.exists()
    is_empty = STORAGE_FILE.stat().st_size == 0 if file_exists else True
    
    # --- FIXED: Added quoting=csv.QUOTE_MINIMAL to safely wrap commas ---
    with open(STORAGE_FILE, 'a', newline='', encoding='utf-8') as reg_file:
        writer = csv.writer(reg_file, quoting=csv.QUOTE_MINIMAL)
        if is_empty:
            # Contains 8 fields now with category included
            writer.writerow(['report', 'alert_type', 'transaction_amount', 'current account balance', 'description', 'category', 'time', 'date'])
        writer.writerows(rows)

def main():
    reports = load_reports()
    if not reports:
        print(f'No transaction reports found in {DATA_FILE} to sort.')
        return

    rows = process_reports(reports)
    save_register(rows)
    print(f'✅ Extracted {len(rows)} transaction report(s) with categories into {STORAGE_FILE}')


if __name__ == '__main__':
    main()