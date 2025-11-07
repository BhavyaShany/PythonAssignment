"""
Name: Bhavya Shany
Date: 03-11-2025
Project: Gradebook Analyzer
"""

import csv
import statistics

def calculate_average(marks_dict):
    return sum(marks_dict.values()) / len(marks_dict)

def calculate_median(marks_dict):
    return statistics.median(marks_dict.values())

def find_max_score(marks_dict):
    return max(marks_dict.values())

def find_min_score(marks_dict):
    return min(marks_dict.values())

def assign_grades(marks_dict):
    grades = {}
    for student, mark in marks_dict.items():
        if mark >= 90:
            grades[student] = "A"
        elif mark >= 80:
            grades[student] = "B"
        elif mark >= 70:
            grades[student] = "C"
        elif mark >= 60:
            grades[student] = "D"
        else:
            grades[student] = "F"
    return grades

def manual_input():
    marks = {}
    n = int(input("Enter number of students: "))
    for i in range(n):
        name = input(f"Enter student {i+1} name: ")
        mark = float(input(f"Enter marks for {name}: "))
        marks[name] = mark
    return marks

def load_csv():
    marks = {}
    file = input("Enter CSV filename (ex: students.csv): ")
    try:
        with open(file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # skip header if exists
            for row in reader:
                marks[row[0]] = float(row[1])
        print("CSV loaded successfully.")
    except:
        print("Error reading file. Make sure it exists.")
    return marks

def print_table(marks, grades):
    print("\nName\t\tMarks\tGrade")
    print("-----------------------------------")
    for student in marks:
        print(f"{student}\t\t{marks[student]}\t{grades[student]}")

def save_csv(marks, grades):
    filename = "grade_output.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Marks", "Grade"])
        for name in marks:
            writer.writerow([name, marks[name], grades[name]])
    print(f"Results saved to {filename}")

def run_program():
    print("\nWelcome to Gradebook Analyzer!")
    print("1. Manual Data Entry")
    print("2. Upload CSV File")

    choice = input("Choose an option: ")

    if choice == "1":
        marks = manual_input()
    elif choice == "2":
        marks = load_csv()
    else:
        print("Invalid choice.")
        return

    if not marks:
        print("No data found.")
        return

    # Stats
    avg = calculate_average(marks)
    median = calculate_median(marks)
    max_score = find_max_score(marks)
    min_score = find_min_score(marks)

    grades = assign_grades(marks)

    # Grade distribution
    grade_counts = {g: list(grades.values()).count(g) for g in "ABCDF"}

    # Pass/fail list comprehension
    passed = [s for s, m in marks.items() if m >= 40]
    failed = [s for s, m in marks.items() if m < 40]

    # Print results
    print_table(marks, grades)
    print("\nStatistics:")
    print(f"Average Marks: {avg:.2f}")
    print(f"Median Marks: {median}")
    print(f"Highest Score: {max_score}")
    print(f"Lowest Score: {min_score}")

    print("\nGrade Distribution:")
    for grade, count in grade_counts.items():
        print(f"{grade}: {count}")

    print(f"\nPassed: {len(passed)} -> {passed}")
    print(f"Failed: {len(failed)} -> {failed}")

    # Bonus: save CSV
    save_choice = input("\nSave results to CSV? (yes/no): ").lower()
    if save_choice == "yes":
        save_csv(marks, grades)

# Repeat loop
while True:
    run_program()
    again = input("\nRun again? (yes/no): ").lower()
    if again != "yes":
        print("Goodbye!")
        break
