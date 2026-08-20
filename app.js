// Recipe data is loaded from recipes-data.js.

const labels = {
  taste: {
    rich: "ガッツリ",
    "semi-rich": "ややガッツリ",
    "semi-light": "ややあっさり",
    light: "あっさり"
  },
  time: {
    easy: "簡単 〜15分",
    normal: "普通 15〜30分",
    slow: "じっくり 30分〜"
  },
  temperature: {
    warm: "温かい",
    cold: "冷たい"
  },
  ingredients: {
    leafyVegetable: "葉物野菜",
    vegetableAll: "野菜",
    mushroom: "きのこ",
    rootVegetable: "根菜",
    soy: "豆腐・大豆系",
    seafood: "魚介",
    egg: "卵",
    noodle: "麺",
    rice: "米",
    chicken: "鶏肉",
    meat: "肉類",
    richDairy: "チーズ・バター・マヨ系",
    beef: "牛肉",
    pork: "豚肉",
    chicken: "鶏肉",
    minced_meat: "挽肉",
    ham: "ハム",
    bacon: "ベーコン",
    aji: "アジ",
    squid: "いか",
    sardine: "イワシ",
    shrimp: "えび",
    shellfish: "貝",
    oyster: "かき",
    crab: "かに",
    salmon: "サケ",
    mackerel: "サバ",
    saury: "サンマ",
    shirasu: "しらす",
    whitefish: "白身魚",
    octopus: "たこ",
    yellowtail: "ブリ",
    scallop: "ほたて",
    tuna_sashimi: "マグロ",
    asparagus: "アスパラ",
    avocado: "アボカド",
    enoki: "えのき茸",
    turnip: "かぶ",
    pumpkin: "かぼちゃ",
    cabbage: "キャベツ",
    cucumber: "きゅうり",
    burdock: "ごぼう",
    komatsuna: "小松菜",
    sweet_potato: "さつま芋",
    taro: "里芋",
    green_bean: "さやいんげん",
    shishito: "ししとう",
    shimeji: "しめじ",
    potato: "じゃが芋",
    chrysanthemum: "春菊",
    celery: "セロリ",
    daikon: "大根",
    bamboo_shoot: "たけのこ",
    onion: "玉ねぎ",
    bok_choy: "チンゲン菜",
    winter_melon: "冬瓜",
    tomato: "トマト",
    nagaimo: "長芋・大和芋",
    eggplant: "なす",
    shiitake: "生しいたけ",
    nira: "にら",
    carrot: "にんじん",
    green_onion: "ネギ",
    napa_cabbage: "白菜",
    bell_pepper: "ピーマン",
    broccoli: "ブロッコリー",
    bitter_melon: "ゴーヤ",
    corn: "コーン缶",
    spinach: "ほうれん草",
    bean_sprouts: "もやし",
    lettuce: "レタス",
    lotus_root: "レンコン",
    egg: "卵",
    quail_egg: "うずら卵",
    tofu: "豆腐",
    atsuage: "厚揚げ",
    aburaage: "油揚げ",
    soybean: "大豆",
    natto: "納豆",
    okara: "おから",
    wakame: "わかめ",
    kiriboshi_daikon: "切り干し大根",
    kombu: "昆布",
    dried_shiitake: "干しいたけ",
    hijiki: "ひじき",
    fried_fishcake: "さつまあげ",
    seaweed_salad: "海藻サラダ",
    chikuwa: "ちくわ",
    mozuku: "もずく",
    canned_tuna: "ツナ",
    jellyfish: "きくらげ",
    mentaiko: "明太子",
    harusame: "春雨",
    ginger: "ショウガ",
    garlic: "にんにく",
    konnyaku: "こんにゃく",
    rice: "ご飯・米",
    udon: "うどん",
    soba: "そば",
    noodles: "中華麺",
    somen: "そうめん",
    ramen: "ラーメン",
    yakisoba_noodles: "焼きそば麺",
    rice_noodles: "ビーフン・フォー",
    pasta: "パスタ",
    cheese: "チーズ",
    butter: "バター",
    mayonnaise: "マヨネーズ",
    milk: "牛乳",
    flour: "小麦粉",
    bread: "パン",
    richDairy: "チーズ・バター・マヨ系",
    curry_roux: "カレールゥ"
  }
};

