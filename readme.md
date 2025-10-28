# 映画知識グラフQAシステム

> 豆瓣映画TOP250を対象とした知識グラフベースの質問応答システム。Webスクレイピング、Neo4jグラフデータベース、インテリジェントなクエリマッチング、Webインターフェースを実装。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 機能

- **Webスクレイピング**: 豆瓣映画TOP250からの自動データ収集
- **知識グラフ**: Neo4jベースのグラフデータベース（映画、監督、脚本家、俳優）
- **スマートQAシステム**: テンプレートマッチング + Levenshtein距離による柔軟な質問応答
- **中国語対応**: 同義語マッピングと自然言語処理による中国語クエリのサポート
- **Webインターフェース**: Flaskベースのインタラクティブなチャットシステム

## クイックスタート

### 1. インストールと設定

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# Neo4j接続情報の設定（config.py）
# NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD を設定

# 知識グラフの構築（Neo4j接続が必要）
python build_graph.py
```

### 2. QAシステムの起動

**コマンドラインテスト:**

```bash
python question_match.py
```

**Webインターフェース:**

```bash
python app.py
# ブラウザで http://localhost:5000 にアクセス
```

### 3. クエリ例

```python
graph_qa = GraphQA()
print(graph_qa.query('霸王别姬的片长？'))           # "霸王别姬的片长是：171分钟"
print(graph_qa.query('张国荣主演过哪些电影？'))      # "张国荣主演过的电影：霸王别姬 / ..."
print(graph_qa.query('肖申克的救赎的评分是多少？'))  # "肖申克的救赎的评分是：9.7"
```

## アーキテクチャ

```text
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Webスクレイピング│─────▶│  知識グラフ      │─────▶│   QAシステム     │◄─────│ Webインターフェース│
│  (240本の映画)   │      │  (Neo4j DB)      │      │ (テンプレート +  │      │  (Flask + UI)   │
│                 │      │                  │      │  類似度計算)     │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘      └─────────────────┘
```

### データモデル

**エンティティ:**

- `MOVIE`: 映画名、評価、概要、ジャンル、制作国、言語、公開日、上映時間
- `PERSON`: 監督、脚本家、俳優

**リレーション:**

- `导演`（監督）: MOVIE → PERSON
- `编剧`（脚本家）: MOVIE → PERSON
- `主演`（主演俳優）: MOVIE → PERSON

## 実装

### 1. データ収集 ✅

**ファイル:** [data/douban_crawler.py](data/douban_crawler.py)

`requests`と`BeautifulSoup4`を使用して豆瓣映画TOP250をスクレイピング。

- **データソース**: <https://movie.douban.com/top250>
- **出力**: `douban_top250_movies.json`（240本、成功率96%）
- **データ内容**: 映画メタデータ、監督、脚本家、俳優、評価、概要

**主要コンポーネント:**

- User-Agentスプーフィングを実装した`Crawler`クラス
- 抽出用パースメソッド: ID、概要、監督、脚本家、俳優、ジャンル、制作国、言語、公開日、上映時間、IMDb ID
- `tqdm`による進捗表示
- エラーハンドリングによる堅牢なスクレイピング

**使用方法:**

```bash
python data/douban_crawler.py
```

### 2. 知識グラフの構築 ✅

**ファイル:** [build_graph.py](build_graph.py)

JSONデータをNeo4jグラフデータベースに変換し、エンティティとリレーションを構築。

- **入力**: `data/douban_top250_movies.json`
- **出力**: Neo4j Cloudデータベース + `data/entities.txt`
- **処理フロー**: JSON解析 → ノード作成（MOVIE、PERSON）→ リレーション作成（导演、编剧、主演）

**主要機能:**

- 自動データ解析機能を持つ`BuildGraph`クラス
- PERSONエンティティの重複排除
- バッチCypherクエリ実行（UNWIND + MATCH + MERGEパターン）
- QAシステム用のエンティティエクスポート

**使用方法:**

```bash
python build_graph.py
```

### 3. 質問応答システム ✅

**ファイル:** [question_match.py](question_match.py)

Levenshtein距離による類似度マッチングを備えたテンプレートベースのQAシステム。

**アプローチ:**

- 正規表現 + 同義語マッピングを使用して質問からエンティティ/属性/リレーションを抽出
- 4つの質問テンプレートとマッチング（詳細は[config.py](config.py)を参照）
- Levenshtein類似度を計算（閾値: 0.1）
- Neo4jにCypherクエリを実行
- 自然言語の回答を返す

**サポートする質問タイプ:**

| タイプ | テンプレート | 例 |
|------|----------|---------|
| エンティティ → リレーション | `%ENT%的%REL%是谁` | "霸王别姬的导演是谁?" |
| 人物 → 映画 | `%ENT%%REL%过哪些电影` | "张国荣主演过哪些电影?" |
| エンティティ関係 | `%ENT0%和%ENT1%是什么关系` | "张国荣和霸王别姬是什么关系?" |
| 属性クエリ | `%ENT%的%ATT%` | "霸王别姬的片长?" |

**主要機能:**

- 同義語正規化（例: "评分"、"打分"、"分数" → "评分"）
- `itertools.permutations`によるスロット組み合わせ生成
- Levenshtein距離によるファジーマッチング
- フォールバックメッセージ: "抱歉，没有找到答案！"

**出力例:**

```text
$ python question_match.py

