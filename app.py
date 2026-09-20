
import streamlit as st
import json
from google import genai

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Ruchi | Make More of What You Have",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# BRAND STYLING
# ============================================================

st.markdown("""
<style>

/* ---------- GENERAL ---------- */

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ---------- RUCHI BRAND HEADER ---------- */

.ruchi-header {
    text-align: center;
    padding: 18px 10px 26px 10px;
}

.ruchi-symbol {
    font-size: 42px;
    line-height: 1;
    margin-bottom: 5px;
}

.ruchi-name {
    font-size: 48px;
    font-weight: 750;
    letter-spacing: -1.5px;
    margin: 0;
}

.ruchi-tagline {
    font-size: 18px;
    opacity: 0.72;
    margin-top: 4px;
}

/* ---------- HERO ---------- */

.ruchi-hero {
    text-align: center;
    padding: 18px 10px 30px 10px;
}

.ruchi-hero h2 {
    margin-bottom: 8px;
}

.ruchi-hero p {
    font-size: 17px;
    opacity: 0.75;
    max-width: 720px;
    margin: auto;
}

/* ---------- SMALL LABEL ---------- */

.ruchi-label {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 700;
    opacity: 0.55;
}

/* ---------- CARDS ---------- */

.ruchi-card {
    border: 1px solid rgba(128,128,128,0.20);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
}

/* ---------- FOOTER ---------- */

.ruchi-footer {
    text-align: center;
    opacity: 0.55;
    font-size: 13px;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "saved_recipes": [],
    "saved_links": [],
    "meal_options": [],
    "current_recipe": None,
    "cooking_step": 0,
    "cooking_started": False,
    "cooking_history": [],
    "last_inputs": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GEMINI
# ============================================================

def get_client():
    try:
        return genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )
    except Exception:
        return None


# ============================================================
# GENERATE THREE MEAL OPTIONS
# ============================================================

def generate_meal_options(
    craving,
    ingredients,
    servings,
    diet,
    allergies,
    spice
):

    client = get_client()

    if client is None:
        return None, "Gemini API key is unavailable."

    prompt = f"""
You are Ruchi, an intelligent everyday kitchen assistant.

Ruchi's purpose is to help people make more of the food and
ingredients they already have.

USER:

Craving:
{craving}

Ingredients already available:
{ingredients}

Servings:
{servings}

Dietary preference:
{diet}

Allergies / avoid:
{allergies}

Spice preference:
{spice}

Suggest exactly THREE practical meals.

Priorities:

1. Make useful use of ingredients already available.
2. Match the user's craving where possible.
3. Avoid unnecessary additional ingredients.
4. Respect dietary preferences and allergies.
5. Keep meals realistic for everyday home cooking.
6. Give meaningfully different options.

Return ONLY valid JSON:

{{
    "options": [
        {{
            "dish_name": "Dish name",
            "description": "Short appetising description",
            "why_it_fits": "Short explanation of why this is a good use of what the user has"
        }},
        {{
            "dish_name": "Dish name",
            "description": "Short appetising description",
            "why_it_fits": "Short explanation"
        }},
        {{
            "dish_name": "Dish name",
            "description": "Short appetising description",
            "why_it_fits": "Short explanation"
        }}
    ]
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = (
                raw.replace("```json", "")
                   .replace("```", "")
                   .strip()
            )

        data = json.loads(raw)

        return data["options"], None

    except Exception as e:
        return None, str(e)


# ============================================================
# GENERATE FULL RECIPE
# ============================================================

def generate_recipe(
    dish,
    ingredients,
    servings,
    diet,
    allergies,
    spice
):

    client = get_client()

    if client is None:
        return None, "Gemini API key is unavailable."

    prompt = f"""
You are Ruchi, an intelligent everyday kitchen assistant.

Create a practical home-cooking recipe.

Dish:
{dish}

Ingredients the user already has:
{ingredients}

Servings:
{servings}

Diet:
{diet}

Allergies / avoid:
{allergies}

Spice preference:
{spice}

Ruchi should help the user make useful use of ingredients
already available.

Return ONLY valid JSON:

{{
    "dish_name": "Dish name",

    "description": "One short appetising description",

    "cooking_time": "Example: 30 minutes",

    "servings": {servings},

    "ingredients": [
        {{
            "name": "Ingredient",
            "quantity": "Quantity",
            "already_have": true
        }}
    ],

    "steps": [
        "Step one",
        "Step two"
    ],

    "substitutions": [
        "Useful substitution"
    ],

    "nutrition": {{
        "calories": "Approximate calories per serving",
        "protein": "Approximate protein per serving"
    }}
}}

Mark already_have as true only when the ingredient
is reasonably present in the user's available ingredient list.

Nutrition values must be approximate.

Do not include text outside the JSON.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = (
                raw.replace("```json", "")
                   .replace("```", "")
                   .strip()
            )

        return json.loads(raw), None

    except Exception as e:
        return None, str(e)


# ============================================================
# BRAND HEADER
# ============================================================

st.markdown("""
<div class="ruchi-header">

    <div class="ruchi-symbol">◡</div>

    <div class="ruchi-name">
        Ruchi
    </div>

    <div class="ruchi-tagline">
        Make More of What You Have.
    </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ============================================================
# NAVIGATION
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍳 My Kitchen",
    "👩‍🍳 Cooking Mode",
    "📊 Kitchen Insights",
    "📚 My Library",
    "✨ Ruchi Plus"
])


# ============================================================
# TAB 1 — MY KITCHEN
# ============================================================

with tab1:

    st.markdown("""
    <div class="ruchi-hero">

        <div class="ruchi-label">
            YOUR KITCHEN, YOUR FOOD
        </div>

        <h2>
            What can we make today?
        </h2>

        <p>
            Tell Ruchi what you already have and what you're
            in the mood for. We'll start there.
        </p>

    </div>
    """, unsafe_allow_html=True)

    craving = st.text_input(
        "What are you in the mood for?",
        placeholder=(
            "Something spicy, comforting, light, "
            "high-protein..."
        )
    )

    ingredients = st.text_area(
        "What's already in your kitchen?",
        placeholder=(
            "Paneer, tomatoes, onion, curd, "
            "capsicum..."
        )
    )

    st.markdown("### Make it yours")

    c1, c2 = st.columns(2)

    with c1:

        servings = st.number_input(
            "Servings",
            min_value=1,
            max_value=10,
            value=2
        )

        diet = st.selectbox(
            "Dietary preference",
            [
                "No preference",
                "Vegetarian",
                "Vegan",
                "Eggetarian"
            ]
        )

    with c2:

        spice = st.selectbox(
            "Spice preference",
            [
                "Mild",
                "Medium",
                "Spicy",
                "Very spicy"
            ]
        )

        allergies = st.text_input(
            "Anything to avoid?",
            placeholder="Peanuts, mushrooms..."
        )

    if st.button(
        "✨ Show Me What I Can Make",
        type="primary",
        use_container_width=True
    ):

        if not craving.strip() and not ingredients.strip():

            st.warning(
                "Give Ruchi a craving or a few ingredients "
                "to start with."
            )

        else:

            st.session_state.last_inputs = {
                "craving": craving,
                "ingredients": ingredients,
                "servings": servings,
                "diet": diet,
                "allergies": allergies,
                "spice": spice
            }

            with st.spinner(
                "Looking through your kitchen..."
            ):

                options, error = generate_meal_options(
                    craving,
                    ingredients,
                    servings,
                    diet,
                    allergies,
                    spice
                )

            if error:

                st.error(
                    f"Ruchi couldn't generate options: {error}"
                )

            else:

                st.session_state.meal_options = options
                st.session_state.current_recipe = None
                st.session_state.cooking_started = False
                st.session_state.cooking_step = 0

    # ========================================================
    # THREE FOOD CHOICES
    # ========================================================

    if st.session_state.meal_options:

        st.markdown("---")

        st.markdown(
            "### 🍽️ Here's what you could make"
        )

        st.caption(
            "These options prioritise useful ingredients "
            "already in your kitchen."
        )

        cols = st.columns(3)

        for i, option in enumerate(
            st.session_state.meal_options[:3]
        ):

            with cols[i]:

                st.markdown(
                    f"### {option.get('dish_name', 'Meal')}"
                )

                st.write(
                    option.get("description", "")
                )

                st.info(
                    option.get(
                        "why_it_fits",
                        "A practical option using what you have."
                    )
                )

                if st.button(
                    "Choose this meal",
                    key=f"meal_{i}",
                    use_container_width=True
                ):

                    data = st.session_state.last_inputs

                    with st.spinner(
                        "Turning it into your meal..."
                    ):

                        recipe, error = generate_recipe(
                            option.get("dish_name", ""),
                            data["ingredients"],
                            data["servings"],
                            data["diet"],
                            data["allergies"],
                            data["spice"]
                        )

                    if error:

                        st.error(
                            f"Ruchi couldn't build the meal: {error}"
                        )

                    else:

                        st.session_state.current_recipe = recipe
                        st.session_state.cooking_step = 0
                        st.session_state.cooking_started = False

                        st.rerun()


    # ========================================================
    # MEAL INTELLIGENCE
    # ========================================================

    recipe = st.session_state.current_recipe

    if recipe:

        st.markdown("---")

        st.markdown(
            '<div class="ruchi-label">YOUR MEAL</div>',
            unsafe_allow_html=True
        )

        st.header(
            recipe.get(
                "dish_name",
                "Your Meal"
            )
        )

        st.write(
            recipe.get(
                "description",
                ""
            )
        )

        ingredients_list = recipe.get(
            "ingredients",
            []
        )

        already_have = [
            x for x in ingredients_list
            if x.get("already_have")
        ]

        missing = [
            x for x in ingredients_list
            if not x.get("already_have")
        ]

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "⏱️ Time",
            recipe.get(
                "cooking_time",
                "N/A"
            )
        )

        m2.metric(
            "🍽️ Serves",
            recipe.get(
                "servings",
                "-"
            )
        )

        m3.metric(
            "🥕 Already Have",
            f"{len(already_have)}/{len(ingredients_list)}"
        )

        st.markdown("### 🥕 Ingredient Intelligence")

        have_col, need_col = st.columns(2)

        with have_col:

            st.markdown(
                "#### Already in your kitchen"
            )

            if already_have:

                for item in already_have:

                    st.write(
                        f"✓ **{item.get('name')}** "
                        f"— {item.get('quantity')}"
                    )

            else:

                st.write(
                    "No ingredients were matched."
                )

        with need_col:

            st.markdown(
                "#### You may still need"
            )

            if missing:

                shopping_list = []

                for item in missing:

                    name = item.get(
                        "name",
                        "Ingredient"
                    )

                    quantity = item.get(
                        "quantity",
                        ""
                    )

                    st.checkbox(
                        f"{name} — {quantity}",
                        key=f"shop_{name}_{recipe.get('dish_name')}"
                    )

                    shopping_list.append(
                        f"{name} — {quantity}"
                    )

                st.text_area(
                    "Shopping list",
                    "\n".join(shopping_list),
                    height=120
                )

            else:

                st.success(
                    "You already have everything you need."
                )

        # ====================================================
        # SUBSTITUTIONS
        # ====================================================

        st.markdown("### 🔄 Easy Swaps")

        substitutions = recipe.get(
            "substitutions",
            []
        )

        if substitutions:

            for item in substitutions:
                st.write(f"• {item}")

        else:

            st.write(
                "No substitutions needed."
            )

        # ====================================================
        # NUTRITION
        # ====================================================

        st.markdown("### 🥗 Nutrition Snapshot")

        nutrition = recipe.get(
            "nutrition",
            {}
        )

        n1, n2 = st.columns(2)

        n1.metric(
            "Approx. calories / serving",
            nutrition.get(
                "calories",
                "N/A"
            )
        )

        n2.metric(
            "Approx. protein / serving",
            nutrition.get(
                "protein",
                "N/A"
            )
        )

        st.caption(
            "Nutrition values are approximate."
        )

        # ====================================================
        # ACTIONS
        # ====================================================

        save_col, cook_col = st.columns(2)

        with save_col:

            if st.button(
                "♡ Save for Later",
                use_container_width=True
            ):

                if (
                    recipe not in
                    st.session_state.saved_recipes
                ):

                    st.session_state.saved_recipes.append(
                        recipe
                    )

                st.success(
                    "Saved to My Library."
                )

        with cook_col:

            if st.button(
                "👩‍🍳 Start Cooking",
                type="primary",
                use_container_width=True
            ):

                st.session_state.cooking_started = True
                st.session_state.cooking_step = 0

                st.success(
                    "Your Cooking Mode is ready."
                )

                st.info(
                    "Open the Cooking Mode tab above."
                )


