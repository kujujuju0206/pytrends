# === Library Installation ===
# Uncomment and run this cell first if libraries are not installed
# !pip install requests pandas numpy matplotlib seaborn ipywidgets plotly openpyxl


# === Library Imports ===
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display, clear_output
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# グラフのスタイル設定
plt.style.use('ggplot')
sns.set(style="whitegrid")
from openpyxl import Workbook # Added for excel export


API_KEY = "ebf17c9dfc6a862ee5944ffc434fc959e6a38f35"

# APIエンドポイントと基本リクエストボディの設定
API_CONFIG = {
    'Google': {
        'url': 'https://api.keywordtool.io/v2/search/volume/google',
        'base_body': {
            "apikey": API_KEY,
            "metrics_location": [2392],  # 日本
            "metrics_language": ["ja"],
            "metrics_network": "googlesearchnetwork",
            "metrics_currency": "JPY",
            "output": "json"
        }
    },
    'Instagram': {
        'url': 'https://api.keywordtool.io/v2/search/volume/instagram',
        'base_body': {
            "apikey": API_KEY,
            "country": "JP",
            "metrics_currency": "JPY",
            "complete": False,
            "output": "json"
        }
    },
    'TikTok': {
        'url': 'https://api.keywordtool.io/v2/search/volume/tiktok',
        'base_body': {
            "apikey": API_KEY,
            "country": "JP",
            "metrics_currency": "JPY",
            "complete": False,
            "output": "json"
        }
    }
}

# プラットフォームごとの色設定
PLATFORM_COLORS = {
    'Google': 'blue',
    'Instagram': 'purple',
    'TikTok': 'black'
}


def fetch_data(keywords, platform):
    """指定されたプラットフォームのキーワードデータをAPIから取得する"""
    if platform not in API_CONFIG:
        print(f"未対応のプラットフォーム: {platform}")
        return None

    config = API_CONFIG[platform]
    url = config['url']
    body = config['base_body'].copy()
    body['keyword'] = keywords

    try:
        print(f"{platform}のデータをリクエスト中...")
        
        # APIリクエストの送信
        response = requests.post(
            url=url,
            json=body,
            headers={"Content-Type": "application/json"}
        )
        
        if not response.ok:
            print(f"{platform}のデータ取得エラー: {response.status_code} - {response.text}")
            return None

        data = response.json()
        print(f"{platform}のデータ取得成功")
        return data
        
    except Exception as e:
        print(f"{platform}のデータ取得中にエラーが発生しました: {str(e)}")
        return None

def process_api_data(api_response, keywords):
    """APIレスポンスをグラフ表示に適した形式に処理する"""
    processed_data = {}
    
    # APIレスポンスの検証
    if not api_response or 'results' not in api_response:
        return processed_data

    results = api_response['results']
    
    # 各キーワードのデータを処理
    for keyword in keywords:
        if keyword in results:
            kw_data = results[keyword]
            monthly_trends = {}
            
            # 月別データの抽出
            for i in range(1, 13):
                month_key = f'm{i}'
                year_key = f'm{i}_year'
                month_num_key = f'm{i}_month'
                
                if all(k in kw_data for k in [month_key, year_key, month_num_key]):
                    year = kw_data[year_key]
                    month = kw_data[month_num_key]
                    volume = kw_data[month_key]
                    
                    if year and month and volume is not None:
                        # datetimeオブジェクトを作成してソート可能にする
                        date_key = datetime(year, month, 1)
                        monthly_trends[date_key] = volume
            
            # 日付でソート
            sorted_trends = dict(sorted(monthly_trends.items()))
            
            # 結果を格納
            processed_data[keyword] = {
                'volume': kw_data.get('volume'),
                'cpc': kw_data.get('cpc'),
                'trends': sorted_trends
            }
    
    return processed_data

def create_dataframe(data, platform, period_months=12):
    """処理されたデータからDataFrameを作成する"""
    if not data:
        return None
    
    # 最新の日付を見つける
    latest_date = None
    for kw_data in data.values():
        if kw_data['trends']:
            current_latest = max(kw_data['trends'].keys())
            if latest_date is None or current_latest > latest_date:
                latest_date = current_latest
    
    if latest_date is None:
        return None
    
    # 開始日を計算
    start_year = latest_date.year
    start_month = latest_date.month - period_months + 1
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start_date = datetime(start_year, start_month, 1)
    
    # データフレームを作成
    df_list = []
    
    for keyword, kw_data in data.items():
        trends = kw_data.get('trends', {})
        
        # 期間でフィルタリング
        filtered_trends = {dt: vol for dt, vol in trends.items() if dt >= start_date}
        
        if filtered_trends:
            for dt, volume in filtered_trends.items():
                df_list.append({
                    'date': dt,
                    'year_month': dt.strftime('%Y/%m'),
                    'keyword': keyword,
                    'platform': platform,
                    'volume': volume
                })
    
    if not df_list:
        return None
        
    return pd.DataFrame(df_list)


