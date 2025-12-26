"""
File parser to extract data from Excel files and populate database
"""
import pandas as pd
import os
from datetime import datetime
import database

CONTENT_DIR = 'Content'

def parse_health_tracker(filepath):
    """Parse Weekly Health Tracker Excel file"""
    try:
        df = pd.read_excel(filepath, sheet_name=0)
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM health_tracker_data')
            
            for _, row in df.iterrows():
                try:
                    date = str(row.get('Date', ''))
                    if pd.isna(date) or date == '':
                        continue
                    
                    weight = float(row.get('Weight', 0)) if pd.notna(row.get('Weight')) else None
                    blood_pressure = str(row.get('Blood Pressure', '')) if pd.notna(row.get('Blood Pressure')) else None
                    blood_sugar = str(row.get('Blood Sugar', '')) if pd.notna(row.get('Blood Sugar')) else None
                    sleep_hours = float(row.get('Sleep Hours', 0)) if pd.notna(row.get('Sleep Hours')) else None
                    exercise_minutes = int(row.get('Exercise Minutes', 0)) if pd.notna(row.get('Exercise Minutes')) else None
                    notes = str(row.get('Notes', '')) if pd.notna(row.get('Notes')) else None
                    
                    cursor.execute('''
                        INSERT INTO health_tracker_data 
                        (date, weight, blood_pressure, blood_sugar, sleep_hours, exercise_minutes, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (date, weight, blood_pressure, blood_sugar, sleep_hours, exercise_minutes, notes))
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
            
            conn.commit()
            print(f"Parsed {len(df)} rows from health tracker")
    except Exception as e:
        print(f"Error parsing health tracker: {e}")

def parse_diet_plan(filepath):
    """Parse Personalized North Indian Diet Plan Excel file"""
    try:
        # Try to read all sheets
        xls = pd.ExcelFile(filepath)
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM diet_plan')
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                
                # Try to identify columns
                for _, row in df.iterrows():
                    try:
                        meal_type = str(row.get('Meal', row.get('Meal Type', 'Unknown'))) if pd.notna(row.get('Meal', row.get('Meal Type'))) else 'Unknown'
                        day = str(row.get('Day', row.get('Day of Week', 'Unknown'))) if pd.notna(row.get('Day', row.get('Day of Week'))) else 'Unknown'
                        food_item = str(row.get('Food Item', row.get('Food', row.get('Item', '')))) if pd.notna(row.get('Food Item', row.get('Food', row.get('Item')))) else ''
                        quantity = str(row.get('Quantity', row.get('Amount', ''))) if pd.notna(row.get('Quantity', row.get('Amount'))) else None
                        calories = int(row.get('Calories', 0)) if pd.notna(row.get('Calories')) else None
                        protein = float(row.get('Protein', 0)) if pd.notna(row.get('Protein')) else None
                        carbs = float(row.get('Carbs', row.get('Carbohydrates', 0))) if pd.notna(row.get('Carbs', row.get('Carbohydrates'))) else None
                        fats = float(row.get('Fats', row.get('Fat', 0))) if pd.notna(row.get('Fats', row.get('Fat'))) else None
                        
                        if food_item and food_item.strip():
                            cursor.execute('''
                                INSERT INTO diet_plan 
                                (meal_type, day, food_item, quantity, calories, protein, carbs, fats)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (meal_type, day, food_item, quantity, calories, protein, carbs, fats))
                    except Exception as e:
                        continue
            
            conn.commit()
            print(f"Parsed diet plan from {len(xls.sheet_names)} sheets")
    except Exception as e:
        print(f"Error parsing diet plan: {e}")

def parse_exercise_plan(filepath):
    """Parse Personalized Weekly Exercise Plan Excel file"""
    try:
        xls = pd.ExcelFile(filepath)
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM exercise_plan')
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                
                for _, row in df.iterrows():
                    try:
                        day = str(row.get('Day', row.get('Day of Week', 'Unknown'))) if pd.notna(row.get('Day', row.get('Day of Week'))) else 'Unknown'
                        exercise_name = str(row.get('Exercise', row.get('Exercise Name', row.get('Workout', '')))) if pd.notna(row.get('Exercise', row.get('Exercise Name', row.get('Workout')))) else ''
                        duration_minutes = int(row.get('Duration', row.get('Duration (min)', 0))) if pd.notna(row.get('Duration', row.get('Duration (min)'))) else None
                        sets = int(row.get('Sets', 0)) if pd.notna(row.get('Sets')) else None
                        reps = int(row.get('Reps', row.get('Repetitions', 0))) if pd.notna(row.get('Reps', row.get('Repetitions'))) else None
                        notes = str(row.get('Notes', '')) if pd.notna(row.get('Notes')) else None
                        
                        if exercise_name and exercise_name.strip():
                            cursor.execute('''
                                INSERT INTO exercise_plan 
                                (day, exercise_name, duration_minutes, sets, reps, notes)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (day, exercise_name, duration_minutes, sets, reps, notes))
                    except Exception as e:
                        continue
            
            conn.commit()
            print(f"Parsed exercise plan from {len(xls.sheet_names)} sheets")
    except Exception as e:
        print(f"Error parsing exercise plan: {e}")

def parse_all_files():
    """Parse all Excel files in Content directory"""
    if not os.path.exists(CONTENT_DIR):
        print(f"Content directory not found: {CONTENT_DIR}")
        return
    
    files = os.listdir(CONTENT_DIR)
    
    for filename in files:
        filepath = os.path.join(CONTENT_DIR, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        if filename == 'Weekly Health Tracker.xlsx':
            print(f"Parsing: {filename}")
            parse_health_tracker(filepath)
        elif 'Diet Plan' in filename or 'diet' in filename.lower():
            print(f"Parsing: {filename}")
            parse_diet_plan(filepath)
        elif 'Exercise Plan' in filename or 'exercise' in filename.lower():
            print(f"Parsing: {filename}")
            parse_exercise_plan(filepath)

if __name__ == '__main__':
    parse_all_files()

