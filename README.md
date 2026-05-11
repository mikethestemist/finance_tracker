# finance_tracker

The Finance Tracker's automation architecture is as follows:

Aim: Build a basic script that checks emails for bank notification and organises my important bank transactions.

Fundamentals: Filter emails for transaction details and organise them


Modules/Stages: 

Part One: Core Engine
- Parsing texts → structured transaction objects
- Categorising transactions 
- Storing/organising transactions 

Part Two: Insights Engine 
- Aggregations (daily/weekly/monthly totals)
- Category breakdowns

Part Three: Visualization 
- Dashboard 

Part Four: Data ingestion 
- Email connection / extraction

Optional: Intelligence layer
- LLM-generated explanations/advice



Additionals: 
- Dashboard to visualise spending
- AI to give advice (or better still, generate a prompt that includes a summay of my spending and demands brief questioning to understand one's spending and give a resonable actionable goal) 

Possible tools:
- Python streamlit

Connections/Integrations:
- Email reading/filtering
- Banks being used / phrases to identify transaction details 
- Your personal LLM to give financial advice / a chatgpt tool ot service that provides that feature