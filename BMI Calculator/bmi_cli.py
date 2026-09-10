"""
BMI Calculator - Beginner Tier (CLI)
Calculates Body Mass Index (BMI) from user input with validation and category classification.
"""

def get_positive_float(prompt):
    """
    Prompts the user for input until a valid positive float is provided.
    
    Handles non-numeric text (ValueError) and non-positive numbers (<= 0)
    with helpful error messages instead of crashing.
    """
    while True:
        raw_value = input(prompt).strip()
        try:
            value = float(raw_value)
            if value <= 0:
                print("Error: Value must be greater than zero. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Error: '{raw_value}' is not a valid number. Please enter a numeric value.")

def calculate_bmi(weight_kg, height_m):
    """
    Calculates Body Mass Index (BMI).
    Formula: weight (kg) / height (m)^2
    """
    return weight_kg / (height_m ** 2)

def classify_bmi(bmi):
    """
    Classifies a BMI value into World Health Organization (WHO) standard categories.
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"

def main():
    print("==========================================")
    print("        BMI Calculator (CLI Version)      ")
    print("==========================================")
    
    weight = get_positive_float("Enter weight (kg): ")
    height = get_positive_float("Enter height (m): ")
    
    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)
    
    print("\n--- Results ---")
    print(f"BMI: {bmi:.2f}")
    print(f"Category: {category}")

if __name__ == "__main__":
    main()
