const fetch = require('node-fetch');

// APIキー
const API_KEY = "ebf17c9dfc6a862ee5944ffc434fc959e6a38f35";

// キーワード
const KEYWORDS = ["つばきファクトリー"];

// APIエンドポイントとリクエストボディ
const API_CONFIG = {
  'Google': {
    'url': 'https://api.keywordtool.io/v2/search/volume/google',
    'body': {
      "apikey": API_KEY,
      "metrics_location": [2392],  // 日本
      "metrics_language": ["ja"],
      "metrics_network": "googlesearchnetwork",
      "metrics_currency": "JPY",
      "output": "json",
      "keyword": KEYWORDS
    }
  }
};

// APIリクエスト関数
async function fetchData(platform) {
  if (!API_CONFIG[platform]) {
    console.log(`未対応のプラットフォーム: ${platform}`);
    return null;
  }

  const config = API_CONFIG[platform];
  const url = config.url;
  const body = config.body;

  console.log(`${platform}のデータをリクエスト中...`);
  console.log(`URL: ${url}`);
  console.log(`リクエストボディ:`, body);

  try {
    // APIリクエストの送信
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    console.log(`レスポンスステータス: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`${platform}のデータ取得エラー: ${response.status} - ${errorText}`);
      return null;
    }

    const data = await response.json();
    console.log(`${platform}のデータ取得成功`);
    return data;
  } catch (error) {
    console.error(`${platform}のデータ取得中にエラーが発生しました: ${error.message}`);
    return null;
  }
}

// メイン関数
async function main() {
  console.log(`キーワード "${KEYWORDS.join(', ')}" の検索ボリュームを取得します...`);
  
  const googleData = await fetchData('Google');
  
  if (googleData) {
    console.log('APIレスポンス:');
    console.log(JSON.stringify(googleData, null, 2));
    
    // 結果の処理
    if (googleData.results) {
      for (const keyword of KEYWORDS) {
        if (googleData.results[keyword]) {
          const kwData = googleData.results[keyword];
          console.log(`\n"${keyword}" の検索ボリューム情報:`);
          console.log(`平均検索ボリューム: ${kwData.volume}`);
          console.log(`CPC: ${kwData.cpc}`);
          
          // 月別データの表示
          console.log('\n月別検索ボリューム:');
          for (let i = 1; i <= 12; i++) {
            const monthKey = `m${i}`;
            const yearKey = `m${i}_year`;
            const monthNumKey = `m${i}_month`;
            
            if (kwData[monthKey] && kwData[yearKey] && kwData[monthNumKey]) {
              console.log(`${kwData[yearKey]}年${kwData[monthNumKey]}月: ${kwData[monthKey]}`);
            }
          }
        } else {
          console.log(`キーワード "${keyword}" のデータが見つかりません。`);
        }
      }
    } else {
      console.log('APIレスポンスに結果が含まれていません。');
    }
  }
}

// 実行
main().catch(error => {
  console.error('エラーが発生しました:', error);
});