const ingredientTasteCategories = [
  {
    id: "leafyVegetable",
    label: "葉物野菜",
    score: 1,
    tags: ["cabbage", "asparagus", "cucumber", "bitter_melon", "green_bean", "shishito", "komatsuna", "chrysanthemum", "celery", "bamboo_shoot", "bok_choy", "winter_melon", "tomato", "eggplant", "napa_cabbage", "nira", "green_onion", "bell_pepper", "broccoli", "spinach", "bean_sprouts", "lettuce"]
  },
  {
    id: "mushroom",
    label: "きのこ",
    score: 2,
    tags: ["enoki", "shimeji", "shiitake", "dried_shiitake", "jellyfish"]
  },
  {
    id: "rootVegetable",
    label: "根菜",
    score: 3,
    tags: ["turnip", "pumpkin", "burdock", "sweet_potato", "taro", "potato", "daikon", "onion", "nagaimo", "carrot", "corn", "lotus_root"]
  },
  {
    id: "soy",
    label: "豆腐・大豆系",
    score: 3,
    tags: ["tofu", "atsuage", "aburaage", "soybean", "natto", "okara"]
  },
  {
    id: "seafood",
    label: "魚介",
    score: 4,
    tags: ["aji", "squid", "sardine", "shrimp", "shellfish", "oyster", "crab", "salmon", "mackerel", "saury", "shirasu", "whitefish", "octopus", "yellowtail", "scallop", "tuna_sashimi", "canned_tuna", "mentaiko", "fried_fishcake", "chikuwa"]
  },
  {
    id: "egg",
    label: "卵",
    score: 5,
    tags: ["egg", "quail_egg"]
  },
  {
    id: "noodle",
    label: "麺",
    score: 6,
    tags: ["udon", "soba", "noodles", "somen", "ramen", "yakisoba_noodles", "rice_noodles", "pasta", "harusame"]
  },
  {
    id: "rice",
    label: "米",
    score: 6,
    tags: ["rice", "bread", "flour"]
  },
  {
    id: "chicken",
    label: "鶏肉",
    score: 6,
    tags: ["chicken"]
  },
  {
    id: "meat",
    label: "肉類",
    score: 8,
    tags: ["beef", "pork", "minced_meat", "ham", "bacon"]
  },
  {
    id: "richDairy",
    label: "チーズ・バター・マヨ系",
    score: 10,
    tags: ["cheese", "butter", "mayonnaise", "milk"]
  }
];

const ingredientTasteCategoryById = ingredientTasteCategories.reduce((map, category) => {
  map[category.id] = category;
  return map;
}, {});

const ingredientTasteCategoryByTag = ingredientTasteCategories.reduce((map, category) => {
  category.tags.forEach((tag) => {
    map[tag] = category;
  });
  return map;
}, {});

const ingredientTasteCategoryIds = new Set(ingredientTasteCategories.map((category) => category.id));

const uncategorizedLightVegetableTags = [
  "asparagus",
  "green_bean",
  "shishito",
  "celery",
  "bamboo_shoot",
  "winter_melon",
  "tomato",
  "eggplant",
  "bell_pepper",
  "broccoli",
  "garlic",
  "ginger",
  "kiriboshi_daikon",
  "konnyaku",
  "wakame",
  "kombu",
  "hijiki",
  "seaweed_salad",
  "mozuku",
  "jellyfish",
  "curry_roux"
];

const fallbackMaterialScoreByTag = uncategorizedLightVegetableTags.reduce((map, tag) => {
  map[tag] = 3;
  return map;
}, {});

const preferredIngredientTasteScore = {
  light: 2,
  "semi-light": 4,
  "semi-rich": 6.5,
  rich: 8.5
};

const tasteDistance = {
  rich: { rich: 0, "semi-rich": 1, "semi-light": 2, light: 3 },
  "semi-rich": { rich: 1, "semi-rich": 0, "semi-light": 1, light: 2 },
  "semi-light": { rich: 2, "semi-rich": 1, "semi-light": 0, light: 1 },
  light: { rich: 3, "semi-rich": 2, "semi-light": 1, light: 0 }
};

const timeDistance = {
  easy: { easy: 0, normal: 1, slow: 2 },
  normal: { easy: 1, normal: 0, slow: 1 },
  slow: { easy: 2, normal: 1, slow: 0 }
};

