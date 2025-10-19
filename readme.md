# 映画情報サイト向け「知識グラフに基づく応答システム（ＫＢＱＡ）」

## プロジェクト概要

このプロジェクトは、豆瓣映画TOP250のデータを活用した対話型ボットシステムです。データクローリングからフロントエンド表示までの全プロセスを網羅し、知識グラフの構築と活用方法を実践的に学習します。

## 主要機能

### 1. データスクレイピング

- `requests`ライブラリを使用
- BeautifulSoup4と正規表現を組み合わせて豆瓣映画TOP250のデータをスクレイピング・解析

### 2. Neo4jグラフデータベース

- Neo4j公式クラウドサービス上でのデータベース構築
- Cypherクエリ言語によるCRUD操作の実装

### 3. テンプレート解析

- 正規表現マッチングによるユーザー質問からの重要情報抽出
- 回答テンプレートを用いたNeo4jからの検索結果取得

### 4. フロントエンドインタラクション

- **UI**: TailwindCSS + Alpine.jsで対話ウィンドウを構築
- **バックエンド**: Flaskでサービスをカプセル化
- フロントエンドとバックエンドの機能統合

---

## 技術的補足

### プロジェクトの特徴

- ゼロから構築する完全な対話型ボットプロジェクト
- データ収集から表示まで、全工程を包括的にカバー

### アプローチについて

複雑な対話プロジェクトでは、意図認識やエンティティ抽出に深層学習モデルが使用されることが一般的です。しかし、本プロジェクトは初めての知識グラフプロジェクトとして、**知識グラフの構築と活用方法**に焦点を当てています。

---

## 実装ステップ

### ステップ1: データクローリング ✅ 完了

#### 実装状況

[data/douban_crawler.py](data/douban_crawler.py)に完全なクローラーが実装済みです。豆瓣映画TOP250の全データを取得し、JSON形式で保存します。

#### 基本情報

- **入口URL**: <https://movie.douban.com/top250>
- **出力ファイル**: `douban_top250_movies.json`
- **データ件数**: 240件（250件中）
  - **注意**: 一部の新規追加映画はWebページ構造が異なるため、現在のパーサーでは解析できません
  - 成功率: 240/250 (96%)
- **データ更新日**: 2025年10月19日

#### 取得データ項目

各映画について以下の情報を取得：

- **基本情報**
  - 映画名（中国語）
  - 映画ID
  - 詳細ページURL
  - 封面画像URL
  - 豆瓣評価スコア

- **制作情報**
  - 監督（名前とURL）
  - 脚本家（名前とURL）
  - 主演俳優（名前とURL）
  - ジャンル
  - 制作国・地域
  - 言語
  - 公開日
  - 上映時間
  - 別名
  - IMDb ID

- **コンテンツ**
  - 映画概要（あらすじ）

#### 実装詳細

**Crawlerクラスの主要メソッド**

1. **`__init__`** ([data/douban_crawler.py:10-13](data/douban_crawler.py#L10-L13))
   - User-Agentヘッダーを設定し、ブラウザアクセスを偽装
   - 豆瓣の反爬虫策に対応

2. **`get_movie_list(url)`** ([data/douban_crawler.py:16-25](data/douban_crawler.py#L16-L25))
   - 指定URLから映画リストページのHTMLを取得
   - BeautifulSoupでCSSセレクタを使用して映画ノードを抽出
   - 映画名とURLのリストを返却

3. **`get_movie_detail(detail)`** ([data/douban_crawler.py:129-164](data/douban_crawler.py#L129-L164))
   - 映画詳細ページから全情報を取得
   - 各種パース関数を呼び出してデータを抽出
   - JSON形式でファイルに追記保存
   - エラーハンドリング機能付き

**パース関数群** (正規表現 + BeautifulSoup)

- `_parse_id`: 映画IDの抽出 ([line 28-30](data/douban_crawler.py#L28-L30))
- `_parse_summary`: 映画概要の抽出 ([line 32-45](data/douban_crawler.py#L32-L45))
- `_parse_directors`: 監督情報の抽出 ([line 47-54](data/douban_crawler.py#L47-L54))
- `_parse_writers`: 脚本家情報の抽出 ([line 56-63](data/douban_crawler.py#L56-L63))
- `_parse_actors`: 主演俳優情報の抽出 ([line 65-72](data/douban_crawler.py#L65-L72))
- `_parse_genres`: ジャンル情報の抽出 ([line 74-81](data/douban_crawler.py#L74-L81))
- `_parse_countries`: 制作国・地域の抽出 ([line 83-88](data/douban_crawler.py#L83-L88))
- `_parse_languages`: 言語情報の抽出 ([line 90-95](data/douban_crawler.py#L90-L95))
- `_parse_pubdates`: 公開日の抽出 ([line 97-104](data/douban_crawler.py#L97-L104))
- `_parse_durations`: 上映時間の抽出 ([line 106-113](data/douban_crawler.py#L106-L113))
- `_parse_other_names`: 別名の抽出 ([line 115-121](data/douban_crawler.py#L115-L121))
- `_parse_imdb`: IMDb IDの抽出 ([line 123-125](data/douban_crawler.py#L123-L125))

#### 技術的なポイント

1. **正規表現フラグ `re.S` の使用**
   - `re.S` (DOTALL) モードで `.` が改行文字も含めて全文字にマッチ
   - 複数行にわたるHTML要素の抽出に必須

2. **BeautifulSoupとの併用**
   - 正規表現で大まかな範囲を抽出
   - BeautifulSoupで精密なHTML解析
   - 2段階処理で柔軟かつ正確な抽出を実現

3. **進捗表示**
   - `tqdm`ライブラリで各ページの処理状況を可視化

4. **エラーハンドリング**
   - `try-except`でエラーを捕捉
   - エラー発生時も処理を継続

#### 実行方法

```bash
python data/douban_crawler.py
```

実行すると、`douban_top250_movies.json` に各映画のデータが1行ずつJSON形式で保存されます。
