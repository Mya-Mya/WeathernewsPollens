# WeathernewsPollens

ウェザーニュースの花粉飛散数データを取得・保存する。

## 導入手順
`CitycodeBookmark.txt`というファイルを作成し、その中に、アプリで参照したい市区町村の市区町村コードとその名前を書く。
市区町村コードと名前は半角スペースで開け、複数登録する場合は改行する。

例えば：
```text
01101 北海道 札幌市中央区
47382 沖縄県 八重山郡与那国町
```

### 参考資料

* [花粉飛散数データ API, Weathernews](https://wxtech.weathernews.com/products/data/api/operations/opendata/getPollenCounts/)
* [市区町村コード一覧, Weathernews](https://wxtech.weathernews.com/products/data/services/opendata-pollen/citycode/)
