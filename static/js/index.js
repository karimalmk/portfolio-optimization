// ======================================================
// Meta initialization
// ======================================================
document.addEventListener("DOMContentLoaded", async () => {
  try {
    await display_strategies();
  } catch (err) {
    console.error("Error displaying strategies:", err);
  }
});

// ======================================================
// Create strategy
// ======================================================
const form = document.getElementById("create-strategy");
if (form) {
  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const form_data = new FormData(this);

    const name = form_data.get("name")?.trim();
    const cash = parseFloat(form_data.get("cash"));

    if (!name) return alert("Enter a strategy name.");
    if (!cash || isNaN(cash) || cash <= 0)
      return alert("Enter a valid cash amount.");

    try {
      const response = await fetch("/api/create-strategy", {
        method: "POST",
        body: form_data,
      });
      if (!response.ok) throw new Error("Server error creating strategy.");

      const data = await response.json();
      if (data.status === "success") {
        await append_strategy(data);
        alert(`Strategy "${data.name}" created with initial cash ${data.cash}`);
        this.reset();
      } else {
        alert(data.message || "Failed to create strategy.");
      }
    } catch (err) {
      console.error("Create strategy failed:", err);
      alert("An unexpected error occurred while creating the strategy.");
    }
  });
}

// ======================================================
// Append new strategy to dropdown
// ======================================================
async function append_strategy(new_strategy) {
  let strategy_selection = document.getElementById("select-strategy");

  // First-time case — build the section
  if (!strategy_selection) {
    await display_strategies();
    strategy_selection = document.getElementById("select-strategy");
  }

  if (!strategy_selection) return console.warn("Strategy select not found.");

  const option = document.createElement("option");
  option.value = new_strategy.id;
  option.textContent = new_strategy.name;
  strategy_selection.appendChild(option);
  strategy_selection.value = new_strategy.id;

  await load_portfolio(new_strategy.id);
}

// ======================================================
// Load strategies dropdown
// ======================================================
async function load_strategies_dropdown() {
  const select = document.getElementById("select-strategy");
  if (!select) return;

  try {
    const response = await fetch("/api/strategies");
    if (!response.ok) throw new Error("Server error loading strategies.");

    const data = await response.json();
    select.innerHTML = `<option value="" disabled selected>— Select strategy —</option>`;

    if (Array.isArray(data.strategies)) {
      data.strategies.forEach((strategy) => {
        const option = document.createElement("option");
        option.value = strategy.id;
        option.textContent = strategy.name;
        select.appendChild(option);
      });
    }

    if (select.value) await load_portfolio(select.value);
  } catch (err) {
    console.error("Dropdown load failed:", err);
    alert("Error loading strategies.");
  }
}

// ======================================================
// Display strategies section
// ======================================================
async function display_strategies() {
  const placeholder = document.getElementById("content-placeholder");
  if (!placeholder) return;

  const exists = await check_strategies_exists();
  if (!exists) return;

  document.getElementById("strategy-content")?.remove();

  const container = document.createElement("div");
  container.id = "strategy-content";
  container.innerHTML = `
    <hr>
    <p>Select an existing strategy:</p>
    <select id="select-strategy"></select>
    <div id="portfolio"></div>
    <button id="edit-strategy" type="button">Edit</button>
    <div id="edit-list"></div>
  `;
  placeholder.appendChild(container);

  await load_strategies_dropdown();
}

// ======================================================
// Check if strategies exist
// ======================================================
async function check_strategies_exists() {
  try {
    const response = await fetch("/api/strategies");
    if (!response.ok) return false;
    const data = await response.json();
    return !!data.exists;
  } catch (err) {
    console.error("Check strategies failed:", err);
    return false;
  }
}

// ======================================================
// Delegated event listeners for rename/delete/done
// ======================================================
document.addEventListener("change", (event) => {
  if (event.target.id === "select-strategy") {
    const id = event.target.value;
    if (id) load_portfolio(id);
  }
});

