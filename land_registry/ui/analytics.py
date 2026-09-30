"""Метрики, зведені таблиці, експорт та деталізація по контрагентах."""
import pandas as pd
import streamlit as st

from ..config import ALL, PARCEL_COLS
from ..exports import XLSX_MIME, make_slug, to_excel
from .filters import Filters
from .map_view import show_contractor_map, show_map


def render_analytics(df: pd.DataFrame, area: pd.DataFrame, cnt: pd.DataFrame, f: Filters) -> None:
    m1, m2, m3 = st.columns(3)
    m1.metric("Контрагентів", len(area))
    m2.metric("Ділянок", df["Кадастровий номер"].nunique())
    m3.metric("Площа, га", f"{area['Разом'].sum():,.2f}")

    if f.council != ALL:
        if st.button("🗺️ Показати на карті (усі контрагенти)"):
            show_map(df, f.main_org)
    else:
        st.caption("Мапа доступна лише для конкретної сільської ради (не для «Всі»).")

    t1, t2 = st.tabs(["Площа, га", "Кількість ділянок"])
    t1.dataframe(area.style.format("{:,.2f}"), width="stretch")
    t2.dataframe(cnt, width="stretch")

    slug = make_slug(f.main_org, f.land_type, f.farm, f.council)
    st.download_button(
        "⬇️ Експорт: усі контрагенти обраного фільтру (підсумок + ділянки)",
        to_excel({
            "Площа": area.reset_index(),
            "Кількість": cnt.reset_index(),
            "Ділянки": df[["Контрагент", *PARCEL_COLS]].sort_values(["Контрагент", "Кадастровий номер"]),
        }),
        file_name=f"{slug}.xlsx",
        mime=XLSX_MIME,
    )

    _render_details(df, area, cnt, f, slug)


def _render_details(df, area, cnt, f: Filters, slug: str) -> None:
    st.subheader("Деталізація по контрагентах")
    for i, name in enumerate(area.index[: f.top_n]):
        contractor_df = df[df["Контрагент"] == name]
        part = contractor_df[PARCEL_COLS].sort_values("Дата завершення")
        with st.expander(f"{name} — {area.loc[name, 'Разом']:,.2f} га · {cnt.loc[name, 'Разом']} діл."):
            st.dataframe(part, width="stretch", hide_index=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "⬇️ Експорт ділянок контрагента",
                    to_excel({"Ділянки": part}),
                    file_name=f"{slug}_{i + 1}.xlsx",
                    mime=XLSX_MIME,
                    key=f"dl_{i}",
                )
            with c2:
                if f.council != ALL:
                    if st.button("🗺️ Показати на карті", key=f"map_{i}"):
                        show_contractor_map(name, contractor_df, f.main_org)
                else:
                    st.caption("Мапа доступна лише для конкретної сільської ради.")
