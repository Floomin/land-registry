"""Бічні фільтри (каскад) та пошук контрагента."""
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from ..config import ALL, BUCKETS, SUGGEST_N


@dataclass(frozen=True)
class Filters:
    main_org: str
    land_type: str
    farm: str
    council: str
    koatuu_list: tuple[str, ...]
    chosen: list[str]
    search: str
    top_n: int


def render_filters(directory: pd.DataFrame) -> Filters | None:
    """Каскад: Підприємство → Тип → Філія → Сільська рада. None — поки не все обрано."""
    with st.sidebar:
        st.header("Фільтри")
        main_org = st.selectbox(
            "Підприємство", sorted(directory["MainOrg"].dropna().unique()),
            index=None, placeholder="Оберіть підприємство",
        )
    if main_org is None:
        st.info("Оберіть підприємство у фільтрах ліворуч, щоб побачити дані.")
        return None
    d1 = directory[directory["MainOrg"] == main_org]

    with st.sidebar:
        land_type = st.selectbox(
            "Тип", [ALL, *sorted(d1["Type"].dropna().unique())],
            index=None, placeholder="Оберіть тип",
        )
    if land_type is None:
        st.info("Оберіть тип у фільтрах ліворуч.")
        return None
    d2 = d1 if land_type == ALL else d1[d1["Type"] == land_type]

    with st.sidebar:
        farm = st.selectbox(
            "Філія", [ALL, *sorted(d2["Farm"].dropna().unique())],
            index=None, placeholder="Оберіть філію",
        )
    if farm is None:
        st.info("Оберіть філію у фільтрах ліворуч.")
        return None
    d3 = d2 if farm == ALL else d2[d2["Farm"] == farm]

    with st.sidebar:
        council = st.selectbox(
            "Сільська рада", [ALL, *sorted(d3["CouncilName"].dropna().unique())],
            index=None, placeholder="Оберіть сільську раду",
        )
    if council is None:
        st.info("Оберіть сільську раду у фільтрах ліворуч.")
        return None
    d4 = d3 if council == ALL else d3[d3["CouncilName"] == council]
    koatuu_list = tuple(d4["KOATUU"].dropna().unique())

    if not koatuu_list:
        st.warning("Немає КОАТУУ, що відповідають обраним фільтрам.")
        return None

    with st.sidebar:
        chosen = st.multiselect("Період завершення оренди", BUCKETS, default=BUCKETS)
        search = st.text_input("Пошук контрагента")
        top_n = st.number_input("Показувати контрагентів (деталізація)", 1, 500, 30)

    return Filters(main_org, land_type, farm, council, koatuu_list, chosen, search, int(top_n))


def apply_search(df: pd.DataFrame, search: str) -> pd.DataFrame:
    """Фільтр за підрядком + live-підказки в сайдбарі."""
    if not search:
        return df
    matches = sorted(m for m in df["Контрагент"].unique() if search.lower() in m.lower())
    with st.sidebar:
        if matches:
            st.caption(f"Знайдено {len(matches)} · перші {min(SUGGEST_N, len(matches))}:")
            for m in matches[:SUGGEST_N]:
                st.caption(f"• {m}")
        else:
            st.caption("Нічого не знайдено")
    return df[df["Контрагент"].isin(matches)]
