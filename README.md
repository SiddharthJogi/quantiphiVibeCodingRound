# Subscription Tracker & Renewal Dashboard

A lightweight, modern web application designed to help users track active software subscriptions, calculate normalized monthly cash-flow burn rates, and identify imminent or overdue renewals via a pristine dashboard.

## 🏗️ Architecture Design

This project adopts a **Modular Scalable Architecture** consisting of a decoupled frontend and backend. This separation of concerns ensures that the user interface, business logic, and data layers can scale or be swapped independently without tight coupling.

### 1. Backend (`/backend`)
Built with **FastAPI** (Python 3.13), the backend acts as a high-performance REST API.
- **`main.py`**: The API routing layer. Handles HTTP requests, CORS, and orchestrates the dependency injection of engines and storage. It also conveniently mounts the static `/frontend` directory for an out-of-the-box unified deployment.
- **`models.py`**: The data validation and schema definition layer using Pydantic. It strictly types incoming payloads and outbound Data Transfer Objects (DTOs).
- **`store.py`**: The persistence layer. Currently implements an in-memory dictionary acting as the operational database for rapid prototyping.
- **`engines.py`**: The pure business logic layer. Completely isolated from the web framework, these engines handle complex date math (evaluating renewal urgency) and decimal currency normalization (converting yearly costs to monthly equivalents).
- **`test_main.py`**: An exhaustive automated test suite powered by `pytest` ensuring 100% compliance with edge cases (e.g., zero-cost rejections, overdue boundary math, and live toggle metrics recalculation).

### 2. Frontend (`/frontend`)
Built with **Vanilla HTML, CSS, and JavaScript**, strictly adhering to modern UI/UX principles (e.g., Light Mode slate palettes, responsive grids).
- **`index.html`**: Semantic structure, segregating the layout into accessible dashboard metrics, data entry forms, and data tables.
- **`style.css`**: A centralized design system utilizing CSS Variables (`:root`) for easy theme management. Includes custom WebKit overrides for consistent cross-browser UI elements (like the date picker and select chevron).
- **`app.js`**: The asynchronous logic layer. Handles optimistic UI updates (e.g., pausing subscriptions instantly before server confirmation) and communicates with the backend REST API via the Fetch API.

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Git

### Installation & Execution

1. **Clone the repository and install dependencies:**
   ```powershell
   git clone https://github.com/SiddharthJogi/quantiphiVibeCodingRound.git
   cd quantiphiVibeCodingRound/backend
   pip install -r requirements.txt
   ```

2. **Run the automated test suite:**
   Ensure the business engines are functioning correctly:
   ```powershell
   pytest test_main.py -v
   ```

3. **Start the application:**
   Launch the FastAPI server (which serves both the API and the static frontend):
   ```powershell
   uvicorn main:app --reload --port 8000
   ```

4. **Access the Application:**
   - **Dashboard**: [http://localhost:8000](http://localhost:8000)
   - **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## ✨ Key Features
- **Vibe Check (Live Toggling)**: Instantly pause subscriptions with a toggle switch. The system recalculates the "Monthly Cash-Flow Burn" instantly.
- **Smart Date Engines**: Automatically flags subscriptions as "Overdue" (red badge) if the date passed, or "Renewing Soon" (amber badge) if the date is within 7 days.
- **Currency Normalization**: Input a yearly subscription, and the backend engine will precisely compute the amortized monthly equivalent for an accurate overall burn rate.
