import numpy as np

def analyze_leaf(image):
    # Simulated Health Analysis Score
    return np.random.randint(55, 98)

def get_soil_logic(moisture):
    # Logic to convert numeric moisture % into actionable status labels
    if moisture < 35: 
        return "🔴 Dry", "CRITICAL: Irrigation required immediately."
    elif 35 <= moisture <= 75: 
        return "🟢 Optimal", "Condition is perfect for growth."
    else: 
        return "🔵 Over-watered", "WARNING: Reduce water to prevent root rot."

def get_nutrient_advice(score):
    if score < 70: 
        return "Nitrogen (N) Deficiency", "Action: Apply organic compost or Urea fertilizer."
    return "Balanced", "Plant appears healthy and well-nourished."