const state = {
  chapters: [],
  relations: [],
  topics: [],
  practiceQuestions: [],
  selected: 3,
  filter: "all",
  query: "",
  relationFilter: "all",
  selectedRelationNode: "",
  selectedTopic: "first-five",
  practiceType: "全部",
  selectedPractice: "",
};

const els = {
  grid: document.querySelector("#chapterGrid"),
  detail: document.querySelector("#chapterDetail"),
  count: document.querySelector("#chapterCount"),
  search: document.querySelector("#searchInput"),
  filters: [...document.querySelectorAll(".filter")],
  relationSvg: document.querySelector("#relationSvg"),
  relationNotes: document.querySelector("#relationNotes"),
  relationFilters: [...document.querySelectorAll(".relation-filter")],
  topicGrid: document.querySelector("#topicGrid"),
  topicDetail: document.querySelector("#topicDetail"),
  practiceFilters: document.querySelector("#practiceFilters"),
  practiceList: document.querySelector("#practiceList"),
  practiceDetail: document.querySelector("#practiceDetail"),
  practiceCount: document.querySelector("#practiceCount"),
};

const relationColors = {
  "情感": "#a33b2b",
  "婚姻": "#b4893c",
  "亲属": "#8b5e3c",
  "权力": "#2c6a68",
  "主仆": "#6f4a8e",
  "冲突": "#5f5146",
  "对照": "#4f6f52",
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
      <h4>本章内容提要</h4>
      <p class="content-summary">${item.content_summary || item.summary}</p>
    </div>
    <div class="detail-block">
      <h4>内容解析</h4>
      <p class="plot-summary">${item.plot_summary || (item.events || []).join("。")}</p>
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
    "贾宝玉": [520, 290],
    "林黛玉": [300, 170],
    "薛宝钗": [740, 170],
    "贾母": [520, 70],
    "王夫人": [700, 300],
    "贾政": [520, 500],
    "袭人": [330, 405],
    "晴雯": [480, 435],
    "紫鹃": [170, 185],
    "王熙凤": [830, 380],
    "贾琏": [990, 380],
    "探春": [655, 505],
    "赵姨娘": [815, 555],
    "香菱": [910, 95],
    "薛蟠": [1030, 165],
    "刘姥姥": [140, 525],
    "贾府": [295, 525],
    "贾雨村": [120, 350],
    "秦可卿": [875, 515],
    "元春": [660, 65],
    "尤二姐": [1000, 515],
  };
  const filteredRelations = state.relations.filter((rel) => {
    const categoryOk = state.relationFilter === "all" || rel.category === state.relationFilter;
    const nodeOk = !state.selectedRelationNode || rel.source === state.selectedRelationNode || rel.target === state.selectedRelationNode;
    return positions[rel.source] && positions[rel.target] && categoryOk && nodeOk;
  });
  const visibleNodeNames = new Set(filteredRelations.flatMap((rel) => [rel.source, rel.target]));
  const nodes = Object.keys(positions).filter((name) => visibleNodeNames.has(name) || !state.selectedRelationNode);
  const lineGroups = state.relations
    .filter((rel) => positions[rel.source] && positions[rel.target])
    .map((rel, index) => {
      const [x1, y1] = positions[rel.source];
      const [x2, y2] = positions[rel.target];
      const color = relationColors[rel.category] || "#72675c";
      const categoryOk = state.relationFilter === "all" || rel.category === state.relationFilter;
      const nodeOk = !state.selectedRelationNode || rel.source === state.selectedRelationNode || rel.target === state.selectedRelationNode;
      const visible = categoryOk && nodeOk;
      const muted = !visible ? " muted" : "";
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2;
      return `
        <g class="relation-edge${muted}" data-relation-index="${index}" tabindex="0" role="button" aria-label="${rel.source}和${rel.target}的关系：${rel.type}">
          <line class="relation-line" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" />
          <text class="relation-label" x="${mx}" y="${my}" fill="${color}">${rel.type}</text>
        </g>
      `;
    }).join("");
  const nodeMarkup = nodes.map((name) => {
    const [x, y] = positions[name];
    const active = name === state.selectedRelationNode ? " active" : "";
    return `<g class="relation-node${active}" data-node="${name}" tabindex="0" role="button" aria-label="查看${name}的人物关系"><circle cx="${x}" cy="${y}" r="38"></circle><text x="${x}" y="${y}">${name}</text></g>`;
  }).join("");
  const legend = Object.entries(relationColors).map(([category, color], index) => {
    const x = 24 + index * 86;
    return `<g class="relation-legend"><circle cx="${x}" cy="24" r="6" fill="${color}" /><text x="${x + 12}" y="28">${category}</text></g>`;
  }).join("");
  els.relationSvg.innerHTML = `${legend}${lineGroups}${nodeMarkup}`;
  const noteRelations = filteredRelations.length ? filteredRelations : state.relations.slice(0, 8);
  const heading = state.selectedRelationNode
    ? `${state.selectedRelationNode}的关系`
    : state.relationFilter === "all" ? "核心关系说明" : `${state.relationFilter}关系`;
  els.relationNotes.innerHTML = `
    <div class="relation-summary">
      <strong>${heading}</strong>
      <p>${state.selectedRelationNode ? "再次点击该人物可回到全局视图。" : "点击人物或关系线，会高亮相关关系并显示关键章节。"}</p>
    </div>
    ${noteRelations.map((rel, index) => `
      <div class="relation-note" data-note-index="${state.relations.indexOf(rel)}">
        <strong><span style="color:${relationColors[rel.category] || "#72675c"}">●</span> ${rel.source} ↔ ${rel.target}</strong>
        <p><b>${rel.type}</b>：${rel.note}</p>
        <div class="relation-chapters">
          ${rel.chapters.map((chapter) => `<button data-relation-chapter="${chapter}">第${String(chapter).padStart(3, "0")}回</button>`).join("")}
        </div>
      </div>
    `).join("")}
  `;
}

