"""
BMI Calculator - Advanced Tier (Tkinter GUI)
Desktop GUI application supporting input validation, color-coded results,
SQLite persistence, multi-user tracking, and matplotlib trend graph visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import bmi_db
from bmi_cli import calculate_bmi, classify_bmi

CATEGORY_COLORS = {
    "Underweight": "#1e88e5",  # Blue
    "Normal": "#2e7d32",       # Green
    "Overweight": "#f57c00",   # Amber / Orange
    "Obese": "#d32f2f"         # Red
}

class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator & History Tracker")
        self.geometry("520x560")
        self.resizable(False, False)
        
        # Initialize Database table
        try:
            bmi_db.init_db()
        except bmi_db.DatabaseError as e:
            messagebox.showerror("Database Initialization Error", str(e))

        self._last_result = None

        # Build UI layout
        self._create_styles()
        self._build_input_section()
        self._build_result_section()
        self._build_history_section()

        # Load initial user list
        self.refresh_user_list()

    def _create_styles(self):
        """Sets up ttk styles for clean visual appearance."""
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

    def _build_input_section(self):
        """Section 1: User name, weight, and height inputs + Calculate button."""
        frame = ttk.LabelFrame(self, text=" Enter Details ", padding=15)
        frame.pack(fill="x", padx=15, pady=10)

        # Name Field
        ttk.Label(frame, text="User Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(frame, width=28, font=("Segoe UI", 10))
        self.name_entry.grid(row=0, column=1, pady=5, padx=5, sticky="e")

        # Weight Field
        ttk.Label(frame, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=5)
        self.weight_entry = ttk.Entry(frame, width=28, font=("Segoe UI", 10))
        self.weight_entry.grid(row=1, column=1, pady=5, padx=5, sticky="e")

        # Height Field
        ttk.Label(frame, text="Height (m):").grid(row=2, column=0, sticky="w", pady=5)
        self.height_entry = ttk.Entry(frame, width=28, font=("Segoe UI", 10))
        self.height_entry.grid(row=2, column=1, pady=5, padx=5, sticky="e")

        # Calculate Button
        self.calc_btn = ttk.Button(frame, text="Calculate BMI", command=self.on_calculate)
        self.calc_btn.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")

    def _build_result_section(self):
        """Section 2: Displays color-coded result label and Save Record button."""
        frame = ttk.LabelFrame(self, text=" Calculation Result ", padding=15)
        frame.pack(fill="x", padx=15, pady=5)

        self.result_label = tk.Label(
            frame,
            text="Enter details above and click Calculate",
            font=("Segoe UI", 12, "bold"),
            fg="#555555",
            bg="#f8f9fa",
            height=2,
            relief="solid",
            bd=1
        )
        self.result_label.pack(fill="x", pady=5)

        self.save_btn = ttk.Button(
            frame,
            text="Save Record to Database",
            state="disabled",
            command=self.on_save
        )
        self.save_btn.pack(fill="x", pady=5)

    def _build_history_section(self):
        """Section 3: Dropdown user selector, refresh button, and trend graph button."""
        frame = ttk.LabelFrame(self, text=" Multi-User History & Trends ", padding=15)
        frame.pack(fill="x", padx=15, pady=10)

        select_frame = ttk.Frame(frame)
        select_frame.pack(fill="x", pady=5)

        ttk.Label(select_frame, text="Select User:").pack(side="left", padx=(0, 5))
        self.user_select = ttk.Combobox(select_frame, state="readonly", width=20, font=("Segoe UI", 10))
        self.user_select.pack(side="left", fill="x", expand=True, padx=5)

        self.refresh_btn = ttk.Button(select_frame, text="🔄", width=4, command=self.refresh_user_list)
        self.refresh_btn.pack(side="right", padx=(5, 0))

        self.graph_btn = ttk.Button(frame, text="Show BMI Trend Graph", command=self.on_show_graph)
        self.graph_btn.pack(fill="x", pady=(10, 5))

    def on_calculate(self):
        """Validates input fields, calculates BMI, updates color-coded result label, enables Save."""
        name = self.name_entry.get().strip()
        weight_raw = self.weight_entry.get().strip()
        height_raw = self.height_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Please enter a user name.")
            return

        try:
            weight = float(weight_raw)
            height = float(height_raw)
        except ValueError:
            messagebox.showerror("Validation Error", "Weight and height must be valid numeric values.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror("Validation Error", "Weight and height must be positive numbers greater than zero.")
            return

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = CATEGORY_COLORS.get(category, "#000000")

        self.result_label.config(
            text=f"BMI: {bmi:.2f}  |  Category: {category}",
            fg=color
        )
        self._last_result = {
            "user_name": name,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category
        }
        self.save_btn.config(state="normal")

    def on_save(self):
        """Saves the calculated BMI record to the database."""
        if not self._last_result:
            return

        try:
            bmi_db.add_record(
                user_name=self._last_result["user_name"],
                weight=self._last_result["weight"],
                height=self._last_result["height"],
                bmi=self._last_result["bmi"],
                category=self._last_result["category"]
            )
            messagebox.showinfo("Success", f"Record saved successfully for {self._last_result['user_name']}!")
            self.save_btn.config(state="disabled")
            self.refresh_user_list()
            # Auto-select the user that was just saved
            self.user_select.set(self._last_result["user_name"])
        except bmi_db.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

    def refresh_user_list(self):
        """Fetches distinct users from database and updates dropdown."""
        try:
            users = bmi_db.get_users()
            self.user_select["values"] = users
            current = self.user_select.get()
            if users and (not current or current not in users):
                self.user_select.set(users[0])
            elif not users:
                self.user_select.set("")
        except bmi_db.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

    def on_show_graph(self):
        """Fetches user records and launches the matplotlib trend graph sub-window."""
        selected_user = self.user_select.get().strip()
        if not selected_user:
            messagebox.showwarning("Selection Required", "Please select a user from the dropdown to view graph.")
            return

        try:
            records = bmi_db.get_records(selected_user)
            if not records:
                messagebox.showinfo("No History", f"No records found for user '{selected_user}'.")
                return
            self._open_graph_window(selected_user, records)
        except bmi_db.DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

    def _open_graph_window(self, user_name, records):
        """Opens a Toplevel window displaying matplotlib trend chart with WHO category bands."""
        graph_win = tk.Toplevel(self)
        graph_win.title(f"BMI History Trend - {user_name}")
        graph_win.geometry("680x520")

        fig = Figure(figsize=(6.5, 4.5), dpi=100)
        ax = fig.add_subplot(111)

        # Lightly shade standard WHO BMI bands in background
        ax.axhspan(0, 18.5, color="#bbdefb", alpha=0.35, label="Underweight (< 18.5)")
        ax.axhspan(18.5, 25.0, color="#c8e6c9", alpha=0.35, label="Normal (18.5 - 24.9)")
        ax.axhspan(25.0, 30.0, color="#ffe0b2", alpha=0.35, label="Overweight (25.0 - 29.9)")
        ax.axhspan(30.0, 50.0, color="#ffcdd2", alpha=0.35, label="Obese (>= 30.0)")

        # Plot BMI history line
        x_indices = list(range(1, len(records) + 1))
        bmis = [r["bmi"] for r in records]
        dates = [r["recorded_at"] for r in records]

        ax.plot(x_indices, bmis, marker="o", color="#1565c0", linewidth=2.5, markersize=7, label="BMI Record")

        # Annotate data points
        for x, y in zip(x_indices, bmis):
            ax.annotate(
                f"{y:.1f}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=9,
                weight="bold"
            )

        ax.set_xticks(x_indices)
        ax.set_xticklabels(dates, rotation=25, ha="right", fontsize=8)
        
        min_bmi = min(bmis)
        max_bmi = max(bmis)
        ax.set_ylim(max(10, min_bmi - 4), max(35, max_bmi + 5))

        ax.set_title(f"BMI History Trend for '{user_name}'", fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel("Record Date / Time", fontsize=10)
        ax.set_ylabel("BMI Index", fontsize=10)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.8)
        ax.grid(True, linestyle="--", alpha=0.5)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def main():
    app = BMIApp()
    app.mainloop()

if __name__ == "__main__":
    main()
