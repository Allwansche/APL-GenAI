from django.shortcuts import render
from .ai_service import generate_meal_plan

def meal_planner(request):
    plan = None
    error = None

    if request.method == "POST":
        days = request.POST.get("days")
        calories = request.POST.get("calories")
        preferences = request.POST.get("preferences", "")

        try:
            plan = generate_meal_plan(int(days), int(calories), preferences)
        except Exception as e:
            error = str(e)

    return render(request, "meal/meal_planner.html", {
        "plan": plan,
        "error": error
    })

