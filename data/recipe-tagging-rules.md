# レシピ特徴タグ判定ルール

このファイルは、ユーザーのスワイプ結果から好みを推定するための特徴タグ判定ルールです。
既存の推薦機能は従来の列を使い続け、新しいタグは追加メタデータとして扱います。

## 入力として使う情報

- YouTubeタイトル
- YouTube概要欄のうち、レシピ説明として使える範囲
- 既存の詳細食材タグ
- 既存の時間・温度・包丁・火の推定列
- `data/recipes-master.csv` の人手確認済みデータ

`recipes-master.csv` に `review_status=confirmed` の行がある場合は、自動判定より優先します。
`review_status=excluded` の行は推薦対象から外します。

## 追加される主な列

- `genre`, `genre_confidence`, `genre_basis`
- `staple`, `staple_confidence`, `staple_basis`
- `dish_shape`, `dish_shape_confidence`, `dish_shape_basis`
- `main_ingredient`, `main_ingredient_confidence`, `main_ingredient_basis`
- `taste_tag`, `taste_tag_confidence`, `taste_tag_basis`
- `temperature_tag`, `temperature_tag_confidence`, `temperature_tag_basis`
- `time_tag`, `time_tag_confidence`, `time_tag_basis`
- `uses_knife_tag`, `uses_knife_tag_confidence`, `uses_knife_tag_basis`
- `uses_heat_tag`, `uses_heat_tag_confidence`, `uses_heat_tag_basis`
- `uses_frying_pan`, `uses_frying_pan_confidence`, `uses_frying_pan_basis`
- `uses_microwave`, `uses_microwave_confidence`, `uses_microwave_basis`
- `tag_review_status`
- `tag_review_reasons`
- `tag_basis_json`

## 判定ルール

### 料理ジャンル

- 韓国: キムチ、ビビンバ、チヂミ、プルコギ、ナムル、スンドゥブ、コチュジャン、ヤンニョムなど
- 中華: チャーハン、餃子、麻婆、天津飯、酢豚、回鍋肉、担々麺、ラーメン、焼きそばなど
- 洋食: パスタ、グラタン、ドリア、オムライス、ハンバーグ、カレー、シチュー、ピザ、トースト、サンド、リゾットなど
- 和食: 和風、照り焼き、生姜焼き、親子丼、牛丼、味噌、醤油、だし、肉じゃが、冷奴、炊き込み、うどん、そばなど
- その他: 上記の根拠が弱いもの

複数ジャンルの語がある場合は、より先に定義された明確なジャンルを採用し、confidenceを下げます。

### 主食

- ご飯: 米、ご飯、丼、炒飯、チャーハン、オムライス、雑炊、リゾット、おにぎりなど
- 麺: うどん、そば、パスタ、ラーメン、そうめん、焼きそば、ビーフン、フォー、春雨など
- パン: 食パン、トースト、サンド、バーガー、ピザ、ホットドッグなど
- その他: 主食タグがないもの

`フライパン`、`ワンパン`、`パン粉` はパン料理の根拠から除外します。

### 料理の形

- 丼: 丼、どんぶり、重、のっけご飯、ご飯に乗せる・かける表現
- 丼以外のご飯もの: リゾット、雑炊、炒飯、チャーハン、オムライス、炊き込み、おにぎり、ドリアなど
- 麺料理: 主食が麺
- パン料理: 主食がパン
- 煮込み: 煮込み、煮物、カレー、シチュー、ポトフ、肉じゃがなど
- 主菜: 肉・魚・卵・豆腐・野菜などの主材料があり、主食料理や煮込みではないもの
- その他: 形の根拠が弱いもの

### 中心食材

- 肉: 牛肉、豚肉、鶏肉、挽肉、ハム、ベーコンなど
- 魚: 鮭、サバ、ブリ、白身魚、アジ、えび、貝、たこ、ツナなど
- 卵: 卵タグ、またはオムライス・チャーハン・オムレツ・卵焼きなど卵の印象が強い料理
- 豆腐・大豆: 豆腐、厚揚げ、油揚げ、大豆、納豆、おからなど
- 野菜中心: 野菜タグが中心で、肉・魚・卵・大豆の主材料が弱いもの
- その他: 中心食材の根拠が弱いもの

### 味

既存の `richness_score` と `taste_level` を元に、以下へ変換します。

- ガッツリ
- ややガッツリ
- ややあっさり
- あっさり

`recipes-master.csv` に `richness` がある場合はそちらを優先します。

### 温度

- 温かい: 焼き、炒め、煮る、揚げる、蒸す、茹でる、丼、ご飯、パン、スープ、鍋、シチューなど
- 冷たい: 冷奴、冷やし、冷製、サラダ、カプレーゼ、ざる、和え、ナムル、漬物など

ご飯系・パン系は原則として温かい料理として扱います。

### 調理時間

タイトル・説明文に `10分` などの分数がある場合はそれを優先します。

- 15分以内
- 15〜30分
- 30分以上

明確な分数がない場合は既存の `時間` 列を使い、confidenceを下げます。

### 調理負荷

- 包丁: 包丁不要・切らないなどはfalse、切る・刻む・みじん切りなどはtrue
- 火: 火を使わない・非加熱などはfalse、焼き・炒め・煮る・揚げる・茹でるなどはtrue
- フライパン: フライパン・ワンパン・炒め・焼きなどはtrue
- 電子レンジ: 電子レンジ・レンジ・レンチンなどはtrue

## 人手確認対象

以下のようにconfidenceが低いものは `data/recipe-tag-review.csv` に抽出します。

- 料理ジャンル、主食、料理の形、中心食材、温度、時間: 0.70未満
- 包丁、火: 0.65未満
- フライパン、電子レンジ: 0.55未満

`tag_review_status` は以下のいずれかです。

- `confirmed`: `recipes-master.csv` で確認済み
- `auto_tagged`: 自動判定済み
- `needs_review`: 人手確認が必要
