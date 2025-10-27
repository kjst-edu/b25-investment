# %%
import requests
import zipfile
import io
import time
from bs4 import BeautifulSoup
from datetime import datetime

class EdinetFinancialAnalyzer:
    BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_documents(self, date):
        """指定日の提出書類を検索"""
        url = f"{self.BASE_URL}/documents.json"
        params = {"date": date, "type": 2}
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def find_company_documents(self, results, company_names, doc_type="120"):
        """特定企業の有価証券報告書を抽出"""
        documents = []
        if results and 'results' in results:
            for doc in results['results']:
                # 有価証券報告書のみ
                if doc['docTypeCode'] == doc_type and doc['filerName'] in company_names:
                    documents.append({
                        'company': doc['filerName'],
                        'docID': doc['docID'],
                        'periodEnd': doc.get('periodEnd', ''),
                        'submitDateTime': doc['submitDateTime']
                    })
        return documents
    
    def download_document(self, doc_id):
        """書類をダウンロード（ZIP形式）"""
        url = f"{self.BASE_URL}/documents/{doc_id}"
        params = {"type": 1}  # 提出本文書
        
        print(f"ダウンロード中: {doc_id}")
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"ダウンロード失敗: {response.status_code}")
            return None
    
    def extract_xbrl_from_zip(self, zip_content):
        """ZIPファイルからXBRLを抽出"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
                # XBRLファイルを探す（通常は PublicDoc フォルダ内）
                xbrl_files = [f for f in z.namelist() 
                             if f.endswith('.xbrl') and 'PublicDoc' in f]
                
                if xbrl_files:
                    with z.open(xbrl_files[0]) as f:
                        return f.read()
        except Exception as e:
            print(f"XBRL抽出エラー: {e}")
        return None
    
    def parse_financial_data(self, xbrl_content):
        """XBRLから財務データを抽出"""
        soup = BeautifulSoup(xbrl_content, 'lxml-xml')
        
        financial_data = {}
        
        # 売上高（複数のタグ名候補）
        sales_tags = [
            'NetSales',  # 売上高
            'OperatingRevenue',  # 営業収益
            'OrdinaryIncome'  # 営業収益（金融機関）
        ]
        
        for tag in sales_tags:
            sales = soup.find(lambda t: t.name and tag in t.name and 'contextRef' in t.attrs)
            if sales and sales.get('contextRef', '').endswith('CurrentYearDuration'):
                financial_data['売上高'] = self._format_amount(sales.text)
                break
        
        # 営業利益
        operating_tags = ['OperatingIncome', 'OperatingProfit']
        for tag in operating_tags:
            op_income = soup.find(lambda t: t.name and tag in t.name and 'contextRef' in t.attrs)
            if op_income and op_income.get('contextRef', '').endswith('CurrentYearDuration'):
                financial_data['営業利益'] = self._format_amount(op_income.text)
                break
        
        # 当期純利益
        net_income = soup.find(lambda t: t.name and 'NetIncome' in t.name and 'contextRef' in t.attrs)
        if net_income and net_income.get('contextRef', '').endswith('CurrentYearDuration'):
            financial_data['当期純利益'] = self._format_amount(net_income.text)
        
        # 総資産
        total_assets = soup.find(lambda t: t.name and 'TotalAssets' in t.name and 'contextRef' in t.attrs)
        if total_assets and total_assets.get('contextRef', '').endswith('CurrentYearInstant'):
            financial_data['総資産'] = self._format_amount(total_assets.text)
        
        # 純資産
        net_assets = soup.find(lambda t: t.name and 'NetAssets' in t.name and 'contextRef' in t.attrs)
        if net_assets and net_assets.get('contextRef', '').endswith('CurrentYearInstant'):
            financial_data['純資産'] = self._format_amount(net_assets.text)
        
        # 自己資本比率を計算
        if '総資産' in financial_data and '純資産' in financial_data:
            try:
                equity_ratio = (financial_data['純資産'] / financial_data['総資産']) * 100
                financial_data['自己資本比率'] = f"{equity_ratio:.2f}%"
            except:
                pass
        
        return financial_data
    
    def _format_amount(self, amount_str):
        """金額を数値に変換（単位：百万円）"""
        try:
            amount = float(amount_str)
            # XBRLは通常、円単位なので百万円に変換
            return int(amount / 1_000_000)
        except:
            return None
    
    def analyze_companies(self, company_names, search_date):
        """複数企業の財務データを取得・分析"""
        print(f"検索日: {search_date}")
        print("=" * 60)
        
        # 書類を検索
        results = self.search_documents(search_date)
        if not results:
            print("検索結果が取得できませんでした")
            return []
        
        # 対象企業の書類を抽出
        documents = self.find_company_documents(results, company_names)
        print(f"\n見つかった書類: {len(documents)}件\n")
        
        all_data = []
        
        for doc in documents:
            print(f"\n企業名: {doc['company']}")
            print(f"期間終了: {doc['periodEnd']}")
            
            # 書類をダウンロード
            zip_content = self.download_document(doc['docID'])
            if not zip_content:
                continue
            
            # XBRLを抽出
            xbrl_content = self.extract_xbrl_from_zip(zip_content)
            if not xbrl_content:
                print("XBRLが見つかりませんでした")
                continue
            
            # 財務データを解析
            financial_data = self.parse_financial_data(xbrl_content)
            
            print("\n【財務データ】")
            for key, value in financial_data.items():
                if isinstance(value, int):
                    print(f"  {key}: {value:,} 百万円")
                else:
                    print(f"  {key}: {value}")
            
            all_data.append({
                'company': doc['company'],
                'period_end': doc['periodEnd'],
                'data': financial_data
            })
            
            print("-" * 60)
            
            # API負荷軽減のため少し待機
            time.sleep(2)
        
        return all_data


# 実行例
if __name__ == "__main__":
    analyzer = EdinetFinancialAnalyzer()
    
    # 分析したい企業（正式名称で指定）
    target_companies = [
        "トヨタ自動車株式会社",
        "ソニーグループ株式会社",
        "株式会社三菱UFJフィナンシャル・グループ",
        "ソフトバンクグループ株式会社"
    ]
    
    # 検索日（有価証券報告書が提出される時期を指定）
    # 3月決算企業なら6月末頃
    search_date = "2024-06-28"
    
    results = analyzer.analyze_companies(target_companies, search_date)
    
    # 結果をまとめて表示
    if results:
        print("\n\n【サマリー】")
        print("=" * 80)
        for result in results:
            print(f"\n{result['company']} ({result['period_end']})")
            for key, value in result['data'].items():
                if isinstance(value, int):
                    print(f"  {key}: {value:,} 百万円")
                else:
                    print(f"  {key}: {value}")

# %%
