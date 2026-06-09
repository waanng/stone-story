const state = {
  chapters: [],
  relations: [],
  topics: [],
  selected: 3,
  filter: "all",
  query: "",
};

const els = {
  grid: document.querySelector("#chapterGrid"),
  detail: document.querySelector("#chapterDetail"),
  count: document.querySelector("#chapterCount"),
  search: document.querySelector("#searchInput"),
  filters: [...document.querySelectorAll(".filter")],
  relationSvg: document.querySelector("#relationSvg"),
  relationNotes: document.querySelector("#relationNotes"),
  topicGrid: document.querySelector("#topicGrid"),
};

const relationColors = {
  "情感/知己": "#a33b2b",
  "婚姻/对照": "#b4893c",
  "对照/竞争": "#6f4a8e",
  "权力/依附": "#2c6a68",
  "婚姻/冲突": "#5f5146",
  "管理/对照": "#2c6a68",
  "主仆/欣赏": "#8b5e3c",
  "主仆/情感支持": "#8b5e3c",
  "贫富/外部视角": "#4f6f52",
};

function stars(num) {
  return "★★★★★".slice(0, num) + "☆☆☆☆☆".slice(0, 5 - num);
}

function chapterLabel(chapter) {
  return `第${String(chapter).padStart(3, "0")}回`;
}

function normalize(text) {
  return String(text || "").toLowerCase().trim();
}

function filteredChapters() {
  const q = normalize(state.query);
  return state.chapters.filter((item) => {
    const filterOk = state.filter === "all" || item.importance === Number(state.filter);
    const haystack = normalize([
      item.chapter,
      item.title,
      item.summary,
      item.characters.join(" "),
      item.exam_points.join(" "),
      item.possible_question,
      item.reference_answer,
    ].join(" "));
    return filterOk && (!q || haystack.includes(q));
  });
}

function renderChapters() {
  const list = filteredChapters();
  els.count.textContent = `${list.length} / ${state.chapters.length} 回`;
  els.grid.innerHTML = list.map((item) => `
    <button class="chapter-card ${item.chapter === state.selected ? "active" : ""}" data-chapter="${item.chapter}">
      <strong>${chapterLabel(item.chapter)}</strong>
      <span>${item.title.replace(/^第.+?回\s*/, "")}</span>
      <em>${stars(item.importance)}</em>
    </button>
  `).join("");
}

function renderDetail() {
  const item = state.chapters.find((chapter) => chapter.chapter === state.selected) || state.chapters[0];
  if (!item) return;
  els.detail.innerHTML = `
    <h3>${chapterLabel(item.chapter)}</h3>
    <div class="detail-title">${item.title}</div>
    <div class="stars" aria-label="考试重要度">${stars(item.importance)}</div>
    <div class="detail-block">
      <h4>一句话概括</h4>
      <p>${item.summary}</p>
    </div>
    <div class="detail-block">
      <h4>主要情节</h4>
      <ul>${item.events.map((event) => `<li>${event}</li>`).join("")}</ul>
    </div>
    <div class="detail-block">
      <h4>本回人物</h4>
      <div class="chips">${item.characters.length ? item.characters.map((name) => `<span class="chip">${name}</span>`).join("") : "<span class='chip'>待补充</span>"}</div>
    </div>
    <div class="detail-block">
      <h4>高考考点</h4>
      <div class="chips">${item.exam_points.map((point) => `<span class="chip">${point}</span>`).join("")}</div>
    </div>
    <div class="detail-block">
      <h4>可能这样考</h4>
      <p>${item.possible_question}</p>
    </div>
    <div class="detail-block answer-block">
      <h4>参考答案</h4>
      <p>${item.reference_answer || "本回参考答案待补充。"}</p>
    </div>
    <div class="detail-block">
      <h4>原文定位</h4>
      <p class="quote">${item.quote}……</p>
      ${item.raw_available ? `<a class="raw-link" href="${item.reader_file || item.raw_file}" target="_blank" rel="noreferrer">打开本回原文</a>` : `<span class="raw-link">原文待补齐，可重新运行资料脚本</span>`}
    </div>
  `;
}

function renderRelations() {
  const positions = {
    "贾宝玉": [450, 205],
    "林黛玉": [250, 105],
    "薛宝钗": [650, 105],
    "王熙凤": [660, 310],
    "贾母": [450, 55],
    "探春": [235, 305],
    "贾琏": [810, 315],
    "晴雯": [450, 360],
    "紫鹃": [95, 112],
    "贾府": [105, 315],
    "刘姥姥": [95, 390],
  };
  const nodes = Object.keys(positions);
  const lines = state.relations
    .filter((rel) => positions[rel.source] && positions[rel.target])
    .map((rel) => {
      const [x1, y1] = positions[rel.source];
      const [x2, y2] = positions[rel.target];
      const color = relationColors[rel.type] || "#72675c";
      return `<line class="relation-line" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" />`;
    }).join("");
  const nodeMarkup = nodes.map((name) => {
    const [x, y] = positions[name];
    return `<g class="relation-node"><circle cx="${x}" cy="${y}" r="38"></circle><text x="${x}" y="${y}">${name}</text></g>`;
  }).join("");
  els.relationSvg.innerHTML = `${lines}${nodeMarkup}`;
  els.relationNotes.innerHTML = state.relations.slice(0, 7).map((rel) => `
    <div class="relation-note">
      <strong>${rel.source} → ${rel.target}</strong>
      <p>${rel.type}：${rel.note}</p>
    </div>
  `).join("");
}

function renderTopics() {
  els.topicGrid.innerHTML = state.topics.map((topic) => `
    <article class="topic-card">
      <h4>${topic.title}</h4>
      <p>${topic.focus}</p>
      <button data-topic="${topic.id}">查看相关章节：${topic.chapters.map((c) => c).join("、")}</button>
    </article>
  `).join("");
}

function bindEvents() {
  els.grid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-chapter]");
    if (!button) return;
    state.selected = Number(button.dataset.chapter);
    renderChapters();
    renderDetail();
  });

  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderChapters();
  });

  els.filters.forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      els.filters.forEach((item) => item.classList.toggle("active", item === button));
      renderChapters();
    });
  });

  els.topicGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-topic]");
    if (!button) return;
    const topic = state.topics.find((item) => item.id === button.dataset.topic);
    if (!topic) return;
    state.filter = "all";
    state.query = "";
    els.search.value = "";
    els.filters.forEach((item) => item.classList.toggle("active", item.dataset.filter === "all"));
    state.selected = topic.chapters[0];
    renderChapters();
    renderDetail();
    document.querySelector("#chapters").scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

async function init() {
  try {
    const response = await fetch("data/honglou_data.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    state.chapters = data.chapters;
    state.relations = data.relations;
    state.topics = data.topics;
    document.querySelector("#metric-chapters").textContent = state.chapters.length;
    bindEvents();
    renderChapters();
    renderDetail();
    renderRelations();
    renderTopics();
  } catch (error) {
    els.detail.innerHTML = `<div class="empty-state">章节数据没有加载成功：${error.message}。如果是直接打开文件，请用本目录的本地服务访问。</div>`;
  }
}

init();