# ============================================================
# TAB 2 — COOKING MODE
# ============================================================

with tab2:

    st.markdown(
        '<div class="ruchi-label">COOK WITH RUCHI</div>',
        unsafe_allow_html=True
    )

    st.header("👩‍🍳 Cooking Mode")

    recipe = st.session_state.current_recipe

    if not recipe:

        st.info(
            "Choose a meal from My Kitchen first."
        )

    elif not st.session_state.cooking_started:

        st.subheader(
            recipe.get(
                "dish_name",
                "Your Meal"
            )
        )

        st.write(
            "Ready when you are."
        )

        if st.button(
            "🔥 Let's Cook",
            type="primary",
            use_container_width=True
        ):

            st.session_state.cooking_started = True
            st.session_state.cooking_step = 0

            st.rerun()

    else:

        steps = recipe.get(
            "steps",
            []
        )

        current = st.session_state.cooking_step

        if not steps:

            st.warning(
                "No cooking steps were generated."
            )

        elif current < len(steps):

            st.caption(
                f"STEP {current + 1} OF {len(steps)}"
            )

            st.progress(
                current / len(steps)
            )

            st.subheader(
                steps[current]
            )

            previous, next_step = st.columns(2)

            with previous:

                if st.button(
                    "← Previous",
                    disabled=(current == 0),
                    use_container_width=True
                ):

                    st.session_state.cooking_step -= 1
                    st.rerun()

            with next_step:

                text = (
                    "Finish Cooking ✓"
                    if current == len(steps) - 1
                    else "Done — Next Step →"
                )

                if st.button(
                    text,
                    type="primary",
                    use_container_width=True
                ):

                    st.session_state.cooking_step += 1
                    st.rerun()

        else:

            st.progress(1.0)

            st.success(
                "You made it! 🍽️"
            )

            st.header(
                recipe.get(
                    "dish_name",
                    "Your Meal"
                )
            )

            st.write(
                "Before you go, tell Ruchi how it turned out."
            )

            rating = st.slider(
                "How did it turn out?",
                1,
                5,
                4
            )

            make_again = st.radio(
                "Would you make this again?",
                [
                    "Yes",
                    "Maybe",
                    "No"
                ],
                horizontal=True
            )

            leftovers = st.radio(
                "Any leftovers?",
                [
                    "No",
                    "Yes"
                ],
                horizontal=True
            )

            if st.button(
                "🍽️ I Made This",
                type="primary",
                use_container_width=True
            ):

                record = {
                    "dish_name":
                        recipe.get(
                            "dish_name",
                            "Meal"
                        ),

                    "ingredients":
                        recipe.get(
                            "ingredients",
                            []
                        ),

                    "nutrition":
                        recipe.get(
                            "nutrition",
                            {}
                        ),

                    "rating":
                        rating,

                    "make_again":
                        make_again,

                    "leftovers":
                        leftovers
                }

                st.session_state.cooking_history.append(
                    record
                )

                if (
                    recipe not in
                    st.session_state.saved_recipes
                ):

                    st.session_state.saved_recipes.append(
                        recipe
                    )

                st.session_state.cooking_started = False
                st.session_state.cooking_step = 0

                st.success(
                    "Meal logged. Your Kitchen Insights "
                    "have been updated."
                )


