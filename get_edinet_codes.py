# %%
import requests
import pandas as pd

# 日付を指定（YYYY-MM-DD）
date = "2025-03-31"

url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
params = {"date": date, "type": 2}  # type=2 → 提出書類リスト
res = requests.get(url, params=params)

data = res.json()
df = pd.DataFrame(data["results"])

# 無印良品、トヨタ、ソニーの書類だけ抽出
target_companies = ["良品計画", "トヨタ自動車", "ソニーグループ"]
df_targets = df[df["filerName"].isin(target_companies)]
print(df_targets[["filerName", "docID", "submitDate"]])

# %%
