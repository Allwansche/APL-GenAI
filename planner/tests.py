from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .planner_engine import normalize_pref, filter_recipes, generate_meal_plan
from .models import MealPlan, DayPlan, Meal

class PlannerEngineTests(TestCase):
    """Tests covering core algorithms in the local offline planner engine."""
    
    def test_normalize_preferences(self):
        """Verify keyword normalizer identifies Swedish and English diet inputs."""
        self.assertIn('laktosfri', normalize_pref("utan laktos, vegan"))
        self.assertIn('vegan', normalize_pref("utan laktos, vegan"))
        self.assertIn('glutenfri', normalize_pref("gluten-free and low-carb"))
        self.assertIn('low-carb', normalize_pref("gluten-free and low-carb"))
        self.assertIn('vegetarisk', normalize_pref("Vego kost"))
        
    def test_filter_recipes_fallback(self):
        """Ensure filter_recipes returns a list even with impossible combinations."""
        # Unreasonable filter criteria
        recipes = filter_recipes('breakfast', ['non-existent-tag'])
        self.assertTrue(len(recipes) > 0, "Filter should fall back to general pool rather than empty.")

    def test_generate_meal_plan_scaling(self):
        """Ensure math scales meals to sum exactly to daily calorie targets."""
        target_cals = 2200
        days = 3
        people = 2
        plan = generate_meal_plan(days, people, target_cals, "laktosfri")
        
        self.assertEqual(plan['days'], days)
        self.assertEqual(plan['people'], people)
        self.assertEqual(plan['calories_target'], target_cals)
        self.assertEqual(len(plan['day_plans']), days)
        
        for dp in plan['day_plans']:
            day_sum = sum(meal['calories'] for meal in dp['meals'])
            # Verify sum matches calorie target perfectly (accounting for integer division rounding adjustments)
            self.assertEqual(day_sum, target_cals, f"Day sum {day_sum} does not match target {target_cals}")
            
            # Verify meal portions scale
            for meal in dp['meals']:
                self.assertTrue(len(meal['ingredients']) > 0)
                # Check that amount string exists
                self.assertIsNotNone(meal['ingredients'][0]['amount'])


class PlannerAPITests(APITestCase):
    """Tests covering REST endpoint routes and CRUD actions."""
    
    def setUp(self):
        # Create a pre-existing MealPlan
        self.plan1 = MealPlan.objects.create(
            days=2,
            people=3,
            calories_target=2000,
            preferences="vegetarisk, laktosfri",
            ai_comment="Kostplan kommentar"
        )
        self.day1 = DayPlan.objects.create(meal_plan=self.plan1, day_number=1)
        self.meal1 = Meal.objects.create(
            day_plan=self.day1,
            meal_type="breakfast",
            title="Äggröra",
            description="Beskrivning",
            ingredients=[{"name": "ägg", "amount": "6 st"}],
            calories=400,
            protein=20.0,
            fat=15.0,
            carbohydrates=10.0
        )

    def test_list_plans(self):
        """Ensure endpoint lists all plans in database."""
        url = reverse('plan-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['days'], 2)

    def test_create_plan(self):
        """Ensure POST successfully creates new database models and returns nested JSON."""
        url = reverse('plan-list-create')
        data = {
            "days": 3,
            "people": 2,
            "calories_target": 1800,
            "preferences": "laktosfri"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify db records created
        self.assertEqual(MealPlan.objects.count(), 2)
        new_plan = MealPlan.objects.exclude(id=self.plan1.id).first()
        self.assertEqual(new_plan.days, 3)
        self.assertEqual(new_plan.calories_target, 1800)
        self.assertEqual(new_plan.day_plans.count(), 3)
        
        # Verify nested response
        self.assertEqual(response.data['id'], new_plan.id)
        self.assertEqual(len(response.data['day_plans']), 3)

    def test_retrieve_plan(self):
        """Ensure individual plan details are retrieved correctly by ID."""
        url = reverse('plan-retrieve-destroy', kwargs={'pk': self.plan1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['days'], 2)
        self.assertEqual(len(response.data['day_plans']), 1)
        self.assertEqual(response.data['day_plans'][0]['meals'][0]['title'], "Äggröra")

    def test_delete_plan(self):
        """Ensure plan can be successfully deleted from database."""
        url = reverse('plan-retrieve-destroy', kwargs={'pk': self.plan1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MealPlan.objects.count(), 0)