const form = document.querySelector("#recommendForm");
const recommendations = document.querySelector("#recommendations");
const summaryStrip = document.querySelector("#summaryStrip");
const template = document.querySelector("#recipeCardTemplate");
const ingredientDialog = document.querySelector("#ingredientDialog");
const openIngredientSelector = document.querySelector("#openIngredientSelector");
const closeIngredientSelector = document.querySelector("#closeIngredientSelector");
const backIngredientSelector = document.querySelector("#backIngredientSelector");
const confirmIngredientSelector = document.querySelector("#confirmIngredientSelector");
const clearIngredientSelector = document.querySelector("#clearIngredientSelector");
const ingredientCount = document.querySelector("#ingredientCount");
const selectedIngredients = document.querySelector("#selectedIngredients");
const videoDialog = document.querySelector("#videoDialog");
const closeVideoDialog = document.querySelector("#closeVideoDialog");
const videoDialogTitle = document.querySelector("#videoDialogTitle");
const videoFrameWrap = document.querySelector("#videoFrameWrap");
const searchButton = document.querySelector("#searchButton");
const changeConditionsLink = document.querySelector("#changeConditionsLink");
const brandHomeLink = document.querySelector("#brandHomeLink");

const defaultConditions = {
  taste: "",
  time: "",
  temperature: "",
  ingredients: [],
  noKnife: false,
  noHeat: false
};

const ingredientChoiceIdsByGroup = {
  meat: ["beef", "pork", "minced_meat", "ham", "bacon"],
  seafood: ["aji", "squid", "sardine", "shrimp", "shellfish", "oyster", "crab", "salmon", "mackerel", "saury", "shirasu", "whitefish", "octopus", "yellowtail", "scallop", "tuna_sashimi", "canned_tuna", "mentaiko"],
  vegetableAll: ["leafyVegetable", "rootVegetable", "cabbage", "cucumber", "komatsuna", "bok_choy", "napa_cabbage", "nira", "green_onion", "spinach", "bean_sprouts", "lettuce", "turnip", "pumpkin", "burdock", "sweet_potato", "taro", "potato", "daikon", "onion", "nagaimo", "carrot", "lotus_root", "tomato", "eggplant", "bell_pepper", "broccoli"],
  leafyVegetable: ["cabbage", "cucumber", "komatsuna", "bok_choy", "napa_cabbage", "nira", "green_onion", "spinach", "bean_sprouts", "lettuce"],
  rootVegetable: ["turnip", "pumpkin", "burdock", "sweet_potato", "taro", "potato", "daikon", "onion", "nagaimo", "carrot", "lotus_root"],
  mushroom: ["enoki", "shimeji", "shiitake", "dried_shiitake", "jellyfish"],
  egg: ["quail_egg"],
  soy: ["tofu", "atsuage", "aburaage", "soybean", "natto", "okara"],
  noodle: ["pasta", "udon", "soba", "noodles", "somen", "ramen", "yakisoba_noodles", "rice_noodles", "harusame"],
  richDairy: ["cheese", "butter"]
};

function readConditions() {
  if (!form) return readConditionsFromUrl();

  const formData = new FormData(form);
  return {
    taste: formData.get("taste") || "",
    time: formData.get("time") || "",
    temperature: formData.get("temperature") || "",
    ingredients: formData.getAll("ingredients"),
    noKnife: formData.has("noKnife"),
    noHeat: formData.has("noHeat")
  };
}

function readConditionsFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
    taste: params.get("taste") || "",
    time: params.get("time") || "",
    temperature: params.get("temperature") || "",
    ingredients: params.getAll("ingredients"),
    noKnife: params.get("noKnife") === "1",
    noHeat: params.get("noHeat") === "1"
  };
}

function isReloadNavigation() {
  const [navigation] = performance.getEntriesByType ? performance.getEntriesByType("navigation") : [];
  if (navigation) return navigation.type === "reload";
  return performance.navigation && performance.navigation.type === 1;
}

function clearConditionUrl() {
  if (!window.location.search) return;
  window.history.replaceState({}, "", `${window.location.pathname}${window.location.hash}`);
}

function readInitialFormConditions() {
  if (!isReloadNavigation()) return readConditionsFromUrl();
  clearConditionUrl();
  return defaultConditions;
}

