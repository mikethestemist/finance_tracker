# email classifier 
import csv, pprint, re, os
from datetime import datetime


NO_TRANSACTIONS_ERR_MESSAGE = "No transactions stored in here."
KEYWORDS = ('debit', 'alert', 'transaction', 'account', 'balance')
VALIDATION_KEYWORDS = ('account balance', 'transaction details', 'narration', 'debit amount', 'credit amount')
emails = ["""

MoniePoint
Debit Alert
Hi IREOLUWA, 
We wish to inform you that a debit transaction occurred on your account with us.
Debit Amount
N 3,500.00

Transaction Detials 
Account Balance: 
N 483.01
Account Number: 
5033428897
Date & Time: 
10 Jun, 2025 | 08:50:51 AM
Narration: 
AIRTIME TO 08147919041 MTN/ATP

""",
"""
MoniePoint
Debit Alert
Hi IREOLUWA, 
We wish to inform you that a debit transaction occurred on your account with us.
Debit Amount
N 350.00

Transaction Detials 
Account Balance: 
N 133.01
Account Number: 
5033428897
Date & Time: 
10 Jun, 2025 | 08:50:52 AM
Narration: 
Auto-Save 10\\% \\on Airtime Purchase for Save As You Transact.

""", 'Hello']
STORAGE_FILE = 'register.csv'

def is_transaction(mail): 
    trans_emails = []
    def check_one(): 
        for email in emails: 
            for keyword in KEYWORDS: 
                if keyword in email.lower(): 
                    trans_emails.append(email)
                    break
        return trans_emails
    
    possible_transactions = check_one()
    def check_two(possible_trans): 
        valid_transactions = []
        uncertain_trans = []
        for trans in possible_trans: 
            score = 0
            for i in VALIDATION_KEYWORDS: 
                if i in trans.lower():
                    score += 1
            if score >= 3: 
                valid_transactions.append(trans)
            else: 
                uncertain_trans.append(trans)

        return valid_transactions, uncertain_trans

    return check_two(possible_transactions)


def extract_details(trans): 
    complete_list = [*trans[0], *trans[1]]
    # money_pattern = re.compile(r'NG?N?\s(\d+,?\d+.?\d+)')

    register = []
    for mail in complete_list: 
        try: 
            text = mail.replace('\n', ' ')
            # print(text, '\n')

            ### get alert type
            alert_type = re.search(r'(\w+)\s+[Aa]lert', text).group()
            # print(alert_type, '\n')


            # transaction_amount = re.findall(r'($|NG?N?\s\d*,?\d+.?\d+)', text)
            # transaction_amount = re.findall(r'[Aa]mount:?\s+($|NG?N?\s\d*,?\d+.?\d+)', text)

            ### get transaction amount
            transaction_amount = re.search(r'([Dd]ebit|[Cc]redit|[Tt]ransaction)\s[Aa]mount:?\s+($|NG?N?\s*\d*,?\d+.?\d+)', text).group(2)
            # print('Transaction amount:', transaction_amount, '\n')

            ### get current account balanace 
            account_balance = re.search(r'[Bb]alance:?\s+($|NG?N?\s*\d*,?\d+.?\d+)', text).group(1)
            # print('Account balance:', account_balance, '\n')


            ### get the transaction details/description/narration
            description = re.search(r'([Nn]arration|[Dd]etails|[Dd]escription):?\s+((\w+|[-])\s?)+(\w+|[-]\s?)+', text).group()
            # print('Description:', description, '\n')
            # ([Nn]arration):?\s+((\w+|[-])\s?)+(\w+|[-]\s?)+

            ### get date and time
            # Date & Time: 
            # 10 Jun, 2025 | 08:50:51 AM

            time = re.search(r'(\d+:\d+(:\d{2})?\s+(([Aa]|[Pp])[Mm])?)', text).group()
            # parsed_time = datetime.strptime(time, '%I:%M %p')
            # standard_time = parsed_time.strftime('%H:%M:%S')
            # time = standard_time
            # print('Time of transaction:', time, '\n')

            # date_formats = ['20-06-2026', '20-06-26', '20/06/2026', '20/06/26', *'20 Jun, 2026', 'January 20th, 2026']
            date = re.search(r'(\d{1,2}-\d{1,2}-\d{2,4})|(\d{1,2}\/\d{1,2}\/\d{2,4})|(\d{1,2}(st|nd|rd|th)?\s\w+,?\s\d{2,4})|(\w+\s\d{1,2}(st|nd|rd|th)?,?\s\d{2,4})', text).group()
            # parsed_date = datetime.strptime(date, '%d %b, %Y')
            # standard_date = parsed_date.strftime('%d-%m-%Y')
            # date = standard_date
            # print('Date:', date, '\n')
            
            info_extracted = [text, alert_type, transaction_amount, account_balance, description, time, date]
            # print(info_extracted)
            register.append(info_extracted) 
        except Exception:
            print('Error:', Exception)
            print('The following mail\'s info was not able to be saved:')
            print(mail)
    # print(register)
    return register

def store_register(register):
    # [text, alert_type, transaction_amount, account_balance, description, time, date]
    print(register)

    if not os.path.exists(STORAGE_FILE): 
        with open(STORAGE_FILE, 'w') as reg_file: 
            csv_writer = csv.writer(reg_file)
            csv_writer.writerow(['report', 'alert_type', 'transaction_amount', 'current account balance', 'description', 'time', 'date'])
            csv_writer.writerows(register)
    else:
        with open(STORAGE_FILE, 'a') as reg_file: 
            csv_writer = csv.writer(reg_file)
            csv_writer.writerows(register)


def main():
    trans = is_transaction(emails)
    if len([*trans[0], *trans[1]]) == 0: 
        print(NO_TRANSACTIONS_ERR_MESSAGE)
    else: 
        register = extract_details(trans)
        # print('Details Extracted. Register:', pprint.pformat(register))
    store_register(register)


main()

