# Task 1:
# Name: Bhavya Shany
# Date: 03-11-2025
# Project: Daily Calorie Tracker
print("Welcome to the Daily Calorie Tracker!")
print("This tool helps you record your meals and calories, calculate totals, and compare against your daily calorie limit.\n")


# Task 2: Get user input
mealnames = []
calorievalues = []

num_meals = int(input("How many meals did you have today? "))

for i in range(num_meals):
    meal = input(f"Enter meal {i+1} name: ")
    calories = float(input(f"Enter calories for {meal}: "))
    mealnames.append(meal)
    calorievalues.append(calories)


# Task 3: Calculations
total_cal = sum(calorievalues)
average_cal = total_cal / len(calorievalues)
daily_limit = float(input("\nEnter your daily calorie limit: "))


# Task 4: Warning System
if total_cal > daily_limit:
    status_message = "You exceeded your daily calorie limit!"
else:
    status_message = "Great job! You stayed within your calorie limit."


# Task 5: Formatted Output
print("\nMeal Name\tCalories")
print("----------------------------------")
for meal, cal in zip(mealnames, calorievalues):
    print(f"{meal}\t\t{cal}")
print("----------------------------------")
print(f"Total:\t\t{total_cal}")
print(f"Average:\t{average_cal:.2f}")
print(status_message)


# Task 6: Save to file (Bonus)
save_choice = input("\nDo you want to save this report? (yes/no): ").lower()

if save_choice == "yes":
    from datetime import datetime
    filename = "calorie_report.txt"
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, "w") as file:
        file.write("Daily Calorie Tracker Report\n")
        file.write(f"Date & Time: {time_stamp}\n\n")
        file.write("Meal\tCalories\n")
        file.write("----------------------------------\n")
        for meal, cal in zip(mealnames, calorievalues):
            file.write(f"{meal}\t{cal}\n")
        file.write("----------------------------------\n")
        file.write(f"Total:\t{total_cal}\n")
        file.write(f"Average:\t{average_cal:.2f}\n")
        file.write(f"Status: {status_message}\n")
    
    print(f"Report saved as {filename}")
else:
    print("Report not saved.")