def plot_trends_matplotlib(df, period_months=12):
    """Matplotlibを使用してトレンドグラフを描画する"""
    if df is None or df.empty:
        print(f"指定された期間 ({period_months}ヶ月) に表示できるデータがありません。")
        return
    
    # プラットフォームとキーワードの組み合わせを取得
    combinations = df.groupby(['platform', 'keyword']).size().reset_index()[['platform', 'keyword']]
    
    # グラフのサイズを設定
    plt.figure(figsize=(12, 8))
    
    # 各組み合わせのデータをプロット
    for _, row in combinations.iterrows():
        platform = row['platform']
        keyword = row['keyword']
        color = PLATFORM_COLORS.get(platform, 'gray')
        
        # フィルタリングしたデータを取得
        subset = df[(df['platform'] == platform) & (df['keyword'] == keyword)]
        subset = subset.sort_values('date')
        
        # プロット
        plt.plot(subset['year_month'], subset['volume'], 
                 marker='o', linestyle='-', linewidth=2, 
                 label=f'{keyword} ({platform})', color=color)
    
    # グラフの設定
    plt.title('キーワード検索ボリューム推移', fontsize=16)
    plt.xlabel('年月', fontsize=12)
    plt.ylabel('検索ボリューム', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='best')
    plt.tight_layout()
    
    plt.show()

def plot_trends_plotly(df, period_months=12):
    """Plotlyを使用してインタラクティブなトレンドグラフを描画する"""
    if df is None or df.empty:
        print(f"指定された期間 ({period_months}ヶ月) に表示できるデータがありません。")
        return
    
    # プラットフォームとキーワードの組み合わせを取得
    combinations = df.groupby(['platform', 'keyword']).size().reset_index()[['platform', 'keyword']]
    
    # Plotlyのグラフオブジェクトを作成
    fig = go.Figure()
    
    # 各組み合わせのデータをプロット
    for _, row in combinations.iterrows():
        platform = row['platform']
        keyword = row['keyword']
        color = PLATFORM_COLORS.get(platform, 'gray')
        
        # フィルタリングしたデータを取得
        subset = df[(df['platform'] == platform) & (df['keyword'] == keyword)]
        subset = subset.sort_values('date')
        
        # プロット
        fig.add_trace(go.Scatter(
            x=subset['year_month'],
            y=subset['volume'],
            mode='lines+markers',
            name=f'{keyword} ({platform})',
            line=dict(color=color, width=2),
            marker=dict(size=8)
        ))
    
    # グラフのレイアウト設定
    fig.update_layout(
        title={
            'text': 'キーワード検索ボリューム推移',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='年月',
        yaxis_title='検索ボリューム',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(240,240,240,0.2)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # グリッド線の設定
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200,200,200,0.2)'
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200,200,200,0.2)'
    )
    
    fig.show()


def generate_demo_data(keywords, platforms, months=12):
    """デモ用のダミーデータを生成する関数"""
    import random
    from datetime import datetime, timedelta
    
    today = datetime.now()
    demo_data = {}
    
    # 各プラットフォームのデータを生成
    for platform in platforms:
        demo_data[platform] = {}
        
        # 各キーワードのデータを生成
        for keyword in keywords:
            # 基本ボリュームを生成
            base_volume = random.randint(5000, 20000)
            
            # CPCを生成
            cpc = round(random.uniform(0.5, 3.0), 2)
            
            # 月別トレンドデータを格納する辞書
            monthly_trends = {}
            
            # 過去months分のデータを生成
            for i in range(months):
                # 日付を計算（現在から過去に遡る）
                date = today - timedelta(days=30 * i)
                date = datetime(date.year, date.month, 1)
                
                # 季節変動要素（1月と7月にピーク）
                month_factor = 1 + 0.2 * abs(((date.month - 1) % 12) / 6 - 1)
                
                # トレンド要素（時間経過で少しずつ増加）
                trend_factor = 1 + 0.05 * (i / months)
                
                # ランダム変動（±10%）
                random_factor = 0.9 + 0.2 * random.random()
                
                # プラットフォーム固有の変動（TikTokは成長率が高い、など）
                platform_factor = 1.0
                if platform == 'TikTok':
                    platform_factor = 1.0 + (0.1 * (months - i) / months)  # 新しいデータほど増加率が高い
                elif platform == 'Instagram':
                    platform_factor = 1.0 + (0.05 * (months - i) / months)
                
                # 最終的なボリュームを計算
                volume = int(base_volume * month_factor / trend_factor * random_factor * platform_factor)
                
                # 結果を格納
                monthly_trends[date] = volume
            
            # キーワードのデータを格納
            demo_data[platform][keyword] = {
                'volume': sum(monthly_trends.values()) // len(monthly_trends),  # 平均値
                'cpc': cpc,
                'trends': monthly_trends
            }
    
    return demo_data

