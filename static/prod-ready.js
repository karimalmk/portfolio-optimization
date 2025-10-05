// ============================
// CREATE STRATEGY
// ============================
document
  .getElementById("create-strategy")
  ?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    this.querySelector("button[type='submit']").disabled = true; // Prevent double submit

    try {
      const response = await fetch("/api/create-strategy", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        alert("Failed to create strategy");
        return;
      }

      const newStrategy = await response.json();
      await ensureStrategySection();
      appendStrategy(newStrategy);
      this.reset();
    } catch (error) {
      console.error("Error creating strategy:", error);
    } finally {
      this.querySelector("button[type='submit']").disabled = false;
    }
  });

// ============================
// DISPLAY STRATEGIES SECTION
// ============================
async function ensureStrategySection() {
  const exists = await checkStrategiesExists();
  const placeholder = document.getElementById("content-placeholder");
  if (!placeholder)
    return console.error("Missing #content-placeholder element");

  // Remove old section if present
  document.getElementById("strategy-content")?.remove();

  if (!exists) return;

  const content = document.createElement("div");
  content.id = "strategy-content";
  content.innerHTML = `
    <hr>
    <p>Select an existing strategy:</p>
    <select id="select-strategy"></select>
    <p></p>
    <table id="portfolio"></table>
    <hr>
    <button id="edit-strategy" type="button">Edit</button>
    <p></p>
    <div id="edit-list"></div>
  `;
  placeholder.appendChild(content);
  await loadStrategiesDropdown();
}

// ============================
// EVENT DELEGATION
// ============================
document.addEventListener("change", (event) => {
  if (event.target.id === "select-strategy") {
    debounceLoadPortfolio(event.target.value);
  }
});

document.addEventListener("click", async (event) => {
  // --- Edit Strategies ---
  if (event.target.id === "edit-strategy") {
    await renderEditTable();
  }

  // --- Rename ---
  if (event.target.classList.contains("rename-strategy")) {
    const strategyId = event.target.dataset.id;
    const cell = document.getElementById(`name-${strategyId}`);
    if (!cell) return;

    cell.innerHTML = `
      <input type="text" id="new-name-${strategyId}" placeholder="New name" />
      <button class="confirm-rename" data-id="${strategyId}">Confirm</button>
    `;
  }

  // --- Confirm Rename (delegated) ---
  if (event.target.classList.contains("confirm-rename")) {
    const id = event.target.dataset.id;
    const input = document.getElementById(`new-name-${id}`);
    const newName = input?.value.trim();
    if (!newName) return alert("Enter a new name");

    const res = await fetch(`/api/rename-strategy/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_name: newName }),
    });

    if (res.ok) {
      document.getElementById(`name-${id}`).textContent = newName;
      await loadStrategiesDropdown(); // update dropdown only
    } else {
      alert("Error renaming strategy");
    }
  }

  // --- Delete ---
  if (event.target.classList.contains("delete-strategy")) {
    const id = event.target.dataset.id;
    const res = await fetch(`/api/delete-strategy/${id}`, { method: "DELETE" });
    if (!res.ok) return alert("Failed to delete strategy");

    event.target.closest("tr").remove();

    const exists = await checkStrategiesExists();
    if (exists) {
      await loadStrategiesDropdown();
    } else {
      document.getElementById("strategy-content")?.remove();
    }
  }

  // --- Done ---
  if (event.target.id === "done") {
    document.getElementById("edit-list").innerHTML = "";
  }
});

// ============================
// RENDER EDIT TABLE
// ============================
async function renderEditTable() {
  const btn = document.getElementById("edit-strategy");
  btn.disabled = true;
  try {
    const res = await fetch("/api/edit-strategy");
    if (!res.ok) return alert("Failed to load strategies");

    const { strategies } = await res.json();
    const container = document.getElementById("edit-list");
    container.innerHTML = "";

    const table = document.createElement("table");
    strategies.forEach((s) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td id="name-${s.id}">${s.name}</td>
        <td>
          <button class="rename-strategy" data-id="${s.id}">Rename</button>
          <button class="delete-strategy" data-id="${s.id}">Delete</button>
        </td>
      `;
      table.appendChild(row);
    });

    container.appendChild(table);

    const doneBtn = document.createElement("button");
    doneBtn.id = "done";
    doneBtn.textContent = "Done";
    container.appendChild(document.createElement("p"));
    container.appendChild(doneBtn);
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

// ============================
// APPEND STRATEGY
// ============================
function appendStrategy(newStrategy) {
  const select = document.getElementById("select-strategy");
  if (!select) return;

  const option = document.createElement("option");
  option.value = newStrategy.id;
  option.text = newStrategy.name;
  select.add(option);
  select.value = newStrategy.id;
  loadPortfolio(newStrategy.id);
}

// ============================
// INITIALIZATION
// ============================
document.addEventListener("DOMContentLoaded", async () => {
  await ensureStrategySection();
});

// ============================
// MODULAR HELPERS
// ============================
async function checkStrategiesExists() {
  const res = await fetch("/api/strategy-list-exists/");
  if (!res.ok) return false;
  const { exists } = await res.json();
  return exists;
}

async function loadStrategiesDropdown() {
  const res = await fetch("/api/strategies");
  if (!res.ok) return;
  const { strategies } = await res.json();

  const select = document.getElementById("select-strategy");
  if (!select) return;
  select.innerHTML = "";

  strategies.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    select.add(opt);
  });
}

async function loadPortfolio(strategyId) {
  const res = await fetch(`/api/load-portfolio/${strategyId}`);
  if (!res.ok) return;

  const { portfolio } = await res.json();
  const table = document.getElementById("portfolio");
  if (!table) return;

  table.innerHTML = "<tr><th>Symbol</th><th>Shares</th></tr>";
  portfolio?.forEach((stock) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${stock.symbol}</td><td>${stock.shares}</td>`;
    table.appendChild(row);
  });
}

// ============================
// DEBOUNCE PORTFOLIO LOADING
// ============================
let portfolioTimeout;
function debounceLoadPortfolio(id) {
  clearTimeout(portfolioTimeout);
  portfolioTimeout = setTimeout(() => loadPortfolio(id), 300);
}
