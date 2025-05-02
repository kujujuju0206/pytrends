#!/usr/bin/env python
import json
from datetime import datetime, timedelta

# APIレスポンスを読み込む
with open('tsubaki-factory-data.json', 'r') as f:
    api_response = json.load(f)
keywords = ["つばきファクトリー"]

# APIレスポンスを処理する関数
def process_api_data(api_response, keywords):
    processed_data = {}
    
    # APIレスポンスの検証
    if not api_response or 'results' not in api_response:
        print("Invalid API response")
        print(f"API response keys: {', '.join(api_response.keys()) if api_response else 'nil'}")
        return processed_data
    
    results = api_response['results']
    print(f"Results keys: {', '.join(results.keys())}")
    
    # 各キーワードを処理
    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        if keyword in results:
            kw_data = results[keyword]
            print(f"Keyword data keys: {', '.join(kw_data.keys())}")
            monthly_trends = {}
            
            # 月別データを抽出
            for i in range(12):
                month_key = f"m{i+1}"
                year_key = f"m{i+1}_year"
                month_num_key = f"m{i+1}_month"
                
                if month_key in kw_data and year_key in kw_data and month_num_key in kw_data:
                    year = kw_data[year_key]
                    month = kw_data[month_num_key]
                    volume = kw_data[month_key]
                    
                    print(f"Month {i+1}: year={year}, month={month}, volume={volume}")
                    
                    if year and month and volume:
                        # 日付キーを作成
                        date_obj = datetime(year, month, 1)
                        date_key = date_obj.strftime('%Y-%m-%d')
                        monthly_trends[date_key] = volume
                else:
                    print(f"Missing data for month {i+1}")
            
            # 日付でソート
            monthly_trends = {k: monthly_trends[k] for k in sorted(monthly_trends.keys())}
            print(f"Monthly trends: {monthly_trends}")
            
            # 処理したデータを保存
            processed_data[keyword] = {
                'volume': kw_data.get('volume'),
                'cpc': kw_data.get('cpc'),
                'trends': monthly_trends
            }
        else:
            print(f"Keyword '{keyword}' not found in results")
    
    print(f"Processed data: {processed_data}")
    return processed_data

# データを処理
processed_data = process_api_data(api_response, keywords)

# 処理結果を表示
print("\n=== 処理結果 ===")
for keyword, data in processed_data.items():
    print(f"\nキーワード: {keyword}")
    print(f"平均検索ボリューム: {data['volume']}")
    print(f"CPC: {data['cpc']}")
    print("\n月別検索ボリューム:")
    
    for date, volume in data['trends'].items():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        print(f"{date_obj.year}年{date_obj.month}月: {volume}")

# Chart.jsで使用するためのデータ形式に変換
chart_data = {
    'Google': processed_data
}

# Chart.jsのデータ形式に変換する関数
def prepare_chart_data(data, period_months=12):
    # 開始日を計算
    today = datetime.now()
    start_date = today - timedelta(days=30 * period_months)
    
    # Chart.js用のデータセットを準備
    datasets = []
    labels = []
    
    # プラットフォームの色
    platform_colors = {
        'Google': 'rgba(66, 133, 244, 1)',
        'YouTube': 'rgba(255, 0, 0, 1)',
        'X': 'rgba(29, 161, 242, 1)',
        'TikTok': 'rgba(238, 29, 82, 1)'
    }
    
    # すべての日付を収集して一貫したラベルを確保
    all_dates = []
    for platform, platform_data in data.items():
        for keyword, keyword_data in platform_data.items():
            for date_str in keyword_data['trends'].keys():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if date_obj >= start_date:
                    all_dates.append(date_obj)
    
    # 日付をソートしてラベルを作成
    all_dates = sorted(list(set(all_dates)))
    labels = [date.strftime('%Y/%m') for date in all_dates]
    
    # データセットを作成
    for platform, platform_data in data.items():
        for keyword, keyword_data in platform_data.items():
            data_points = []
            
            # 各ラベル（日付）に対応する値を見つけるか、Noneを使用
            for date in all_dates:
                date_str = date.strftime('%Y-%m-%d')
                data_points.append(keyword_data['trends'].get(date_str))
            
            # データセットオブジェクトを作成
            datasets.append({
                'label': f"{keyword} ({platform})",
                'data': data_points,
                'borderColor': platform_colors.get(platform, 'gray'),
                'backgroundColor': platform_colors.get(platform, 'gray'),
                'borderWidth': 2,
                'tension': 0.1,
                'pointRadius': 3,
                'pointHoverRadius': 5
            })
    
    return {'labels': labels, 'datasets': datasets}

# Chart.js用のデータを準備
chart_js_data = prepare_chart_data(chart_data)

print("\n=== Chart.js用データ ===")
print(f"ラベル: {', '.join(chart_js_data['labels'])}")
print(f"データセット数: {len(chart_js_data['datasets'])}")
for dataset in chart_js_data['datasets']:
    print(f"  {dataset['label']}: {dataset['data']}")

# Chart.js用のデータをJSONファイルに保存
with open('chart_data.json', 'w') as f:
    json.dump(chart_js_data, f, indent=2)
print("\nChart.js用のデータを chart_data.json に保存しました。")