# ============================================================
# TAB 3 — KITCHEN INSIGHTS
# ============================================================

with tab3:

    st.markdown(
        '<div class="ruchi-label">YOUR KITCHEN OVER TIME</div>',
        unsafe_allow_html=True
    )

    st.header("📊 Kitchen Insights")

    history = st.session_state.cooking_history

    if not history:

        st.info(
            "Your kitchen story starts with your first meal. "
            "Cook something with Ruchi and tap "
            "'I Made This' to begin."
        )

    else:

        pantry_uses = []
        ratings = []
        repeat_meals = 0

        for meal in history:

            ratings.append(
                meal.get(
                    "rating",
                    0
                )
            )

            if meal.get(
                "make_again"
            ) == "Yes":

                repeat_meals += 1

            for ingredient in meal.get(
                "ingredients",
                []
            ):

                if ingredient.get(
                    "already_have"
                ):

                    pantry_uses.append(
                        ingredient.get(
                            "name",
                            "Ingredient"
                        )
                    )

        avg_rating = (
            sum(ratings) / len(ratings)
            if ratings
            else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Meals Made",
            len(history)
        )

        c2.metric(
            "Pantry Ingredient Uses",
            len(pantry_uses)
        )

        c3.metric(
            "Average Rating",
            f"{avg_rating:.1f}/5"
        )

        c4.metric(
            "Would Make Again",
            repeat_meals
        )

        st.markdown("---")

        st.subheader(
            "🥕 What You've Been Using"
        )

        if pantry_uses:

            unique = list(
                dict.fromkeys(
                    pantry_uses
                )
            )

            st.write(
                " • ".join(unique)
            )

        else:

            st.write(
                "No pantry ingredient use logged yet."
            )

        st.subheader(
            "🍲 Your Cooking History"
        )

        for meal in reversed(history):

            title = meal.get(
                "dish_name",
                "Meal"
            )

            with st.expander(title):

                st.write(
                    f"⭐ **Rating:** "
                    f"{meal.get('rating')}/5"
                )

                st.write(
                    f"♡ **Make again:** "
                    f"{meal.get('make_again')}"
                )

                st.write(
                    f"🥡 **Leftovers:** "
                    f"{meal.get('leftovers')}"
                )

                nutrition = meal.get(
                    "nutrition",
                    {}
                )

                st.write(
                    "**Nutrition snapshot:** "
                    f"{nutrition.get('calories', 'N/A')} calories, "
                    f"{nutrition.get('protein', 'N/A')} protein "
                    "per serving (approx.)"
                )

        st.caption(
            "Kitchen Insights are based only on meals and "
            "ingredients logged during your Ruchi session."
        )


