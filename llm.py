import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Groq retired llama3-70b-8192; see https://console.groq.com/docs/deprecations
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL = (os.getenv("GROQ_MODEL") or DEFAULT_GROQ_MODEL).strip()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert SQL assistant. Your job is to convert natural language questions into valid MySQL SQL queries.

Rules:
- Output ONLY the raw SQL query. No explanation, no markdown, no code fences.
- Use backticks around table and column names.
- Always use SELECT queries only — never INSERT, UPDATE, DELETE, or DROP.
- If the question cannot be answered with the given schema, reply with: ERROR: Cannot answer this question with the available tables.
- Use LIMIT 100 by default unless the user specifies a different number.
- Be careful with JOINs — only join tables that have clear foreign key relationships.
"""


def build_prompt(schema: str, question: str) -> str:
    return f"""Here is the database schema:

{schema}

Convert this question into a MySQL SQL query:
{question}"""


def extract_sql(raw: str) -> str:
    """
    Strip any accidental markdown code fences from the LLM output.
    """
    # Remove ```sql ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE).replace("```", "")
    return cleaned.strip()


def generate_sql(schema: str, question: str) -> str:
    """
    Send the schema + question to Groq and return the generated SQL string.
    Raises ValueError if the LLM signals it cannot answer.
    """
    prompt = build_prompt(schema, question)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0,        # deterministic output for SQL
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    sql = extract_sql(raw)

    if sql.upper().startswith("ERROR:"):
        raise ValueError(sql)

    return sql
