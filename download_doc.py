import csv
import requests

API_KEY = "e675a431de2a412681794f62c8850a20"

def download_document(doc_id):
    url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
    params = {"type": "2"}
    headers = {"X-API-KEY": API_KEY}
    r = requests.get(url, params=params, headers=headers)

    if r.status_code == 200:
        filename = f"{doc_id}.zip"
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"{doc_id}: ダウンロード完了")
    else:
        print(f"{doc_id}: 失敗（{r.status_code}")


# === CSV の docID を読み込み、有価証券報告書だけDL ===
with open("edinet_documents_2years_ago.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["docTypeCode"] == "120":  # 120 = 有価証券報告書
            download_document(row["docID"])
