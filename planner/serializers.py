from rest_framework import serializers
from .models import MealPlan, DayPlan, Meal

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'meal_type', 'title', 'description', 'ingredients', 'calories', 'protein', 'fat', 'carbohydrates']

class DayPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = DayPlan
        fields = ['id', 'day_number', 'meals']

class MealPlanSerializer(serializers.ModelSerializer):
    day_plans = DayPlanSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ['id', 'days', 'people', 'calories_target', 'preferences', 'ai_comment', 'created_at', 'day_plans']
