// ============ 전역 상태 ============
let currentConversationId = null;
let allDataRecords = [];
let currentChartAsset = "금";
let currentCurrency = "USD";
let usdToKrwRate = 1350; // API 실패 시 사용할 대체 환율
let lastSummaryData = null;

// ============ 초기화 ============
document.addEventListener("DOMContentLoaded", () => {
  initDarkMode();
  fetchExchangeRate();
  loadSummary();
  loadDataList();
  loadConversations();

  document.getElementById("chatSendBtn").addEventListener("click", sendChatMessage);
  document.getElementById("chatInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
  document.getElementById("newChatBtn").addEventListener("click", startNewChat);
  document.getElementById("dataForm").addEventListener("submit", handleAddData);
  document.getElementById("exportCsvBtn").addEventListener("click", exportCSV);
  document.getElementById("exportJsonBtn").addEventListener("click", exportJSON);

  document.querySelectorAll(".chip[data-asset]").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip[data-asset]").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      currentChartAsset = chip.dataset.asset;
      drawChart();
    });
  });

  document.querySelectorAll(".chip[data-currency]").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip[data-currency]").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      currentCurrency = chip.dataset.currency;
      renderSummary(lastSummaryData);
      renderDataTable();
      drawChart();
    });
  });
});

// ============ 다크모드 ============
function initDarkMode() {
  const saved = localStorageSafeGet("theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateDarkModeIcon(saved);

  document.getElementById("darkModeToggle").addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    updateDarkModeIcon(next);
    localStorageSafeSet("theme", next);
    drawChart(); // 차트 색상 갱신
  });
}

function updateDarkModeIcon(theme) {
  document.getElementById("darkModeToggle").textContent = theme === "dark" ? "☀️" : "🌙";
}

// localStorage 접근 실패(사파리 프라이빗 모드 등) 대비 안전 래퍼
function localStorageSafeGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function localStorageSafeSet(key, value) {
  try { localStorage.setItem(key, value); } catch { /* ignore */ }
}

// ============ 환율 조회 ============
async function fetchExchangeRate() {
  try {
    const res = await fetch("https://api.exchangerate-api.com/v4/latest/USD");
    if (!res.ok) throw new Error("환율 조회 실패");
    const data = await res.json();
    if (data?.rates?.KRW) {
      usdToKrwRate = data.rates.KRW;
      updateRateNotice();
      // 이미 렌더링된 화면이 있다면 새 환율로 다시 그림
      if (lastSummaryData) renderSummary(lastSummaryData);
      if (allDataRecords.length) {
        renderDataTable();
        drawChart();
      }
    }
  } catch (err) {
    console.warn("실시간 환율 조회 실패, 대체 환율(1 USD ≈ " + usdToKrwRate + " KRW) 사용:", err.message);
  }
}

function updateRateNotice() {
  const el = document.getElementById("rateNotice");
  if (el) el.textContent = `1 USD ≈ ${usdToKrwRate.toLocaleString()} KRW`;
}

// ============ 통화 변환/표시 유틸 ============
function formatPrice(usdValue) {
  if (usdValue === null || usdValue === undefined || isNaN(usdValue)) return "-";
  if (currentCurrency === "KRW") {
    const krw = usdValue * usdToKrwRate;
    return `₩${Math.round(krw).toLocaleString()}`;
  }
  return `$${usdValue.toFixed(2)}`;
}

function convertForChart(usdValue) {
  return currentCurrency === "KRW" ? usdValue * usdToKrwRate : usdValue;
}

