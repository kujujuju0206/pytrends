# キーワードボリューム検索ツール (Google Colab版)

このツールは、Google、Instagram、TikTokの指定キーワードに対する期間別の検索ボリューム増減推移を表示するGoogle Colabノートブックです。

## 機能

- 複数のキーワードを同時に検索（カンマ区切りで入力）
- Google、Instagram、TikTokの3つのプラットフォームから選択可能
- 過去3ヶ月、6ヶ月、12ヶ月の期間を選択可能
- 検索ボリュームの推移をインタラクティブなグラフで表示
- 各プラットフォームを異なる色で識別（Google: 青、Instagram: 紫、TikTok: 黒）
- データをExcelファイルにエクスポート可能

## 使い方

1. `keyword_volume_tool.ipynb`ファイルをGoogle Colabで開きます
   - [Google Colabで開く](https://colab.research.google.com/github/kujujuju0206/pytrends/blob/pyscript-keyword-tool-v2/keyword_volume_tool.ipynb)
2. すべてのセルを順番に実行します（Runtime > Run all）
3. UIが表示されたら、以下の手順で操作します：
   - キーワード入力欄に検索したいキーワードをカンマ区切りで入力します（例: ファッション, 旅行, スポーツ）
   - プラットフォームを選択します（複数選択可能）
   - 期間を選択します
   - グラフタイプを選択します（Plotly: インタラクティブ、Matplotlib: 静的）
   - 「検索」ボタンをクリックします
4. グラフが表示されるまで待ちます
5. 必要に応じて「Excelにエクスポート」ボタンをクリックし、データをExcelファイルに保存します

## APIについて

このツールは[Keywordtool.io API](https://keywordtool.io/api)を使用しています。APIキーは実際の運用では安全に管理する必要があります。

## デモ機能

APIが利用できない環境でテストするために、デモデータ生成機能が実装されています。ノートブック内の`test_with_demo_data()`関数のコメントを外して実行することで、APIを使わずにデモデータでグラフを表示できます。

## 注意事項

- APIキーは実際の運用では環境変数などから安全に取得する方法を検討してください
- 大量のキーワードを一度に検索すると、APIのレート制限に達する可能性があります
- Google Colabの無料版では、セッションの有効期限や実行時間に制限があります

## 技術スタック

- Python: データ処理とAPI連携
- Pandas: データ操作
- Plotly/Matplotlib: グラフ描画
- ipywidgets: インタラクティブなUI
- Keywordtool.io API: 検索ボリュームデータの取得