function buildConditionsQuery(conditions) {
  const params = new URLSearchParams();
  if (conditions.taste) params.set("taste", conditions.taste);
  if (conditions.time) params.set("time", conditions.time);
  if (conditions.temperature) params.set("temperature", conditions.temperature);
  conditions.ingredients.forEach((item) => params.append("ingredients", item));
  if (conditions.noKnife) params.set("noKnife", "1");
  if (conditions.noHeat) params.set("noHeat", "1");
  return params.toString();
}

function buildPageUrl(page, conditions) {
  const query = buildConditionsQuery(conditions);
  return query ? `${page}?${query}` : page;
}

function applyConditionsToForm(conditions) {
  if (!form) return;

  ["taste", "time", "temperature"].forEach((name) => {
    form.querySelectorAll(`input[name="${name}"]`).forEach((input) => {
      input.checked = false;
    });
    const input = form.querySelector(`input[name="${name}"][value="${conditions[name]}"]`);
    if (input) input.checked = true;
  });

  form.querySelectorAll('input[name="ingredients"]').forEach((input) => {
    input.checked = conditions.ingredients.includes(input.value);
    input.indeterminate = false;
  });

  const noKnife = form.querySelector('input[name="noKnife"]');
  const noHeat = form.querySelector('input[name="noHeat"]');
  if (noKnife) noKnife.checked = conditions.noKnife;
  if (noHeat) noHeat.checked = conditions.noHeat;
}

function goToResults() {
  window.location.href = buildPageUrl("results.html", readConditions());
}

function hasActiveConditions(conditions) {
  return Boolean(
    conditions.taste ||
    conditions.time ||
    conditions.temperature ||
    conditions.noKnife ||
    conditions.noHeat ||
    conditions.ingredients.length > 0
  );
}

function getRandomRecommendations(recipeList) {
  const shuffled = recipeList.slice();
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
  }

  return shuffled.map((recipe) => ({
    ...recipe,
    score: 0,
    reasons: ["条件なしでランダムに選びました"]
  }));
}

function scoreRecipe(recipe, conditions) {
  let score = 0;
  const reasons = [];

  const richnessProfile = getTentativeRichnessProfile(recipe);
  if (conditions.taste && preferredIngredientTasteScore[conditions.taste]) {
    const tasteScore = Math.max(
      0,
      28 - Math.abs(preferredIngredientTasteScore[conditions.taste] - richnessProfile.score) * 4
    );
    score += tasteScore;
    if (tasteScore >= 18) reasons.push(`味の傾向が「${labels.taste[conditions.taste]}」に近い`);
  }

  if (conditions.time && timeDistance[conditions.time]) {
    const timeScore = Math.max(0, 22 - timeDistance[conditions.time][recipe.time] * 9);
    score += timeScore;
    if (timeScore >= 13) reasons.push(`調理時間が「${labels.time[conditions.time]}」に合う`);
  }

  if (conditions.temperature && recipe.temperature === conditions.temperature) {
    score += 16;
    reasons.push(`${labels.temperature[conditions.temperature]}料理として作りやすい`);
  }

  const recipeIngredientProfile = getIngredientTasteProfile(recipe);
  const recipeIngredientCategoryIds = recipeIngredientProfile.categoryIds;
  const recipeIngredientTags = recipe.detailedIngredients || [];
  const selectedIngredientProfile = getSelectedIngredientProfile(conditions.ingredients);
  const matchedIngredientTags = selectedIngredientProfile.tagIds.filter((item) => recipeIngredientTags.includes(item));
  const matchedIngredientCategories = selectedIngredientProfile.categoryIds.filter((item) => recipeIngredientCategoryIds.includes(item));
  if (matchedIngredientTags.length > 0) {
    score += Math.min(22, matchedIngredientTags.length * 12);
    reasons.push(`使用食材: ${matchedIngredientTags.map((item) => labels.ingredients[item] || item).join("・")}`);
  } else if (matchedIngredientCategories.length > 0) {
    score += Math.min(20, matchedIngredientCategories.length * 10);
    reasons.push(`使用カテゴリ: ${matchedIngredientCategories.map((item) => labels.ingredients[item] || item).join("・")}`);
  } else if (conditions.ingredients.length === 0) {
    score += 4;
  } else {
    score -= 8;
  }

  const loadBonus = Math.max(0, 14 - recipe.effort * 3 - recipe.dishes * 2);
  score += loadBonus;
  if (recipe.effort <= 2 && recipe.dishes <= 2) reasons.push("工程数と洗い物が少なめ");

  if (conditions.noKnife) {
    if (!recipe.knife) {
      score += 14;
      reasons.push("包丁を使わずに作れる");
    } else {
      score -= 18;
    }
  }

  if (conditions.noHeat) {
    if (!recipe.heat) {
      score += 14;
      reasons.push("火を使わずに作れる");
    } else {
      score -= 18;
    }
  }

  score += Math.max(0, 7 - recipe.oil);

  return {
    ...recipe,
    score: Math.max(0, Math.round(score)),
    reasons: reasons.slice(0, 4)
  };
}

