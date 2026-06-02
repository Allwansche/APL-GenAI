import openai
from django.conf import settings
import json

openai.api_key = settings.OPENAI_API_KEY

def generate_meal_plan(days, calories, preferences):
    prompt = f"""
    Du är en dietist. Skapa en matplan för {days} dagar.
    Max {calories} kcal per dag.
    Preferenser: {preferences}.

    Svara i JSON med struktur:
    [
      {{
        "day": 1,
        "meals": [
          {{"name": "Havregrynsgröt", "type": "frukost", "calories": 400, "description": "..." }},
          {{"name": "Kycklingsallad", "type": "lunch", "calories": 600, "description": "..." }},
          {{"name": "Lax med grönsaker", "type": "middag", "calories": 800, "description": "..." }}
        ],
        "total_calories": 1800
      }}
    ]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Du är expert på kost och näring."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message["content"]

    try:
        return json.loads(content)
    except:
        return content
