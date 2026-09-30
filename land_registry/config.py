"""Константи та налаштування застосунку."""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PAGE_ICON = str(ROOT / "UPI.png") if (ROOT / "UPI.png").exists() else "🌾"

TABLE = os.getenv("DB_TABLE", "[dbo].[LandRegistryData]")

# ---------- Періоди завершення оренди ----------
FIRST_YEAR = 2026  # "до 31.12.26", далі по одному року
YEARS = list(range(FIRST_YEAR + 1, FIRST_YEAR + 5))  # 2027..2030
B_ENDED = "Закінчились"
B_FIRST = f"До 31.12.{FIRST_YEAR}"
B_AFTER = f"Після {YEARS[-1]}"
B_NONE = "Без дати"
BUCKETS = [B_ENDED, B_FIRST, *map(str, YEARS), B_AFTER, B_NONE]
SUMMARY_BUCKETS = [B_ENDED, B_FIRST, *map(str, YEARS)]  # без "Після 2030" і "Без дати"

ALL = "— Всі —"
SUGGEST_N = 10


def today():
    """Поточна дата (обчислюється при кожному виклику, а не при імпорті)."""
    import pandas as pd

    return pd.Timestamp(date.today())


# ---------- Excel-стилі зведеної таблиці ----------
LEVEL_STYLES = {
    0: {"fill": "1F4E78", "font_color": "FFFFFF", "bold": True, "size": 12},
    1: {"fill": "2E75B6", "font_color": "FFFFFF", "bold": True, "size": 11},
    2: {"fill": "9DC3E6", "font_color": "000000", "bold": True, "size": 11},
    3: {"fill": "DDEBF7", "font_color": "000000", "bold": True, "size": 10},
    4: {"fill": None, "font_color": "000000", "bold": False, "size": 10},
}

# ---------- Карта ----------
CATEGORY_COLORS = {
    B_ENDED: "#e41a1c",
    B_FIRST: "#ff7f00",
    "2027": "#ffe600",
    "2028": "#4daf4a",
    "2029": "#377eb8",
    "2030": "#984ea3",
    B_AFTER: "#f781bf",
    B_NONE: "#999999",
}
FIELD_COLOR = "#8e24aa"  # фіолетовий контур полів
GOOGLE_SAT_URL = "https://mt1.google.com/vt/lyrs=y&hl=uk&gl=ua&x={x}&y={y}&z={z}"
FIELD_TABLES = {
    "Зоря Поділля ТОВ ПК": ("[dbo].[FIELD_84]", "Name"),
    "Поділля ПК ПрАТ": ("[dbo].[FIELD_PKP]", "field_name_old"),
}

PARCEL_COLS = [
    "Кадастровий номер", "Площа, га", "Власник за ДЗК",
    "Сільська рада", "Дата завершення", "Категорія",
]