# ============================================================
# TAB 4 — LIBRARY
# ============================================================

with tab4:

    st.markdown(
        '<div class="ruchi-label">KEEP WHAT INSPIRES YOU</div>',
        unsafe_allow_html=True
    )

    st.header("📚 My Library")

    meals_tab, inspiration_tab = st.tabs([
        "Saved Meals",
        "Food Inspiration"
    ])

    with meals_tab:

        if not st.session_state.saved_recipes:

            st.info(
                "Meals you save will appear here."
            )

        else:

            for recipe in st.session_state.saved_recipes:

                with st.expander(
                    recipe.get(
                        "dish_name",
                        "Saved Meal"
                    )
                ):

                    st.write(
                        recipe.get(
                            "description",
                            ""
                        )
                    )

                    st.markdown(
                        "**Ingredients**"
                    )

                    for item in recipe.get(
                        "ingredients",
                        []
                    ):

                        st.write(
                            f"• {item.get('name')} "
                            f"— {item.get('quantity')}"
                        )

                    st.markdown(
                        "**How to make it**"
                    )

                    for i, step in enumerate(
                        recipe.get(
                            "steps",
                            []
                        ),
                        1
                    ):

                        st.write(
                            f"{i}. {step}"
                        )

    with inspiration_tab:

        st.write(
            "Saw something you'd like to cook later? "
            "Keep the link here."
        )

        url = st.text_input(
            "Food inspiration link",
            placeholder=(
                "Paste a recipe, reel or video link"
            )
        )

        note = st.text_input(
            "Add a note",
            placeholder=(
                "Try this for dinner..."
            )
        )

        if st.button(
            "🔖 Save Inspiration"
        ):

            if url.strip():

                st.session_state.saved_links.append({
                    "url": url,
                    "note": note
                })

                st.success(
                    "Saved."
                )

            else:

                st.warning(
                    "Paste a link first."
                )

        if st.session_state.saved_links:

            st.markdown("---")

            for item in st.session_state.saved_links:

                st.markdown(
                    f"**{item.get('note') or 'Food idea'}**"
                )

                st.write(
                    item.get("url")
                )