function renderTopics() {
  els.topicGrid.innerHTML = state.topics.map((topic) => `
    <article class="topic-card ${topic.id === state.selectedTopic ? "active" : ""}" data-topic-card="${topic.id}">
      <div class="topic-card-head">
        <h4>${topic.title}</h4>
        <span class="topic-stars">${stars(topic.importance)}</span>
      </div>
      <p>${topic.focus}</p>
      <div class="topic-chapters">${topic.chapters.slice(0, 6).map((chapter) => `<span>${chapterLabel(chapter)}</span>`).join("")}</div>
      <button data-topic="${topic.id}">进入专题</button>
    </article>
  `).join("");
  renderTopicDetail();
}

function renderTopicDetail() {
  const topic = state.topics.find((item) => item.id === state.selectedTopic) || state.topics[0];
  if (!topic || !els.topicDetail) return;
  state.selectedTopic = topic.id;
  els.topicDetail.innerHTML = `
    <article class="topic-detail-shell">
      <div class="topic-main">
        <div class="topic-detail-head">
          <div>
            <span class="topic-eyebrow">高考专题</span>
            <h4>${topic.title}</h4>
          </div>
          <span class="topic-stars">${stars(topic.importance)}</span>
        </div>
        <section class="topic-block">
          <h5>这个专题考什么</h5>
          <p>${topic.exam_target}</p>
        </section>
        <section class="topic-block">
          <h5>核心理解</h5>
          <p>${topic.core}</p>
        </section>
        <section class="topic-block">
          <h5>常见问法</h5>
          <div class="topic-question-list">
            ${topic.questions.map((question) => `<p>${question}</p>`).join("")}
          </div>
        </section>
        <section class="topic-block answer-block">
          <h5>参考答案模板</h5>
          <p>${topic.answer_template}</p>
        </section>
      </div>
      <aside class="topic-side">
        <section class="topic-block">
          <h5>必会人物</h5>
          <div class="chips">${topic.people.map((name) => `<span class="chip">${name}</span>`).join("")}</div>
        </section>
        <section class="topic-block">
          <h5>必须记住</h5>
          <div class="topic-know-list">${topic.must_know.map((item) => `<span>${item}</span>`).join("")}</div>
        </section>
        <section class="topic-block">
          <h5>相关章节</h5>
          <div class="topic-chapter-buttons">
            ${topic.chapters.map((chapter) => `<button data-topic-chapter="${chapter}">${chapterLabel(chapter)}</button>`).join("")}
          </div>
        </section>
      </aside>
    </article>
  `;
}

function practiceTypes() {
  return ["全部", ...new Set(state.practiceQuestions.map((item) => item.type))];
}

function filteredPracticeQuestions() {
  if (state.practiceType === "全部") return state.practiceQuestions;
  return state.practiceQuestions.filter((item) => item.type === state.practiceType);
}

function renderPractice() {
  if (!els.practiceFilters || !els.practiceList || !els.practiceDetail) return;
  const types = practiceTypes();
  const questions = filteredPracticeQuestions();
  if (!state.selectedPractice || !questions.some((item) => item.id === state.selectedPractice)) {
    state.selectedPractice = questions[0]?.id || "";
  }
  els.practiceCount.textContent = `${questions.length} / ${state.practiceQuestions.length} 题`;
  els.practiceFilters.innerHTML = types.map((type) => `
    <button class="practice-filter ${type === state.practiceType ? "active" : ""}" data-practice-type="${type}">
      ${type}
    </button>
  `).join("");
  els.practiceList.innerHTML = questions.map((item) => `
    <button class="practice-card ${item.id === state.selectedPractice ? "active" : ""}" data-practice-id="${item.id}">
      <span>${item.type} · ${item.level}</span>
      <strong>${item.question}</strong>
      <em>${item.topic}</em>
    </button>
  `).join("");
  renderPracticeDetail();
}

