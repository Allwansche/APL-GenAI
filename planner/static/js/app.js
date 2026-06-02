// Global Application State
let currentPlan = null;
let calorieChartInstance = null;
let macroChartInstance = null;

// Initial Setup on Page Load
document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});

// Update display label of input sliders dynamically
function updateSliderVal(sliderId, displayId, suffix) {
    const slider = document.getElementById(sliderId);
    const display = document.getElementById(displayId);
    if (slider && display) {
        display.textContent = slider.value + suffix;
    }
}

// Fetch all saved plans and render them in the sidebar
async function loadHistory() {
    const historyList = document.getElementById("history-list");
    try {
        const response = await fetch("/api/plans/");
        if (!response.ok) throw new Error("Kunde inte hämta historik");
        
        const plans = await response.json();
        
        if (plans.length === 0) {
            historyList.innerHTML = `<div class="history-empty">Inga tidigare planer sparade.</div>`;
            return;
        }
        
        historyList.innerHTML = "";
        plans.forEach(plan => {
            const date = new Date(plan.created_at).toLocaleDateString("sv-SE", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });
            
            const activeClass = (currentPlan && currentPlan.id === plan.id) ? "active" : "";
            
            const item = document.createElement("div");
            item.className = `history-item ${activeClass}`;
            item.onclick = (e) => {
                // Prevent trigger when clicking the delete button
                if (e.target.closest('.btn-delete-history')) return;
                selectPlan(plan.id);
            };
            
            // Collect preference summary for tiny badge
            let prefSummary = plan.preferences ? plan.preferences : "Standard";
            if (prefSummary.length > 22) prefSummary = prefSummary.substring(0, 20) + "...";
            
            item.innerHTML = `
                <div class="history-info">
                    <span class="history-name">${plan.days} Dagar (${plan.calories_target} kcal)</span>
                    <span class="history-meta"><i class="fa-solid fa-tag"></i> ${prefSummary} &bull; ${date}</span>
                </div>
                <button class="btn-delete-history" onclick="deletePlan(${plan.id})" title="Ta bort plan">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;
            
            historyList.appendChild(item);
        });
        
    } catch (error) {
        console.error(error);
        historyList.innerHTML = `<div class="history-empty text-danger">Fel vid inläsning av historik.</div>`;
    }
}

// Select a plan and render its dashboard details
async function selectPlan(planId) {
    toggleLoading(true);
    try {
        const response = await fetch(`/api/plans/${planId}/`);
        if (!response.ok) throw new Error("Matplanen kunde inte hämtas");
        
        currentPlan = await response.json();
        
        // Hide welcome panel, show dashboard
        document.getElementById("welcome-board").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
        
        renderPlanDetails(currentPlan);
        loadHistory(); // Re-render sidebar to update the active highlight class
        
    } catch (error) {
        alert("Ett fel uppstod: " + error.message);
    } finally {
        toggleLoading(false);
    }
}

// Delete a plan by ID
async function deletePlan(planId) {
    if (!confirm("Är du säker på att du vill radera denna matplan?")) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });
        
        if (!response.ok) throw new Error("Planen kunde inte raderas");
        
        // If the active plan was deleted, reset dashboard
        if (currentPlan && currentPlan.id === planId) {
            currentPlan = null;
            document.getElementById("dashboard").style.display = "none";
            document.getElementById("welcome-board").style.display = "block";
        }
        
        loadHistory();
        
    } catch (error) {
        alert(error.message);
    }
}

// Submit Form to generate a new Meal Plan
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const days = parseInt(document.getElementById("input-days").value);
    const people = parseInt(document.getElementById("input-people").value);
    const caloriesTarget = parseInt(document.getElementById("input-calories").value);
    const otherPref = document.getElementById("input-other-pref").value.trim();
    
    // Aggregate checkboxes
    const checkboxes = form.querySelectorAll('input[name="pref_tags"]:checked');
    const checkedPrefs = Array.from(checkboxes).map(cb => cb.value);
    
    if (otherPref) {
        checkedPrefs.push(otherPref);
    }
    
    const preferencesString = checkedPrefs.join(", ");
    
    toggleLoading(true);
    
    try {
        const response = await fetch("/api/plans/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                days: days,
                people: people,
                calories_target: caloriesTarget,
                preferences: preferencesString
            })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Misslyckades att generera kostplan");
        }
        
        currentPlan = await response.json();
        
        // Hide welcome panel, show dashboard
        document.getElementById("welcome-board").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
        
        renderPlanDetails(currentPlan);
        loadHistory();
        
    } catch (error) {
        alert("Fel: " + error.message);
    } finally {
        toggleLoading(false);
    }
}

// Render everything on the Dashboard using parsed meal plan JSON
function renderPlanDetails(plan) {
    // 1. Text elements
    document.getElementById("plan-title").textContent = `Personlig Matplan (${plan.calories_target} kcal)`;
    document.getElementById("plan-meta").innerHTML = `
        <i class="fa-solid fa-users"></i> ${plan.people} personer &bull; 
        <i class="fa-solid fa-calendar-day"></i> ${plan.days} dagar &bull; 
        <i class="fa-solid fa-tag"></i> ${plan.preferences ? plan.preferences : 'Inga kostrestriktioner'}
    `;
    document.getElementById("dietitian-comment").textContent = plan.ai_comment;
    
    // 2. Aggregate average stats for labels
    let totalCarbs = 0;
    let totalProtein = 0;
    let totalFat = 0;
    let totalMealsCount = 0;
    
    const dayLabels = [];
    const dailyCalorieTotals = [];
    
    plan.day_plans.forEach(day => {
        dayLabels.push(`Dag ${day.day_number}`);
        let dayCals = 0;
        
        day.meals.forEach(meal => {
            totalCarbs += meal.carbohydrates;
            totalProtein += meal.protein;
            totalFat += meal.fat;
            dayCals += meal.calories;
            totalMealsCount++;
        });
        
        dailyCalorieTotals.push(dayCals);
    });
    
    // Calculate average macros per day (not per meal)
    const daysCount = plan.day_plans.length;
    const avgCarbs = Math.round(totalCarbs / daysCount);
    const avgProtein = Math.round(totalProtein / daysCount);
    const avgFat = Math.round(totalFat / daysCount);
    
    document.getElementById("stats-carbs").textContent = `${avgCarbs}g`;
    document.getElementById("stats-protein").textContent = `${avgProtein}g`;
    document.getElementById("stats-fat").textContent = `${avgFat}g`;
    document.getElementById("stats-target-calories").textContent = `${plan.calories_target} kcal / dag`;
    
    // 3. Render Chart.js - Daily Calories Trajectory
    renderCalorieChart(dayLabels, dailyCalorieTotals, plan.calories_target);
    
    // 4. Render Chart.js - Donut Macros Split
    renderMacroChart(avgCarbs, avgProtein, avgFat);
    
    // 5. Populate Day Navigation Tabs
    const tabsContainer = document.getElementById("day-tabs");
    tabsContainer.innerHTML = "";
    
    plan.day_plans.forEach(day => {
        const btn = document.createElement("button");
        btn.className = `tab-btn ${day.day_number === 1 ? 'active' : ''}`;
        btn.textContent = `Dag ${day.day_number}`;
        btn.onclick = () => {
            // Toggle active tabs
            tabsContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMealsForDay(day.day_number);
        };
        tabsContainer.appendChild(btn);
    });
    
    // Initial render of Day 1 meals
    renderMealsForDay(1);
}

// Render Day-by-Day Calorie Line Chart
function renderCalorieChart(labels, dataPoints, targetCalories) {
    const ctx = document.getElementById('calorieChart').getContext('2d');
    
    if (calorieChartInstance) {
        calorieChartInstance.destroy();
    }
    
    calorieChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Beräknade kalorier',
                    data: dataPoints,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#ffffff',
                    pointHoverRadius: 7
                },
                {
                    label: 'Ditt kalorimål',
                    data: Array(labels.length).fill(targetCalories),
                    borderColor: 'rgba(239, 68, 68, 0.4)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#9ca3af',
                        font: { family: 'Inter', size: 11 }
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { family: 'Inter' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#9ca3af', font: { family: 'Inter' } }
                }
            }
        }
    });
}

// Render Macronutrients Donut Chart
function renderMacroChart(carbs, protein, fat) {
    const ctx = document.getElementById('macroChart').getContext('2d');
    
    if (macroChartInstance) {
        macroChartInstance.destroy();
    }
    
    // Math to convert grams to kcal to understand calorie share
    // Carbs: 4 kcal/g, Protein: 4 kcal/g, Fat: 9 kcal/g
    const carbKcal = carbs * 4;
    const protKcal = protein * 4;
    const fatKcal = fat * 9;
    
    macroChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Kolhydrater', 'Protein', 'Fett'],
            datasets: [{
                data: [carbKcal, protKcal, fatKcal],
                backgroundColor: ['#06b6d4', '#10b981', '#f97316'],
                borderWidth: 2,
                borderColor: '#111827',
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Eget legend-gränssnitt finns bredvid ritningen
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const totalVal = context.dataset.data.reduce((a, b) => a + b, 0);
                            const currentVal = context.raw;
                            const percentage = Math.round((currentVal / totalVal) * 100);
                            const grams = context.label === 'Kolhydrater' ? carbs : (context.label === 'Protein' ? protein : fat);
                            return `${context.label}: ${grams}g (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Render specific Breakfast, Lunch, and Dinner Cards for selected Day
function renderMealsForDay(dayNumber) {
    const grid = document.getElementById("meal-grid");
    grid.innerHTML = "";
    
    const dayData = currentPlan.day_plans.find(d => d.day_number === dayNumber);
    if (!dayData) return;
    
    dayData.meals.forEach(meal => {
        const card = document.createElement("article");
        card.className = "meal-card";
        
        let typeIcon = "🍳";
        let typeLabel = "Frukost";
        if (meal.meal_type === "lunch") {
            typeIcon = "🥗";
            typeLabel = "Lunch";
        } else if (meal.meal_type === "dinner") {
            typeIcon = "🍲";
            typeLabel = "Middag";
        }
        
        // Assemble ingredients list checks
        let ingHtml = "";
        meal.ingredients.forEach((ing, i) => {
            const inputId = `ing-${meal.id}-${i}`;
            ingHtml += `
                <li>
                    <label style="display: flex; align-items: center; width: 100%; cursor: pointer;">
                        <input type="checkbox" id="${inputId}" onchange="toggleIngredientCheck('${inputId}')">
                        <span>${ing.name} (${ing.amount})</span>
                    </label>
                </li>
            `;
        });
        
        card.innerHTML = `
            <div class="meal-type-badge">
                <span>${typeIcon}</span>
                <span>${typeLabel}</span>
            </div>
            <h4>${meal.title}</h4>
            <p class="meal-desc">${meal.description}</p>
            <div class="meal-calories-badge">${meal.calories} kcal</div>
            
            <div class="meal-nutrients-grid">
                <div class="nutr-item">
                    <span class="lbl">Kolhydrater</span>
                    <span class="num">${Math.round(meal.carbohydrates)}g</span>
                </div>
                <div class="nutr-item">
                    <span class="lbl">Protein</span>
                    <span class="num">${Math.round(meal.protein)}g</span>
                </div>
                <div class="nutr-item">
                    <span class="lbl">Fett</span>
                    <span class="num">${Math.round(meal.fat)}g</span>
                </div>
            </div>
            
            <div class="meal-ingredients">
                <h5><i class="fa-solid fa-basket-shopping"></i> Ingredienser:</h5>
                <ul class="ing-list">
                    ${ingHtml}
                </ul>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Handle crossing off ingredients checklist
function toggleIngredientCheck(id) {
    const cb = document.getElementById(id);
    if (!cb) return;
    
    const label = cb.closest('label');
    const span = label.querySelector('span');
    if (cb.checked) {
        span.style.textDecoration = "line-through";
        span.style.color = "var(--text-muted)";
    } else {
        span.style.textDecoration = "none";
        span.style.color = "var(--text-secondary)";
    }
}

// Helpers
function toggleLoading(show) {
    const overlay = document.getElementById("loading-overlay");
    const btn = document.getElementById("btn-generate");
    if (overlay && btn) {
        if (show) {
            overlay.style.display = "flex";
            btn.disabled = true;
            btn.innerHTML = `<span class="loader" style="width:16px; height:16px; border-width:2px; margin:0 auto;"></span>`;
        } else {
            overlay.style.display = "none";
            btn.disabled = false;
            btn.innerHTML = `<span class="btn-text">Generera matplan</span> <i class="fa-solid fa-wand-magic-sparkles"></i>`;
        }
    }
}

// Get CSRF Token helper for POST/DELETE requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
