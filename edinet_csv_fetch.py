import requests

API_KEY = "e675a431de2a412681794f62c8850a20"
docID = "S100SBBM"

url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{docID}"
params = {
    "type": 2,  # 書類本体（ZIP）
    "Subscription-Key": API_KEY
}

response = requests.get(url, params=params)
if response.status_code != 200:
    print("ダウンロード失敗:", response.status_code, response.text)
    exit()

# ZIPとして保存
zip_filename = f"{docID}.zip"
with open(zip_filename, "wb") as f:
    f.write(response.content)

print(f"ダウンロード完了: {zip_filename}")
