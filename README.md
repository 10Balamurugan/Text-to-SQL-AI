# 🧠 Text-to-SQL AI

Convert plain English questions into SQL queries and get instant results — powered by **Groq (LLaMA 3 70B)** and a **Streamlit** interface.

## 🚀 Demo

> "Show me the top 10 customers by total orders"
> → SELECT `customer_name`, COUNT(*) as total_orders FROM orders GROUP BY customer_name ORDER BY total_orders DESC LIMIT 10;

## ✨ Features

- 💬 Ask questions in plain English — no SQL knowledge needed
- ⚡ Ultra-fast inference via Groq (LLaMA 3 70B)
- 🔒 Read-only safety — only SELECT queries are allowed
- 📋 Auto schema detection — reads your DB tables automatically
- 📊 Results shown as interactive table with CSV download
- 🕓 Query history with one-click re-run

## 🗂️ Project Structure

```
text_to_sql/
├── .env              # API keys & DB credentials
├── requirements.txt  # Dependencies
├── app.py            # Streamlit UI
├── db.py             # DB connection, schema reader, query runner
└── llm.py            # Groq API + prompt builder
```

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/text-to-sql-ai.git
cd text-to-sql-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate    # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env
# Edit .env with your Groq API key and DB details

# 5. Run the app
streamlit run app.py
```

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| GROQ_API_KEY | Get free key at console.groq.com |
| DB_HOST | MySQL host (default: localhost) |
| DB_PORT | MySQL port (default: 3306) |
| DB_USER | MySQL username |
| DB_PASSWORD | MySQL password |
| DB_NAME | Target database name |

## 🛠️ Tech Stack

- **LLM**: Groq — LLaMA 3 70B (free tier)
- **UI**: Streamlit
- **Database**: MySQL / SQLite
- **Language**: Python 3.9+
- **Key libs**: LangChain, pandas, mysql-connector-python

## 📌 Use Cases

- Quickly explore any MySQL database without writing SQL
- Business analysts querying data with natural language
- Learning SQL by seeing generated queries

## 🙌 Author

Built by Balamurugan· Data Science student at Besant Technologies, Bangalore