# ============================================================
# TAB 5 — RUCHI PLUS
# ============================================================

with tab5:

    st.markdown(
        '<div class="ruchi-label">MORE FROM YOUR KITCHEN</div>',
        unsafe_allow_html=True
    )

    st.header("✨ Ruchi Plus")

    st.write(
        "The core Ruchi experience stays simple. "
        "Ruchi Plus represents the future premium layer "
        "for people who want deeper kitchen intelligence."
    )

    free, plus = st.columns(2)

    with free:

        st.subheader(
            "Ruchi"
        )

        st.markdown("""
**Free**

✓ Meal discovery  
✓ Ingredient-based suggestions  
✓ Personalised meals  
✓ Ingredient intelligence  
✓ Cooking Mode  
✓ Kitchen Insights  
✓ Saved meals  
✓ Food inspiration
""")

        st.success(
            "Current plan"
        )

    with plus:

        st.subheader(
            "Ruchi Plus"
        )

        st.markdown("""
**Coming Soon**

Everything in Ruchi, plus:

✓ Deeper nutrition insights  
✓ Advanced pantry intelligence  
✓ Longer cooking history  
✓ Advanced meal planning  
✓ Deeper personalisation  
✓ Future premium features
""")

        st.button(
            "Coming Soon",
            disabled=True,
            use_container_width=True
        )

    st.caption(
        "Ruchi Plus is a proposed future subscription tier. "
        "Payments are not part of the current MVP."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
<div class="ruchi-footer">

<strong>Ruchi</strong><br>
Make More of What You Have.

</div>
""", unsafe_allow_html=True)
