(function () {
  const assignmentMount = document.querySelector("#surveyAssignmentGrid");
  const searchedConditionsMount = document.querySelector("#surveySearchedConditions");
  const recommendForm = document.querySelector("#recommendForm");
  const formMount = document.querySelector("#surveyFormFrame");
  const rawUrl = window.SURVEY_FORM_EMBED_URL || "";

  const assignmentOptions = {
    taste: [
      ["rich", "ガッツリ"],
      ["semi-rich", "ややガッツリ"],
      ["semi-light", "ややあっさり"],
      ["light", "あっさり"]
    ],
    time: [
      ["easy", "簡単 〜15分"],
      ["normal", "普通 15〜30分"],
      ["slow", "じっくり 30分〜"]
    ],
    temperature: [
      ["warm", "温かい"],
      ["cold", "冷たい"]
    ],
    dishType: [
      ["rice", "丼物"],
      ["bread", "パン系"],
      ["noodle", "麺系"],
      ["side", "おかず系"],
      ["soup", "汁物系"],
      ["any", "指定なし"]
    ],
    mainIngredient: [
      ["meat", "肉"],
      ["fish", "魚"],
      ["egg", "卵"],
      ["soy", "豆腐・大豆"],
      ["vegetable", "野菜中心"],
      ["other", "その他"],
      ["any", "指定なし"]
    ]
  };

  const assignmentLabels = {
    taste: "味",
    time: "調理時間",
    temperature: "温度",
    dishType: "料理タイプ",
    mainIngredient: "中心食材"
  };

  function pickRandom(options) {
    return options[Math.floor(Math.random() * options.length)];
  }

  function createAssignment() {
    return Object.fromEntries(
      Object.entries(assignmentOptions).map(([name, options]) => [name, pickRandom(options)])
    );
  }

  function renderAssignment(assignment) {
    renderConditionGrid(assignmentMount, assignment);
  }

  function renderConditionGrid(mount, assignment) {
    if (!mount) return;

    mount.replaceChildren();
    Object.entries(assignment).forEach(([name, [, label]]) => {
      const item = document.createElement("div");
      item.className = "survey-assignment-item";

      const key = document.createElement("span");
      key.textContent = assignmentLabels[name];

      const value = document.createElement("strong");
      value.textContent = label;

      item.append(key, value);
      mount.appendChild(item);
    });
  }

  function applyAssignment(assignment) {
    if (!recommendForm) return;

    Object.entries(assignment).forEach(([name, [value]]) => {
      const input = recommendForm.querySelector(`input[name="${name}"][value="${value}"]`);
      if (input) input.checked = true;
    });
  }

  if (assignmentMount) {
    const assignment = createAssignment();
    renderAssignment(assignment);
    applyAssignment(assignment);
    window.addEventListener("pageshow", () => {
      applyAssignment(assignment);
    });
  }

  if (searchedConditionsMount) {
    const params = new URLSearchParams(window.location.search);
    const searchedConditions = Object.fromEntries(
      Object.entries(assignmentOptions).map(([name, options]) => {
        const value = params.get(name) || "";
        const option = options.find(([optionValue]) => optionValue === value);
        return [name, option || ["", "未選択"]];
      })
    );
    renderConditionGrid(searchedConditionsMount, searchedConditions);
  }

  if (!formMount || !rawUrl) return;

  try {
    const url = new URL(rawUrl);
    if (url.protocol !== "https:" || url.hostname !== "docs.google.com") return;

    formMount.replaceChildren();
    const iframe = document.createElement("iframe");
    iframe.src = url.href;
    iframe.title = "ユーザー調査アンケート";
    iframe.loading = "lazy";
    iframe.textContent = "読み込んでいます...";
    formMount.appendChild(iframe);
  } catch {
    // Invalid survey URLs leave the placeholder visible.
  }
})();
