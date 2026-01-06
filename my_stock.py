import yfinance as yf
import pandas as pd
import os

# ==========================================
# 設定エリア
# ==========================================
# 読み込むCSVファイル名
INPUT_CSV = "company_list_2702.csv"

# 証券コードが入っている列名
CODE_COLUMN = "証券コード"

# データの取得期間 (1d, 5d, 1mo, 1y, 5y, max)
PERIOD = "1y"

# 保存先フォルダ名
OUTPUT_DIR = "stock_data"
# ==========================================

def download_stocks_from_csv():
    # 1. CSVから証券コードを読み込む
    if not os.path.exists(INPUT_CSV):
        print(f"エラー: {INPUT_CSV} が見つかりません。ファイル名と場所を確認してください。")
        return

    try:
        # 日本語を含むCSVに対応するため cp932 で読み込み
        try:
            df_master = pd.read_csv(INPUT_CSV, encoding='cp932')
        except:
            df_master = pd.read_csv(INPUT_CSV, encoding='utf-8')

        # 列名の存在チェック
        if CODE_COLUMN not in df_master.columns:
            print(f"エラー: CSV内に '{CODE_COLUMN}' という列名が見つかりません。")
            print(f"現在の列名一覧: {list(df_master.columns)}")
            return

        # 証券コードを取得し、".T" を付与してリスト化
        # 数値の場合は整数にしてから文字列化、欠損値(NaN)は除外
        raw_codes = df_master[CODE_COLUMN].dropna().unique()
        stock_list = []
        for code in raw_codes:
            # 整数にしてから文字列にする（1301.0 のような表示を防ぐ）
            clean_code = str(int(code)) if isinstance(code, float) else str(code)
            stock_list.append(clean_code + ".T")
        
        print(f"CSVから {len(stock_list)} 件の銘柄を読み込みました。")
    
    except Exception as e:
        print(f"CSVの読み込み中にエラーが発生しました: {e}")
        return

    # 2. 保存用フォルダを作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"フォルダ '{OUTPUT_DIR}' を作成しました。")

    # 3. 株価のダウンロード
    print("株価データ取得開始...")

    for ticker_symbol in stock_list:
        try:
            print(f"取得中: {ticker_symbol}...", end="", flush=True)
            
            # yfinanceでデータ取得
            ticker_obj = yf.Ticker(ticker_symbol)
            df = ticker_obj.history(period=PERIOD)

            if df.empty:
                print(" 失敗（データなし。コードが正しいか確認してください）")
                continue

            # 保存パス作成 (例: stock_data/1301.T.csv)
            file_path = os.path.join(OUTPUT_DIR, f"{ticker_symbol}.csv")
            
            # CSV保存
            df.to_csv(file_path)
            print(f" 完了")

        except Exception as e:
            print(f" エラー発生 ({ticker_symbol}): {e}")

    print(f"\nすべての処理が終了しました。'{OUTPUT_DIR}' フォルダ内のCSVを確認してください。")

if __name__ == "__main__":
    download_stocks_from_csv()