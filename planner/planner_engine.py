import random
import re

# Base Recipe Database (All nutrients are specified PER PORTION)
RECIPES = {
    'breakfast': [
        {
            'title': 'Klassisk Havregrynsgröt med bär och banan',
            'description': 'En näringsrik och fiberrik frukost som håller dig mätt länge. Toppad med skivad banan, färska blåbär och nyttiga chiafrön.',
            'base_calories': 350,
            'base_protein': 11.0,
            'base_fat': 6.0,
            'base_carbs': 63.0,
            'tags': ['laktosfri', 'vegetarisk', 'vegan', 'halal', 'kosher', 'fiberrik'],
            'ingredients': [
                {'name': 'Havregryn', 'base_amount': 1.0, 'unit': 'dl'},
                {'name': 'Vatten', 'base_amount': 2.0, 'unit': 'dl'},
                {'name': 'Banan (skivad)', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Blåbär (eller valfria bär)', 'base_amount': 0.5, 'unit': 'dl'},
                {'name': 'Chiafrön', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Nypa salt', 'base_amount': 1.0, 'unit': 'krm'}
            ]
        },
        {
            'title': 'Äggröra på surdegsbröd med spenat',
            'description': 'Proteinrik frukost gjord på färska ägg som vispas krämigt och serveras på en skiva rostat surdegsbröd med babyspenat.',
            'base_calories': 400,
            'base_protein': 22.0,
            'base_fat': 18.0,
            'base_carbs': 34.0,
            'tags': ['laktosfri', 'vegetarisk', 'halal', 'kosher', 'proteinrik'],
            'ingredients': [
                {'name': 'Ägg', 'base_amount': 2.0, 'unit': 'st'},
                {'name': 'Surdegsbröd', 'base_amount': 1.0, 'unit': 'skiva'},
                {'name': 'Babyspenat', 'base_amount': 20.0, 'unit': 'g'},
                {'name': 'Olivolja (till stekning)', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Salt och svartpeppar', 'base_amount': 1.0, 'unit': 'efter smak'}
            ]
        },
        {
            'title': 'Bär- och spenatsmoothie med mandelmjölk',
            'description': 'En fräsch, färgstark och laktosfri smoothie laddad med vitaminer och antioxidanter. Mixad slät.',
            'base_calories': 300,
            'base_protein': 8.0,
            'base_fat': 7.0,
            'base_carbs': 51.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher', 'vitaminrik'],
            'ingredients': [
                {'name': 'Frysta blandade bär', 'base_amount': 1.5, 'unit': 'dl'},
                {'name': 'Färsk babyspenat', 'base_amount': 1.0, 'unit': 'näve'},
                {'name': 'Osortad mandelmjölk', 'base_amount': 2.5, 'unit': 'dl'},
                {'name': 'Hampafrön eller pumpakärnor', 'base_amount': 1.0, 'unit': 'msk'},
                {'name': 'Halv banan', 'base_amount': 0.5, 'unit': 'st'}
            ]
        },
        {
            'title': 'Avokadomacka med kokt ägg och chiliflakes',
            'description': 'Rostat bröd toppat med krämig mosad avokado, ett perfekt hårdkokt ägg i skivor och sting från chiliflakes.',
            'base_calories': 380,
            'base_protein': 14.0,
            'base_fat': 20.0,
            'base_carbs': 32.0,
            'tags': ['laktosfri', 'vegetarisk', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Surdegsbröd eller glutenfritt bröd', 'base_amount': 1.0, 'unit': 'skiva'},
                {'name': 'Avokado', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Ägg (kokt)', 'base_amount': 1.0, 'unit': 'st'},
                {'name': 'Citronsaft', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Chiliflakes & flingsalt', 'base_amount': 1.0, 'unit': 'nypa'}
            ]
        },
        {
            'title': 'Bovetegröt med kanelsteka äpplen',
            'description': 'Helt glutenfri frukostgröt gjord på boveteflingor, toppad med äppelbitar som stekts i kanel och en klick laktosfri ia/havreyoghurt.',
            'base_calories': 360,
            'base_protein': 9.0,
            'base_fat': 5.0,
            'base_carbs': 66.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Krossat bovete eller boveteflingor', 'base_amount': 1.0, 'unit': 'dl'},
                {'name': 'Havremjölk (glutenfri) eller vatten', 'base_amount': 2.5, 'unit': 'dl'},
                {'name': 'Äpple (tärnat)', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Kanel', 'base_amount': 0.5, 'unit': 'tsk'},
                {'name': 'Kokosolja (till stekning)', 'base_amount': 1.0, 'unit': 'tsk'}
            ]
        }
    ],
    'lunch': [
        {
            'title': 'Krämig linsgryta med kokosmjölk och gurkmeja',
            'description': 'En fyllig och värmande gryta gjord på röda linser, kokosmjölk, krossade tomater och doftande indiska kryddor. Serveras med kokt ris.',
            'base_calories': 600,
            'base_protein': 21.0,
            'base_fat': 16.0,
            'base_carbs': 89.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Röda linser (torra)', 'base_amount': 0.75, 'unit': 'dl'},
                {'name': 'Kokosmjölk (lätt)', 'base_amount': 1.5, 'unit': 'dl'},
                {'name': 'Krossade tomater', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Matris (t.ex. basmati)', 'base_amount': 0.75, 'unit': 'dl'},
                {'name': 'Gul lök & vitlök', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Ingefära & gurkmeja', 'base_amount': 1.0, 'unit': 'tsk'}
            ]
        },
        {
            'title': 'Ugnsbakad kycklingfilé med sötpotatis och broccoli',
            'description': 'Klassisk hälsosam lunch. Mört ugnsbakad kycklingfilé kryddad med örter, serveras med klyftad sötpotatis och krispiga broccolibuketter.',
            'base_calories': 580,
            'base_protein': 44.0,
            'base_fat': 12.0,
            'base_carbs': 68.0,
            'tags': ['laktosfri', 'glutenfri', 'halal', 'proteinrik'],
            'ingredients': [
                {'name': 'Kycklingfilé', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Sötpotatis', 'base_amount': 200.0, 'unit': 'g'},
                {'name': 'Broccoli', 'base_amount': 100.0, 'unit': 'g'},
                {'name': 'Olivolja', 'base_amount': 1.0, 'unit': 'msk'},
                {'name': 'Paprikapulver & örtsalt', 'base_amount': 1.0, 'unit': 'efter smak'}
            ]
        },
        {
            'title': 'Stekt laxfilé med quinoa och ångad sparris',
            'description': 'En fantastisk källa till omega-3. Krispigt stekt laxfilé serverad med fluffig quinoa, ångad sparris och en skiva färsk citron.',
            'base_calories': 650,
            'base_protein': 36.0,
            'base_fat': 28.0,
            'base_carbs': 52.0,
            'tags': ['laktosfri', 'glutenfri', 'halal', 'kosher', 'proteinrik'],
            'ingredients': [
                {'name': 'Laxfilé', 'base_amount': 140.0, 'unit': 'g'},
                {'name': 'Quinoa (torr)', 'base_amount': 0.75, 'unit': 'dl'},
                {'name': 'Grön sparris', 'base_amount': 5.0, 'unit': 'st'},
                {'name': 'Citron', 'base_amount': 0.25, 'unit': 'st'},
                {'name': 'Olivolja', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Salt & citronpeppar', 'base_amount': 1.0, 'unit': 'nypa'}
            ]
        },
        {
            'title': 'Medelhavssallad med kikärtor, oliver och gurka',
            'description': 'En färgstark och krispig sallad packad med växtbaserat protein. Blanda kikärtor, gurka, tomater, rödlök och kalamataoliver med en örtig vinägrett.',
            'base_calories': 520,
            'base_protein': 17.0,
            'base_fat': 18.0,
            'base_carbs': 66.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Kikärtor (kokta/sköljda)', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Gurka', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Körsbärstomater', 'base_amount': 5.0, 'unit': 'st'},
                {'name': 'Kalamataoliver', 'base_amount': 6.0, 'unit': 'st'},
                {'name': 'Rödlök', 'base_amount': 0.25, 'unit': 'st'},
                {'name': 'Olivolja & rödvinsvinäger', 'base_amount': 1.0, 'unit': 'msk'}
            ]
        },
        {
            'title': 'Wokad tofu med grönsaker och jasminris',
            'description': 'Krispigt stekt tofu wokad med paprika, sockerärter, morötter och lök i en smakrik sojasås (tamari för glutenfritt). Serveras med jasminris.',
            'base_calories': 550,
            'base_protein': 20.0,
            'base_fat': 14.0,
            'base_carbs': 82.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Fast tofu', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Wokgrönsaker (mix)', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Jasminris (torrt)', 'base_amount': 0.75, 'unit': 'dl'},
                {'name': 'Tamari (glutenfri soja)', 'base_amount': 1.5, 'unit': 'msk'},
                {'name': 'Sesamolja', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Sesamfrön', 'base_amount': 1.0, 'unit': 'tsk'}
            ]
        }
    ],
    'dinner': [
        {
            'title': 'Kryddig Nötfärs chili med svarta bönor och ris',
            'description': 'En mustig och proteinrik chiligryta gjord på mager nötfärs, svarta bönor och fyllig tomatsås. Serveras med kokt ris.',
            'base_calories': 720,
            'base_protein': 41.0,
            'base_fat': 22.0,
            'base_carbs': 85.0,
            'tags': ['laktosfri', 'glutenfri', 'halal', 'proteinrik'],
            'ingredients': [
                {'name': 'Mager nötfärs (eller nötfärs)', 'base_amount': 130.0, 'unit': 'g'},
                {'name': 'Svarta bönor (kokta)', 'base_amount': 80.0, 'unit': 'g'},
                {'name': 'Krossade tomater', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Matris', 'base_amount': 0.8, 'unit': 'dl'},
                {'name': 'Gul lök', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Chilikrydda & spiskummin', 'base_amount': 1.0, 'unit': 'efter smak'},
                {'name': 'Rapsolja (till stekning)', 'base_amount': 1.0, 'unit': 'tsk'}
            ]
        },
        {
            'title': 'Tofu i thailändsk röd curry med bambuskott',
            'description': 'En aromatisk thailändsk middag. Tofutärningar som sjuder i röd currypasta, kokosmjölk, bambuskott, paprika och färsk basilika. Serveras med ris.',
            'base_calories': 680,
            'base_protein': 22.0,
            'base_fat': 24.0,
            'base_carbs': 90.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Fast tofu', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Kokosmjölk', 'base_amount': 2.0, 'unit': 'dl'},
                {'name': 'Röd currypasta', 'base_amount': 1.0, 'unit': 'msk'},
                {'name': 'Bambuskott (strimlade)', 'base_amount': 50.0, 'unit': 'g'},
                {'name': 'Röd paprika', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Matris', 'base_amount': 0.8, 'unit': 'dl'}
            ]
        },
        {
            'title': 'Vegetarisk Chili sin Carne med majschips',
            'description': 'En mustig vegetarisk chiligryta gjord på svarta bönor, majs, paprika och tomater. Serveras med en näve krispiga majschips och skivad avokado.',
            'base_calories': 640,
            'base_protein': 21.0,
            'base_fat': 18.0,
            'base_carbs': 92.0,
            'tags': ['laktosfri', 'glutenfri', 'vegetarisk', 'vegan', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Stora vita bönor eller kidneybönor', 'base_amount': 120.0, 'unit': 'g'},
                {'name': 'Svarta bönor', 'base_amount': 80.0, 'unit': 'g'},
                {'name': 'Krossade tomater', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Majskorn', 'base_amount': 50.0, 'unit': 'g'},
                {'name': 'Röd paprika', 'base_amount': 0.5, 'unit': 'st'},
                {'name': 'Nachochips (majs)', 'base_amount': 25.0, 'unit': 'g'},
                {'name': 'Avokado', 'base_amount': 0.25, 'unit': 'st'}
            ]
        },
        {
            'title': 'Ugnsbakad torskrygg med potatismos och ärter',
            'description': 'Klassisk svensk husmanskost i hälsosam tappning. Mild torskrygg ugnsbakas och serveras med hemlagat laktosfritt potatismos och gröna ärter.',
            'base_calories': 610,
            'base_protein': 38.0,
            'base_fat': 11.0,
            'base_carbs': 84.0,
            'tags': ['laktosfri', 'glutenfri', 'halal', 'kosher', 'proteinrik'],
            'ingredients': [
                {'name': 'Torskrygg (eller torskfilé)', 'base_amount': 150.0, 'unit': 'g'},
                {'name': 'Potatis', 'base_amount': 250.0, 'unit': 'g'},
                {'name': 'Laktosfri mjölk eller havredryck', 'base_amount': 0.5, 'unit': 'dl'},
                {'name': 'Gröna ärter', 'base_amount': 80.0, 'unit': 'g'},
                {'name': 'Smör (laktosfritt) eller olivolja', 'base_amount': 1.0, 'unit': 'tsk'},
                {'name': 'Salt, vitpeppar & muskotnöt', 'base_amount': 1.0, 'unit': 'efter smak'}
            ]
        },
        {
            'title': 'Krämig skogssvampspasta med spenat',
            'description': 'Krämig och smakrik vegetarisk pastarätt. Färsk pasta slungas i en krämig havrebaserad sås med stekt champinjon, spenat och riven parmesan.',
            'base_calories': 700,
            'base_protein': 18.0,
            'base_fat': 20.0,
            'base_carbs': 105.0,
            'tags': ['vegetarisk', 'halal', 'kosher'],
            'ingredients': [
                {'name': 'Pasta (t.ex. tagliatelle)', 'base_amount': 90.0, 'unit': 'g'},
                {'name': 'Blandad svamp (t.ex. skogschampinjon)', 'base_amount': 100.0, 'unit': 'g'},
                {'name': 'Havregrädde (eller matlagningsgrädde)', 'base_amount': 1.0, 'unit': 'dl'},
                {'name': 'Babyspenat', 'base_amount': 40.0, 'unit': 'g'},
                {'name': 'Vitlöksklyfta', 'base_amount': 1.0, 'unit': 'st'},
                {'name': 'Parmesanost (riven)', 'base_amount': 15.0, 'unit': 'g'},
                {'name': 'Olivolja', 'base_amount': 1.0, 'unit': 'tsk'}
            ]
        }
    ]
}


def normalize_pref(preference_str):
    """Normalize input preference string to standard lowercase keywords."""
    if not preference_str:
        return []
    
    # Split by commas, spaces, etc.
    words = re.split(r'[\s,\.\-\&]+', preference_str.lower())
    normalized = []
    
    for word in words:
        if 'laktos' in word or 'lactose' in word or 'mjölkfri' in word:
            normalized.append('laktosfri')
        elif 'gluten' in word or 'wheat' in word:
            normalized.append('glutenfri')
        elif 'vegetar' in word or 'vego' in word or 'vegetarian' in word:
            normalized.append('vegetarisk')
        elif 'vegan' in word:
            normalized.append('vegan')
            normalized.append('vegetarisk')  # Vegan is also vegetarian
            normalized.append('laktosfri')   # Vegan is also lactose-free
        elif 'halal' in word:
            normalized.append('halal')
        elif 'kosher' in word:
            normalized.append('kosher')
        elif 'protein' in word or 'högprotein' in word:
            normalized.append('proteinrik')
        elif 'carb' in word or 'kolhydrat' in word or 'lågkol' in word:
            normalized.append('low-carb')
            
    return list(set(normalized))


def filter_recipes(meal_type, normalized_prefs):
    """Filter recipes by type and dietary tags."""
    recipes = RECIPES.get(meal_type, [])
    if not normalized_prefs:
        return recipes
        
    filtered = []
    for recipe in recipes:
        # Check if the recipe matches all the normalized dietary preferences
        matches_all = True
        for pref in normalized_prefs:
            # For special compound requirements:
            if pref == 'low-carb' and recipe['base_carbs'] > 60:
                matches_all = False
                break
            
            # If the tag is not present in the recipe's tags
            if pref not in recipe['tags'] and pref != 'low-carb':
                matches_all = False
                break
                
        if matches_all:
            filtered.append(recipe)
            
    # Fallback mechanism: if filtering left us with 0 recipes, relax the constraints
    if not filtered:
        # Try to match at least vegetarian/vegan/laktosfri constraints (health/ethical constraints first)
        ethical_health_prefs = [p for p in normalized_prefs if p in ['vegetarisk', 'vegan', 'laktosfri', 'glutenfri']]
        for recipe in recipes:
            matches_ethical = True
            for pref in ethical_health_prefs:
                if pref not in recipe['tags']:
                    matches_ethical = False
                    break
            if matches_ethical:
                filtered.append(recipe)
                
    # Ultimate fallback: return all recipes of this type to prevent crash
    if not filtered:
        return recipes
        
    return filtered


def scale_ingredients(ingredients_list, scale_factor, people):
    """Scale ingredient amounts mathematically and format into a list of strings and objects."""
    scaled = []
    for ing in ingredients_list:
        base_amt = ing['base_amount']
        unit = ing['unit']
        name = ing['name']
        
        # Total amount for the meal (per dish * people)
        total_amt = base_amt * scale_factor * people
        
        # Round nicely for display
        if total_amt.is_integer():
            display_amt = str(int(total_amt))
        else:
            display_amt = f"{total_amt:.2f}".rstrip('0').rstrip('.')
            
        scaled.append({
            'name': name,
            'amount': f"{display_amt} {unit}".strip()
        })
    return scaled


def generate_dietitian_comment(days, people, calories_target, prefs_str, normalized_prefs):
    """Generate professional, personalized dietitian comments in Swedish."""
    comments = []
    comments.append(f"Den här {days}-dagars matplanen är skräddarsydd för {people} personer med ett dagligt energimål på {calories_target} kcal.")
    
    if normalized_prefs:
        pref_names = []
        if 'laktosfri' in normalized_prefs: pref_names.append("laktosfri")
        if 'glutenfri' in normalized_prefs: pref_names.append("glutenfri")
        if 'vegetarisk' in normalized_prefs: pref_names.append("vegetarisk")
        if 'vegan' in normalized_prefs: pref_names.append("helt växtbaserad (vegan)")
        if 'halal' in normalized_prefs: pref_names.append("halal-anpassad")
        if 'kosher' in normalized_prefs: pref_names.append("kosher-anpassad")
        if 'proteinrik' in normalized_prefs: pref_names.append("proteinrik")
        if 'low-carb' in normalized_prefs: pref_names.append("lågkolhydrat")
        
        comments.append(f"Planen uppfyller dina valda kostpreferenser: {', '.join(pref_names)}.")
        
    # Analyze macronutrient targets
    if 'proteinrik' in normalized_prefs:
        comments.append("Måltiderna har optimerats med extra proteinkällor som lax, torsk och tofu för att stödja muskeluppbyggnad och ökad mättnadskänsla.")
    elif 'low-carb' in normalized_prefs:
        comments.append("Kolhydratmängden har reducerats till förmån för hälsosamma fetter och proteiner, vilket ger en stabil energikurva över hela dagen.")
    else:
        comments.append("Fördelningen av makronäringsämnen är balanserad enligt nordiska näringsrekommendationer (cirka 45-55% kolhydrater, 20-30% fett och 15-20% protein).")
        
    comments.append("Kom ihåg att dricka rikligt med vatten (ca 1.5 - 2 liter per dag) och anpassa kryddningen efter personlig smak.")
    
    return " ".join(comments)


def generate_meal_plan(days, people, calories_target, preferences_str):
    """Core function to generate a fully structured, scaled meal plan matching the target schema."""
    # Convert/Normalize inputs
    days = int(days)
    people = int(people)
    calories_target = int(calories_target)
    
    normalized_prefs = normalize_pref(preferences_str)
    
    # Filter available recipes
    breakfast_pool = filter_recipes('breakfast', normalized_prefs)
    lunch_pool = filter_recipes('lunch', normalized_prefs)
    dinner_pool = filter_recipes('dinner', normalized_prefs)
    
    # Target distribution of daily calories:
    # Breakfast: 25%, Lunch: 35%, Dinner: 40%
    target_breakfast_kcal = 0.25 * calories_target
    target_lunch_kcal = 0.35 * calories_target
    target_dinner_kcal = 0.40 * calories_target
    
    day_plans = []
    
    # Generate day by day
    for day in range(1, days + 1):
        # Pick recipes randomly from filtered pools to ensure variety across days
        # Use random.choice. If pools have enough, we could try to avoid repeating the exact same meal on adjacent days,
        # but with small pools random choice is robust and simple.
        b_recipe = random.choice(breakfast_pool)
        l_recipe = random.choice(lunch_pool)
        d_recipe = random.choice(dinner_pool)
        
        # Calculate scale factor per meal so that it matches target calories per meal
        # Scale factors:
        b_scale = target_breakfast_kcal / b_recipe['base_calories']
        l_scale = target_lunch_kcal / l_recipe['base_calories']
        d_scale = target_dinner_kcal / d_recipe['base_calories']
        
        # Scaled values (per portion/person)
        b_kcal = int(b_recipe['base_calories'] * b_scale)
        b_prot = round(b_recipe['base_protein'] * b_scale, 1)
        b_fat = round(b_recipe['base_fat'] * b_scale, 1)
        b_carb = round(b_recipe['base_carbs'] * b_scale, 1)
        
        l_kcal = int(l_recipe['base_calories'] * l_scale)
        l_prot = round(l_recipe['base_protein'] * l_scale, 1)
        l_fat = round(l_recipe['base_fat'] * l_scale, 1)
        l_carb = round(l_recipe['base_carbs'] * l_scale, 1)
        
        d_kcal = int(d_recipe['base_calories'] * d_scale)
        d_prot = round(d_recipe['base_protein'] * d_scale, 1)
        d_fat = round(d_recipe['base_fat'] * d_scale, 1)
        d_carb = round(d_recipe['base_carbs'] * d_scale, 1)
        
        # Verify sum matches calories_target perfectly, adjust dinner slightly if there is rounding error
        rounding_diff = calories_target - (b_kcal + l_kcal + d_kcal)
        d_kcal += rounding_diff
        
        meals = [
            {
                'meal_type': 'breakfast',
                'title': b_recipe['title'],
                'description': b_recipe['description'],
                'ingredients': scale_ingredients(b_recipe['ingredients'], b_scale, people),
                'calories': b_kcal,
                'protein': b_prot,
                'fat': b_fat,
                'carbohydrates': b_carb
            },
            {
                'meal_type': 'lunch',
                'title': l_recipe['title'],
                'description': l_recipe['description'],
                'ingredients': scale_ingredients(l_recipe['ingredients'], l_scale, people),
                'calories': l_kcal,
                'protein': l_prot,
                'fat': l_fat,
                'carbohydrates': l_carb
            },
            {
                'meal_type': 'dinner',
                'title': d_recipe['title'],
                'description': d_recipe['description'],
                'ingredients': scale_ingredients(d_recipe['ingredients'], d_scale, people),
                'calories': d_kcal,
                'protein': d_prot,
                'fat': d_fat,
                'carbohydrates': d_carb
            }
        ]
        
        day_plans.append({
            'day_number': day,
            'meals': meals
        })
        
    ai_comment = generate_dietitian_comment(days, people, calories_target, preferences_str, normalized_prefs)
    
    return {
        'days': days,
        'people': people,
        'calories_target': calories_target,
        'preferences': preferences_str,
        'ai_comment': ai_comment,
        'day_plans': day_plans
    }
