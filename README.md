# 調理条件に基づく動画レシピ推薦システム

一人暮らし大学生・若年層を想定した、動画レシピ推薦Webプロトタイプです。

## 目的

料理名で検索するのではなく、味・調理時間・温度・使用食材・調理負荷から「今日作りやすい料理動画」を3件に絞って推薦します。

## 実装内容

- 味の4段階選択
- 調理時間の3段階選択
- 温度の選択
- 食材はカテゴリ選択と個別材料選択を併用し、親カテゴリを選ぶと該当材料をまとめて選択
- 包丁なし・火なしのオプション
- 実在YouTube料理動画1000件の推薦データ
- 推薦カードからYouTube動画をサイト内で埋め込み再生
- 調理負荷、洗い物、工程数を含むスコアリング
- 味の傾向は、個別材料をカテゴリへ変換したうえで材料・油感・投稿者傾向からrichness_scoreを計算し、全レシピの四分位数で4段階分類
- 推薦結果を常に3件だけ表示
- ゆるい料理イラスト背景と食材カテゴリのアイコン表示

## 使い方

YouTube埋め込みを安定して動かすため、`index.html` の直開きではなくローカルサーバー経由で開きます。

```bash
python3 -m http.server 8000
```

ブラウザで次を開きます。

```text
http://127.0.0.1:8000/index.html
```

YouTube Data APIで収集した実在する料理動画1000件を推薦対象にしています。

- 1000件版CSV: `data/1000件料理レシピ.csv`
- API取得元データ: `data/youtube_api_recipes.json`, `data/youtube_api_recipes.csv`
- アプリ用1000件データ: `recipes-data.js`
- 食材カテゴリ味スコア表: `data/ingredient-taste-categories.csv`
- 食材の1人前基準量表: `data/ingredient-serving-standards.csv`
- 材料スコア計算スクリプト: `scripts/ingredient_score.py`
- 食材タグ再精査スクリプト: `scripts/curate_recipe_ingredients.py`
- YouTube検索候補: `data/youtube_candidates.json`
- YouTube公開メタデータ: `data/youtube_details.json`
- 1000件収集スクリプト: `scripts/collect_youtube_api_recipes.py`
- 1000件生成スクリプト: `scripts/build_recipe_dataset.py`
- 品質チェックスクリプト: `scripts/check_recipe_quality.py`
- 人手確認済みデータ台帳: `data/recipes-master.csv`
- 100件監査サンプル作成スクリプト: `scripts/create_recipe_audit_sample.py`
- 旧100件再生成スクリプト: `scripts/collect_recipe_candidates.py`, `scripts/fetch_video_details.py`, `scripts/build_100_recipe_data.py`

推薦カードのサムネイルまたは「サイト内で見る」を押すと、YouTube動画を埋め込み表示します。「YouTubeで開く」から元動画にも移動できます。

CSVにはYouTube埋め込み用の `video_id` 列を持たせています。

外部動画サービスを将来追加できるよう、動画ソースは次の共通列でも管理します。

- `platform`: `youtube`、`instagram`、`tiktok` などのサービス名
- `external_id`: 各サービス側の動画ID
- `video_url`: 各サービスの動画URL

既存の `video_id`、`動画URL`、`url` はYouTube互換用として残しています。

## 1000件データ作成の流れ

YouTube Data APIのキーを環境変数に設定してから実行します。

```bash
export YOUTUBE_API_KEY="取得したAPIキー"
```

1. YouTube Data APIで1000件収集

```bash
python3 scripts/collect_youtube_api_recipes.py --target-count 1000
```

2. 取得データをCSV/JSONに保存

この処理は収集スクリプト内で同時に行います。

- JSON: `data/youtube_api_recipes.json`
- CSV: `data/youtube_api_recipes.csv`

3. 食材抽出・スコア化

```bash
python3 scripts/build_recipe_dataset.py \
  --input data/youtube_api_recipes.json \
  --master-data data/recipes-master.csv \
  --csv-output data/1000件料理レシピ.csv \
  --json-output data/1000_recipes_scored.json \
  --js-output recipes-data.js
```

`data/recipes-master.csv` に `review_status=confirmed` の行がある場合は、YouTube説明文からの自動抽出よりも台帳の `exact_ingredients`、調理時間、包丁、火などを優先します。未確認データは `fact_status=estimated` として出力し、確認済みデータと区別します。

4. 品質チェック

```bash
python3 scripts/check_recipe_quality.py data/1000件料理レシピ.csv --fail-on-warning
```

「卵液不要なのに卵タグが入る」「親子丼に白身魚タグが混入する」など、推薦説明に直結する不整合はP0として検出します。

5. 推薦カードにYouTube埋め込み

`recipes-data.js` が更新されていれば、`index.html` を開くだけで推薦カードから埋め込み再生できます。

## データ修正・監査フロー

修正期間中に公開用データへ戻れるよう、現在のバックアップを `data/backups/20260823/` に置いています。

- `data/backups/20260823/recipes-data.js`
- `data/backups/20260823/recipes-extra.js`

料理データと推薦説明が不整合な場合は、まず `data/recipes-master.csv` に確認済みの正解データを追加します。

主な列:

- `video_id`: YouTube動画ID
- `exact_ingredients`: 正しい食材タグ。カンマ区切り
- `time`, `temperature`, `uses_knife`, `uses_heat`: 確認済みの調理条件
- `reviewer`, `reviewed_at`, `review_status`: 確認者、確認日、確認状態
- `source`, `notes`: 根拠とメモ

100件を層化抽出して人手確認する場合は、次を実行します。

```bash
python3 scripts/create_recipe_audit_sample.py \
  --input data/1000件料理レシピ.csv \
  --output data/recipe-audit-sample.csv \
  --count 100
```

確認済みの修正を反映するときは、必ず `build_recipe_dataset.py` で再生成してから `check_recipe_quality.py --fail-on-warning` を通します。

## スコア列の追加

`ingredient_categories` 列を持つCSVに、`ingredient_score`、`richness_score`、`taste_level` を追加できます。

```bash
python3 scripts/ingredient_score.py input.csv output.csv
```

`詳細食材タグ` から `ingredient_categories` だけを作る場合は、次のコマンドを使います。

```bash
python3 scripts/ingredient_score.py --categories-only input.csv output.csv
```

100件CSVの明らかな誤タグを料理名ベースで再精査する場合は、次のコマンドを使います。

```bash
python3 scripts/curate_recipe_ingredients.py
```

`taste_level` は固定しきい値ではなく、CSV内の全 `richness_score` のQ1、Q2、Q3で分類します。

現在の味スコアは `0.6×材料 + 0.3×油感 + 0.1×投稿者` で計算します。

## 1人前換算

分量付きデータに拡張する場合は、材料量を1人前あたりに統一してから材料スコアを計算します。

例: 豚肉400g・2人前の場合、1人前は200gです。豚肉の標準1人前量を200gと定めているため、肉類のカテゴリスコアをそのまま使います。

個数表記の食材は `data/ingredient-serving-standards.csv` の `unit_g` でg換算します。例: 玉ねぎ1個=200g、卵1個=50g。
