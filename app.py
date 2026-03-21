import streamlit as st
# Import your other necessary libraries (tensorflow, numpy, etc.)

# --- STEP 1: FIX THE ADVICE FUNCTION ---
def get_nutrient_advice(prediction):
    """
    This function must ALWAYS return exactly two strings:
    (Nutrient Deficiency, Recommended Action)
    """
    # Example logic - replace with your actual class names
    if prediction == "Healthy":
        return "None", "Your plant is healthy! Keep up the good work."
    elif prediction == "Yellowish":
        return "Nitrogen Deficiency", "Apply a nitrogen-rich fertilizer or compost."
    elif prediction == "Brown Spots":
        return "Potassium/Fungal issue", "Check soil moisture and apply balanced NPK."
    
    # CRITICAL: The 'else' or 'default' return prevents the ValueError
    return "Analyzing...", "Try taking a clearer photo of the leaf in better light."

# --- STEP 2: UPDATE THE MAIN APP LOGIC ---
st.title("AgroMind Ultimate")
st.write("Processing Leaf Image...")

# Assuming 'prediction' is the output from your model
# We wrap the call in a try-except block for extra safety
try:
    # This is the line that was crashing in your screenshot
    nut, nut_adv = get_nutrient_advice(prediction)
except Exception as e:
    # If anything goes wrong, the app stays running with these defaults
    nut, nut_adv = "Pending Diagnosis", "Ensure the leaf is centered in the frame."

# --- STEP 3: DISPLAY RESULTS ---
st.subheader(f"Detected Condition: {prediction}")
st.write(f"**Nutrient Status:** {nut}")
st.write(f"**Action Plan:** {nut_adv}")
