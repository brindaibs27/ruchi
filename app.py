
import streamlit as st
import json
from google import genai

st.set_page_config(
    page_title="Ruchi",
    page_icon="🍲",
    layout="wide"
)

# -------------------------
# SESSION STATE
# -------------------------

if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = []

if "saved_links" not in st.session_state:
    st.session_state.saved_links = []

if "current_recipe" not in st.session_state:
    st.session_state.current_recipe = None


# -------------------------
# AI CONNECTION
# -------------------------

def get_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception:
        return None


def generate_recipe(
    craving,
    available_ingredients,
    servings,
    diet,
    allergies,
    spice_level
):
    client = get_client()

    if client is None:
        return None, "Gemini API key has not been added to Streamlit Secrets."

    prompt = f"""
You are Ruchi, an AI assistant for everyday home cooking.

Create one practical recipe based on the user's needs.

USER INPUT
Craving or dish idea: {craving}
Ingredients already available: {available_ingredients}
Servings: {servings}
Dietary preference: {diet}
Allergies: {allergies}
Spice preference: {spice_level}

Return ONLY valid JSON in this structure:

{{
    "dish_name": "Name of dish",
    "description": "One short sentence",
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
        "Step 1",
        "Step 2"
    ],
    "substitutions": [
        "Possible substitution 1",
        "Possible substitution 2"
    ],
    "nutrition": {{
        "calories": "Approximate calories per serving",
        "protein": "Approximate protein per serving"
    }}
}}

Important:
- Keep the recipe realistic and suitable for daily cooking.
- Prefer common ingredients.
- Respect allergies and dietary preferences.
- Mark already_have as true only when the ingredient appears in the user's available ingredients.
- If the user gives no available ingredients, mark all ingredients as false.
- Do not include commentary outside the JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        recipe = json.loads(raw)

        return recipe, None

    except Exception as e:
        return None, str(e)


# -------------------------
# APP HEADER
# -------------------------

st.title("🍲 Ruchi")
st.subheader("Your AI recipe maker for everyday cooking")

st.write(
    "Tell Ruchi what you're craving or what ingredients you already have, "
    "and get a personalised recipe you can actually cook."
)

st.markdown("---")


# -------------------------
# TABS
# -------------------------

tab1, tab2, tab3 = st.tabs(
    ["🍳 Create Recipe", "🛒 Ingredient Cart", "📚 My Library"]
)


# -------------------------
# CREATE RECIPE
# -------------------------

with tab1:

    st.header("What would you like to cook?")

    craving = st.text_input(
        "Tell Ruchi what you're craving or the dish you want",
        placeholder="Example: I want something spicy and high-protein"
    )

    available_ingredients = st.text_area(
        "What ingredients do you already have?",
        placeholder="Example: paneer, onion, tomato, curd"
    )

    st.subheader("Personalise your recipe")

    col1, col2 = st.columns(2)

    with col1:
        servings = st.number_input(
            "Number of servings",
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

    with col2:
        spice_level = st.selectbox(
            "Spice preference",
            [
                "Mild",
                "Medium",
                "Spicy",
                "Very spicy"
            ]
        )

        allergies = st.text_input(
            "Allergies or ingredients to avoid",
            placeholder="Example: peanuts, mushrooms"
        )

    if st.button("✨ Create My Recipe", use_container_width=True):

        if not craving and not available_ingredients:
            st.warning(
                "Please enter either a craving/dish idea or some available ingredients."
            )

        else:
            with st.spinner("Ruchi is creating your recipe..."):

                recipe, error = generate_recipe(
                    craving,
                    available_ingredients,
                    servings,
                    diet,
                    allergies,
                    spice_level
                )

            if error:
                st.error(f"Something went wrong: {error}")

            else:
                st.session_state.current_recipe = recipe
                st.success("Your recipe is ready!")


    recipe = st.session_state.current_recipe

    if recipe:

        st.markdown("---")
        st.header(recipe.get("dish_name", "Your Recipe"))

        st.write(recipe.get("description", ""))

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Cooking Time",
                recipe.get("cooking_time", "Not specified")
            )

        with col2:
            st.metric(
                "Servings",
                recipe.get("servings", servings)
            )

        st.subheader("Ingredients")

        for item in recipe.get("ingredients", []):
            status = "✅" if item.get("already_have") else "🛒"

            st.write(
                f"{status} **{item.get('name')}** — "
                f"{item.get('quantity')}"
            )

        st.subheader("Steps")

        for i, step in enumerate(recipe.get("steps", []), start=1):
            st.write(f"**{i}.** {step}")

        st.subheader("Possible Substitutions")

        substitutions = recipe.get("substitutions", [])

        if substitutions:
            for substitution in substitutions:
                st.write(f"- {substitution}")
        else:
            st.write("No substitutions suggested.")

        st.subheader("Basic Nutrition")

        nutrition = recipe.get("nutrition", {})

        col1, col2 = st.columns(2)

        col1.metric(
            "Calories / serving",
            nutrition.get("calories", "N/A")
        )

        col2.metric(
            "Protein / serving",
            nutrition.get("protein", "N/A")
        )

        if st.button("💾 Save Recipe"):
            if recipe not in st.session_state.saved_recipes:
                st.session_state.saved_recipes.append(recipe)

            st.success("Recipe saved to your Library.")


# -------------------------
# INGREDIENT CART
# -------------------------

with tab2:

    st.header("🛒 Smart Ingredient Cart")

    recipe = st.session_state.current_recipe

    if not recipe:
        st.info(
            "Create a recipe first. Ruchi will then show the ingredients you still need."
        )

    else:

        missing = [
            item
            for item in recipe.get("ingredients", [])
            if not item.get("already_have")
        ]

        already_have = [
            item
            for item in recipe.get("ingredients", [])
            if item.get("already_have")
        ]

        st.subheader("You already have")

        if already_have:
            for item in already_have:
                st.write(
                    f"✅ {item.get('name')} — {item.get('quantity')}"
                )
        else:
            st.write("No available ingredients were matched.")

        st.subheader("You still need")

        if missing:
            shopping_text = ""

            for item in missing:
                st.checkbox(
                    f"{item.get('name')} — {item.get('quantity')}",
                    key=f"cart_{item.get('name')}"
                )

                shopping_text += (
                    f"{item.get('name')} — "
                    f"{item.get('quantity')}\n"
                )

            st.text_area(
                "Copy your shopping list",
                shopping_text,
                height=150
            )

        else:
            st.success("You already have everything needed for this recipe! 🎉")


# -------------------------
# LIBRARY
# -------------------------

with tab3:

    st.header("📚 My Library")

    recipe_tab, inspiration_tab = st.tabs(
        ["Saved Recipes", "Saved Inspiration"]
    )

    with recipe_tab:

        if not st.session_state.saved_recipes:
            st.info("You haven't saved any recipes yet.")

        else:
            for i, recipe in enumerate(
                st.session_state.saved_recipes,
                start=1
            ):
                with st.expander(
                    f"{i}. {recipe.get('dish_name', 'Saved Recipe')}"
                ):
                    st.write(recipe.get("description", ""))

                    st.write("**Ingredients**")

                    for item in recipe.get("ingredients", []):
                        st.write(
                            f"- {item.get('name')} — "
                            f"{item.get('quantity')}"
                        )

                    st.write("**Steps**")

                    for j, step in enumerate(
                        recipe.get("steps", []),
                        start=1
                    ):
                        st.write(f"{j}. {step}")

    with inspiration_tab:

        st.write(
            "Save a food reel, YouTube video, recipe page or other food link "
            "that you want to revisit later."
        )

        inspiration_url = st.text_input(
            "Food inspiration URL",
            placeholder="Paste a link here"
        )

        inspiration_note = st.text_input(
            "Optional note",
            placeholder="Example: Try this pasta next weekend"
        )

        if st.button("🔖 Save Inspiration"):

            if inspiration_url:

                st.session_state.saved_links.append(
                    {
                        "url": inspiration_url,
                        "note": inspiration_note
                    }
                )

                st.success("Saved to your Inspiration Library.")

            else:
                st.warning("Please paste a URL first.")

        st.markdown("---")

        if not st.session_state.saved_links:
            st.info("No inspiration links saved yet.")

        else:
            for i, item in enumerate(
                st.session_state.saved_links,
                start=1
            ):
                st.write(
                    f"**{i}.** {item.get('note') or 'Saved food inspiration'}"
                )

                st.write(item.get("url"))


st.markdown("---")

st.caption(
    "Ruchi MVP | AI recipe maker for everyday cooking"
)
