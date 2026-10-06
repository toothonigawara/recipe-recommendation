const swipeDishPool = typeof SWIPE_DISHES !== "undefined" ? SWIPE_DISHES : [];

const swipeState = {
  deck: [],
  currentIndex: 0,
  results: [],
  isAnimating: false,
  drag: {
    active: false,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0
  }
};

const swipeConfig = {
  sessionSize: 8,
  swipeThreshold: 90
};

const swipeElements = {
  card: document.querySelector("#swipeCard"),
  cardArea: document.querySelector("#swipeCardArea"),
  image: document.querySelector("#swipeDishImage"),
  name: document.querySelector("#swipeDishName"),
  meta: document.querySelector("#swipeDishMeta"),
  progressText: document.querySelector("#swipeProgressText"),
  progressBar: document.querySelector("#swipeProgressBar"),
  likeButton: document.querySelector("#swipeLikeButton"),
  dislikeButton: document.querySelector("#swipeDislikeButton"),
  complete: document.querySelector("#swipeComplete"),
  resultButton: document.querySelector("#swipeResultButton"),
  restartButton: document.querySelector("#swipeRestartButton"),
  debugOutput: document.querySelector("#swipeDebugOutput")
};

function shuffleDishes(dishes) {
  return [...dishes]
    .map((dish) => ({ dish, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map((item) => item.dish);
}

function selectSwipeDishes(dishes, sessionSize = swipeConfig.sessionSize) {
  return shuffleDishes(dishes).slice(0, sessionSize);
}

function getNextSwipeDish(state = swipeState) {
  return state.deck[state.currentIndex] || null;
}

function buildSwipeResult(dish, action, order) {
  return {
    dish_id: dish.id,
    dish_name: dish.dish_name,
    action,
    order,
    genre: dish.genre,
    staple: dish.staple,
    dish_type: dish.dish_type,
    main_ingredient: dish.main_ingredient,
    taste_level: dish.taste_level,
    temperature: dish.temperature,
    cooking_time: dish.cooking_time
  };
}

function summarizeSwipeResults(results) {
  const liked = results.filter((result) => result.action === "like");
  const summary = {
    total: results.length,
    like: liked.length,
    dislike: results.length - liked.length,
    likedGenres: countBy(liked, "genre"),
    likedStaples: countBy(liked, "staple"),
    likedMainIngredients: countBy(liked, "main_ingredient"),
    likedTasteLevels: countBy(liked, "taste_level"),
    likedTemperatures: countBy(liked, "temperature")
  };
  return summary;
}

function pickMostCommon(items, key) {
  const counts = countBy(items, key);
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([value]) => value)[0] || "";
}

function countBy(items, key) {
  return items.reduce((counts, item) => {
    const value = item[key] || "未設定";
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
}

function mapTasteLevel(value) {
  return {
    "ガッツリ": "rich",
    "ややガッツリ": "semi-rich",
    "ややあっさり": "semi-light",
    "あっさり": "light"
  }[value] || "";
}

function mapCookingTime(value) {
  return {
    "15分以内": "easy",
    "15〜30分": "normal",
    "30分以上": "slow"
  }[value] || "";
}

function mapTemperature(value) {
  return {
    "温かい": "warm",
    "冷たい": "cold"
  }[value] || "";
}

function mapDishType(value) {
  if (value === "丼" || value === "ご飯もの") return "rice";
  if (value === "パン料理") return "bread";
  if (value === "麺料理") return "noodle";
  if (value === "汁物") return "soup";
  return "side";
}

function mapMainIngredient(value) {
  return {
    "肉": "meat",
    "魚": "fish",
    "卵": "egg",
    "豆腐・大豆": "soy",
    "野菜中心": "vegetable",
    "その他": "other"
  }[value] || "";
}

function inferRecommendationConditions(results) {
  const liked = results.filter((result) => result.action === "like");
  const source = liked.length > 0 ? liked : [];

  return {
    taste: mapTasteLevel(pickMostCommon(source, "taste_level")),
    time: mapCookingTime(pickMostCommon(source, "cooking_time")),
    temperature: mapTemperature(pickMostCommon(source, "temperature")),
    dishType: mapDishType(pickMostCommon(source, "dish_type")),
    mainIngredient: mapMainIngredient(pickMostCommon(source, "main_ingredient"))
  };
}

function buildResultsUrl(results) {
  const conditions = inferRecommendationConditions(results);
  const params = new URLSearchParams();
  Object.entries(conditions).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return query ? `results.html?${query}` : "results.html";
}

function updateDebugOutput() {
  if (!swipeElements.debugOutput) return;

  const payload = {
    results: swipeState.results,
    summary: summarizeSwipeResults(swipeState.results)
  };
  swipeElements.debugOutput.textContent = JSON.stringify(payload, null, 2);
}

function renderSwipeDish() {
  const dish = getNextSwipeDish();
  const progressTotal = swipeState.deck.length || swipeConfig.sessionSize;
  const progressCurrent = Math.min(swipeState.currentIndex + 1, progressTotal);

  if (!dish) {
    renderSwipeComplete();
    return;
  }

  swipeElements.image.src = dish.image;
  swipeElements.image.alt = `${dish.dish_name}の仮画像`;
  swipeElements.name.textContent = dish.dish_name;
  swipeElements.meta.textContent = `${dish.genre} / ${dish.cooking_time}`;
  swipeElements.progressText.textContent = `${progressCurrent} / ${progressTotal}`;
  swipeElements.progressBar.style.width = `${(swipeState.currentIndex / progressTotal) * 100}%`;

  swipeElements.card.hidden = false;
  swipeElements.complete.hidden = true;
  setSwipeButtonsDisabled(false);
  resetCardPosition();
  updateDebugOutput();
}

function renderSwipeComplete() {
  swipeElements.card.hidden = true;
  swipeElements.complete.hidden = false;
  swipeElements.progressText.textContent = `${swipeState.deck.length} / ${swipeState.deck.length}`;
  swipeElements.progressBar.style.width = "100%";
  setSwipeButtonsDisabled(true);
  if (swipeElements.resultButton) {
    swipeElements.resultButton.disabled = false;
  }
  updateDebugOutput();
  console.log("swipe results", swipeState.results);
  console.log("swipe summary", summarizeSwipeResults(swipeState.results));
  console.log("recommendation conditions", inferRecommendationConditions(swipeState.results));
}

function setSwipeButtonsDisabled(disabled) {
  [swipeElements.likeButton, swipeElements.dislikeButton].forEach((button) => {
    if (button) button.disabled = disabled;
  });
}

function resetCardPosition() {
  swipeState.isAnimating = false;
  swipeElements.card.classList.remove("is-like", "is-dislike", "is-resetting");
  swipeElements.card.style.transform = "";
}

function moveCard(x, y) {
  const rotate = Math.max(-14, Math.min(14, x / 14));
  swipeElements.card.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg)`;
  swipeElements.card.classList.toggle("is-like", x > 24);
  swipeElements.card.classList.toggle("is-dislike", x < -24);
}

function recordSwipe(action) {
  const dish = getNextSwipeDish();
  if (!dish) return;

  swipeState.results.push(buildSwipeResult(dish, action, swipeState.currentIndex + 1));
  swipeState.currentIndex += 1;
  window.swipePrototype.results = swipeState.results;
  window.swipePrototype.summary = summarizeSwipeResults(swipeState.results);
  renderSwipeDish();
}

function answerSwipe(action) {
  if (swipeState.isAnimating) return;

  const direction = action === "like" ? 1 : -1;
  swipeState.isAnimating = true;
  setSwipeButtonsDisabled(true);
  swipeElements.card.classList.toggle("is-like", action === "like");
  swipeElements.card.classList.toggle("is-dislike", action === "dislike");
  swipeElements.card.style.transform = `translate(${direction * 120}vw, -12px) rotate(${direction * 18}deg)`;

  window.setTimeout(() => {
    recordSwipe(action);
  }, 220);
}

function startDrag(event) {
  if (swipeState.isAnimating || !getNextSwipeDish()) return;

  swipeState.drag.active = true;
  swipeState.drag.startX = event.clientX;
  swipeState.drag.startY = event.clientY;
  swipeState.drag.currentX = 0;
  swipeState.drag.currentY = 0;
  swipeElements.card.setPointerCapture(event.pointerId);
}

function moveDrag(event) {
  if (!swipeState.drag.active) return;

  swipeState.drag.currentX = event.clientX - swipeState.drag.startX;
  swipeState.drag.currentY = event.clientY - swipeState.drag.startY;
  moveCard(swipeState.drag.currentX, swipeState.drag.currentY);
}

function endDrag(event) {
  if (!swipeState.drag.active) return;

  swipeState.drag.active = false;
  swipeElements.card.releasePointerCapture(event.pointerId);

  const distance = swipeState.drag.currentX;
  if (Math.abs(distance) >= swipeConfig.swipeThreshold) {
    answerSwipe(distance > 0 ? "like" : "dislike");
    return;
  }

  swipeElements.card.classList.add("is-resetting");
  window.setTimeout(resetCardPosition, 160);
}

function restartSwipeSession() {
  swipeState.deck = selectSwipeDishes(swipeDishPool);
  swipeState.currentIndex = 0;
  swipeState.results = [];
  window.swipePrototype.results = swipeState.results;
  window.swipePrototype.summary = {};
  if (swipeElements.resultButton) {
    swipeElements.resultButton.disabled = true;
  }
  renderSwipeDish();
}

window.swipePrototype = {
  get deck() {
    return swipeState.deck;
  },
  get results() {
    return swipeState.results;
  },
  set results(value) {
    swipeState.results = value;
  },
  summary: {},
  selectSwipeDishes,
  getNextSwipeDish,
  summarizeSwipeResults,
  inferRecommendationConditions,
  buildResultsUrl,
  restart: restartSwipeSession
};

if (swipeElements.card && swipeDishPool.length > 0) {
  swipeElements.likeButton.addEventListener("click", () => answerSwipe("like"));
  swipeElements.dislikeButton.addEventListener("click", () => answerSwipe("dislike"));
  swipeElements.resultButton.addEventListener("click", () => {
    window.location.href = buildResultsUrl(swipeState.results);
  });
  swipeElements.restartButton.addEventListener("click", restartSwipeSession);

  swipeElements.card.addEventListener("pointerdown", startDrag);
  swipeElements.card.addEventListener("pointermove", moveDrag);
  swipeElements.card.addEventListener("pointerup", endDrag);
  swipeElements.card.addEventListener("pointercancel", endDrag);

  document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") answerSwipe("like");
    if (event.key === "ArrowLeft") answerSwipe("dislike");
  });

  restartSwipeSession();
}
