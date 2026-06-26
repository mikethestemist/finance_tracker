# email classifier 

import csv, pprint, re
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
N 3,50.00

Transaction Detials 
Account Balance: 
N133.01
Account Number: 
5033428897
Date & Time: 
10 Jun, 2025 | 08:50:52 AM
Narration: 
Auto-Save 10\\% \\on Airtime Purchase for Save As You Transact.

""", 'Hello']


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

    register = {}
    for mail in complete_list: 
        mail = mail.replace('\n', ' ')
        transaction_type = re.search(r'[A-za-z]+\s[aA]lert', mail).group()
        transaction_amount = re.search(r'NG?N?\s?(\d+,?\d+.?\d+)', mail).group()
        # account_balance = re.search(r'[Bb]alance:?\s?NG?N?\s(\d+,?\d+.?\d+)', mail).group()
        date_and_time = 'rmdir /s /q .git'
        narration = re.search(r'[Nn]arration|[Dd]etails|[Rr]emark:?\s(\w+)', mail).group()

        print(transaction_amount, transaction_type, 'account_balance', narration)

    
    # pprint.pprint(trans)
    # register = {}
    # for i, each_trans in enumerate([*trans[0], *trans[1]]):
    #     trans_details = each_trans.lower().split('\n')
    #     alert_type =    trans_details[trans_details.index('moniepoint') + 1]
    #     try: 
    #         amount =    trans_details[trans_details.index('debit amount') + 1][2:]
    #     except: 
    #         amount =    trans_details[trans_details.index('credit amount') + 1][2:]
    #     narration =     trans_details[trans_details.index('narration: ')  + 1]
    #     date_and_time = trans_details[trans_details.# email classifier 

import csv, pprint, re
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
N133.01
Account Number: 
5033428897
Date & Time: 
10 Jun, 2025 | 08:50:52 AM
Narration: 
Auto-Save 10\\% \\on Airtime Purchase for Save As You Transact.

""", 'Hello']


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

    register = {}
    for mail in complete_list: 
        text = mail.replace('\n', ' ')
        # print(text, '\n')

        ### get alert type
        alert_type = re.search(r'(\w+)\s+[Aa]lert', text).group()
        # print(alert_type, '\n')


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
        # print('Description:', description, '\n')


        ### get date and time
        # Date & Time: 
        # 10 Jun, 2025 | 08:50:51 AM

        time = re.search(r'(\d+:\d+(:\d{2})?\s+(([Aa]|[Pp])[Mm])?)', text).group()
        # print('Time of transaction:', time, '\n')

        # date_formats = ['20-06-2026', '20-06-26', '20/06/2026', '20/06/26', '20th Jun, 2026', 'January 20th, 2026']
        date = re.search(r'(\d{1,2}-\d{1,2}-\d{2,4})|(\d{1,2}\/\d{1,2}\/\d{2,4})|(\d{1,2}(st|nd|rd|th)?\s\w+,?\s\d{2,4})|(\w+\s\d{1,2}(st|nd|rd|th)?,?\s\d{2,4})', text).group()
        # print('Date:', date, '\n')
        

        print(text, alert_type, transaction_amount, account_balance, description, time, date)
        # register[] 

def main():
    trans = is_transaction(emails)
    if len([*trans[0], *trans[1]]) == 0: 
        print(NO_TRANSACTIONS_ERR_MESSAGE)
    else: 
        register = extract_details(trans)
        print('Details Extracted. Register:', pprint.pformat(register))

main()

index('date & time: ')  + 1]
    #     register[i] = {'alert_type': alert_type, 'amount': amount, 'narration': narration,'date_and_time': date_and_time}
    # # print(register)
    # return register


def main():
    trans = is_transaction(emails)
    if len([*trans[0], *trans[1]]) == 0: 
        print(NO_TRANSACTIONS_ERR_MESSAGE)
    else: 
        register = extract_details(trans)
        print('Details Extracted. Register:', pprint.pformat(register))

main()

