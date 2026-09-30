"""Підключення до MS SQL Server."""
import os
from urllib.parse import quote_plus

import streamlit as st
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={os.environ['DB_SERVER']}",
        f"DATABASE={os.environ['DB_NAME']}",
        "TrustServerCertificate=yes",
    ]
    if os.getenv("DB_TRUSTED", "0") == "1":
        parts.append("Trusted_Connection=yes")
    else:
        parts += [f"UID={os.environ['DB_USER']}", f"PWD={os.environ['DB_PASSWORD']}"]
    return create_engine("mssql+pyodbc:///?odbc_connect=" + quote_plus(";".join(parts)))