function getSelectedIngredientProfile(selectedIds) {
  const categoryIds = new Set();
  const tagIds = new Set();

  selectedIds.forEach((id) => {
    if (ingredientTasteCategoryIds.has(id)) {
      categoryIds.add(id);
    }

    const category = ingredientTasteCategoryByTag[id];
    if (category) {
      tagIds.add(id);
      categoryIds.add(category.id);
    }
  });

  return {
    categoryIds: Array.from(categoryIds),
    tagIds: Array.from(tagIds)
  };
}

function getTrustedUrl(rawUrl, allowedHosts) {
  try {
    const url = new URL(rawUrl);
    if (url.protocol !== "https:") return "";
    if (!allowedHosts.some((host) => url.hostname === host || url.hostname.endsWith(`.${host}`))) return "";
    return url.href;
  } catch {
    return "";
  }
}

function getTrustedYoutubeUrl(rawUrl) {
  return getTrustedUrl(rawUrl, ["youtube.com", "youtu.be"]);
}

function getTrustedVideoUrl(rawUrl) {
  return getTrustedUrl(rawUrl, ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "vt.tiktok.com"]);
}

function getTrustedThumbnailUrl(rawUrl) {
  return getTrustedUrl(rawUrl, ["ytimg.com"]);
}

function getVideoPlatform(recipe) {
  return String(recipe.platform || "youtube").toLowerCase();
}

function buildVideoUrl(recipe) {
  const trustedRecipeUrl = getTrustedVideoUrl(recipe.videoUrl || recipe.url || "");
  if (trustedRecipeUrl) return trustedRecipeUrl;
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(`${recipe.creator} ${recipe.title}`)}`;
}

function buildYoutubeUrl(recipe) {
  return buildVideoUrl(recipe);
}

function getYoutubeVideoId(recipe) {
  if (getVideoPlatform(recipe) !== "youtube") return "";
  if (recipe.externalId) return recipe.externalId;
  if (recipe.videoId) return recipe.videoId;
  const source = recipe.videoUrl || recipe.url || "";
  const match = source.match(/(?:shorts\/|youtu\.be\/|v=)([A-Za-z0-9_-]{11})/);
  return match ? match[1] : "";
}

function getYoutubeThumbnail(recipe) {
  const trustedThumbnailUrl = getTrustedThumbnailUrl(recipe.thumbnailUrl || "");
  if (trustedThumbnailUrl) return trustedThumbnailUrl;
  const videoId = getYoutubeVideoId(recipe);
  if (!videoId) {
    return "assets/hero-illustration.svg";
  }
  return `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
}

function buildYoutubeEmbedUrl(recipe, autoplay = false) {
  const videoId = getYoutubeVideoId(recipe);
  if (!videoId) return "";
  const params = new URLSearchParams({
    rel: "0",
    playsinline: "1",
    modestbranding: "1"
  });
  if (autoplay) params.set("autoplay", "1");
  if (/^https?:$/.test(window.location.protocol) && window.location.origin) {
    params.set("origin", window.location.origin);
  }
  return `https://www.youtube.com/embed/${videoId}?${params.toString()}`;
}

function createYoutubeIframe(recipe, autoplay = false) {
  const embedUrl = buildYoutubeEmbedUrl(recipe, autoplay);
  if (!embedUrl) return null;

  const iframe = document.createElement("iframe");
  iframe.src = embedUrl;
  iframe.title = recipe.title;
  iframe.loading = "lazy";
  iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
  iframe.allowFullscreen = true;
  return iframe;
}

