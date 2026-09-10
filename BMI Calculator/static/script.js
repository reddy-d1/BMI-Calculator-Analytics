/**
 * BMI Health Dashboard - Client Application Logic
 * Integrates calculation, database storage, and Chart.js trend visualization.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const bmiForm = document.getElementById("bmiForm");
    const userNameInput = document.getElementById("userName");
    const weightInput = document.getElementById("weight");
    const heightInput = document.getElementById("height");

    const resultBox = document.getElementById("resultBox");
    const bmiScoreDisplay = document.getElementById("bmiScore");
    const categoryBadge = document.getElementById("categoryBadge");
    const gaugeIndicator = document.getElementById("gaugeIndicator");
    const recommendationText = document.getElementById("recommendationText");
    const saveBtn = document.getElementById("saveBtn");

    const userSelect = document.getElementById("userSelect");
    const refreshUsersBtn = document.getElementById("refreshUsersBtn");
    const emptyState = document.getElementById("emptyState");
    const chartWrapper = document.getElementById("chartWrapper");
    const tableWrapper = document.getElementById("tableWrapper");
    const historyTableBody = document.getElementById("historyTableBody");

    let currentCalculation = null;
    let chartInstance = null;

    // Recommendations Map
    const RECOMMENDATIONS = {
        "Underweight": "Your weight is below the standard WHO range. Focus on nutrient-rich foods and balanced calories.",
        "Normal": "Your weight is in the healthy WHO range for your height. Keep up the good balanced habits!",
        "Overweight": "Your weight is slightly above the normal range. Regular exercise and nutritional awareness can help.",
        "Obese": "Your weight is significantly above the WHO normal range. Consider consulting a health professional."
    };

    // Color Palette Map
    const CATEGORY_COLORS = {
        "Underweight": "#3b82f6",
        "Normal": "#10b981",
        "Overweight": "#f59e0b",
        "Obese": "#ef4444"
    };

    // Load initial user list from backend SQLite DB
    fetchUserList();

    // Event Listeners
    bmiForm.addEventListener("submit", handleCalculate);
    saveBtn.addEventListener("click", handleSaveRecord);
    userSelect.addEventListener("change", handleUserSelectionChange);
    refreshUsersBtn.addEventListener("click", fetchUserList);

    /**
     * Handles Form Submission for Calculation
     */
    async function handleCalculate(e) {
        e.preventDefault();
        const user_name = userNameInput.value.trim();
        const weight = parseFloat(weightInput.value);
        const height = parseFloat(heightInput.value);

        if (!user_name || isNaN(weight) || isNaN(height) || weight <= 0 || height <= 0) {
            showToast("Please enter a valid user name, weight (>0), and height (>0).", "error");
            return;
        }

        try {
            const response = await fetch("/api/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ weight, height })
            });
            const data = await response.json();

            if (!response.ok) {
                showToast(data.error || "Calculation failed.", "error");
                return;
            }

            currentCalculation = {
                user_name,
                weight: data.weight,
                height: data.height,
                bmi: data.bmi,
                category: data.category
            };

            renderCalculationResult(currentCalculation);
        } catch (err) {
            showToast("Network error calculating BMI.", "error");
        }
    }

    /**
     * Renders Calculation Score, Category Badge, and Gauge Fill
     */
    function renderCalculationResult(res) {
        bmiScoreDisplay.textContent = res.bmi.toFixed(2);
        categoryBadge.textContent = res.category;
        categoryBadge.className = `category-badge ${res.category}`;

        // Calculate gauge percentage (10 to 40 BMI scale)
        const minBMI = 12;
        const maxBMI = 40;
        const clampedBMI = Math.min(Math.max(res.bmi, minBMI), maxBMI);
        const pct = ((clampedBMI - minBMI) / (maxBMI - minBMI)) * 100;

        gaugeIndicator.style.width = `${pct}%`;
        gaugeIndicator.style.backgroundColor = CATEGORY_COLORS[res.category] || "#3b82f6";

        recommendationText.textContent = RECOMMENDATIONS[res.category] || "";
        resultBox.classList.remove("hidden");
    }

    /**
     * Saves Record to SQLite Database
     */
    async function handleSaveRecord() {
        if (!currentCalculation) return;

        try {
            const response = await fetch("/api/records", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(currentCalculation)
            });
            const data = await response.json();

            if (!response.ok) {
                showToast(data.error || "Failed to save record.", "error");
                return;
            }

            showToast(`Record saved successfully for ${data.user_name}!`, "success");
            
            // Refresh User Dropdown and auto-select
            await fetchUserList();
            userSelect.value = data.user_name;
            loadUserHistory(data.user_name);
        } catch (err) {
            showToast("Error connecting to server.", "error");
        }
    }

    /**
     * Fetches distinct user list from SQLite
     */
    async function fetchUserList() {
        try {
            const response = await fetch("/api/users");
            const data = await response.json();
            if (!response.ok) return;

            const selectedValue = userSelect.value;
            userSelect.innerHTML = '<option value="">Select User...</option>';
            
            data.users.forEach(user => {
                const opt = document.createElement("option");
                opt.value = user;
                opt.textContent = user;
                userSelect.appendChild(opt);
            });

            if (selectedValue && data.users.includes(selectedValue)) {
                userSelect.value = selectedValue;
            }
        } catch (err) {
            console.error("Failed fetching user list:", err);
        }
    }

    /**
     * User Dropdown Change Event Handler
     */
    function handleUserSelectionChange() {
        const selectedUser = userSelect.value;
        if (!selectedUser) {
            emptyState.classList.remove("hidden");
            chartWrapper.classList.add("hidden");
            tableWrapper.classList.add("hidden");
            return;
        }
        loadUserHistory(selectedUser);
    }

    /**
     * Loads Records and Renders Chart + Table
     */
    async function loadUserHistory(userName) {
        try {
            const response = await fetch(`/api/records/${encodeURIComponent(userName)}`);
            const data = await response.json();

            if (!response.ok || !data.records || data.records.length === 0) {
                emptyState.classList.remove("hidden");
                chartWrapper.classList.add("hidden");
                tableWrapper.classList.add("hidden");
                return;
            }

            emptyState.classList.add("hidden");
            chartWrapper.classList.remove("hidden");
            tableWrapper.classList.remove("hidden");

            renderTrendChart(data.records);
            renderHistoryTable(data.records);
        } catch (err) {
            showToast("Error loading user records.", "error");
        }
    }

    /**
     * Renders Interactive Chart.js Trend Chart
     */
    function renderTrendChart(records) {
        const ctx = document.getElementById("trendChart").getContext("2d");

        const labels = records.map(r => r.recorded_at);
        const bmiData = records.map(r => r.bmi);
        const pointColors = records.map(r => CATEGORY_COLORS[r.category] || "#3b82f6");

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "BMI Score",
                    data: bmiData,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: pointColors,
                    pointBorderColor: "#ffffff",
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `BMI: ${context.parsed.y} (${records[context.dataIndex].category})`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#9ca3af", font: { family: "Inter", size: 11 } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" }
                    },
                    y: {
                        ticks: { color: "#9ca3af", font: { family: "Inter", size: 11 } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        suggestedMin: 15,
                        suggestedMax: 35
                    }
                }
            }
        });
    }

    /**
     * Renders History Table Rows
     */
    function renderHistoryTable(records) {
        historyTableBody.innerHTML = "";
        // Show newest records first in table
        [...records].reverse().forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.recorded_at}</td>
                <td>${r.weight} kg</td>
                <td>${r.height} m</td>
                <td><strong>${r.bmi.toFixed(2)}</strong></td>
                <td><span class="category-badge ${r.category}">${r.category}</span></td>
            `;
            historyTableBody.appendChild(tr);
        });
    }

    /**
     * Displays Floating Toast Messages
     */
    function showToast(message, type = "success") {
        const container = document.getElementById("toastContainer");
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${type === "success" ? "✅" : "⚠️"}</span> <span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
});
