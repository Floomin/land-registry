"""Усі SQL-запити до БД (з кешуванням Streamlit)."""
import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, text

from .config import TABLE
from .db import get_engine
from .geo import wkt_to_geojson


@st.cache_data(ttl=600)
def load_directory() -> pd.DataFrame:
    q = """
        SELECT KOATUU, MainOrg, Farm, CouncilName, [Type], [Відділення]
        FROM [dbo].[KoatuuDirectory]
        ORDER BY MainOrg, [Type], Farm, CouncilName
    """
    with get_engine().connect() as c:
        return pd.read_sql(text(q), c)


@st.cache_data(ttl=900)
def load_all_parcels() -> pd.DataFrame:
    """Всі ділянки реєстру (без прив'язки до конкретного КОАТУУ) — для зведеної таблиці."""
    q = f"""
        SELECT KOATUU, Area_DZK, User_DRRP, User_DZK, Use_End_Calc
        FROM {TABLE}
        WHERE KOATUU IS NOT NULL
    """
    with get_engine().connect() as c:
        return pd.read_sql(text(q), c)


@st.cache_data(ttl=600)
def load_parcels(koatuu_list: tuple[str, ...]) -> pd.DataFrame:
    q = text(
        f"""
        SELECT KOATUU, Cad_Num, Area_DZK, Owner_DZK, User_DRRP, User_DZK, Use_End_Calc
        FROM {TABLE}
        WHERE KOATUU IN :koatuu_list
        """
    ).bindparams(bindparam("koatuu_list", expanding=True))
    with get_engine().connect() as c:
        return pd.read_sql(q, c, params={"koatuu_list": list(koatuu_list)})


@st.cache_data(ttl=600)
def load_parcel_geoms(cad_list: tuple[str, ...]) -> pd.DataFrame:
    q = text(
        """
        SELECT LTRIM(RTRIM(cadasrNumb)) AS cadasrNumb, Shape.STAsText() AS WKT
        FROM [dbo].[PARCEL_]
        WHERE LTRIM(RTRIM(cadasrNumb)) IN :cad_list
        """
    ).bindparams(bindparam("cad_list", expanding=True))
    with get_engine().connect() as c:
        df = pd.read_sql(q, c, params={"cad_list": list(cad_list)})
    df["GeomJson"] = df["WKT"].apply(wkt_to_geojson)
    # якщо в PARCEL_ трапляються дублі кадастрового номера — беремо перший запис
    return df.drop_duplicates("cadasrNumb", keep="first")


@st.cache_data(ttl=3600)
def load_field_geoms(table: str, name_col: str) -> pd.DataFrame:
    q = f"""
        SELECT [{name_col}] AS FieldName, Shape.STAsText() AS WKT
        FROM {table}
    """
    with get_engine().connect() as c:
        df = pd.read_sql(text(q), c)
    df["GeomJson"] = df["WKT"].apply(wkt_to_geojson)
    return df
