"""Карта ділянок (folium) у модальному вікні."""
import json

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from ..config import CATEGORY_COLORS, FIELD_COLOR, FIELD_TABLES, GOOGLE_SAT_URL
from ..geo import bounds_of_geojson
from ..repository import load_field_geoms, load_parcel_geoms


def _parcel_features(data: pd.DataFrame) -> tuple[list[dict], list[dict]] | None:
    """GeoJSON-фічі ділянок + геометрії для меж. None — повідомлення вже показано."""
    cad_nums = tuple(data["Кадастровий номер"].dropna().astype(str).str.strip().unique())
    if not cad_nums:
        st.info("Немає ділянок для відображення.")
        return None

    parcels_geo = load_parcel_geoms(cad_nums)
    if parcels_geo.empty:
        st.warning("Геометрію не знайдено в PARCEL_ для обраних ділянок.")
        return None

    info = data.copy()
    info["Кадастровий номер"] = info["Кадастровий номер"].astype(str).str.strip()
    info = info.set_index("Кадастровий номер")

    features, geoms = [], []
    for _, row in parcels_geo.iterrows():
        cad = row["cadasrNumb"]
        if cad not in info.index or not row["GeomJson"]:
            continue
        try:
            geom = json.loads(row["GeomJson"])
        except (TypeError, ValueError):
            continue
        props = info.loc[cad]
        if isinstance(props, pd.DataFrame):  # кілька рядків на ту саму ділянку
            props = props.iloc[0]
        geoms.append(geom)
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "cad": cad,
                "category": props["Категорія"],
                "contractor": props["Контрагент"],
                "owner": props["Власник за ДЗК"] or "",
                "area": round(float(props["Площа, га"]), 2),
            },
        })
    return features, geoms


def _field_features(main_org: str) -> list[dict]:
    table_farm = FIELD_TABLES.get(main_org)
    if not table_farm:
        return []
    fields_geo = load_field_geoms(*table_farm)
    out = []
    for _, row in fields_geo.iterrows():
        if not row["GeomJson"]:
            continue
        try:
            geom = json.loads(row["GeomJson"])
        except (TypeError, ValueError):
            continue
        out.append({"type": "Feature", "geometry": geom, "properties": {"field": row["FieldName"]}})
    return out


def render_map(data: pd.DataFrame, main_org: str) -> None:
    result = _parcel_features(data)
    if result is None:
        return
    features, geoms = result
    if not features:
        st.warning("Не вдалося зіставити геометрію з обраними ділянками.")
        return

    bounds = bounds_of_geojson(geoms)
    center = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2]

    fmap = folium.Map(location=center, tiles=None, control_scale=True)
    folium.TileLayer(
        tiles=GOOGLE_SAT_URL, attr="Google", name="Google Супутник", overlay=False,
    ).add_to(fmap)

    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        name="Ділянки",
        style_function=lambda f: {
            "color": CATEGORY_COLORS.get(f["properties"]["category"], "#999999"),
            "weight": 1,
            "fillColor": CATEGORY_COLORS.get(f["properties"]["category"], "#999999"),
            "fillOpacity": 0.45,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["cad", "contractor", "owner", "area", "category"],
            aliases=["Кад. номер", "Контрагент", "Власник", "Площа, га", "Категорія"],
        ),
    ).add_to(fmap)

    field_features = _field_features(main_org)
    if field_features:
        folium.GeoJson(
            {"type": "FeatureCollection", "features": field_features},
            name="Контури полів",
            style_function=lambda f: {"color": FIELD_COLOR, "weight": 2, "fillOpacity": 0},
            tooltip=folium.GeoJsonTooltip(fields=["field"], aliases=["Поле"]),
        ).add_to(fmap)

    folium.LayerControl().add_to(fmap)
    fmap.fit_bounds(bounds)
    st_folium(fmap, width=None, height=650, returned_objects=[])

    legend = " &nbsp; ".join(
        f"<span style='color:{c}'>■</span> {b}" for b, c in CATEGORY_COLORS.items()
    )
    legend += f" &nbsp; <span style='color:{FIELD_COLOR}'>▭</span> Контур поля"
    st.markdown(legend, unsafe_allow_html=True)


@st.dialog("Карта ділянок", width="large")
def show_map(data: pd.DataFrame, main_org: str) -> None:
    render_map(data, main_org)


@st.dialog("Карта ділянок контрагента", width="large")
def show_contractor_map(name: str, data: pd.DataFrame, main_org: str) -> None:
    st.caption(name)
    render_map(data, main_org)