霸王别姬的介绍是：影片借一出《霸王别姬》的京戏，牵扯出三个人之间一段随时代风云变幻的爱恨情仇...
```

### 4. Webインターフェース ✅

**ファイル:** [app.py](app.py), [templates/chat.html](templates/chat.html)

FlaskベースのRESTful APIとインタラクティブなチャットUI。

- **フレームワーク**: Flask
- **エンドポイント**:
  - `GET /`: チャットインターフェース
  - `POST /search`: 質問応答API
- **フロントエンド**: HTML + JavaScript + CSS

**主要機能:**

- リアルタイムチャットUI
- JSON形式のレスポンス
- GraphQAシステムとの統合
- レスポンシブデザイン

**使用方法:**

```bash
python app.py
# ブラウザで http://localhost:5000 にアクセス
```

**APIエンドポイント:**

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"question": "霸王别姬的导演是谁？"}'
```

## プロジェクト構成

```text
kbqa_movie/
├── code/
│   ├── config.py                      # 設定ファイルとテンプレート
│   ├── build_graph.py                 # 知識グラフ構築
│   ├── question_match.py              # QAシステム
│   ├── app.py                         # Flask Webアプリケーション
│   ├── demo.py                        # 開発用テストスニペット
│   ├── requirements.txt               # 依存パッケージ
│   ├── readme.md                      # このファイル（日本語版README）
│   ├── data/
│   │   ├── douban_crawler.py          # Webスクレイパー
│   │   ├── douban_top250_movies.json  # 映画データ（240件）
│   │   └── entities.txt               # マッチング用エンティティリスト
│   └── templates/
│       └── chat.html                  # チャットUIテンプレート
└── Part3_KBQA-movie/                  # 元のコース資料
```

## 設定

[config.py](config.py)の内容:

- **Neo4j接続情報**: URI、ユーザー名、パスワード
- **類似度閾値**: Levenshteinマッチング用の`THRESHOLD = 0.1`
- **同義語マップ**: 7種類の属性タイプ、3種類のリレーションタイプと中国語同義語
- **質問テンプレート**: Cypherクエリと回答フォーマットを含む4種類のテンプレート

## 依存パッケージ

```text
flask              # Webフレームワーク（将来のフロントエンド用）
Beautifulsoup4     # HTMLパーサー
requests           # HTTPクライアント
pandas             # データ処理（オプション）
tqdm               # プログレスバー
py2neo             # Neo4jクライアント
python-Levenshtein # 文字列類似度計算
```

インストール方法:

```bash
pip install -r requirements.txt
```

## 最新の改善内容（2025年10月）

### 完成した機能

- ✅ **Levenshtein距離マッチング**: クエリのバリエーションや誤字に対応
- ✅ **Neo4j統合**: py2neoによる直接的なデータベースクエリ
- ✅ **エラーハンドリング**: 未知のクエリに対するグレースフルなフォールバック
- ✅ **コードドキュメント**: [build_graph.py](build_graph.py)の包括的なdocstring
- ✅ **Webインターフェース**: FlaskベースのインタラクティブなチャットUI
- ✅ **REST API**: JSON形式の質問応答エンドポイント

### テストと開発

- [demo.py](demo.py): Levenshtein距離、スロット組み合わせ、正規表現マッチング、defaultdict操作の単体テスト
- [question_match.py](question_match.py): コマンドラインテストインターフェース
- [app.py](app.py): Flask Webアプリケーション

## 今後の改善予定

### 計画中の機能

- **深層学習モデル**: BERTによる意図認識とエンティティ抽出
- **高度なテンプレート**: 複数条件クエリ、ランキング/比較クエリ（例: "評価が最も高い映画は？"）
- **ファジー検索の強化**: より良いスペル修正、音声マッチング
- **Neo4j最適化**: インデックス作成、クエリパフォーマンスチューニング
- **UI強化**: レスポンシブデザイン、多言語対応、検索履歴

## 備考

- **プロジェクト完成日**: 2025年10月28日
- **データ収集日**: 2025年10月19日
- **データ成功率**: 240/250本（一部の新しい映画は異なるHTML構造を持つ）
- **言語サポート**: 豊富な同義語マッピングによる中国語サポート
- **データベース**: Neo4j Cloud（Neo4j+S プロトコル）
- **開発環境**: Python 3.7+, Flask 3.0+

## 実装状況

| コンポーネント | 状態 | ファイル |
|-------------|------|---------|
| データ収集 | ✅ 完了 | [data/douban_crawler.py](data/douban_crawler.py) |
| 知識グラフ構築 | ✅ 完了 | [build_graph.py](build_graph.py) |
| QAシステム | ✅ 完了 | [question_match.py](question_match.py) |
| REST API | ✅ 完了 | [app.py](app.py) |
| Webインターフェース | ✅ 完了 | [templates/chat.html](templates/chat.html) |
| 設定管理 | ✅ 完了 | [config.py](config.py) |

## ライセンス

[MIT License](LICENSE)

---

**使用技術:** Python 3.7+ | Flask 3.0+ | Neo4j 5.0+ | BeautifulSoup4 | py2neo | Levenshtein
