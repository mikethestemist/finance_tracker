import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timedelta

import email
import imaplib
from dotenv import load_dotenv
from email.header import decode_header


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR,'data','.env'))

EMAIL = os.getenv('EMAIL') or os.getenv('GMAIL_USER')
PASSWORD = os.getenv('PASSWORD') or os.getenv('APP_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')

if not EMAIL or not PASSWORD:
    raise ValueError('EMAIL and a Gmail app password must be set in the .env file.')


def decode_header_value(value):
    if not value:
        return ''

    decoded_parts = []
    for part, encoding in decode_header(value):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
        else:
            decoded_parts.append(part)
    return ''.join(decoded_parts)


def get_message_text(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() in {'text/plain', 'text/html'} and 'attachment' not in str(part.get('Content-Disposition')):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
    else:
        if message.get_content_type() in {'text/plain', 'text/html'}:
            payload = message.get_payload(decode=True)
            if payload:
                return payload.decode(message.get_content_charset() or 'utf-8', errors='ignore')
    return ''


def get_email_date(message):
    raw_date = message.get('Date')
    if raw_date:
        return decode_header_value(raw_date)

    return ''


def is_probable_transaction_report(message):
    subject = decode_header_value(message.get('Subject', '')).lower()
    from_address = decode_header_value(message.get('From', '')).lower()
    body = get_message_text(message).lower()

    keywords = [
        'transaction', 'debit', 'credit', 'alert', 'account', 'balance',
        'bank', 'payment', 'withdrawal', 'deposit', 'narration'
    ]

    text_blob = f'{subject} {from_address} {body}'
    score = sum(1 for keyword in keywords if keyword in text_blob)

    return score >= 3


def fetch_recent_emails(address, password, days=30, max_emails=50):
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
    mail = None

    try:
        print('🔌 Connecting to Gmail...')
        socket.setdefaulttimeout(15)
        mail = imaplib.IMAP4_SSL('imap.gmail.com', timeout=15)

        print('🔐 Logging in...')
        mail.login(address, password)

        print('📥 Opening inbox...')
        mail.select('inbox', readonly=True)

        print(f'🔎 Searching for emails from the last {days} days...')
        status, messages = mail.search(None, f'(SINCE {cutoff_date})')
        if status != 'OK':
            raise RuntimeError(f'Email search failed: {status}')

        email_ids = messages[0].split()
        print(f'📬 Found {len(email_ids)} matching messages. Processing the latest {min(len(email_ids), max_emails)}...')

        recent_emails = []
        for index, email_id in enumerate(email_ids[-max_emails:], start=1):
            print(f'   [{index}/{min(len(email_ids), max_emails)}] Checking message {email_id.decode() if isinstance(email_id, bytes) else email_id}...')
            status, data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                print('      Skipping this message due to a fetch error.')
                continue

            raw_email = data[0][1]
            message = email.message_from_bytes(raw_email)
            if not is_probable_transaction_report(message):
                print('      Not a likely transaction report. Skipping.')
                continue

            recent_emails.append({
                'id': email_id.decode() if isinstance(email_id, bytes) else email_id,
                'subject': decode_header_value(message.get('Subject')),
                'from': decode_header_value(message.get('From')),
                'date': get_email_date(message),
                'body': get_message_text(message),
            })
            print('      Saved as a likely bank transaction report.')

        print('✅ Finished processing emails.')
        return recent_emails
    except (TimeoutError, socket.timeout, imaplib.IMAP4.error, ConnectionResetError, OSError) as exc:
        raise RuntimeError(f'Could not read emails from Gmail: {exc}') from exc
    finally:
        if mail is not None:
            try:
                mail.close()
                mail.logout()
                print('🔒 Connection closed.')
            except Exception:
                pass


def save_transaction_reports(emails, output_file='transaction_reports.json'):
    # Define and automatically generate the 'data' subdirectory 
    data_dir = os.path.join(BASE_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Target file path inside the data folder
    output_path = os.path.join(data_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(emails, handle, indent=2, ensure_ascii=False)
    return output_path


def main():
    # --- CONFIGURATION FOR TIMEFRAME ---
    timeframe = '1_month'  # Options available: '1_week', '1_month', '6_months', '1_year'
    
    timeframe_days = {
        '1_week': 7,
        '1_month': 30,
        '6_months': 180,
        '1_year': 365
    }
    
    chosen_days = timeframe_days.get(timeframe, 30)
    max_to_fetch = 500 if chosen_days > 30 else 50

    print(f'🚀 Starting email fetch process for the last {timeframe} ({chosen_days} days)...')
    emails = fetch_recent_emails(EMAIL, PASSWORD, days=chosen_days, max_emails=max_to_fetch)

    if not emails:
        print(f'No emails were found in the last {chosen_days} days.')
        return

    print(f'📊 Found {len(emails)} emails from the last {chosen_days} days.')
    for item in emails:
        print('-' * 60)
        print(f"Subject: {item['subject']}")
        print(f"From: {item['from']}")
        print(f"Date: {item['date']}")
        print(item['body'][:400].replace('\n', ' ').strip())

    output_path = save_transaction_reports(emails)
    print(f'💾 Saved likely transaction reports to {output_path}')

    sorter_path = os.path.join(BASE_DIR, 'Email_Sorter--Transactions.py')
    print('🧠 Sending reports to the sorter...')
    subprocess.run([sys.executable, sorter_path], cwd=BASE_DIR, check=False)


if __name__ == '__main__':
    main()