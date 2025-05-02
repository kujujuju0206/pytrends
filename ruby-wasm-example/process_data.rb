#!/usr/bin/env ruby
require 'json'
require 'date'

# APIレスポンスを読み込む
api_response = JSON.parse(File.read('tsubaki-factory-data.json'))
keywords = ["つばきファクトリー"]

# APIレスポンスを処理する関数
def process_api_data(api_response, keywords)
  processed_data = {}
  
  # APIレスポンスの検証
  if !api_response || !api_response.key?('results')
    puts "Invalid API response"
    puts "API response keys: #{api_response ? api_response.keys.join(', ') : 'nil'}"
    return processed_data
  end
  
  results = api_response['results']
  puts "Results keys: #{results.keys.join(', ')}"
  
  # 各キーワードを処理
  keywords.each do |keyword|
    puts "Processing keyword: #{keyword}"
    if results.key?(keyword)
      kw_data = results[keyword]
      puts "Keyword data keys: #{kw_data.keys.join(', ')}"
      monthly_trends = {}
      
      # 月別データを抽出
      12.times do |i|
        month_key = "m#{i+1}"
        year_key = "m#{i+1}_year"
        month_num_key = "m#{i+1}_month"
        
        if kw_data.key?(month_key) && kw_data.key?(year_key) && kw_data.key?(month_num_key)
          year = kw_data[year_key]
          month = kw_data[month_num_key]
          volume = kw_data[month_key]
          
          puts "Month #{i+1}: year=#{year}, month=#{month}, volume=#{volume}"
          
          if year && month && volume
            # 日付キーを作成
            date_key = Date.new(year, month, 1).strftime('%Y-%m-%d')
            monthly_trends[date_key] = volume
          end
        else
          puts "Missing data for month #{i+1}"
        end
      end
      
      # 日付でソート
      monthly_trends = monthly_trends.sort.to_h
      puts "Monthly trends: #{monthly_trends.inspect}"
      
      # 処理したデータを保存
      processed_data[keyword] = {
        'volume' => kw_data['volume'],
        'cpc' => kw_data['cpc'],
        'trends' => monthly_trends
      }
    else
      puts "Keyword '#{keyword}' not found in results"
    end
  end
  
  puts "Processed data: #{processed_data.inspect}"
  processed_data
end

# データを処理
processed_data = process_api_data(api_response, keywords)

# 処理結果を表示
puts "\n=== 処理結果 ==="
processed_data.each do |keyword, data|
  puts "\nキーワード: #{keyword}"
  puts "平均検索ボリューム: #{data['volume']}"
  puts "CPC: #{data['cpc']}"
  puts "\n月別検索ボリューム:"
  
  data['trends'].each do |date, volume|
    date_obj = Date.parse(date)
    puts "#{date_obj.year}年#{date_obj.month}月: #{volume}"
  end
end

# Chart.jsで使用するためのデータ形式に変換
chart_data = {
  'Google' => processed_data
}

# Chart.jsのデータ形式に変換する関数
def prepare_chart_data(data, period_months=12)
  # 開始日を計算
  today = Date.today
  start_date = today << period_months
  
  # Chart.js用のデータセットを準備
  datasets = []
  labels = []
  
  # プラットフォームの色
  platform_colors = {
    'Google' => 'rgba(66, 133, 244, 1)',
    'YouTube' => 'rgba(255, 0, 0, 1)',
    'X' => 'rgba(29, 161, 242, 1)',
    'TikTok' => 'rgba(238, 29, 82, 1)'
  }
  
  # すべての日付を収集して一貫したラベルを確保
  all_dates = []
  data.each do |platform, platform_data|
    platform_data.each do |keyword, keyword_data|
      keyword_data['trends'].each do |date_str, _|
        date = Date.parse(date_str)
        all_dates << date if date >= start_date
      end
    end
  end
  
  # 日付をソートしてラベルを作成
  all_dates.uniq!.sort!
  labels = all_dates.map { |date| date.strftime('%Y/%m') }
  
  # データセットを作成
  data.each do |platform, platform_data|
    platform_data.each do |keyword, keyword_data|
      data_points = []
      
      # 各ラベル（日付）に対応する値を見つけるか、nullを使用
      all_dates.each do |date|
        date_str = date.strftime('%Y-%m-%d')
        data_points << (keyword_data['trends'][date_str] || nil)
      end
      
      # データセットオブジェクトを作成
      datasets << {
        label: "#{keyword} (#{platform})",
        data: data_points,
        borderColor: platform_colors[platform] || 'gray',
        backgroundColor: platform_colors[platform] || 'gray',
        borderWidth: 2,
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5
      }
    end
  end
  
  { labels: labels, datasets: datasets }
end

# Chart.js用のデータを準備
chart_js_data = prepare_chart_data(chart_data)

puts "\n=== Chart.js用データ ==="
puts "ラベル: #{chart_js_data[:labels].join(', ')}"
puts "データセット数: #{chart_js_data[:datasets].length}"
chart_js_data[:datasets].each do |dataset|
  puts "  #{dataset[:label]}: #{dataset[:data].join(', ')}"
end

# Chart.js用のデータをJSONファイルに保存
File.write('chart_data.json', JSON.pretty_generate(chart_js_data))
puts "\nChart.js用のデータを chart_data.json に保存しました。"