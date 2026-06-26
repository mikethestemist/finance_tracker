import re 
emails ="""

MoniePoint
Debit Alert
Hi IREOLUWA, 
We wish to inform you that a debit transaction occurred on your account with us.
Debit Amount
N 350.00

Transaction Detials 
Account Balance: 
N133.01
Account Number: 
5033428897
Date & Time: 
10 Jun, 2025 | 08:50:52 AM
Narration: 
Auto-Save 10\\% \\on Airtime Purchase for Save As You Transact.
"""
### make multi-line text single-line
text = ' '.join(emails.split())
print(text, '\n')

### get alert type
alert_type = re.search(r'(\w+)\s+[Aa]lert', text).group()
print(alert_type, '\n')


# transaction_amount = re.findall(r'($|NG?N?\s\d*,?\d+.?\d+)', text)
# transaction_amount = re.findall(r'[Aa]mount:?\s+($|NG?N?\s\d*,?\d+.?\d+)', text)

### get transaction amount
transaction_amount = re.search(r'([Dd]ebit|[Cc]redit|[Tt]ransaction)\s[Aa]mount:?\s+($|NG?N?\s\d*,?\d+.?\d+)', text).group(2)
print('Transaction amount:', transaction_amount, '\n')

### get current account balanace 
account_balance = re.search(r'[Bb]alance:?\s+($|NG?N?\s\d*,?\d+.?\d+)', text).group()
print('Account balance:', account_balance, '\n')


### get the transaction details/description/narration
description = re.search(r'([Nn]arration|[Dd]etails|[Dd]escription):?\s+(\w+\s?(\w+)?\s?(\w+)?\s?(\w+)?\s?(\w+)?\s?)', text).group(2)
print('Description:', description, '\n')


### get date and time
# Date & Time: 
# 10 Jun, 2025 | 08:50:51 AM

time = re.search(r'(\d+:\d+(:\d{2})?\s+(([Aa]|[Pp])[Mm])?)', text).group()
print('Time of transaction:', time, '\n')

# date_formats = ['20-06-2026', '20-06-26', '20/06/2026', '20/06/26', '20th Jun, 2026', 'January 20th, 2026']
date = re.search(r'(\d{1,2}-\d{1,2}-\d{2,4})|(\d{1,2}\/\d{1,2}\/\d{2,4})|(\d{1,2}(st|nd|rd|th)?\s\w+,?\s\d{2,4})|(\w+\s\d{1,2}(st|nd|rd|th)?,?\s\d{2,4})', text).group()
print('Date:', date, '\n')
