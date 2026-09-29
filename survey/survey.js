(function () {
  const formMount = document.querySelector("#surveyFormFrame");
  const rawUrl = window.SURVEY_FORM_EMBED_URL || "";

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