document.addEventListener("click", async (event) => {
  const target = event.target;

  // --- Edit Mode ---
  if (target.id === "edit-strategy") {
    try {
      const response = await fetch("/api/strategies");
      if (!response.ok) throw new Error();
      const data = await response.json();

      const container = document.getElementById("edit-list");
      container.innerHTML = "";

      const table = document.createElement("table");
      data.strategies.forEach((stock) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td id="name-${stock.id}">${stock.name}</td>
          <td>
            <button class="rename-strategy" data-id="${stock.id}">Rename</button>
            <button class="delete-strategy" data-id="${stock.id}">Delete</button>
          </td>
        `;
        table.appendChild(row);
      });
      container.appendChild(table);
      container.insertAdjacentHTML(
        "beforeend",
        `<button id="done">Done</button>`
      );
    } catch (err) {
      console.error("Edit mode error:", err);
      alert("Failed to load strategies for editing.");
    }
  }

  // --- Rename ---
  if (target.classList.contains("rename-strategy")) {
    const id = target.dataset.id;
    const name_cell = document.getElementById(`name-${id}`);
    if (!name_cell) return;

    name_cell.innerHTML = `
      <input type="text" id="new-name-${id}" placeholder="New name" autocomplete="off" />
      <button type="button" id="confirm-rename-${id}">Confirm</button>
    `;
    document.getElementById(`new-name-${id}`).focus();
  }

  // --- Confirm rename ---
  if (target.id.startsWith("confirm-rename-")) {
    const id = target.id.replace("confirm-rename-", "");
    const input = document.getElementById(`new-name-${id}`);
    const new_name = input?.value?.trim();

    if (!new_name) return alert("Enter a new name.");
    try {
      const response = await fetch(`/api/rename-strategy/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_name }),
      });
      if (!response.ok) throw new Error();

      const name_cell = document.getElementById(`name-${id}`);
      if (name_cell) name_cell.textContent = new_name;
      await load_strategies_dropdown();
    } catch (err) {
      console.error("Rename failed:", err);
      alert("Rename failed.");
    }
  }

  // --- Delete ---
  if (target.classList.contains("delete-strategy")) {
    const id = target.dataset.id;
    if (!confirm("Are you sure you want to delete this strategy?")) return;

    try {
      const response = await fetch(`/api/delete-strategy/${id}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error();

      target.closest("tr")?.remove();
      const still_exists = await check_strategies_exists();
      if (!still_exists) document.getElementById("strategy-content")?.remove();
      else await load_strategies_dropdown();
    } catch (err) {
      console.error("Delete failed:", err);
      alert("Failed to delete strategy.");
    }
  }

  // --- Done ---
  if (target.id === "done") {
    const container = document.getElementById("edit-list");
    if (container) container.innerHTML = "";
    const still_exists = await check_strategies_exists();
    if (!still_exists) document.getElementById("strategy-content")?.remove();
    else await load_strategies_dropdown();
  }
});

// ======================================================
// Load portfolio
// ======================================================
async function load_portfolio(strategy_id) {
  if (!strategy_id) return;

  try {
    const response = await fetch(`/api/portfolio/${strategy_id}`);
    if (!response.ok) throw new Error();
    const data = await response.json();

    const div = document.getElementById("portfolio");
    if (!div) return;

    div.innerHTML = "";

    const overview = data.overview;
    const portfolio = data.portfolio;

    if (overview) {
      const t = document.createElement("table");
      t.innerHTML = `
        <tr><th>Starting Cash</th><td>${overview.starting_cash}</td></tr>
        <tr><th>Current Cash</th><td>${overview.current_cash}</td></tr>
        <tr><th>Total Value</th><td>${overview.total_value}</td></tr>
        <tr><th>Overall Return</th><td>${overview.overall_return}%</td></tr>
      `;
      div.appendChild(t);
    }

    if (Array.isArray(portfolio) && portfolio.length > 0) {
      const table = document.createElement("table");
      table.innerHTML = `
        <thead>
          <tr>
            <th>Ticker</th><th>Shares</th><th>Price</th><th>Value</th>
            <th>Weighted Price</th><th>Return</th>
          </tr>
        </thead>
        <tbody>
          ${portfolio
            .map(
              (stock) => `
              <tr>
                <td>${stock.ticker}</td>
                <td>${stock.shares}</td>
                <td>${stock.price}</td>
                <td>${stock.share_value}</td>
                <td>${stock.weighted_price}</td>
                <td>${stock.stock_return}%</td>
              </tr>`
            )
            .join("")}
        </tbody>
      `;
      div.appendChild(table);
    }
  } catch (err) {
    console.error("Portfolio load failed:", err);
    alert("Failed to load portfolio data.");
  }
}