function loadVideoIntoFrame(videoFrame, loadButton, recipe) {
  const iframe = createYoutubeIframe(recipe, true);
  if (!iframe) {
    window.open(buildVideoUrl(recipe), "_blank", "noopener");
    return;
  }

  loadButton.hidden = true;
  videoFrame.classList.add("is-playing");
  videoFrame.appendChild(iframe);
}

function getIngredientTasteProfile(recipe) {
  const tags = recipe.detailedIngredients || [];
  const categories = [];
  const seenCategoryIds = new Set();
  const materialScores = [];

  tags.forEach((tag) => {
    const category = ingredientTasteCategoryByTag[tag];
    if (category) {
      materialScores.push(category.score);
      if (!seenCategoryIds.has(category.id)) {
        seenCategoryIds.add(category.id);
        categories.push(category);
      }
      return;
    }
    if (fallbackMaterialScoreByTag[tag]) {
      materialScores.push(fallbackMaterialScoreByTag[tag]);
    }
  });

  if (materialScores.length === 0) {
    return {
      score: 5,
      categoryIds: [],
      categories: ["未分類"]
    };
  }

  const average = materialScores.reduce((sum, score) => sum + score, 0) / materialScores.length;
  return {
    score: Math.round(average * 10) / 10,
    categoryIds: categories.map((category) => category.id),
    categories: categories
      .slice()
      .sort((a, b) => a.score - b.score)
      .map((category) => category.label)
  };
}

function getCreatorTasteScore(recipe) {
  const text = `${recipe.creator || ""} ${recipe.style || ""}`;
  if (/リュウジ|バズレシピ|だれウマ|まるみ|がっつり|ガッツリ|濃い/.test(text)) return 8;
  if (/コウケンテツ|Koh|Kurashiru|クラシル|家庭|丁寧/.test(text)) return 5;
  if (/デリッシュ|DELISH|macaroni|マカロニ|初心者|簡単/.test(text)) return 4;
  if (/ダイエット|さっぱり|ヘルシー/.test(text)) return 3;
  return 5;
}

function getTentativeRichnessProfile(recipe) {
  const material = getIngredientTasteProfile(recipe).score;
  const oil = Math.max(1, Math.min(10, (recipe.oil || 3) * 2));
  const creator = getCreatorTasteScore(recipe);

  // 仮モデル:
  // 味スコア = 0.6 * 材料 + 0.3 * 油感 + 0.1 * 投稿者
  const score = material * 0.6 + oil * 0.3 + creator * 0.1;
  return {
    score: Math.round(score * 10) / 10,
    material,
    oil,
    creator
  };
}

function openIngredientDialog() {
  if (!ingredientDialog) return;
  ingredientDialog.hidden = false;
  document.body.classList.add("dialog-open");
}

function closeIngredientDialog() {
  if (!ingredientDialog) return;
  ingredientDialog.hidden = true;
  document.body.classList.remove("dialog-open");
}

function openVideoDialog(recipe) {
  if (!videoDialog || !videoDialogTitle || !videoFrameWrap) return;

  const iframe = createYoutubeIframe(recipe, true);
  if (!iframe) {
    window.open(buildVideoUrl(recipe), "_blank", "noopener");
    return;
  }

  videoDialogTitle.textContent = recipe.title;
  videoFrameWrap.innerHTML = "";
  videoFrameWrap.appendChild(iframe);

  videoDialog.hidden = false;
  document.body.classList.add("dialog-open");
}

function closeVideoDialogModal() {
  if (!videoDialog || !videoFrameWrap) return;
  videoDialog.hidden = true;
  videoFrameWrap.innerHTML = "";
  document.body.classList.remove("dialog-open");
}

function renderSelectedIngredients(conditions) {
  if (!selectedIngredients || !ingredientCount) return;

  selectedIngredients.innerHTML = "";

  const visibleSelection = getVisibleSelectedIngredients(conditions.ingredients);

  if (visibleSelection.length === 0) {
    ingredientCount.textContent = "未選択";
    const empty = document.createElement("span");
    empty.textContent = "カテゴリ未選択";
    selectedIngredients.appendChild(empty);
    return;
  }

  ingredientCount.textContent = `${visibleSelection.length}件`;
  const visibleIngredients = visibleSelection.slice(0, 8);
  visibleIngredients.forEach((item) => {
    const chip = document.createElement("span");
    chip.textContent = labels.ingredients[item] || item;
    selectedIngredients.appendChild(chip);
  });

  if (visibleSelection.length > visibleIngredients.length) {
    const more = document.createElement("span");
    more.textContent = `+${visibleSelection.length - visibleIngredients.length}`;
    selectedIngredients.appendChild(more);
  }
}

