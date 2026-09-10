# ⚖️ BMI Calculator & Health Analytics Suite

A comprehensive Body Mass Index (BMI) tracking and analytics suite written in Python, featuring a **Localhost Web Dashboard**, a **Desktop GUI Application**, an **Interactive CLI Tool**, and persistent **SQLite Multi-User Data Storage**.

---

## 🌟 Features Overview

* **🌐 Localhost Web Dashboard (`app.py`)**:
  * Glassmorphism dark mode UI built with HTML5, CSS3, and JavaScript.
  * Real-time calculation, score display, and animated WHO health gauge meter.
  * Interactive historical trend graphs powered by **Chart.js**.
  * REST API endpoints for calculations, user profiles, and record management.
* **🖥️ Desktop GUI (`bmi_gui.py`)**:
  * Built using Python's `tkinter` & `ttk` widget libraries.
  * Embedded **Matplotlib** trend charts with WHO health category background bands (`axhspan`).
  * Dynamic color-coded feedback (Blue, Green, Amber, Red).
* **🗄️ SQLite Database Layer (`bmi_db.py`)**:
  * Multi-user profile management (`records` table).
  * Robust custom exception handling (`DatabaseError`) and connection safety.
* **💻 Command-Line Interface (`bmi_cli.py`)**:
  * Input validation loops catching non-numeric text and non-positive inputs.
* **🧪 Test Suite (`test_bmi.py`)**:
  * Automated unit tests covering mathematical accuracy, WHO boundary cases, and database operations.

---

## 📁 Project Directory Structure

```text
BMI Calculator/
├── app.py              # Flask Web Server (Localhost:5000)
├── bmi_gui.py          # Tkinter Desktop GUI Application
├── bmi_cli.py          # Command-Line Interface Application
├── bmi_db.py           # SQLite Data Access Layer & Operations
├── test_bmi.py         # Automated Unit Test Suite
├── bmi_records.db      # SQLite Database File (auto-generated)
├── templates/
│   └── index.html      # Web Application HTML View
└── static/
    ├── style.css       # Glassmorphism Dark Mode Stylesheet
    └── script.js       # Client Logic & Chart.js Integration
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed on your machine. Install the required dependencies:

```bash
pip install flask matplotlib
```

---

## 🏃 How to Run Each Tier

### 1. Launch Localhost Web Dashboard (Recommended)
Run the Flask server:
```bash
python app.py
```
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

### 2. Launch Desktop GUI Application
Run the `tkinter` desktop app:
```bash
python bmi_gui.py
```

### 3. Launch Command-Line (CLI) Application
Run the terminal interactive calculator:
```bash
python bmi_cli.py
```

### 4. Run Automated Test Suite
Execute unit tests to verify logic and database integrity:
```bash
python -m unittest test_bmi.py
```

---

## 📊 WHO BMI Classification Reference

| Category | BMI Range ($\text{kg/m}^2$) | Color Indicator |
|---|---|---|
| **Underweight** | $< 18.5$ | 🔵 Blue |
| **Normal** | $18.5 - 24.9$ | 🟢 Green |
| **Overweight** | $25.0 - 29.9$ | 🟠 Amber / Orange |
| **Obese** | $\ge 30.0$ | 🔴 Red |

---

## 🔌 REST API Documentation (Localhost)

| Method | Endpoint | Description | Sample Payload |
|---|---|---|---|
| `POST` | `/api/calculate` | Computes BMI score & category | `{"weight": 70, "height": 1.75}` |
| `GET` | `/api/users` | Lists distinct user profiles | N/A |
| `GET` | `/api/records/<user_name>` | Retrieves user record history | N/A |
| `POST` | `/api/records` | Saves a measurement record | `{"user_name": "Alex", "weight": 70, "height": 1.75, "bmi": 22.86, "category": "Normal"}` |

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
