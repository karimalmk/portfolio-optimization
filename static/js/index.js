// ======================================================
// Create strategy
// ======================================================
document
  .getElementById("create-strategy")
  ?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const response = await fetch("/api/create-strategy", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    await append_strategy(data);
    if (data.status == "success") {
      alert(`Strategy "${data.name}" created with initial cash ${data.cash}`);
      this.reset();
    }
  });

async function append_strategy(newStrategy) {
  if (!newStrategy) return;
  let select = document.getElementById("select-strategy");

  if (!document.getElementById("strategy-content")) {
    await display_strategies();
    select = document.getElementById("select-strategy");
  }

  if (select) {
    const option = document.createElement("option");
    option.value = newStrategy.id;
    option.text = newStrategy.name;
    select.add(option);
    select.value = newStrategy.id;
    await load_portfolio(newStrategy.id);
  }
}

// ======================================================
// Display strategies
// ======================================================
async function display_strategies() {
  const exists = await check_strategies_exists();
  const placeholder = document.getElementById("content-placeholder");
  if (!placeholder) return console.error("Missing #content-placeholder");

  document.getElementById("strategy-content")?.remove();

  if (!exists) return;

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

// ----- DOM auto-load ------
document.addEventListener("DOMContentLoaded", display_strategies);

// ======================================================
// Event delegation
// ======================================================
document.addEventListener("change", (event) => {
  if (event.target.id === "select-strategy") {
    load_portfolio(event.target.value);
  }
});

document.addEventListener("click", async (event) => {
  const target = event.target;

  // ----- Edit Mode -----
  if (target.id === "edit-strategy") {
    const response = await fetch("/api/strategies");
    if (!response.ok) return alert("Failed to load strategies");

    const data = await response.json();
    const strategies = data.strategies;
    const container = document.getElementById("edit-list");
    container.innerHTML = "";

    const table = document.createElement("table");
    strategies.forEach((stock) => {
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
  }

  // ----- Rename -----
  if (target.classList.contains("rename-strategy")) {
    const id = target.dataset.id;
    const nameCell = document.getElementById(`name-${id}`);
    nameCell.innerHTML = `
      <input type="text" id="new-name-${id}" placeholder="New name" autocomplete="off" />
      <button type="button" id="confirm-rename-${id}">Confirm</button>
    `;
    document.getElementById(`new-name-${id}`).focus();
  }

  // ----- Confirm rename -----
  if (target.id.startsWith("confirm-rename-")) {
    const id = target.id.replace("confirm-rename-", "");
    const newName = document.getElementById(`new-name-${id}`).value.trim();
    if (!newName) return alert("Enter a new name");

    const response = await fetch(`/api/rename-strategy/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_name: newName }),
    });

    if (response.ok) {
      // Update name in table directly
      const nameCell = document.getElementById(`name-${id}`);
      nameCell.textContent = newName;

      // Refresh dropdown without resetting edit mode
      await load_strategies_dropdown();
    }
  }

  // ----- Delete -----
  if (target.classList.contains("delete-strategy")) {
    const id = target.dataset.id;
    const response = await fetch(`/api/delete-strategy/${id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      target.closest("tr").remove();
      const stillExists = await check_strategies_exists();
      if (!stillExists) document.getElementById("strategy-content")?.remove();
      else await load_strategies_dropdown();
    } else {
      alert("Failed to delete strategy");
    }
  }

  // ----- Done -----
  if (target.id === "done") {
    document.getElementById("edit-list").innerHTML = "";
    const stillExists = await check_strategies_exists();
    if (!stillExists) document.getElementById("strategy-content")?.remove();
    else await load_strategies_dropdown();
  }
});

// ======================================================
// Load portfolio
// ======================================================
async function load_portfolio(strategy_id) {
  const response = await fetch(`/api/portfolio/${strategy_id}`);
  if (!response.ok) return;

  const data = await response.json();
  const portfolio = data.portfolio;
  const overview = data.overview;

  const div = document.getElementById("portfolio");
  if (!div) return;
  div.innerHTML = "";

  // ---- Overview ----
  if (overview) {
    const overviewTable = document.createElement("table");
    overviewTable.innerHTML = `
      <tr><th>Starting Cash</th><td>${overview.starting_cash}</td></tr>
      <tr><th>Current Cash</th><td>${overview.current_cash}</td></tr>
      <tr><th>Total Value</th><td>${overview.total_value}</td></tr>
      <tr><th>Overall Return</th><td>${overview.overall_return.toFixed(2)}%</td></tr>
    `;
    div.appendChild(overviewTable);
  }

  // ---- Portfolio ----
  if (portfolio) {
    const table = document.createElement("table");
    table.innerHTML = `
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Shares</th>
          <th>Price</th>
          <th>Value</th>
          <th>Weighted Price</th>
          <th>Return</th>
        </tr>
      </thead>
      <tbody>
        ${portfolio // Dynamically generate rows without using innerHTML in a loop
          .map(
            (stock) => `
            <tr>
              <td>${stock.ticker}</td>
              <td>${stock.shares}</td>
              <td>${stock.share_price}</td>
              <td>${stock.total_share_value}</td>
              <td>${stock.weighted_price}</td>
              <td>${stock.stock_return}%</td>
            </tr>
          `
          )
          .join("")}
      </tbody>
    `;
    div.appendChild(table);
  }
}

// ======================================================
// Check strategies exist
// ======================================================
async function check_strategies_exists() {
  const response = await fetch("/api/strategies");
  if (!response.ok) return false;
  const data = await response.json();
  return !!data.exists;
}

// ======================================================
// Load strategies dropdown
// ======================================================
async function load_strategies_dropdown() {
  const response = await fetch("/api/strategies");
  const data = await response.json();
  const select = document.getElementById("select-strategy");

  select.innerHTML = `
    <option value="" disabled selected>— Select strategy —</option>
    ${data.strategies
      .map((stock) => `<option value="${stock.id}">${stock.name}</option>`)
      .join("")}
  `;
}
