"""Бізнес-логіка: категорії дат, підготовка даних, зведені таблиці."""
import pandas as pd

from .config import (
    B_AFTER,
    B_ENDED,
    B_FIRST,
    B_NONE,
    BUCKETS,
    FIRST_YEAR,
    SUMMARY_BUCKETS,
    YEARS,
    today,
)


def bucketize(d: pd.Series) -> pd.Series:
    now = today()
    out = pd.Series(B_NONE, index=d.index, dtype="object")
    ok = d.notna()
    out[ok & (d < now)] = B_ENDED
    out[ok & (d >= now) & (d <= pd.Timestamp(FIRST_YEAR, 12, 31))] = B_FIRST
    for y in YEARS:
        out[ok & (d.dt.year == y)] = str(y)
    out[ok & (d.dt.year > YEARS[-1])] = B_AFTER
    return out


def _with_common_columns(raw: pd.DataFrame) -> pd.DataFrame:
    """Контрагент (User_DRRP → User_DZK), площа, дата, категорія."""
    df = raw.copy()
    user = df["User_DRRP"].astype("string").str.strip().replace("", pd.NA)
    user = user.fillna(df["User_DZK"].astype("string").str.strip().replace("", pd.NA))
    df["Контрагент"] = user.fillna("— без користувача —")
    df["Площа, га"] = pd.to_numeric(df["Area_DZK"], errors="coerce").fillna(0)
    df["Дата завершення"] = pd.to_datetime(df["Use_End_Calc"], errors="coerce")
    df["Категорія"] = bucketize(df["Дата завершення"])
    return df


def prepare(raw: pd.DataFrame, koatuu_to_council: dict) -> pd.DataFrame:
    df = _with_common_columns(raw)
    df["Сільська рада"] = df["KOATUU"].astype(str).map(koatuu_to_council)
    df = df.rename(columns={"Cad_Num": "Кадастровий номер", "Owner_DZK": "Власник за ДЗК"})
    # одна ділянка — один раз на контрагента/категорію
    return df.drop_duplicates(["Контрагент", "Кадастровий номер", "Категорія"])


def build_area_count(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Зведення «контрагент × період»: площа та кількість ділянок."""
    area = df.pivot_table(index="Контрагент", columns="Категорія", values="Площа, га",
                          aggfunc="sum", fill_value=0).reindex(columns=BUCKETS, fill_value=0)
    cnt = df.pivot_table(index="Контрагент", columns="Категорія", values="Кадастровий номер",
                         aggfunc="nunique", fill_value=0).reindex(columns=BUCKETS, fill_value=0)
    area["Разом"] = area.sum(axis=1)
    cnt["Разом"] = df.groupby("Контрагент")["Кадастровий номер"].nunique()
    area = area.sort_values("Разом", ascending=False)
    cnt = cnt.loc[area.index]
    return area, cnt


def prepare_summary(raw: pd.DataFrame, directory: pd.DataFrame) -> pd.DataFrame:
    """Всі ділянки реєстру + ієрархія з довідника, обмежено 6 потрібними категоріями."""
    df = raw.copy()
    df["KOATUU"] = df["KOATUU"].astype(str).str.strip()
    df = _with_common_columns(df)
    df = df[df["Категорія"].isin(SUMMARY_BUCKETS)]

    dir_slim = directory[["KOATUU", "MainOrg", "Farm", "Type", "Відділення", "CouncilName"]].copy()
    dir_slim["KOATUU"] = dir_slim["KOATUU"].astype(str).str.strip()
    dir_slim["Відділення"] = dir_slim["Відділення"].fillna("Інформація відсутня")
    dir_slim["CouncilName"] = dir_slim["CouncilName"].fillna("—")

    return df.merge(dir_slim, on="KOATUU", how="inner")


def build_pivot(summary_df: pd.DataFrame) -> pd.DataFrame:
    pivot = summary_df.pivot_table(
        index=["MainOrg", "Farm", "Type", "Відділення", "CouncilName", "Контрагент"],
        columns="Категорія", values="Площа, га", aggfunc="sum", fill_value=0,
    )
    pivot = pivot.reindex(columns=SUMMARY_BUCKETS, fill_value=0)
    pivot["Разом"] = pivot[SUMMARY_BUCKETS].sum(axis=1)
    return pivot.reset_index()
