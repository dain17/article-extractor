# article-extractor

Seleniumを用いたスクレイピングによりサイトの情報を取得するツールです．

## Seleniumの準備
ツールを使用する前提として，Seleniumを導入する必要があります．(→[参考](https://qiita.com/Chanmoro/items/9a3c86bb465c1cce738a))

Seleniumは以下のいずれかの方法によって導入できます．
```
# 1. dockerを用いた場合のSeleniumの導入
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome:3.141.59-xenon

# 2. webdriverを用いた場合のSeleniumの導入
# chromedriver-binaryのバージョンには自分のchromeのバージョンを指定する
pip install chromedriver-binary==78.*
```

次にpythonとSeleniumのバインディングを行います．
```
pip install selenium
```

## 実行方法
article-extractorディレクトリの元で以下のコードを入力することで実行できます

```
python src/main.py -d yahoo -c science -n 10 -o ./articles/
```

### オプションについて
|オプション名|非短縮系|説明|デフォルト|
|-|-|-|-|
|-d|--domain|記事を抽出したドメインのキー（factory.pyにて定義）|'yahoo'|
|-c|--category|カテゴリのキー（yahoo.py等にて定義）||
|-n|--num|記事の最大抽出数|10|
|-o|--output|出力先のフォルダ|'./articles/'|

### 看護過去問での実行例など
```
python src/main.py -d kango -c 308 -n 10000
```
- 看護の過去問の抽出においてはカテゴリを101にすると必修問題が，308にすると一般・状況設定問題が抽出されます
    - この番号はURLに使用されている番号と対応します
    - 例えばカテゴリに102を設定した際は，https://www.kango-roo.com/kokushi/kako/102/ 以降が抽出され，https://www.kango-roo.com/kokushi/kako/101/ は抽出されません
- 入力する抽出数が記事数を超える場合は，できる限り抽出されます
    - エラー等で中断された場合，過去に訪れたサイトにはアクセスせずスキップされます

## 参考サイト
[10分で理解する Selenium](https://qiita.com/Chanmoro/items/9a3c86bb465c1cce738a)