def test_with_demo_data():
    """デモデータを使用してグラフをテスト表示する"""
    # デモデータの生成
    keywords = ['ファッション', '旅行', 'スポーツ']
    platforms = ['Google', 'Instagram', 'TikTok']
    demo_data = generate_demo_data(keywords, platforms, 12)
    
    # DataFrameの作成
    all_dfs = []
    for platform, platform_data in demo_data.items():
        df = create_dataframe(platform_data, platform, 12)
        if df is not None:
            all_dfs.append(df)
    
    # 全てのDataFrameを結合
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # グラフ描画
    print("デモデータでグラフを表示しています...")
    plot_trends_plotly(combined_df, 12)
    print("デモデータでグラフを表示しています。実際のAPIデータではありません。")




def export_to_excel(df, filename='keyword_volume_data.xlsx'):
    """データをExcelファイルにエクスポートする"""
    if df is None or df.empty:
        print("エクスポートするデータがありません。")
        return
    
    # プラットフォームとキーワードの組み合わせごとにシートを作成
    with pd.ExcelWriter(filename) as writer:
        # サマリーシートを作成
        summary = df.pivot_table(
            index=['keyword', 'platform'],
            values='volume',
            aggfunc=['mean', 'min', 'max']
        ).reset_index()
        
        summary.columns = ['キーワード', 'プラットフォーム', '平均ボリューム', '最小ボリューム', '最大ボリューム']
        summary.to_excel(writer, sheet_name='サマリー', index=False)
        
        # 各プラットフォームのシートを作成
        for platform in df['platform'].unique():
            platform_df = df[df['platform'] == platform].copy()
            
            # ピボットテーブルを作成（キーワード×年月）
            pivot_df = platform_df.pivot_table(
                index='keyword',
                columns='year_month',
                values='volume',
                aggfunc='first'
            ).reset_index()
            
            pivot_df.to_excel(writer, sheet_name=platform, index=False)
    
    print(f"データを {filename} にエクスポートしました。")
    return filename


# 検索ボタンの作成
search_button = widgets.Button(
    description='検索',
    button_style='primary',
    tooltip='キーワード検索を実行',
    icon='search'
)

# キーワード入力フィールドの作成
keywords_input = widgets.Text(
    value='',
    placeholder='キーワードをカンマ区切りで入力',
    description='キーワード:',
    disabled=False
)

# プラットフォーム選択チェックボックスの作成
platform_checkboxes = {
    'Google': widgets.Checkbox(value=True, description='Google'),
    'Instagram': widgets.Checkbox(value=False, description='Instagram'),
    'TikTok': widgets.Checkbox(value=False, description='TikTok')
}

# 期間選択ドロップダウンの作成
period_dropdown = widgets.Dropdown(
    options=[('過去12ヶ月', 12), ('過去6ヶ月', 6), ('過去3ヶ月', 3)],
    value=12,
    description='期間:',
    disabled=False,
)

# グラフタイプ選択の作成
plot_type = widgets.RadioButtons(
    options=['Plotly (インタラクティブ)', 'Matplotlib (静的)'],
    value='Plotly (インタラクティブ)',
    description='グラフタイプ:',
    disabled=False
)

# 出力エリアの作成
output = widgets.Output()

# エクスポートボタンの作成
export_button = widgets.Button(
    description='Excelにエクスポート',
    disabled=True,
    button_style='success',
    tooltip='データをExcelファイルにエクスポート',
    icon='file-excel'
)

export_output = widgets.Output()

# グローバル変数で最後に取得したデータを保持
last_data_df = None