function renderSummary(conditions) {
  if (!summaryStrip) return;

  const visibleIngredients = getVisibleSelectedIngredients(conditions.ingredients);
  const tags = [
    conditions.taste ? labels.taste[conditions.taste] : "",
    conditions.time ? labels.time[conditions.time] : "",
    conditions.temperature ? labels.temperature[conditions.temperature] : "",
    ...visibleIngredients.map((item) => labels.ingredients[item] || item)
  ].filter(Boolean);

  if (conditions.noKnife) tags.push("包丁なし");
  if (conditions.noHeat) tags.push("火なし");

  summaryStrip.innerHTML = "";
  tags.forEach((tag) => {
    const element = document.createElement("span");
    element.textContent = tag;
    summaryStrip.appendChild(element);
  });
}

function getCategoryGroups() {
  if (!ingredientDialog) return Object.keys(ingredientChoiceIdsByGroup);

  return Array.from(ingredientDialog.querySelectorAll("[data-category-toggle]"))
    .map((input) => input.dataset.categoryToggle)
    .filter(Boolean);
}

function getCategoryItems(groupId) {
  if (!ingredientDialog) return [];

  return Array.from(ingredientDialog.querySelectorAll("[data-category-item]"))
    .filter((input) => input.dataset.categoryItem.split(/\s+/).includes(groupId));
}

function getCategoryItemIds(groupId) {
  const domItems = getCategoryItems(groupId).map((input) => input.value);
  if (domItems.length > 0) return domItems;
  return ingredientChoiceIdsByGroup[groupId] || [];
}

function syncCategoryToggle(groupId) {
  if (!ingredientDialog) return;

  const toggle = ingredientDialog.querySelector(`[data-category-toggle="${groupId}"]`);
  const items = getCategoryItems(groupId);
  if (!toggle || items.length === 0) return;

  const checkedCount = items.filter((input) => input.checked).length;
  toggle.checked = checkedCount === items.length;
  toggle.indeterminate = checkedCount > 0 && checkedCount < items.length;
}

function syncAllCategoryToggles() {
  getCategoryGroups().forEach(syncCategoryToggle);
}

function getVisibleSelectedIngredients(selectedIds) {
  const selectedSet = new Set(selectedIds);
  const hiddenIds = new Set();
  const visibleIds = [];

  getCategoryGroups().forEach((groupId) => {
    if (!selectedSet.has(groupId)) return;

    getCategoryItemIds(groupId).forEach((id) => hiddenIds.add(id));

    if (labels.ingredients[groupId]) {
      visibleIds.push(groupId);
    }
  });

  selectedIds.forEach((id) => {
    if (!hiddenIds.has(id) && !visibleIds.includes(id)) {
      visibleIds.push(id);
    }
  });

  return visibleIds;
}

