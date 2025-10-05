// ============================
// CREATE STRATEGY
// ============================
document
  .getElementById("create-strategy")
  ?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    try {
      const response = await fetch("/api/create-strategy", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        alert("Failed to create strategy");
        return;
      }

      const new_strategy = await response.json();
      append_strategy(new_strategy);

      this.reset();
      await display_strategies();
    } catch (error) {
      console.error("Error creating strategy:", error);
    }
  });

// ============================
// DISPLAY STRATEGIES SECTION
// ============================
async function display_strategies() {
  const exists = await check_strategies_exists();
  const placeholder = document.getElementById("content-placeholder");

  if (!placeholder)
    return console.error("Missing #content-placeholder element");

  // Clear old content before re-adding
  const existing = document.getElementById("strategy-content");
  if (existing) existing.remove();

  if (exists) {
    const strategy_content = document.createElement("div");
    strategy_content.id = "strategy-content";
    strategy_content.innerHTML = `
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
    placeholder.appendChild(strategy_content);
    await load_strategies_dropdown();
  }
}

// ============================
// EVENT DELEGATION
// ============================
document.addEventListener("change", function (event) {
  if (event.target.id === "select-strategy") {
    load_portfolio(event.target.value);
  }
});

document.addEventListener("click", async function (event) {
  // Edit button
  if (event.target.id === "edit-strategy") {
    const response = await fetch("/api/edit-strategy");
    if (!response.ok) return alert("Failed to load strategies");

    const { strategies } = await response.json();
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
    container.innerHTML += `<p></p><button id="done">Done</button>`;
  }

  // Rename
  if (event.target.classList.contains("rename-strategy")) {
    const strategy_id = event.target.dataset.id;
    const name_field = document.getElementById(`name-${strategy_id}`);
    name_field.innerHTML = `
      <input type="text" id="new-name-${strategy_id}" placeholder="New name" />
      <button id="confirm-rename-${strategy_id}">Confirm</button>
    `;

    document
      .getElementById(`confirm-rename-${strategy_id}`)
      .addEventListener("click", async () => {
        const new_name = document
          .getElementById(`new-name-${strategy_id}`)
          .value.trim();
        if (!new_name) return alert("Enter a new name");

        const response = await fetch(`/api/rename-strategy/${strategy_id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ new_name }),
        });

        if (response.ok) {
          document.getElementById("edit-strategy").click();
        } else {
          alert("Error renaming strategy");
        }
      });
  }

  // Delete
  if (event.target.classList.contains("delete-strategy")) {
    const strategy_id = event.target.dataset.id;

    const response = await fetch(`/api/delete-strategy/${strategy_id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      event.target.closest("tr").remove();
    } else {
      alert("Failed to delete strategy");
    }

    const exists = await check_strategies_exists();
    if (!exists) {
      document.getElementById("edit-list").innerHTML = "";
      document.getElementById("strategy-content")?.remove();
    } else {
      await load_strategies_dropdown();
    }
  }

  // Done
  if (event.target.id === "done") {
    document.getElementById("edit-list").innerHTML = "";

    const exists = await check_strategies_exists();
    if (!exists) {
      document.getElementById("strategy-content")?.remove();
    } else {
      await load_strategies_dropdown();
    }
  }
});

// ============================
// APPEND STRATEGY
// ============================
async function append_strategy(new_strategy) {
  let select = document.getElementById("select-strategy");

  if (!document.getElementById("strategy-content")) {
    await display_strategies();
    select = document.getElementById("select-strategy");
  }

  if (select) {
    const option = document.createElement("option");
    option.value = new_strategy.id;
    option.text = new_strategy.name;
    select.add(option);
    select.value = new_strategy.id;
    load_portfolio(new_strategy.id);
  }
}

// Forcing a strategy content load
document.addEventListener("DOMContentLoaded", async () => {
  await display_strategies();
});

// ============================
// MODULAR FUNCTIONS
// ============================
async function check_strategies_exists() {
  const response = await fetch("/api/strategy-list-exists/");
  if (!response.ok) return false;
  const { exists } = await response.json();
  return exists;
}

async function load_strategies_dropdown() {
  const response = await fetch("/api/strategies");
  if (!response.ok) return;
  const data = await response.json();
  const select = document.getElementById("select-strategy");
  if (!select) return;
  select.innerHTML = "";
  data.strategies?.forEach((strategy) => {
    const option = document.createElement("option");
    option.value = strategy.id;
    option.text = strategy.name;
    select.add(option);
  });
}

async function load_portfolio(strategy_id) {
  const response = await fetch(`/api/load-portfolio/${strategy_id}`);
  if (!response.ok) return;
  const data = await response.json();

  const table = document.getElementById("portfolio");
  if (!table) return;

  const portfolio = data.portfolio;
  table.innerHTML = "<tr><th>Symbol</th><th>Shares</th></tr>";

  portfolio.forEach((stock) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${stock.symbol}</td><td>${stock.shares}</td>`;
    table.appendChild(row);
  });
}