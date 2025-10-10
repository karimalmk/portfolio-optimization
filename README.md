# Portfolio Analytics

A **Flask-based portfolio management and analytics application** that allows users to **create investment strategies**, **manage stock portfolios**, **analyze performance**, and **execute transactions** — all through a clean, interactive web interface.

---

## 🎥 Demo
[Insert video link here]

---

## 🧭 Overview

### Portfolio Dashboard
- Create, rename, and delete portfolio strategies.  
- Display key portfolio analytics, including:
  - Cash balances  
  - Stock-level and overall returns  
  - Current and weighted prices  
  - Portfolio weight contributions  
- All stock quotes and metrics are standardized in **USD**, with compatibility across **30+ major exchanges**.

### Transactions
- Buy or sell shares with real-time validation (cash balance, share availability, etc.).  
- Deposit or withdraw funds, with instant portfolio-level updates and alerts.  

---

## 🧩 Project Architecture

### Flask Application Structure
The project is organized around a **modular Flask architecture**:

- A core `app.py` file handles global routes and app configuration.  
- A dedicated `blueprints/` directory defines specific API endpoints for each UI page.  
- Clear separation of concerns:
  - No inline JavaScript in HTML templates  
  - Distinct modules for database, API, and UI logic  
  - Controlled abstraction and minimal coupling between components  

---

## 🖼️ HTML Templates

### `layout.html`
Defines the core structure:
1. `<title>`  
2. `<header>`  
3. `<main>`  

> Note: both `header` and `main` are nested inside `<body>` for semantic alignment.

### `index.html` and `transactions.html`
- **Minimal static HTML**, relying on **JavaScript for dynamic rendering**.  
- Two key placeholders:
  - `content-placeholder` (in `index.html`): dynamically displays portfolio data and strategy edits.  
    - “Create strategy” input remains always visible for consistent UX and simpler logic.  
  - `input-placeholder` (in `transactions.html`): dynamically injects quote data and confirmation buttons after user actions.

---

## ⚙️ JavaScript Logic

### `transactions.js`
- Defines a **whitelist of valid actions** to prevent unwanted event propagation.  
- Uses a `strategy.selection` boolean to initialize async requests that sync selected strategies with the Flask backend (`transactions.py`).  
- Employs **event delegation** for dynamically rendered elements (e.g., buy/sell buttons not present at `DOMContentLoaded`).  

### `index.js`
- Combines `DOMContentLoaded` listeners and event delegation for portfolio display and editing.  
- Previous versions attempted auto-selection after renaming strategies but introduced sync issues — replaced with a **manual re-selection** flow for cleaner UX.

#### _AI Usage_
- Replaced repetitive ternary expressions with `switch` statements for downstream event delegation (`deposit`, `withdraw`, `buy`, `sell`).  
- Dynamically generated element IDs for buy/sell forms to trigger the correct transaction logic and client-side alerts.  
- Implemented consistent error handling for parsing user input and server API responses.  

---

## 🐍 Python Blueprints

Each blueprint corresponds to a specific page and JS file for clarity and modularity.

### `strategies.py`
Dedicated API for `index.js`.  
Handles:
- Creating new strategies  
- Loading and displaying portfolios  
- Renaming and deleting strategies  

### `transactions.py`
Dedicated API for `transactions.js`.  
Handles:
- Strategy selection  
- Deposits and withdrawals  
- Quotes, buy, and sell operations  

> Buying and selling share events are unified under a shared listener that dynamically references IDs of buy/sell form elements for cleaner, non-redundant logic.

#### _AI Usage_
- Introduced `try/finally` for clean database management and connection hygiene.  
- Implemented proper `abort()` error messages for user feedback.  

---

## 🧠 Helper Modules

### `api.py` (YFinance Integration)
- Custom stock quote API built using the **yfinance** library (inspired by CS50’s Finance problem set).  
- Implements caching for efficiency:
  - Stock quotes cached during market close.  
  - Cache cleared automatically upon market reopening.  
- Includes a dictionary of major exchanges with currency conversions to USD for consistent analytics.  
- Caching is handled in-memory for simplicity and low maintenance — no persistent DB cache.

### `setup.py`
- Provides `get_db()` and `close_db()` helpers for single-threaded DB interaction.  
- Converts Flask HTTP errors into **JSON responses** for client-side alert rendering.  

#### _AI Usage_
- Guided implementation of a clean, modular caching system with `LAST_MARKET_STATE` tracking.  
- Designed reusable Flask error handlers for consistent alert messages across the app.  

---

## 🗄️ Database Design

Defined in `portfolio.sql`, containing three core tables:

1. **strategy** – main portfolio strategies (primary key `id` referenced client- and server-side).  
2. **portfolio** – individual stock holdings within each strategy.  
3. **transactions** – records of executed trades, cash flows, and prices at execution.  

---

## 🎨 Styling

- Uses **Bootstrap CSS** for layout and responsiveness.  
- Includes a **custom `dark_mode.css`** for a minimalist, modern aesthetic.

---