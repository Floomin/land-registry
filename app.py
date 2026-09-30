"""Точка входу Streamlit: uv run streamlit run app.py"""
import streamlit as st

from land_registry.config import PAGE_ICON
from land_registry.domain import build_area_count, prepare
from land_registry.repository import load_directory, load_parcels
from land_registry.ui.analytics import render_analytics
from land_registry.ui.filters import apply_search, render_filters
from land_registry.ui.summary import render_summary_section

st.set_page_config(page_title="Аналіз реєстру земель", layout="wide", page_icon=PAGE_ICON)
st.title("Аналіз реєстру земельних ділянок")

try:
    directory = load_directory()
except Exception as e:  # noqa: BLE001
    st.error(f"Помилка підключення до БД: {e}")
    st.stop()

if directory.empty:
    st.warning("Довідник [KoatuuDirectory] порожній.")
    st.stop()

render_summary_section(directory)

filters = render_filters(directory)
if filters is None:
    st.stop()

koatuu_to_council = dict(zip(directory["KOATUU"].astype(str), directory["CouncilName"], strict=True))
df_all = prepare(load_parcels(filters.koatuu_list), koatuu_to_council)
df_all = df_all[df_all["Категорія"].isin(filters.chosen)]
df = apply_search(df_all, filters.search)

if df.empty:
    st.info("Немає даних за обраними фільтрами.")
    st.stop()

area, cnt = build_area_count(df)
render_analytics(df, area, cnt, filters)