// ============ 데이터 요약 ============
async function loadSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/summary`);
    const data = await res.json();
    lastSummaryData = data;
    renderSummary(data);
  } catch (err) {
    document.getElementById("summaryContent").innerHTML =
      `<p class="loading-text">요약 정보를 불러오지 못했습니다.</p>`;
  }
}

function renderSummary(summary) {
  const container = document.getElementById("summaryContent");
  if (!summary || summary.count === 0) {
    container.innerHTML = `<p class="loading-text">저장된 데이터가 없습니다.</p>`;
    return;
  }

  const goldTrend = summary.trend?.["금"] || "-";
  const silverTrend = summary.trend?.["은"] || "-";
  const ratio = summary.ratio?.gold_silver_ratio ?? "-";
  const goldAvg = summary.metrics?.["금"]?.average;
  const silverAvg = summary.metrics?.["은"]?.average;

  const rows = [
    ["기간", summary.period, "총 데이터", `${summary.count}개`],
    [`금 평균가 (${currentCurrency}/oz)`, formatPrice(goldAvg), `은 평균가 (${currentCurrency}/oz)`, formatPrice(silverAvg)],
    ["금 추세", goldTrend, "은 추세", silverTrend],
    ["금/은 비율", ratio, "환율 기준", `1 USD ≈ ${usdToKrwRate.toLocaleString()} KRW`],
  ];

  container.innerHTML = `
    <div class="summary-table">
      ${rows.map(([l1, v1, l2, v2]) => `
        <div class="cell label">${l1}</div>
        <div class="cell value" id="${l1 === "환율 기준" ? "" : ""}">${v1}</div>
        <div class="cell label">${l2}</div>
        <div class="cell value" id="${l2 === "환율 기준" ? "rateNotice" : ""}">${v2}</div>
      `).join("")}
    </div>
  `;
}

// ============ 데이터 목록 + 차트 ============
async function loadDataList() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data`);
    allDataRecords = await res.json();
    renderDataTable();
    drawChart();
  } catch (err) {
    document.getElementById("dataTableBody").innerHTML =
      `<tr><td colspan="4" class="loading-text">데이터를 불러오지 못했습니다.</td></tr>`;
  }
}

function renderDataTable() {
  const header = document.getElementById("valueColumnHeader");
  if (header) header.textContent = `값 (${currentCurrency})`;

  const tbody = document.getElementById("dataTableBody");
  if (allDataRecords.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="loading-text">데이터가 없습니다.</td></tr>`;
    return;
  }

  // 최신 50개만 테이블에 표시 (전체는 차트/요약에 반영, 테이블은 가독성을 위해 제한)
  const sorted = [...allDataRecords].sort((a, b) => (a.date < b.date ? 1 : -1));
  const recent = sorted.slice(0, 50);

  tbody.innerHTML = recent.map((item) => `
    <tr>
      <td>${item.date}</td>
      <td>${formatPrice(item.value)}</td>
      <td>${item.memo}</td>
      <td>
        <button onclick="handleDeleteData('${item.id}')" class="delete-btn">삭제</button>
      </td>
    </tr>
  `).join("");
}

async function handleAddData(e) {
  e.preventDefault();
  const date = document.getElementById("dataDate").value;
  const value = parseFloat(document.getElementById("dataValue").value);
  const memo = document.getElementById("dataMemo").value;

  if (!date || isNaN(value)) {
    alert("날짜와 값을 올바르게 입력해주세요.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date, value, memo }),
    });
    if (!res.ok) throw new Error("추가 실패");

    document.getElementById("dataForm").reset();
    await loadDataList();
    await loadSummary();
  } catch (err) {
    alert("데이터 추가에 실패했습니다: " + err.message);
  }
}

async function handleDeleteData(id) {
  if (!confirm("이 데이터를 삭제하시겠습니까?")) return;
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("삭제 실패");
    await loadDataList();
    await loadSummary();
  } catch (err) {
    alert("삭제에 실패했습니다: " + err.message);
  }
}

// ============ 차트 (순수 Canvas, 라이브러리 미사용) ============
function drawChart() {
  const canvas = document.getElementById("priceChart");
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;

  const cssWidth = canvas.clientWidth || 800;
  const cssHeight = 300;
  canvas.width = cssWidth * dpr;
  canvas.height = cssHeight * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, cssWidth, cssHeight);

  const filtered = allDataRecords
    .filter((r) => r.memo === currentChartAsset)
    .sort((a, b) => (a.date > b.date ? 1 : -1));

  if (filtered.length === 0) {
    ctx.fillStyle = getCssVar("--text-secondary");
    ctx.font = "13px sans-serif";
    ctx.fillText("표시할 데이터가 없습니다.", 20, 30);
    return;
  }

  const padding = { top: 20, right: 20, bottom: 30, left: 70 };
  const chartW = cssWidth - padding.left - padding.right;
  const chartH = cssHeight - padding.top - padding.bottom;

  const values = filtered.map((r) => convertForChart(r.value));
  const minV = Math.min(...values);
  const maxV = Math.max(...values);
  const range = maxV - minV || 1;

  const lineColor = currentChartAsset === "금" ? getCssVar("--gold") : getCssVar("--silver");
  const textColor = getCssVar("--text-secondary");
  const borderColor = getCssVar("--border");

  // 축
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + chartH);
  ctx.lineTo(padding.left + chartW, padding.top + chartH);
  ctx.stroke();

  // Y축 라벨 (최대/최소/중간)
  ctx.fillStyle = textColor;
  ctx.font = "11px sans-serif";
  ctx.textAlign = "right";
  [maxV, (maxV + minV) / 2, minV].forEach((v, i) => {
    const y = padding.top + (chartH / 2) * i;
    const label = currentCurrency === "KRW" ? Math.round(v).toLocaleString() : v.toFixed(1);
    ctx.fillText(label, padding.left - 8, y + 4);
  });

  // 선 그래프
  ctx.strokeStyle = lineColor;
  ctx.lineWidth = 2;
  ctx.beginPath();
  filtered.forEach((point, i) => {
    const x = padding.left + (chartW / (filtered.length - 1 || 1)) * i;
    const convertedValue = convertForChart(point.value);
    const y = padding.top + chartH - ((convertedValue - minV) / range) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // X축 라벨 (시작/끝 날짜)
  ctx.fillStyle = textColor;
  ctx.textAlign = "left";
  ctx.fillText(filtered[0].date, padding.left, cssHeight - 8);
  ctx.textAlign = "right";
  ctx.fillText(filtered[filtered.length - 1].date, padding.left + chartW, cssHeight - 8);
}

function getCssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

window.addEventListener("resize", () => {
  if (allDataRecords.length) drawChart();
});

// ============ 채팅 ============
async function sendChatMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  appendChatBubble("user", message);
  input.value = "";
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: currentConversationId,
        use_tools: false,
      }),
    });
    if (!res.ok) throw new Error("AI 응답 실패");

    const data = await res.json();
    currentConversationId = data.conversation_id;
    appendChatBubble("assistant", data.reply);
    await loadConversations();
  } catch (err) {
    appendChatBubble("assistant", "죄송합니다. 답변을 가져오는 중 오류가 발생했습니다.");
  } finally {
    setLoading(false);
  }
}

function appendChatBubble(role, text) {
  const container = document.getElementById("chatMessages");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function setLoading(isLoading) {
  document.getElementById("loadingIndicator").classList.toggle("hidden", !isLoading);
  document.getElementById("chatSendBtn").disabled = isLoading;
}

function startNewChat() {
  currentConversationId = null;
  document.getElementById("chatMessages").innerHTML = "";
}

// ============ 대화 기록 ============
async function loadConversations() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`);
    const list = await res.json();
    renderConversationList(list);
  } catch (err) {
    document.getElementById("conversationList").innerHTML =
      `<li class="loading-text">불러오지 못했습니다.</li>`;
  }
}

