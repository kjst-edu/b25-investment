from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "master_financial_indicators.csv"

META_COLS = ["証券コード", "企業名", "17業種区分", "年度", "提出日", "docID", "EDINETコード", "決算期間"]
ZERO_AS_MISSING_COLS = [
    "営業利益率",
    "ROE",
    "ROA",
    "自己資本比率",
    "流動比率",
    "フリーCF",
    "営業CFマージン",
    "売上高成長率",
    "営業利益成長率",
    "当期純利益成長率",
    "売上高(億円)",
    "営業利益(億円)",
    "当期純利益(億円)",
    "総資産(億円)",
    "自己資本(億円)",
    "流動資産(億円)",
    "流動負債(億円)",
    "固定資産(億円)",
    "負債総額(億円)",
    "営業CF(億円)",
    "投資CF(億円)",
    "財務CF(億円)",
    "フリーCF(億円)"
]

def load_master_financials() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSVが見つかりません: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", low_memory=False)

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

    for c in ZERO_AS_MISSING_COLS:
        if c in df.columns:
            df.loc[df[c] == 0, c] = pd.NA

    return df
