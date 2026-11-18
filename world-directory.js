/* Native front-page links first; search and filters enhance the same directory. */
(() => {
  "use strict";

  const root = document.getElementById("world-directory");
  if (!root) return;
  const search = root.querySelector("#world-search");
  const cards = [...root.querySelectorAll("#world-links > a")];
  const buttons = [...root.querySelectorAll("button[data-category]")];
  const count = root.querySelector("#world-count");
  const empty = root.querySelector("#world-empty");
  const more = root.querySelector("#world-more");
  const pageSize = 18;
  let category = "All";
  let limit = pageSize;

  const normalize = (value) => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const text = cards.map((card) => normalize(
    [...card.querySelectorAll("strong, .world-description, .world-category")]
      .map((item) => item.textContent.trim())
      .concat(card.getAttribute("href")).join(" ")
  ));

  function filter() {
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    const matches = [];
    cards.forEach((card, index) => {
      const matchesCategory = category === "All" || card.dataset.category === category;
      const matchesSearch = words.every((word) => text[index].includes(word));
      if (matchesCategory && matchesSearch) matches.push(card);
      card.hidden = !(matchesCategory && matchesSearch && matches.length <= limit);
    });

    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.category === category));
    }
    const shown = Math.min(matches.length, limit);
    const description = category === "All" ? "worlds & projects" : category.toLowerCase();
    count.textContent = `Showing ${shown} of ${matches.length} ${description}${words.length ? " matching your search" : ""}.`;
    empty.hidden = matches.length !== 0;
    more.hidden = matches.length <= limit;
    more.textContent = `Show ${Math.min(pageSize, matches.length - shown)} more worlds`;
    return matches;
  }

  function resetLimit() {
    limit = pageSize;
    filter();
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      category = button.dataset.category;
      resetLimit();
    });
  }
  search.addEventListener("input", resetLimit);
  root.querySelector("#world-clear").addEventListener("click", () => {
    search.value = "";
    category = "All";
    resetLimit();
    search.focus();
  });
  more.addEventListener("click", () => {
    const previousLimit = limit;
    limit += pageSize;
    filter()[previousLimit]?.focus();
  });

  const archive = document.getElementById("legacy-archive");
  function openArchiveFromHash() {
    if (archive && ["#legacy-archive", "#site-extras"].includes(location.hash)) {
      archive.open = true;
    }
  }
  window.addEventListener("hashchange", openArchiveFromHash);
  root.querySelector(".world-archive-link a")?.addEventListener("click", () => {
    if (archive) archive.open = true;
  });
  openArchiveFromHash();
  filter();
  root.classList.add("directory-ready");
})();
