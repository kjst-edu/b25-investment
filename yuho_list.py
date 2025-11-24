# %%
import pandas as pd

# 元の提出書類リスト（2年間分CSV）
INPUT_CSV = "edinet_documents_2years_ago.csv"
OUTPUT_CSV = "yuho_list.csv"

# CSV読み込み
df = pd.read_csv(INPUT_CSV)

# 1. docTypeCode=120 → 有価証券報告書候補
yuho = df[df["docTypeCode"] == 120]

# 2. docDescription に「有価証券報告書」を含むものだけ
yuho = yuho[yuho["docDescription"].str.contains("有価証券報告書", na=False)]

# 3. 訂正有報を除外
yuho = yuho[~yuho["docDescription"].str.contains("訂正", na=False)]

# 4. filerName でソート（任意）
yuho = yuho.sort_values(by="filerName")

# 5. CSV 出力（UTF-8-SIG で Excelでも文字化け防止）
yuho.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# %%
print(f"有価証券報告書だけを抽出しました → {OUTPUT_CSV}")
# %%
print(f"抽出件数: {len(yuho)} 件")



# %%
