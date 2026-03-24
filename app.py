import streamlit as st
import pandas as pd
import mysql.connector
from db import get_schema, run_query, test_connection
from llm import GROQ_MODEL, generate_sql

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text-to-SQL AI",
    page_icon="🧠",
    layout="wide",
)

# ── Custom CSS (professional light + whitespace) ──────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #ffffff; }
    [data-testid="stHeader"] { background: rgba(255, 255, 255, 0.9); border-bottom: 1px solid #e5e7eb; }
    [data-testid="stSidebarContent"] { background: #f6f7f9; border-right: 1px solid #e5e7eb; }

    .sql-box {
        background: #ffffff;
        color: #111827;
        padding: 14px 16px;
        border-radius: 12px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.55;
        white-space: pre-wrap;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 10px rgba(17, 24, 39, 0.06);
        margin-bottom: 16px;
    }
    .status-ok  { color: #065f46; font-weight: 600; }
    .status-err { color: #b91c1c; font-weight: 600; }

    /* Give default Streamlit containers a “card” feel without heavy styling. */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧠 Text-to-SQL AI")
st.caption("Ask questions in plain English — get SQL + results instantly.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    # DB connection status
    st.subheader("Database")
    if st.button("🔌 Test Connection"):
        with st.spinner("Connecting..."):
            ok = test_connection()
        if ok:
            st.markdown('<p class="status-ok">✅ Connected successfully</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-err">❌ Connection failed — check .env</p>', unsafe_allow_html=True)

    # Show schema
    st.subheader("Schema")
    if st.button("📋 View DB Schema"):
        try:
            schema = get_schema()
            st.code(schema, language="sql")
        except Exception as e:
            st.error(f"Could not fetch schema: {e}")

    st.divider()
    st.subheader("💡 Example Questions")
    examples = [
        "Show me the top 10 customers by total orders",
        "How many products are in each category?",
        "What is the total revenue for each month in 2024?",
        "List all employees hired after January 2023",
        "Which product has the highest average rating?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["question_input"] = ex

    st.divider()
    st.caption("Powered by Groq · Llama 3.3 70B · MySQL")


# ── Query history (session state) ────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []

if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""

# ── Main input ────────────────────────────────────────────────────────────────
question = st.text_input(
    "Ask a question about your database:",
    placeholder="e.g. Show me the top 5 customers by revenue",
    value=st.session_state["question_input"],
    key="question_input",
)

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("🚀 Run", use_container_width=True, type="primary")
with col2:
    clear_btn = st.button("🗑️ Clear History", use_container_width=True)

if clear_btn:
    st.session_state["history"] = []
    st.rerun()

# ── Main logic ────────────────────────────────────────────────────────────────
if run_btn and question.strip():
    with st.spinner("Fetching database schema..."):
        try:
            schema = get_schema()
        except mysql.connector.Error as e:
            if e.errno == 1045:
                st.error(
                    "MySQL access denied (wrong **DB_USER** / **DB_PASSWORD** in `.env`). "
                    "Confirm the password with MySQL Workbench or `mysql -u root -p`, then update `.env` and restart the app."
                )
            elif e.errno == 1049:
                st.error(
                    f"Unknown database. Check **DB_NAME** in `.env` (must match `SHOW DATABASES;`). {e}"
                )
            else:
                st.error(f"Database error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Database error: {e}")
            st.stop()

    with st.spinner("Generating SQL with Groq..."):
        try:
            sql = generate_sql(schema, question)
        except ValueError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"LLM error: {e}")
            st.stop()

    st.subheader("Generated SQL")
    st.markdown(f'<div class="sql-box">{sql}</div>', unsafe_allow_html=True)

    with st.spinner("Running query on MySQL..."):
        try:
            df = run_query(sql)
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.stop()

    # Results
    st.subheader(f"Results — {len(df)} row(s)")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Rows returned", len(df))
    col_b.metric("Columns", len(df.columns))
    col_c.metric("Model", GROQ_MODEL.split("/")[-1])

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        data=csv,
        file_name="query_results.csv",
        mime="text/csv",
    )

    # Save to history
    st.session_state["history"].insert(0, {
        "question": question,
        "sql": sql,
        "rows": len(df),
    })

elif run_btn:
    st.warning("Please enter a question first.")

# ── Query history ─────────────────────────────────────────────────────────────
if st.session_state["history"]:
    st.divider()
    st.subheader("📜 Query History")
    for i, item in enumerate(st.session_state["history"]):
        with st.expander(f"Q{i+1}: {item['question']}  ({item['rows']} rows)"):
            st.markdown(f'<div class="sql-box">{item["sql"]}</div>', unsafe_allow_html=True)
            if st.button(f"Re-run this query", key=f"rerun_{i}"):
                st.session_state["question_input"] = item["question"]
                st.rerun()