function renderCards(scoredRecipes) {
  if (!recommendations || !template) return;

  recommendations.innerHTML = "";

  scoredRecipes.slice(0, 3).forEach((recipe, index) => {
    const card = template.content.cloneNode(true);
    const article = card.querySelector(".recipe-card");
    const videoFrame = card.querySelector(".card-video-frame");
    const videoLoadButton = card.querySelector(".video-load-button");
    const image = card.querySelector("img");
    const rank = card.querySelector(".rank-badge");
    const creator = card.querySelector(".creator");
    const score = card.querySelector(".score");
    const title = card.querySelector("h3");
    const description = card.querySelector(".description");
    const metaRow = card.querySelector(".meta-row");
    const reasonBox = card.querySelector(".reason-box");
    const youtubeLink = card.querySelector(".youtube-link");
    const videoUrl = buildVideoUrl(recipe);

    article.style.setProperty("--rank", index + 1);
    image.src = getYoutubeThumbnail(recipe);
    image.alt = `${recipe.title}の動画サムネイル`;
    image.addEventListener("error", () => {
      const videoId = getYoutubeVideoId(recipe);
      if (videoId && !image.dataset.fallbackApplied) {
        image.dataset.fallbackApplied = "true";
        image.src = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
      }
    });
    videoLoadButton.addEventListener("click", () => {
      loadVideoIntoFrame(videoFrame, videoLoadButton, recipe);
    });
    rank.textContent = `#${index + 1}`;
    creator.textContent = recipe.creator;
    score.textContent = "おすすめ";
    title.textContent = recipe.title;
    description.textContent = recipe.description;

    [
      labels.taste[recipe.taste],
      labels.time[recipe.time],
      labels.temperature[recipe.temperature],
      `油${recipe.oil}/5`,
      `負荷${recipe.effort}/5`,
      `洗い物${recipe.dishes}`
    ].forEach((text) => {
      const pill = document.createElement("span");
      pill.textContent = text;
      metaRow.appendChild(pill);
    });

    const reasonText = recipe.reasons.length > 0
      ? recipe.reasons.join("。") + "。"
      : "条件に合いやすい候補です。";
    reasonBox.textContent = `${reasonText} 食材カテゴリ: ${getIngredientTasteProfile(recipe).categories.join("・")}`;

    youtubeLink.href = videoUrl;
    youtubeLink.textContent = getVideoPlatform(recipe) === "youtube" ? "YouTubeで開く" : "動画を開く";
    recommendations.appendChild(card);
  });
}

function updateRecommendations() {
  const conditions = readConditions();
  const recommendedRecipes = hasActiveConditions(conditions)
    ? recipes
        .map((recipe) => scoreRecipe(recipe, conditions))
        .sort((a, b) => b.score - a.score)
    : getRandomRecommendations(recipes);

  renderSelectedIngredients(conditions);
  renderSummary(conditions);
  renderCards(recommendedRecipes);

  [changeConditionsLink, brandHomeLink].forEach((link) => {
    if (link) link.href = buildPageUrl("index.html", conditions);
  });
}

if (form) {
  applyConditionsToForm(readInitialFormConditions());
  window.addEventListener("pageshow", () => {
    applyConditionsToForm(readConditionsFromUrl());
    updateRecommendations();
  });
  form.addEventListener("change", updateRecommendations);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    goToResults();
  });
}

if (searchButton) {
  searchButton.addEventListener("click", (event) => {
    event.preventDefault();
    goToResults();
  });
}

if (ingredientDialog) {
  ingredientDialog.addEventListener("change", (event) => {
    if (!event.target.matches('input[type="checkbox"]')) return;

    const toggleGroup = event.target.dataset.categoryToggle;
    if (toggleGroup) {
      getCategoryItems(toggleGroup).forEach((input) => {
        input.checked = event.target.checked;
      });
      event.target.indeterminate = false;
    }

    syncAllCategoryToggles();
  });

  ingredientDialog.addEventListener("click", (event) => {
    if (event.target === ingredientDialog) closeIngredientDialog();
  });
}

if (openIngredientSelector) openIngredientSelector.addEventListener("click", openIngredientDialog);
if (closeIngredientSelector) closeIngredientSelector.addEventListener("click", closeIngredientDialog);
if (backIngredientSelector) backIngredientSelector.addEventListener("click", closeIngredientDialog);
if (confirmIngredientSelector) {
  confirmIngredientSelector.addEventListener("click", () => {
    updateRecommendations();
    closeIngredientDialog();
  });
}
if (clearIngredientSelector && ingredientDialog) {
  clearIngredientSelector.addEventListener("click", () => {
    ingredientDialog.querySelectorAll('input[type="checkbox"]').forEach((input) => {
      input.checked = false;
      input.indeterminate = false;
    });
    updateRecommendations();
  });
}
if (closeVideoDialog) closeVideoDialog.addEventListener("click", closeVideoDialogModal);
if (videoDialog) {
  videoDialog.addEventListener("click", (event) => {
    if (event.target === videoDialog) closeVideoDialogModal();
  });
}
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (videoDialog && !videoDialog.hidden) {
    closeVideoDialogModal();
  } else if (ingredientDialog && !ingredientDialog.hidden) {
    closeIngredientDialog();
  }
});
syncAllCategoryToggles();
updateRecommendations();
