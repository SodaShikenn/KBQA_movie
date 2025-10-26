# 映画情報サイト向け「知識グラフに基づく応答システム」

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

---

### ステップ2: 知識グラフの構築 ✅ 完了

#### 実装状況

[build_graph.py](build_graph.py)に完全な知識グラフ構築システムが実装済みです。スクレイピングしたJSON データをNeo4jグラフデータベースに変換し、エンティティ（実体）とリレーション（関係）を構築します。

#### 基本情報

- **入力ファイル**: `data/douban_top250_movies.json`
- **出力先**: Neo4j Cloud データベース
- **エンティティ出力**: `data/entities.txt` (質問応答システムで使用)
- **データベース**: Neo4j+S (クラウドサービス)

#### データモデル

**エンティティタイプ**

1. **MOVIE（映画）ノード**
   - プロパティ:
     - `id`: 映画ID
     - `name`: 映画名
     - `評分`: 豆瓣評価スコア
     - `介绍`: 映画概要（あらすじ）
     - `类型`: ジャンル（複数ある場合は`/`で連結）
     - `国家`: 制作国・地域
     - `语言`: 言語
     - `上映`: 公開日
     - `片长`: 上映時間

2. **PERSON（人物）ノード**
   - プロパティ:
     - `name`: 人物名（監督、脚本家、俳優）

**リレーションタイプ**

1. **導演（監督）**: `(MOVIE)-[:导演]->(PERSON)`
2. **編剧（脚本家）**: `(MOVIE)-[:编剧]->(PERSON)`
3. **主演（主演俳優）**: `(MOVIE)-[:主演]->(PERSON)`

#### 実装詳細

**BuildGraphクラスの主要メソッド**