# 検索ボタンのイベントハンドラを更新
def on_search_button_clicked_with_export(b):
    global last_data_df
    
    with output:
        clear_output()
        
        # 入力値の取得と検証
        keywords = [kw.strip() for kw in keywords_input.value.split(",") if kw.strip()]
        selected_platforms = [platform for platform, checkbox in platform_checkboxes.items() if checkbox.value]
        period_months = period_dropdown.value
        
        # 入力チェック
        if not keywords:
            print("キーワードを入力してください。")
            export_button.disabled = True
            return
            
        if not selected_platforms:
            print("少なくとも1つのプラットフォームを選択してください。")
            export_button.disabled = True
            return
        
        print("検索を開始します...")
        
        # 各プラットフォームのデータを取得
        all_dfs = []
        
        for platform in selected_platforms:
            # APIからデータを取得
            api_response = fetch_data(keywords, platform)
            
            if api_response:
                # データを処理
                processed_data = process_api_data(api_response, keywords)
                
                if processed_data:
                    # DataFrameを作成
                    df = create_dataframe(processed_data, platform, period_months)
                    
                    if df is not None:
                        all_dfs.append(df)
                    else:
                        print(f"{platform}: 指定された期間のデータがありません。")
                else:
                    print(f"{platform}: データが見つからないか、処理に失敗しました。")
        
        # 結果の検証
        if not all_dfs:
            print("有効なデータが取得できませんでした。グラフは表示されません。")
            export_button.disabled = True
            last_data_df = None
            return
        
        # 全てのDataFrameを結合
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # グローバル変数に保存
        last_data_df = combined_df
        
        # エクスポートボタンを有効化
        export_button.disabled = False
        
        # グラフ描画
        print("グラフを描画中...")
        if plot_type.value == 'Plotly (インタラクティブ)':
            plot_trends_plotly(combined_df, period_months)
        else:
            plot_trends_matplotlib(combined_df, period_months)
        
        print("検索完了")

# エクスポートボタンのイベントハンドラ
def on_export_button_clicked(b):
    with export_output:
        clear_output()
        
        if last_data_df is not None:
            # ファイル名を生成（現在の日時を含む）
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"keyword_volume_data_{timestamp}.xlsx"
            
            # エクスポート実行
            export_to_excel(last_data_df, filename)
        else:
            print("エクスポートするデータがありません。まず検索を実行してください。")

# ボタンにイベントハンドラを設定
search_button.on_click(on_search_button_clicked_with_export)
export_button.on_click(on_export_button_clicked)

# エクスポートボタンとその出力を表示
display(export_button, export_output)


# === Main Execution Block ===
def main():
    print("Keyword Volume Search Tool")
    print("=========================")

    # Get Keywords
    keywords_str = input("Enter keywords (comma-separated, e.g., ファッション, 旅行): ")
    keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    if not keywords:
        print("Error: No keywords entered.")
        return

    # Get Platforms
    print("Select platforms (enter comma-separated numbers, e.g., 1,3):")
    platform_options = ['Google', 'Instagram', 'TikTok']
    for i, p in enumerate(platform_options):
        print(f"  {i+1}. {p}")
    platform_choices_str = input("Enter choices: ")
    try:
        selected_indices = [int(choice.strip()) - 1 for choice in platform_choices_str.split(',') if choice.strip()]
        selected_platforms = [platform_options[i] for i in selected_indices if 0 <= i < len(platform_options)]
    except ValueError:
        print("Error: Invalid platform selection.")
        return
    if not selected_platforms:
        print("Error: No platforms selected.")
        return

    # Get Period
    print("Select period:")
    period_options = {1: 12, 2: 6, 3: 3}
    print("  1. Past 12 months")
    print("  2. Past 6 months")
    print("  3. Past 3 months")
    try:
        period_choice = int(input("Enter choice (1-3): "))
        period_months = period_options.get(period_choice)
        if period_months is None:
            raise ValueError
    except ValueError:
        print("Error: Invalid period selection.")
        return

    # Get Plot Type
    print("Select graph type:")
    plot_options = {1: 'Plotly (インタラクティブ)', 2: 'Matplotlib (静的)'}
    print("  1. Plotly (Interactive)")
    print("  2. Matplotlib (Static)")
    try:
        plot_choice = int(input("Enter choice (1-2): "))
        plot_type_value = plot_options.get(plot_choice)
        if plot_type_value is None:
            raise ValueError
    except ValueError:
        print("Error: Invalid graph type selection.")
        return

    print("Starting search...")

    # Fetch and process data
    all_dfs = []
    last_data_df = None # For export

    for platform in selected_platforms:
        api_response = fetch_data(keywords, platform)
        if api_response:
            processed_data = process_api_data(api_response, keywords)
            if processed_data:
                df = create_dataframe(processed_data, platform, period_months)
                if df is not None:
                    all_dfs.append(df)
                else:
                    print(f"{platform}: No data found for the specified period.")
            else:
                 print(f"{platform}: Could not process API response.")
        # else: fetch_data prints error

    # Combine and plot
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        last_data_df = combined_df # Store for export

        print("Plotting graph...")
        if plot_type_value == 'Plotly (インタラクティブ)':
            plot_trends_plotly(combined_df, period_months)
        else:
            plot_trends_matplotlib(combined_df, period_months)
        print("Search finished.")

        # Ask user if they want to export
        export_choice = input("Export results to Excel? (yes/no): ").lower()
        if export_choice == 'yes':
            if last_data_df is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"keyword_volume_data_{timestamp}.xlsx"
                export_to_excel(last_data_df, filename)
            else:
                print("No data available to export.")

    else:
        print("No data could be retrieved or processed for any platform.")

if __name__ == "__main__":
    main()