function renderConversationList(list) {
  const ul = document.getElementById("conversationList");
  if (list.length === 0) {
    ul.innerHTML = `<li class="loading-text">저장된 대화가 없습니다.</li>`;
    return;
  }

  ul.innerHTML = list.map((conv) => `
    <li onclick="loadConversationDetail('${conv.id}')">
      <span class="conv-delete" onclick="event.stopPropagation(); deleteConversation('${conv.id}')">삭제</span>
      <div class="conv-title">${escapeHtml(conv.title)}</div>
      <div class="conv-meta">${conv.message_count}개 메시지</div>
    </li>
  `).join("");
}

async function loadConversationDetail(id) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
    if (!res.ok) throw new Error("불러오기 실패");
    const data = await res.json();

    currentConversationId = data.id;
    const container = document.getElementById("chatMessages");
    container.innerHTML = "";
    data.messages.forEach((m) => appendChatBubble(m.role, m.content));
  } catch (err) {
    alert("대화를 불러오지 못했습니다.");
  }
}

async function deleteConversation(id) {
  if (!confirm("이 대화를 삭제하시겠습니까?")) return;
  try {
    await fetch(`${API_BASE_URL}/api/conversations/${id}`, { method: "DELETE" });
    if (currentConversationId === id) startNewChat();
    await loadConversations();
  } catch (err) {
    alert("삭제에 실패했습니다.");
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ============ 내보내기 (CSV / JSON) ============
function exportCSV() {
  if (allDataRecords.length === 0) {
    alert("내보낼 데이터가 없습니다.");
    return;
  }
  const header = "date,value_usd,memo\n";
  const rows = allDataRecords.map((r) => `${r.date},${r.value},${r.memo}`).join("\n");
  downloadFile(header + rows, "gold_silver_data.csv", "text/csv");
}

function exportJSON() {
  if (allDataRecords.length === 0) {
    alert("내보낼 데이터가 없습니다.");
    return;
  }
  downloadFile(JSON.stringify(allDataRecords, null, 2), "gold_silver_data.json", "application/json");
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType + ";charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}