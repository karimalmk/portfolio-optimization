// ============================
// Create strategy
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
// Display strategies
// ============================
async function display_strategies() {
  const exists = await check_strategies_exists();
  const placeholder = document.getElementById("content-placeholder");
  if (!placeholder)
    return console.error("Missing #content-placeholder element");

  document.getElementById("strategy-content")?.remove();

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
// Event delegation
// ============================
document.addEventListener("change", (event) => {
  if (event.target.id === "select-strategy") {
    load_portfolio(event.target.value);
  }
});

document.addEventListener("click", async (event) => {
  // Edit mode
  if (event.target.id === "edit-strategy") {
    const response = await fetch("/api/strategies");
    if (!response.ok) return alert("Failed to load strategies");

    const data = await response.json();
    const strategies = data.strategies;
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
    const id = event.target.dataset.id;
    const nameCell = document.getElementById(`name-${id}`);
    nameCell.innerHTML = `
      <input type="text" id="new-name-${id}" placeholder="New name" />
      <button id="confirm-rename-${id}">Confirm</button>
    `;
  }

  // Confirm rename
  if (event.target.id.startsWith("confirm-rename-")) {
    const id = event.target.id.replace("confirm-rename-", "");
    const newName = document.getElementById(`new-name-${id}`).value.trim();
    if (!newName) return alert("Enter a new name");

    const response = await fetch(`/api/rename-strategy/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_name: newName }),
    });

    if (response.ok) {
      await display_strategies();
    } else {
      alert("Error renaming strategy");
    }
  }

  // Delete
  if (event.target.classList.contains("delete-strategy")) {
    const id = event.target.dataset.id;
    const response = await fetch(`/api/delete-strategy/${id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      event.target.closest("tr").remove();
      const stillExists = await check_strategies_exists();
      if (!stillExists) {
        document.getElementById("edit-list").innerHTML = "";
        document.getElementById("strategy-content")?.remove();
      } else {
        await load_strategies_dropdown();
      }
    } else {
      alert("Failed to delete strategy");
    }
  }

  // Done
  if (event.target.id === "done") {
    document.getElementById("edit-list").innerHTML = "";
    const stillExists = await check_strategies_exists();
    if (!stillExists) {
      document.getElementById("strategy-content")?.remove();
    } else {
      await load_strategies_dropdown();
    }
  }
});

// ============================
// Append strategy
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
    await load_portfolio(new_strategy.id);
  }
}

// ============================
// Portfolio loader
// ============================
async function load_portfolio(strategy_id) {
  try {
    const response = await fetch(`/api/portfolio/${strategy_id}`);
    if (!response.ok) return;

    const portfolio = await response.json();
    const table = document.getElementById("portfolio");
    if (!table) return;

    table.innerHTML = "";

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>Symbol</th>
        <th>Shares</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    // Handle empty or null portfolios safely
    if (!portfolio || portfolio.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td colspan="2" style="text-align:center; font-style:italic;">
          No holdings in this strategy.
        </td>
      `;
      tbody.appendChild(row);
    } else {
      portfolio.forEach((stock) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${stock.symbol}</td>
          <td>${stock.shares}</td>
        `;
        tbody.appendChild(row);
      });
    }

    table.appendChild(tbody);
  } catch (error) {
    console.error("Error loading portfolio:", error);
  }
}

// ============================
// Check if strategies exist
// ============================
async function check_strategies_exists() {
  try {
    const response = await fetch("/api/strategies");
    if (!response.ok) return false;
    const data = await response.json();
    return !!data.exists;
  } catch (error) {
    console.error("Error checking strategies:", error);
    return false;
  }
}

// ============================
// Load strategies dropdown
// ============================
async function load_strategies_dropdown() {
  const response = await fetch("/api/strategies");
  if (!response.ok) return;

  const data = await response.json();
  const strategies = data.strategies;
  const select = document.getElementById("select-strategy");
  if (!select) return;

  select.innerHTML = "";

  // Add a default empty option first
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "— Select a strategy —";
  defaultOption.disabled = true;
  defaultOption.selected = true;
  select.appendChild(defaultOption);

  // Then add actual strategies
  strategies.forEach((s) => {
    const option = document.createElement("option");
    option.value = s.id;
    option.text = s.name;
    select.add(option);
  });
}


// ============================
// DOM ready
// ============================
document.addEventListener("DOMContentLoaded", display_strategies);