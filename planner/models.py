from django.db import models

class MealPlan(models.Model):
    days = models.IntegerField()
    people = models.IntegerField(default=2)
    calories_target = models.IntegerField()
    preferences = models.TextField(blank=True, default='')
    ai_comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Plan for {self.people} people - {self.days} days ({self.calories_target} kcal)"

class DayPlan(models.Model):
    meal_plan = models.ForeignKey(MealPlan, related_name='day_plans', on_delete=models.CASCADE)
    day_number = models.IntegerField()

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} of {self.meal_plan}"

class Meal(models.Model):
    day_plan = models.ForeignKey(DayPlan, related_name='meals', on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20)  # breakfast, lunch, dinner
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    ingredients = models.JSONField(default=list)  # List of ingredients with quantities e.g. [{"name": "havregryn", "amount": "1 dl"}]
    calories = models.IntegerField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbohydrates = models.FloatField()

    def __str__(self):
        return f"{self.meal_type.capitalize()}: {self.title} ({self.calories} kcal)"
