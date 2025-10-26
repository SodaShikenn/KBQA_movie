# 映画知識グラフQAシステム

> 豆瓣映画TOP250を対象とした知識グラフベースの質問応答システム。Webスクレイピング、Neo4jグラフデータベース、インテリジェントなクエリマッチングを実装。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 機能

- **Webスクレイピング**: 豆瓣映画TOP250からの自動データ収集
- **知識グラフ**: Neo4jベースのグラフデータベース（映画、監督、脚本家、俳優）
- **スマートQAシステム**: テンプレートマッチング + Levenshtein距離による柔軟な質問応答
- **中国語対応**: 同義語マッピングと自然言語処理による中国語クエリのサポート

## クイックスタート

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 知識グラフの構築（Neo4j接続が必要）
python build_graph.py

# QAシステムのテスト
python question_match.py
```

**クエリ例:**

```python
graph_qa = GraphQA()
print(graph_qa.query('霸王别姬的片长？'))           # "171分钟"
print(graph_qa.query('张国荣主演过哪些电影？'))      # 映画リストを返す
print(graph_qa.query('肖申克的救赎的评分是多少？'))  # "9.7"
```

## アーキテクチャ

```text
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Webスクレイピング│─────▶│  知識グラフ      │─────▶│   QAシステム     │
│  (240本の映画)   │      │  (Neo4j DB)      │      │ (テンプレート +  │
│                 │      │                  │      │  類似度計算)     │
└─────────────────┘      └──────────────────┘      └─────────────────┘
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

171分钟
张国荣 / 张丰毅 / 巩俐 / 葛优
霸王别姬是张国荣的：主演
抱歉，没有找到答案！
弗兰克·德拉邦特 / 斯蒂芬·金
```

## プロジェクト構成

```text
KBQA_movie/
├── config.py                      # 設定ファイルとテンプレート
├── build_graph.py                 # 知識グラフ構築
├── question_match.py              # QAシステム
├── demo.py                        # 開発用テストスニペット
├── requirements.txt               # 依存パッケージ
├── readme.md                      # 英語版README
├── readme_ja.md                   # このファイル（日本語版）
└── data/
    ├── douban_crawler.py          # Webスクレイパー
    ├── douban_top250_movies.json  # 映画データ（240件）
    └── entities.txt               # マッチング用エンティティリスト
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

### QAシステムの強化

- ✅ **Levenshtein距離マッチング**: クエリのバリエーションや誤字に対応
- ✅ **Neo4j統合**: py2neoによる直接的なデータベースクエリ
- ✅ **エラーハンドリング**: 未知のクエリに対するグレースフルなフォールバック
- ✅ **コードドキュメント**: [build_graph.py](build_graph.py)の包括的なdocstring

### テストと開発

- [demo.py](demo.py): Levenshtein距離、スロット組み合わせ、正規表現マッチング、defaultdict操作の単体テスト

## 今後の改善予定

### 計画中の機能

- **深層学習モデル**: BERTによる意図認識とエンティティ抽出
- **高度なテンプレート**: 複数条件クエリ、ランキング/比較クエリ（例: "評価が最も高い映画は？"）
- **ファジー検索の強化**: より良いスペル修正、音声マッチング
- **Neo4j最適化**: インデックス作成、クエリパフォーマンスチューニング

### フロントエンド（未実装）

- FlaskバックエンドAPI
- TailwindCSS + Alpine.js UI
- リアルタイムチャットインターフェース

## 備考

- **データ更新日**: 2025年10月19日
- **成功率**: 240/250本（一部の新しい映画は異なるHTML構造を持つ）
- **言語**: 豊富な同義語マッピングによる中国語サポート
- **データベース**: Neo4j Cloud（Neo4j+S）

## ライセンス

[MIT License](LICENSE)

---

**使用技術:** Python 3.7+ | Neo4j 5.0+ | BeautifulSoup4 | py2neo | Levenshtein
