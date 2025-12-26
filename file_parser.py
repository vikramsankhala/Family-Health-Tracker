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
        xls = pd.ExcelFile(filepath)
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM diet_plan')
            
            # Focus on the "Weekly Meal Plan" sheet
            if 'Weekly Meal Plan' in xls.sheet_names:
                df = pd.read_excel(filepath, sheet_name='Weekly Meal Plan', header=2)
                
                # Get meal types from first row (row 0)
                meal_types = []
                if len(df) > 0:
                    first_row = df.iloc[0]
                    for col_idx in range(1, len(first_row)):
                        header_val = str(first_row.iloc[col_idx]).strip() if pd.notna(first_row.iloc[col_idx]) else ''
                        if 'BREAKFAST' in header_val.upper():
                            meal_types.append(('Breakfast', col_idx))
                        elif 'MID-MORNING' in header_val.upper() or 'MID MORNING' in header_val.upper():
                            meal_types.append(('Mid-Morning', col_idx))
                        elif 'LUNCH' in header_val.upper():
                            meal_types.append(('Lunch', col_idx))
                        elif 'AFTERNOON' in header_val.upper() or 'SNACK' in header_val.upper():
                            meal_types.append(('Afternoon Snack', col_idx))
                        elif 'DINNER' in header_val.upper():
                            meal_types.append(('Dinner', col_idx))
                        elif 'BEDTIME' in header_val.upper() or 'BED TIME' in header_val.upper():
                            meal_types.append(('Bedtime', col_idx))
                
                # Parse each row starting from row 1 (skip header row)
                for idx in range(1, len(df)):
                    row = df.iloc[idx]
                    day = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
                    if not day or day.upper() in ['DAY', 'NAN', 'NONE', '']:
                        continue
                    
                    # Extract meals for each meal type
                    for meal_type, col_idx in meal_types:
                        if col_idx < len(row):
                            food_item = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ''
                            if food_item and food_item.upper() not in ['NAN', 'NONE', '']:
                                cursor.execute('''
                                    INSERT INTO diet_plan 
                                    (meal_type, day, food_item, quantity, calories, protein, carbs, fats)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (meal_type, day, food_item, None, None, None, None, None))
            
            conn.commit()
            print(f"Parsed diet plan from Weekly Meal Plan sheet")
    except Exception as e:
        print(f"Error parsing diet plan: {e}")
        import traceback
        traceback.print_exc()

def parse_exercise_plan(filepath):
    """Parse Personalized Weekly Exercise Plan Excel file"""
    try:
        xls = pd.ExcelFile(filepath)
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM exercise_plan')
            
            # Parse Phase sheets (Phase 1, Phase 2, Phase 3)
            phase_sheets = [s for s in xls.sheet_names if 'Phase' in s and 'Week' in s]
            
            current_day = None
            for sheet_name in phase_sheets:
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name, header=3)
                    
                    for idx, row in df.iterrows():
                        # Check if this row indicates a new day
                        time_of_day = str(row.get('Time of Day', '')).strip() if pd.notna(row.get('Time of Day')) else ''
                        activity = str(row.get('Activity', '')).strip() if pd.notna(row.get('Activity')) else ''
                        notes = str(row.get('Notes', '')).strip() if pd.notna(row.get('Notes')) else ''
                        
                        # If Time of Day contains a day name, update current_day
                        if time_of_day:
                            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            for day_name in day_names:
                                if day_name.upper() in time_of_day.upper():
                                    current_day = day_name
                                    break
                        
                        # If we have an activity, insert it
                        if activity and activity.upper() not in ['NAN', 'NONE', '']:
                            # Extract duration from activity if possible
                            duration_minutes = None
                            if 'min' in activity.lower():
                                import re
                                match = re.search(r'(\d+)\s*min', activity.lower())
                                if match:
                                    duration_minutes = int(match.group(1))
                            
                            # Extract sets and reps if mentioned
                            sets = None
                            reps = None
                            if 'sets' in activity.lower() or 'reps' in activity.lower():
                                import re
                                set_match = re.search(r'(\d+)\s*sets?', activity.lower())
                                rep_match = re.search(r'(\d+)\s*reps?', activity.lower())
                                if set_match:
                                    sets = int(set_match.group(1))
                                if rep_match:
                                    reps = int(rep_match.group(1))
                            
                            day_to_use = current_day if current_day else sheet_name
                            cursor.execute('''
                                INSERT INTO exercise_plan 
                                (day, exercise_name, duration_minutes, sets, reps, notes)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (day_to_use, activity, duration_minutes, sets, reps, notes))
                except Exception as e:
                    print(f"Error parsing sheet {sheet_name}: {e}")
                    continue
            
            conn.commit()
            print(f"Parsed exercise plan from {len(phase_sheets)} phase sheets")
    except Exception as e:
        print(f"Error parsing exercise plan: {e}")
        import traceback
        traceback.print_exc()

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

