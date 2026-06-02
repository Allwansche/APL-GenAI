from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MealPlan, DayPlan, Meal
from .serializers import MealPlanSerializer
from .planner_engine import generate_meal_plan

def index_view(request):
    """Renders the main Single Page Application (SPA) frontend."""
    return render(request, 'index.html')

def standalone_view(request):
    """Renders the offline browser-local mode of the SPA inside Django."""
    return render(request, 'standalone.html')

class MealPlanListCreateAPIView(APIView):
    """API endpoint to list and create meal plans."""
    
    def get(self, request):
        plans = MealPlan.objects.all().order_by('-created_at')
        serializer = MealPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Read parameters with defaults
        days = request.data.get('days', 3)
        people = request.data.get('people', 2)
        calories_target = request.data.get('calories_target', 1800)
        preferences = request.data.get('preferences', '')

        # Generate using local engine
        try:
            plan_data = generate_meal_plan(days, people, calories_target, preferences)
        except Exception as e:
            return Response({"error": f"Failed to generate plan: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Save to database inside a transaction (implicit, or simple procedural)
        meal_plan = MealPlan.objects.create(
            days=plan_data['days'],
            people=plan_data['people'],
            calories_target=plan_data['calories_target'],
            preferences=plan_data['preferences'],
            ai_comment=plan_data['ai_comment']
        )

        for dp_data in plan_data['day_plans']:
            day_plan = DayPlan.objects.create(
                meal_plan=meal_plan,
                day_number=dp_data['day_number']
            )
            for m_data in dp_data['meals']:
                Meal.objects.create(
                    day_plan=day_plan,
                    meal_type=m_data['meal_type'],
                    title=m_data['title'],
                    description=m_data['description'],
                    ingredients=m_data['ingredients'],
                    calories=m_data['calories'],
                    protein=m_data['protein'],
                    fat=m_data['fat'],
                    carbohydrates=m_data['carbohydrates']
                )

        serializer = MealPlanSerializer(meal_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MealPlanRetrieveDestroyAPIView(APIView):
    """API endpoint to retrieve or delete specific meal plans."""
    
    def get(self, request, pk):
        try:
            plan = MealPlan.objects.prefetch_related('day_plans__meals').get(pk=pk)
        except MealPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MealPlanSerializer(plan)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            plan = MealPlan.objects.get(pk=pk)
        except MealPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
