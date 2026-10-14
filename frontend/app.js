const API = "http://127.0.0.1:5000/api";

const chartsReady = typeof Chart !== "undefined";
if (chartsReady) {
  Chart.defaults.color = "#cbd5e1";
  Chart.defaults.borderColor = "rgba(255, 255, 255, 0.08)";
}

const CHART_COLORS = ["#11a58f", "#7c3aed", "#2dd4bf", "#f59e0b", "#ec4899", "#60a5fa", "#a3e635", "#f87171"];

const $ = (id) => document.getElementById(id);
async function api(path, options) {
  const response = await fetch(API + path, options);
  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    // the reply had no JSON body
  }
  if (!response.ok) {
    throw new Error((data && data.error) || "Something went wrong (" + response.status + ")");
  }
  return data;
}

function post(path, body) {
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function showMessage(text, ok = true) {
  const el = $("msg");
  el.textContent = text;
  el.style.color = ok ? "#22c55e" : "#ef4444";
}

function isoDate(d) {
  return (
    d.getFullYear() + "-" +
    String(d.getMonth() + 1).padStart(2, "0") + "-" +
    String(d.getDate()).padStart(2, "0")
  );
}

function monthKey() {
  return isoDate(new Date()).slice(0, 7);
}

function rupees(n) {
  return "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}
let allExpenses = [];
let currentBudget = null;
let pieChart = null;
let barChart = null;
async function loadAll() {
  try {
    const [expenses, summary, insights, budget] = await Promise.all([
      api("/expenses"),
      api("/summary"),
      api("/insights"),
      api("/budget?month=" + monthKey()),
    ]);

    allExpenses = expenses;
    currentBudget = budget.amount;

    renderFilter();
    renderList();
    renderPie(summary.by_category);
    renderBar();
    renderInsights(insights);
    renderBudget();
  } catch (error) {
    showMessage("Could not load data. Is the backend running? (See the Console for details.)", false);
    console.error(error);
  }
}
$("parseBtn").addEventListener("click", async () => {
  const sms = $("sms").value.trim();
  if (!sms) return showMessage("Paste a message first.", false);

  $("parseBtn").disabled = true;
  try {
    const result = await post("/parse-sms", { sms: sms });
    showMessage("Saved " + rupees(result.amount) + " at " + result.merchant + " under " + result.category);
    $("sms").value = "";
    await loadAll();
  } catch (error) {
    showMessage(error.message, false);
  } finally {
    $("parseBtn").disabled = false;
  }
});

$("addBtn").addEventListener("click", async () => {
  const amount = Number($("amount").value);
  const merchant = $("merchant").value.trim();
  if (!amount || amount <= 0) return showMessage("Enter a valid amount.", false);

  $("addBtn").disabled = true;
  try {
    const result = await post("/expense", { amount: amount, merchant: merchant });
    showMessage("Saved " + rupees(amount) + " under " + result.category);
    $("amount").value = "";
    $("merchant").value = "";
    await loadAll();
  } catch (error) {
    showMessage(error.message, false);
  } finally {
    $("addBtn").disabled = false;
  }
});
function renderFilter() {
  const select = $("filter");
  const previous = select.value;
  const categories = [...new Set(allExpenses.map((e) => e.category))];

  select.innerHTML = '<option value="">All categories</option>';
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    select.appendChild(option);
  });
  select.value = categories.includes(previous) ? previous : "";
}

function renderList() {
  const chosen = $("filter").value;
  const body = $("list");
  body.innerHTML = "";

  const rows = allExpenses.filter((e) => !chosen || e.category === chosen);

  if (rows.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 5;
    td.textContent = "No expenses yet. Add one above.";
    tr.appendChild(td);
    body.appendChild(tr);
    return;
  }

  rows.forEach((e) => {
    const tr = document.createElement("tr");

    [e.date, e.merchant || "-", e.category, rupees(e.amount)].forEach((text) => {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    });

    const actionCell = document.createElement("td");
    const button = document.createElement("button");
    button.textContent = "Delete";
    button.className = "del";
    button.addEventListener("click", () => deleteExpense(e.id));
    actionCell.appendChild(button);
    tr.appendChild(actionCell);

    body.appendChild(tr);
  });
}

async function deleteExpense(id) {
  if (!confirm("Delete this expense?")) return;
  try {
    await api("/expense/" + id, { method: "DELETE" });
    showMessage("Expense deleted.");
    await loadAll();
  } catch (error) {
    showMessage(error.message, false);
  }
}

$("filter").addEventListener("change", renderList);
function renderPie(byCategory) {
  if (!chartsReady) return;
  if (pieChart) pieChart.destroy();

  pieChart = new Chart($("pie"), {
    type: "doughnut",
    data: {
      labels: byCategory.map((c) => c.category),
      datasets: [
        {
          data: byCategory.map((c) => c.total),
          backgroundColor: CHART_COLORS,
          borderColor: "#0e0f14",
        },
      ],
    },
  });
}

function renderBar() {
  if (!chartsReady) return;

  const labels = [];
  const totals = [];
  for (let i = 6; i >= 0; i--) {
    const day = new Date();
    day.setDate(day.getDate() - i);
    const key = isoDate(day);
    labels.push(key.slice(5));
    const total = allExpenses
      .filter((e) => e.date === key)
      .reduce((sum, e) => sum + e.amount, 0);
    totals.push(Math.round(total * 100) / 100);
  }

  if (barChart) barChart.destroy();
  barChart = new Chart($("bar"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Spent (₹)", data: totals, backgroundColor: "#11a58f", borderRadius: 6 },
      ],
    },
    options: { plugins: { legend: { display: false } } },
  });
}
function renderInsights(data) {
  const list = $("insights");
  list.innerHTML = "";

  const lines = [];
  if (data.this_week > 0 || data.last_week > 0) {
    lines.push("This week: " + rupees(data.this_week) + "  |  Last week: " + rupees(data.last_week));
  }
  if (data.insights && data.insights.length > 0) {
    data.insights.forEach((tip) => lines.push(tip));
  }
  if (lines.length === 0) {
    lines.push("Add a few expenses to see insights.");
  }

  lines.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    list.appendChild(li);
  });
}
$("budgetBtn").addEventListener("click", async () => {
  const amount = Number($("budget").value);
  if (!amount || amount <= 0) return showMessage("Enter a valid budget.", false);

  try {
    await post("/budget", { month: monthKey(), amount: amount });
    currentBudget = amount;
    $("budget").value = "";
    showMessage("Budget saved.");
    renderBudget();
  } catch (error) {
    showMessage(error.message, false);
  }
});

function renderBudget() {
  const fill = $("barFill");
  const text = $("budgetText");
  const alertBox = $("alert");
  alertBox.textContent = "";

  if (!currentBudget) {
    fill.style.width = "0";
    text.textContent = "No budget set for this month.";
    return;
  }

  const spent = allExpenses
    .filter((e) => e.date.startsWith(monthKey()))
    .reduce((sum, e) => sum + e.amount, 0);

  const percent = Math.round((spent / currentBudget) * 100);

  fill.style.width = Math.min(percent, 100) + "%";
  fill.style.background = percent >= 100 ? "#ef4444" : percent >= 80 ? "#f59e0b" : "#11a58f";
  text.textContent = rupees(spent) + " of " + rupees(currentBudget) + " used (" + percent + "%)";

  if (percent >= 100) {
    alertBox.textContent = "You have gone over this month's budget.";
  } else if (percent >= 80) {
    alertBox.textContent = "Warning: you have used " + percent + "% of this month's budget.";
  }
}
loadAll();