1. **`__init__()`** ([build_graph.py:12-27](build_graph.py#L12-L27))
   - `entity_data`: エンティティデータを格納する辞書
   - `relation_data`: リレーションデータを格納する辞書
   - Neo4jデータベースへの接続を確立
   - `parse_raw_data()`を自動実行してJSONデータを解析

2. **`parse_raw_data()`** ([build_graph.py:29-86](build_graph.py#L29-L86))
   - JSON ファイルから映画データを読み込み
   - 各映画について以下を実行:
     - 映画エンティティの作成（属性付き）
     - 監督・脚本家・俳優のエンティティ作成（重複排除）
     - 各リレーションの記録

3. **`dump_entities()`** ([build_graph.py:88-103](build_graph.py#L88-L103))
   - 全エンティティ名を`entities.txt`にエクスポート
   - 質問応答システムでのエンティティ認識に使用

4. **`create_entities()`** ([build_graph.py:105-130](build_graph.py#L105-L130))
   - Neo4jにエンティティノードを一括作成
   - Cypher CREATE文を動的に生成
   - 属性値内の特殊文字をエスケープ処理

5. **`create_relations()`** ([build_graph.py:132-164](build_graph.py#L132-L164))
   - Neo4jにリレーションエッジを一括作成
   - UNWIND + MATCH + MERGEパターンを使用
   - 3種類のリレーション（導演、編剧、主演）を作成

#### 技術的なポイント

1. **`defaultdict`の活用**
   - キーの事前定義不要で柔軟なデータ構造を構築

2. **重複排除**
   - 人物エンティティの重複をチェックして効率的に管理

3. **バッチ処理**
   - 複数のCREATE/MERGE文を一度に実行し、パフォーマンスを向上

4. **Cypherクエリパターン**
   - UNWIND: リストを展開
   - MATCH: ノードを検索
   - MERGE: 存在しない場合のみ作成（冪等性を保証）

#### 実行方法

```bash
python build_graph.py
```

実行すると以下の処理が順次実行されます：

1. JSONデータの解析
2. エンティティファイルのエクスポート
3. Neo4jへのエンティティノード作成
4. Neo4jへのリレーションエッジ作成

---

### ステップ3: 質問応答システム ✅ 完了

#### 実装状況

[question_match.py](question_match.py)にテンプレートベースの質問応答システムが実装済みです。ユーザーの自然言語質問から重要情報を抽出し、Neo4jクエリに変換して回答を生成します。

#### 基本情報

- **アプローチ**: テンプレートマッチング + 正規表現
- **サポートする質問タイプ**: 4種類（[config.py:105-133](config.py#L105-L133)に定義）
- **エンティティ認識**: 辞書ベース（`entities.txt`を使用）
- **同義語マッピング**: [config.py:12-103](config.py#L12-L103)に定義

#### サポートする質問テンプレート

1. **タイプ1: エンティティのリレーション先を問う** ([config.py:106-112](config.py#L106-L112))
   - テンプレート: `%ENT%的%REL%是谁/有哪些`
   - 例: 「霸王別姬の監督は誰？」「大話西遊の主演は誰？」
   - Cypher: 映画から指定リレーションで繋がる人物を取得

2. **タイプ2: 人物が関わった映画を問う** ([config.py:113-119](config.py#L113-L119))
   - テンプレート: `%ENT%%REL%过哪些电影`
   - 例: 「張国栄が主演した映画は？」「周星馳が監督した映画は？」
   - Cypher: 人物から指定リレーションで繋がる映画を取得

3. **タイプ3: 2つのエンティティ間の関係を問う** ([config.py:120-126](config.py#L120-L126))
   - テンプレート: `%ENT0%和%ENT1%是什么关系`
   - 例: 「張国栄と霸王別姬の関係は？」
   - Cypher: 2つのエンティティ間のリレーションタイプを取得

4. **タイプ4: エンティティの属性を問う** ([config.py:127-133](config.py#L127-L133))
   - テンプレート: `%ENT%的%ATT%`
   - 例: 「霸王別姬の上映時間は？」「阿甘正伝の評価は？」
   - Cypher: ノードの属性値を取得

#### 実装詳細

**GraphQAクラスの主要メソッド**

1. **`parse_mention_entities(text)`** ([question_match.py:8-16](question_match.py#L8-L16))
   - テキストから映画名・人物名を抽出
   - `entities.txt`の全エンティティとマッチング
   - 正規表現で複数エンティティを同時検出

2. **`parse_mention_attributes(text)`** ([question_match.py:18-20](question_match.py#L18-L20))
   - テキストから属性キーワードを抽出
   - 同義語マップ（[config.py:13-73](config.py#L13-L73)）を使用
   - 例: 「評分」「打分」「分数」→全て「評分」に正規化

3. **`parse_mention_relations(text)`** ([question_match.py:22-24](question_match.py#L22-L24))
   - テキストからリレーションキーワードを抽出
   - 同義語マップ（[config.py:75-102](config.py#L75-L102)）を使用
   - 例: 「主演」「演員」「出演」→全て「主演」に正規化

4. **`get_mention_slots(text)`** ([question_match.py:26-34](question_match.py#L26-L34))
   - 上記3つのパーサーを統合
   - スロット辞書を返す: `{'%ENT%': [...], '%ATT%': [...], '%REL%': [...]}`

5. **`check_slots(cypher_slots, slots)`** ([question_match.py:52-56](question_match.py#L52-L56))
   - テンプレートに必要なスロット数と抽出されたスロット数を比較
   - 不足している場合はテンプレート適用不可と判定

6. **`get_slots_combinations(cypher_slots, slots)`** ([question_match.py:36-50](question_match.py#L36-L50))
   - 複数のエンティティがある場合の組み合わせを生成
   - `itertools.permutations`で順列を生成
   - 例: 2つのエンティティで1つ必要な場合→2通りの組み合わせ

7. **`replace_token_in_string(string, combination)`** ([question_match.py:58-61](question_match.py#L58-L61))
   - テンプレート内のプレースホルダー��実際の値に置換
   - 質問・Cypher・回答の3つを生成

8. **`expand_templates(slots)`** ([question_match.py:63-74](question_match.py#L63-L74))
   - 全テンプレートに対してスロットの適合性をチェック
   - 適合するテンプレートから候補質問・Cypher・回答を生成

9. **`query(text)`** ([question_match.py:77-81](question_match.py#L77-L81))
   - メインエントリーポイント
   - スロット抽出→テンプレート展開→結果出力

#### 技術的なポイント

1. **同義語正規化**
   - 多様な表現を標準形に統一
   - 例: 「片長」「時長」「多長」→「片長」

2. **順列組み合わせ生成**
   - `itertools.permutations`と`itertools.product`を組み合わせ
   - 複数エンティティの全組み合わせパターンを網羅

3. **テンプレートの柔軟性**
   - プレースホルダー（`%ENT%`、`%REL%`、`%ATT%`）で汎用化
   - 新しいテンプレートを`config.py`に追加するだけで拡張可能

4. **正規表現の活用**
   - `|`演算子で複数パターンを同時マッチング
   - 特殊文字（括弧）を除去して安全な正規表現を構築

#### 実行例

[question_match.py:83-87](question_match.py#L83-L87)のサンプルコード：

```python
graph_qa = GraphQA()
graph_qa.query('霸王别姬的片长？')
graph_qa.query('霸王别姬是谁主演的？')
graph_qa.query('张国荣和霸王别姬是什么关系？')
```

---

## 設定ファイル

### [config.py](config.py)

プロジェクト全体の設定を一元管理：

1. **パス設定** ([config.py:1-5](config.py#L1-L5))
   - `BASE_PATH`: プロジェクトルート
   - `RAW_DATA_PATH`: JSON データファイル
   - `ENTITIES_PATH`: エンティティリストファイル

2. **Neo4j接続情報** ([config.py:7-9](config.py#L7-L9))
   - URI、ユーザー名、パスワード

3. **同義語マップ** ([config.py:12-103](config.py#L12-L103))
   - `attributes`: 属性の同義語辞書（7種類の属性）
   - `relations`: リレーションの同義語辞書（3種類のリレーション）

4. **質問テンプレート** ([config.py:105-134](config.py#L105-L134))
   - 4種類の質問パターン定義
   - 各テンプレートは以下を含む:
     - `question`: 質問パターン
     - `cypher`: 対応するCypherクエリ
     - `answer`: 回答フォーマット
     - `slots`: 必要なスロット数
     - `example`: 使用例

---

## 依存パッケージ

[requirements.txt](requirements.txt)に記載：

```
flask                  # Webフレームワーク（将来のフロントエンド用）
Beautifulsoup4         # HTMLパーサー
requests               # HTTPクライアント
pandas                 # データ処理（オプション）
tqdm                   # プログレスバー表示
py2neo                 # Neo4jクライアント
python-Levenshtein     # 文字列類似度計算（オプション）
```

### インストール方法

```bash
pip install -r requirements.txt
```

---

## プロジェクト実行手順

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. データのクローリング（オプション）

既存の`data/douban_top250_movies.json`を使用する場合はスキップ可能：

```bash
python data/douban_crawler.py
```

### 3. 知識グラフの構築

```bash
python build_graph.py
```

実行内容：
- JSONデータを解析
- `data/entities.txt`を生成
- Neo4jにノードとエッジを作成

### 4. 質問応答システムのテスト

```bash
python question_match.py
```

サンプル質問が実行され、スロット抽出結果とテンプレート展開結果が表示されます。

---

## ファイル構成

```
KBQA_movie/
├── config.py              # プロジェクト設定ファイル
├── build_graph.py         # 知識グラフ構築スクリプト
├── question_match.py      # 質問応答システム
├── demo.py                # デモスクリプト
├── requirements.txt       # 依存パッケージ一覧
├── readme.md              # 本ドキュメント
└── data/
    ├── douban_crawler.py          # 豆瓣クローラー
    ├── douban_top250_movies.json  # 映画データ（240件）
    └── entities.txt               # エンティティリスト
```

---

## 今後の拡張予定

### ステップ4: フロントエンドインタラクション（未実装）

- Flaskバックエンドの構築
- TailwindCSS + Alpine.jsでのUI実装
- リアルタイム対話インターフェース

### 改善案

1. **深層学習モデルの導入**
   - 意図認識の精度向上
   - エンティティ抽出の改善（BERTなど）

2. **質問テンプレートの拡張**
   - より複雑な質問パターンのサポート
   - 複数条件を含む質問への対応

3. **あいまい検索の実装**
   - Levenshtein距離による類似検索
   - スペルミス対応

4. **Neo4jクエリの最適化**
   - インデックスの追加
   - クエリパフォーマンスの改善