function renderPracticeDetail() {
  const item = state.practiceQuestions.find((question) => question.id === state.selectedPractice) || filteredPracticeQuestions()[0];
  if (!item) {
    els.practiceDetail.innerHTML = `<div class="empty-state">暂无训练题。</div>`;
    return;
  }
  state.selectedPractice = item.id;
  els.practiceDetail.innerHTML = `
    <div class="practice-detail-head">
      <div>
        <span class="practice-badge">${item.type} · ${item.level}</span>
        <h4>${item.question}</h4>
      </div>
      <span>${item.topic}</span>
    </div>
    <section class="practice-block">
      <h5>三步答题法</h5>
      <div class="practice-steps">
        ${item.thinking.map((step, index) => `
          <div>
            <strong>${index + 1}</strong>
            <p>${step}</p>
          </div>
        `).join("")}
      </div>
    </section>
    <section class="practice-block">
      <h5>得分点</h5>
      <div class="chips">${item.points.map((point) => `<span class="chip">${point}</span>`).join("")}</div>
    </section>
    <section class="practice-block answer-block">
      <h5>参考答案</h5>
      <p>${item.answer}</p>
    </section>
    <section class="practice-block">
      <h5>容易丢分点</h5>
      <p>${item.pitfall}</p>
    </section>
    <section class="practice-block">
      <h5>相关章节</h5>
      <div class="topic-chapter-buttons">
        ${item.chapters.map((chapter) => `<button data-practice-chapter="${chapter}">${chapterLabel(chapter)}</button>`).join("")}
      </div>
    </section>
  `;
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

  els.relationFilters.forEach((button) => {
    button.addEventListener("click", () => {
      state.relationFilter = button.dataset.relationFilter;
      state.selectedRelationNode = "";
      els.relationFilters.forEach((item) => item.classList.toggle("active", item === button));
      renderRelations();
    });
  });

  els.relationSvg.addEventListener("click", (event) => {
    const node = event.target.closest("[data-node]");
    if (node) {
      const name = node.dataset.node;
      state.selectedRelationNode = state.selectedRelationNode === name ? "" : name;
      renderRelations();
      return;
    }
    const edge = event.target.closest("[data-relation-index]");
    if (edge) {
      const rel = state.relations[Number(edge.dataset.relationIndex)];
      if (!rel) return;
      state.selectedRelationNode = "";
      state.relationFilter = rel.category;
      els.relationFilters.forEach((item) => item.classList.toggle("active", item.dataset.relationFilter === rel.category));
      renderRelations();
    }
  });

  els.relationNotes.addEventListener("click", (event) => {
    const chapterButton = event.target.closest("[data-relation-chapter]");
    if (!chapterButton) return;
    state.selected = Number(chapterButton.dataset.relationChapter);
    renderChapters();
    renderDetail();
    document.querySelector("#chapters").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  els.topicGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-topic]");
    const card = event.target.closest("[data-topic-card]");
    const topicId = button?.dataset.topic || card?.dataset.topicCard;
    if (!topicId) return;
    const topic = state.topics.find((item) => item.id === topicId);
    if (!topic) return;
    state.selectedTopic = topic.id;
    renderTopics();
    els.topicDetail.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  els.topicDetail.addEventListener("click", (event) => {
    const chapterButton = event.target.closest("[data-topic-chapter]");
    if (!chapterButton) return;
    state.filter = "all";
    state.query = "";
    els.search.value = "";
    els.filters.forEach((item) => item.classList.toggle("active", item.dataset.filter === "all"));
    state.selected = Number(chapterButton.dataset.topicChapter);
    renderChapters();
    renderDetail();
    document.querySelector("#chapters").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  els.practiceFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-practice-type]");
    if (!button) return;
    state.practiceType = button.dataset.practiceType;
    state.selectedPractice = "";
    renderPractice();
  });

  els.practiceList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-practice-id]");
    if (!button) return;
    state.selectedPractice = button.dataset.practiceId;
    renderPractice();
  });

  els.practiceDetail.addEventListener("click", (event) => {
    const chapterButton = event.target.closest("[data-practice-chapter]");
    if (!chapterButton) return;
    state.filter = "all";
    state.query = "";
    els.search.value = "";
    els.filters.forEach((item) => item.classList.toggle("active", item.dataset.filter === "all"));
    state.selected = Number(chapterButton.dataset.practiceChapter);
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
    state.practiceQuestions = data.practice_questions || [];
    state.selectedTopic = state.topics[0]?.id || state.selectedTopic;
    state.selectedPractice = state.practiceQuestions[0]?.id || "";
    document.querySelector("#metric-chapters").textContent = state.chapters.length;
    document.querySelector("#metric-topics").textContent = state.topics.length;
    bindEvents();
    renderChapters();
    renderDetail();
    renderRelations();
    renderTopics();
    renderPractice();
    if (window.location.hash) {
      document.querySelector(window.location.hash)?.scrollIntoView({ block: "start" });
    }
  } catch (error) {
    els.detail.innerHTML = `<div class="empty-state">章节数据没有加载成功：${error.message}。如果是直接打开文件，请用本目录的本地服务访问。</div>`;
  }
}

init();
