// Handle create strategy form
document
  .getElementById("create-strategy")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    let formData = new FormData(this);
    let response = await fetch("/api/create-strategy", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      alert("Failed to create strategy");
      return;
    }

    let newStrategy = await response.json();
    appendStrategyToDropdown(newStrategy);
  });

// Handle dropdown selection
document
  .getElementById("select-strategy")
  .addEventListener("change", function () {
    loadPortfolio(this.value);
  });

// Show edit options upon clicking "Edit Strategy"
document
  .getElementById("edit-strategy")
  .addEventListener("click", async function (event) {
    event.preventDefault();

    const response = await fetch("/api/edit-strategy");
    if (!response.ok) {
      alert("Failed to load strategies");
      return;
    }

    const data = await response.json();
    const strategies = data.strategies;

    const container = document.getElementById("edit-list");
    container.innerHTML = "";

    const tbody = document.createElement("tbody");
    strategies.forEach((s) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
      <td>${s.name}</td>
      <td>
        <button class="rename-strategy" data-id="${s.id}">Rename</button>
        <button class="delete-strategy" data-id="${s.id}">Delete</button>
      </td>
    `;
      tbody.appendChild(tr);
    });
    tbody.innerHTML += `<button id="done">Done</button>`;
    container.appendChild(tbody);
  });

// Handle rename, delete, and done buttons (event delegation)
document
  .getElementById("edit-list")
  .addEventListener("click", function (event) {
    // Rename strategy
    if (event.target.classList.contains("rename-strategy")) {
      event.preventDefault();
      const strategy_id = event.target.dataset.id;
      const new_name = prompt("Enter new strategy name:");
      if (!new_name) return;

      fetch(`/api/rename-strategy/${strategy_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_name }),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to rename strategy");
          return res.json();
        })
        .then(() => {
          alert("Strategy renamed successfully");
          document.getElementById("edit-strategy").click(); // refresh list
        })
        .catch(() => alert("Error renaming strategy"));
    }

    // Delete strategy
    if (event.target.classList.contains("delete-strategy")) {
      event.preventDefault();
      const strategy_id = event.target.dataset.id;
      if (!confirm("Delete this strategy?")) return;

      fetch(`/api/delete-strategy/${strategy_id}`, { method: "DELETE" })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to delete strategy");
          return res.json();
        })
        .then(() => {
          alert("Strategy deleted");
          event.target.closest("tr").remove();
        })
        .catch(() => alert("Error deleting strategy"));
    }

    // Done editing
    if (event.target.id === "done") {
      event.preventDefault();
      const strategy_id = event.target.dataset.id;

      // Here you can add any logic needed when done editing
      const container = document.getElementById("edit-list");
      container.innerHTML = "";
    }
  });

//////// MODULAR FUNCTIONS ////////

// Load portfolio for selected strategy
async function loadPortfolio(strategy_id) {
  try {
    let response = await fetch(`/api/portfolio/${strategy_id}`);
    if (!response.ok) throw new Error("Failed to load portfolio");

    let data = await response.json();

    let html = `
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
          </tr>
        </thead>
        <tbody>
    `;

    data.portfolio.forEach((stock) => {
      html += `
        <tr>
          <td>${stock.symbol}</td>
          <td>${stock.shares}</td>
        </tr>
      `;
    });

    html += `
        </tbody>
      </table>
    `;

    document.getElementById("portfolio").innerHTML = html;
  } catch (err) {
    console.error(err);
    document.getElementById("portfolio").innerText = "Error loading portfolio";
  }
}

// Append a new strategy to dropdown
function appendStrategyToDropdown(strategy) {
  let select = document.getElementById("select-strategy");
  let option = document.createElement("option");
  option.value = strategy.id;
  option.text = strategy.name;
  select.add(option);

  select.value = strategy.id; // auto-select
  loadPortfolio(strategy.id); // auto-load portfolio
}
