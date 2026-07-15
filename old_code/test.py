### error was in the input email: initially didn't support N133.01 without the space after 'N'
import re 
emails = """"
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

text = ''.join(emails)
print(text, '\n')

transaction_amount = re.search(r'([Dd]ebit|[Cc]redit|[Tt]ransaction)\s[Aa]mount:?\s+($|NG?N?\s*\d*,?\d+.?\d+)', text).group(2)
print('Transaction amount:', transaction_amount, '\n')

account_balance = re.search(r'[Bb]alance:?\s+($|NG?N?\s*\d*,?\d+.?\d+)', text).group()
print('Account balance:', account_balance, '\n')
