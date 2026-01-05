# server/data_loader.py
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "master_financial_indicators.csv"

META_COLS = ["証券コード", "企業名", "17業種区分", "年度", "提出日", "docID", "EDINETコード", "決算期間"]

def load_master_financials() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSVが見つかりません: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", low_memory=False)

    # 型を整える
    df["証券コード"] = df["証券コード"].astype(str).str.zfill(4)
    df["年度"] = pd.to_numeric(df["年度"], errors="coerce").astype("Int64")

    # 数値列をまとめて数値化
    for c in df.columns:
        if c in META_COLS:
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 欠損年度を落とす
    df = df.dropna(subset=["年度"]).copy()
    df["年度"] = df["年度"].astype(int)

    return df
