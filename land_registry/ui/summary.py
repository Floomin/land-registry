"""Блок «Зведена таблиця по підприємствах» (не залежить від бічних фільтрів)."""
import pandas as pd
import streamlit as st

from ..domain import build_pivot, prepare_summary
from ..exports import XLSX_MIME, build_summary_workbook
from ..repository import load_all_parcels


def render_summary_section(directory: pd.DataFrame) -> None:
    with st.expander("📊 Зведена таблиця по підприємствах (усі дані, окрема сторінка на підприємство)"):
        st.caption(
            "Ієрархія: Філія → Тип → Відділення → Сільська рада → Контрагент. "
            "Площа по роках завершення договору: Закінчились / 2026 / 2027 / 2028 / 2029 / 2030. "
            "У Excel рівні можна згортати (кнопки групування зліва від рядків)."
        )
        if st.button("Сформувати зведену таблицю", key="build_summary_btn"):
            st.session_state["summary_ready"] = True

        if not st.session_state.get("summary_ready"):
            return
        with st.spinner("Формую зведену таблицю..."):
            summary_df = prepare_summary(load_all_parcels(), directory)
        if summary_df.empty:
            st.warning("Немає даних для зведеної таблиці.")
            return
        excel_bytes = build_summary_workbook(build_pivot(summary_df))
        st.download_button(
            "⬇️ Завантажити зведену таблицю (Excel)",
            excel_bytes,
            file_name="zvedena_tablytsia.xlsx",
            mime=XLSX_MIME,
            key="summary_download",
        )
