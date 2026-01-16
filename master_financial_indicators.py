import pandas as pd
import numpy as np

# ================= config =================
INPUT_FILE = "master_financial_indicators.csv" 
OUTPUT_FILE = "master_financial_indicators_v2.csv"
# ==========================================

def calculate_master_data():
    print("データを読み込み中...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"エラー: {INPUT_FILE} が見つかりません。")
        return

    # 1. 前処理：重複排除とソート（古い順に並べないと成長率がバグるため）
    df = df.drop_duplicates(subset=["証券コード", "年度"], keep='last')
    df = df.sort_values(["証券コード", "年度"])

    id_cols = ["証券コード", "企業名", "17業種区分", "年度", "提出日", "docID"]
    calc_cols = [
        "売上高", "営業利益", "当期純利益", "総資産", "自己資本", 
        "流動資産", "流動負債", "固定資産", "負債総額", 
        "営業CF", "投資CF", "財務CF"
    ]
    
    for col in calc_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 【重要】0.0を「データなし」に置き換える（キャッシュフロー項目のみ）
    # これにより「不明」な会社を「CFゼロ」と誤判定するのを防ぎます
    cf_cols = ["営業CF", "投資CF", "財務CF"]
    df[cf_cols] = df[cf_cols].replace(0, np.nan)

    print("収益性・安全性の指標を再計算中...")
    
    # --- 収益性 ---
    df["営業利益率"] = np.where(df["売上高"] > 0, (df["営業利益"] / df["売上高"] * 100).round(2), np.nan)
    df["ROE"] = np.where(df["自己資本"] > 0, (df["当期純利益"] / df["自己資本"] * 100).round(2), np.nan)
    df["ROA"] = np.where(df["総資産"] > 0, (df["当期純利益"] / df["総資産"] * 100).round(2), np.nan)
    
    # --- 安全性 ---
    df["自己資本比率"] = np.where(df["総資産"] > 0, (df["自己資本"] / df["総資産"] * 100).round(2), np.nan)
    df["流動比率"] = np.where(df["流動負債"] > 0, (df["流動資産"] / df["流動負債"] * 100).round(2), np.nan)
    df["固定比率"] = (df["固定資産"] / df["自己資本"] * 100).round(2)
    # --- キャッシュフロー ---
    # 片方でもNaNならフリーCFもNaN（不明）になる
    df["フリーCF"] = df["営業CF"] + df["投資CF"]
    df["営業CFマージン"] = np.where(
        (df["売上高"] > 0) & (df["営業CF"].notna()), 
        (df["営業CF"] / df["売上高"] * 100).round(2), 
        np.nan
    )

    print("成長性の指標を計算中...")
    growth_cols = ["売上高成長率", "営業利益成長率", "当期純利益成長率"]
    for col_name, target_col in zip(growth_cols, ["売上高", "営業利益", "当期純利益"]):
        df[col_name] = (
            df.groupby("証券コード")[target_col]
            .pct_change()
            .mul(100)
            .round(2)
        )
    df[growth_cols] = df[growth_cols].fillna(0)

    print("単位の変換（億円）を実行中...")
    unit_cols = calc_cols + ["フリーCF"]
    for col in unit_cols:
        # すでに「億円」列がある場合は上書き、ない場合は新規作成
        df[f"{col}(億円)"] = (df[col] / 100_000_000).round(2)

    # 最終処理
    df = df.replace([np.inf, -np.inf], np.nan)
    all_columns = df.columns.tolist()
    indicator_cols = [c for c in all_columns if c not in id_cols]
    df = df[id_cols + indicator_cols]

    df.to_csv(OUTPUT_FILE, index=False, encoding='utf_8_sig')
    print("-" * 30)
    print(f"成功！ 正確なマスターを作成しました: {OUTPUT_FILE}")

if __name__ == "__main__":
    calculate_master_data()