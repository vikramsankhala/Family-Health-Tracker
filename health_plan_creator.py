"""
Script to create and populate the 16-week health plan
Goal: Reach 1mg Risperidone at night only + Normal biomarkers
"""
import database
from datetime import datetime, timedelta
import json

def create_health_plan():
    """Create comprehensive 16-week health plan"""
    
    # Calculate start date (today)
    start_date = datetime.now()
    
    plan = [
        {
            "week_number": 1,
            "week_start_date": start_date.strftime("%Y-%m-%d"),
            "medication_dose": "Current dose - 0.25mg (if > 1mg) OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <140/90, Blood Sugar: 80-100 (fasting), Weight: Baseline, Sleep: 7-8 hours",
            "diet_focus": "Eliminate processed foods, reduce sugar, increase vegetables, whole grains, lean proteins. Mediterranean diet principles.",
            "exercise_plan": "Light walking 20-30 min/day, 5 days/week. Gentle stretching 10 min daily.",
            "sleep_target_hours": 7.5,
            "stress_management": "Daily meditation 10 min, deep breathing exercises, journaling",
            "key_milestones": "Baseline biomarker testing, establish routine, medication assessment",
            "progress_notes": ""
        },
        {
            "week_number": 2,
            "week_start_date": (start_date + timedelta(weeks=1)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue gradual reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <135/85, Blood Sugar: 80-100 (fasting), Weight: -0.5kg, Sleep: 7-8 hours",
            "diet_focus": "Continue Mediterranean diet. Add omega-3 rich foods (salmon, walnuts, flaxseeds). Reduce sodium to <2000mg/day.",
            "exercise_plan": "Walking 30-40 min/day, 5 days/week. Add light strength training 2x/week (bodyweight exercises).",
            "sleep_target_hours": 7.5,
            "stress_management": "Meditation 15 min, progressive muscle relaxation, maintain sleep schedule",
            "key_milestones": "First week of consistent routine, monitor medication response",
            "progress_notes": ""
        },
        {
            "week_number": 3,
            "week_start_date": (start_date + timedelta(weeks=2)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <130/80, Blood Sugar: 80-100 (fasting), Weight: -1kg, Sleep: 7-8 hours",
            "diet_focus": "Increase fiber intake (25-30g/day). Add fermented foods (yogurt, kefir) for gut health. Limit caffeine to morning only.",
            "exercise_plan": "Walking 40-45 min/day, 5 days/week. Strength training 3x/week. Add yoga 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Meditation 20 min, nature walks, social connections",
            "key_milestones": "Improved energy levels, better sleep quality",
            "progress_notes": ""
        },
        {
            "week_number": 4,
            "week_start_date": (start_date + timedelta(weeks=3)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <130/80, Blood Sugar: 80-100 (fasting), Weight: -1.5kg, Sleep: 7-8 hours, Cholesterol: Check",
            "diet_focus": "Maintain Mediterranean diet. Intermittent fasting option (12-14 hour window). Focus on anti-inflammatory foods.",
            "exercise_plan": "Walking 45 min/day, 5 days/week. Strength training 3x/week. Yoga 2x/week. Add 1 day rest.",
            "sleep_target_hours": 8.0,
            "stress_management": "Continue all practices. Add gratitude journaling. Review progress.",
            "key_milestones": "First month complete. Comprehensive biomarker check. Medication review with doctor.",
            "progress_notes": ""
        },
        {
            "week_number": 5,
            "week_start_date": (start_date + timedelta(weeks=4)).strftime("%Y-%m-%d"),
            "medication_dose": "If > 1mg: Reduce by 0.25mg OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <125/80, Blood Sugar: 80-100 (fasting), Weight: -2kg, Sleep: 7-8 hours",
            "diet_focus": "Continue established patterns. Add more plant-based proteins. Reduce red meat to 1x/week.",
            "exercise_plan": "Walking 45-50 min/day, 5 days/week. Strength training 3x/week. Yoga 3x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Advanced meditation techniques, breathing exercises, maintain routine",
            "key_milestones": "Increased exercise capacity, improved mood stability",
            "progress_notes": ""
        },
        {
            "week_number": 6,
            "week_start_date": (start_date + timedelta(weeks=5)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <125/80, Blood Sugar: 80-100 (fasting), Weight: -2.5kg, Sleep: 7-8 hours",
            "diet_focus": "Focus on blood sugar stability. Low glycemic index foods. Regular meal timing.",
            "exercise_plan": "Walking 50 min/day, 5 days/week. Strength training 3x/week. Yoga 3x/week. Add swimming/cycling 1x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Continue all practices. Add mindfulness-based stress reduction (MBSR) techniques.",
            "key_milestones": "Stable blood sugar patterns, improved cardiovascular fitness",
            "progress_notes": ""
        },
        {
            "week_number": 7,
            "week_start_date": (start_date + timedelta(weeks=6)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -3kg, Sleep: 7-8 hours",
            "diet_focus": "Optimize nutrient density. Add more leafy greens, berries, nuts. Maintain protein intake.",
            "exercise_plan": "Walking 50-60 min/day, 5 days/week. Strength training 3x/week. Yoga 3x/week. Swimming/cycling 1x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Advanced stress management, maintain social support network",
            "key_milestones": "Improved biomarkers, medication reduction progress",
            "progress_notes": ""
        },
        {
            "week_number": 8,
            "week_start_date": (start_date + timedelta(weeks=7)).strftime("%Y-%m-%d"),
            "medication_dose": "Continue reduction OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -3.5kg, Sleep: 7-8 hours, Full lipid panel",
            "diet_focus": "Maintain all established patterns. Review and optimize based on biomarker results.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 3x/week. Yoga 3x/week. Swimming/cycling 1x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Comprehensive review of stress management strategies. Adjust as needed.",
            "key_milestones": "2-month milestone. Comprehensive health assessment. Medication review.",
            "progress_notes": ""
        },
        {
            "week_number": 9,
            "week_start_date": (start_date + timedelta(weeks=8)).strftime("%Y-%m-%d"),
            "medication_dose": "If > 1mg: Reduce to 1.5mg OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -4kg, Sleep: 7-8 hours",
            "diet_focus": "Continue optimization. Add more variety. Focus on sustainable habits.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 1x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Focus on consistency.",
            "key_milestones": "Approaching 1mg target, improved overall health",
            "progress_notes": ""
        },
        {
            "week_number": 10,
            "week_start_date": (start_date + timedelta(weeks=9)).strftime("%Y-%m-%d"),
            "medication_dose": "If > 1mg: Reduce to 1.25mg OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -4.5kg, Sleep: 7-8 hours",
            "diet_focus": "Maintain established patterns. Fine-tune based on individual response.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Continue all practices. Evaluate effectiveness.",
            "key_milestones": "Close to medication goal, stable biomarkers",
            "progress_notes": ""
        },
        {
            "week_number": 11,
            "week_start_date": (start_date + timedelta(weeks=10)).strftime("%Y-%m-%d"),
            "medication_dose": "If > 1mg: Reduce to 1mg OR Maintain 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -5kg, Sleep: 7-8 hours",
            "diet_focus": "Maintain optimal nutrition. Focus on long-term sustainability.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Focus on mental health.",
            "key_milestones": "REACH 1MG TARGET! Monitor closely for stability.",
            "progress_notes": ""
        },
        {
            "week_number": 12,
            "week_start_date": (start_date + timedelta(weeks=11)).strftime("%Y-%m-%d"),
            "medication_dose": "MAINTAIN 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: -5kg, Sleep: 7-8 hours, Comprehensive panel",
            "diet_focus": "Maintain all healthy patterns. Ensure nutritional adequacy.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Review and adjust as needed.",
            "key_milestones": "3-month milestone. Maintain 1mg for 2 weeks. Comprehensive assessment.",
            "progress_notes": ""
        },
        {
            "week_number": 13,
            "week_start_date": (start_date + timedelta(weeks=12)).strftime("%Y-%m-%d"),
            "medication_dose": "MAINTAIN 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: Maintain, Sleep: 7-8 hours",
            "diet_focus": "Continue maintenance phase. Focus on consistency.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Build resilience.",
            "key_milestones": "Stable on 1mg, normal biomarkers maintained",
            "progress_notes": ""
        },
        {
            "week_number": 14,
            "week_start_date": (start_date + timedelta(weeks=13)).strftime("%Y-%m-%d"),
            "medication_dose": "MAINTAIN 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: Maintain, Sleep: 7-8 hours",
            "diet_focus": "Maintain optimal nutrition. Continue healthy habits.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Long-term sustainability focus.",
            "key_milestones": "Consistent maintenance, improved quality of life",
            "progress_notes": ""
        },
        {
            "week_number": 15,
            "week_start_date": (start_date + timedelta(weeks=14)).strftime("%Y-%m-%d"),
            "medication_dose": "MAINTAIN 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: Maintain, Sleep: 7-8 hours",
            "diet_focus": "Maintain all patterns. Ensure variety and enjoyment.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Review progress.",
            "key_milestones": "Approaching 4-month milestone, stable maintenance",
            "progress_notes": ""
        },
        {
            "week_number": 16,
            "week_start_date": (start_date + timedelta(weeks=15)).strftime("%Y-%m-%d"),
            "medication_dose": "MAINTAIN 1mg",
            "medication_timing": "Night (9-10 PM)",
            "target_biomarkers": "BP: <120/80, Blood Sugar: 80-100 (fasting), Weight: Maintain, Sleep: 7-8 hours, Full comprehensive panel",
            "diet_focus": "Maintain optimal nutrition. Long-term lifestyle integration.",
            "exercise_plan": "Walking 60 min/day, 5 days/week. Strength training 4x/week. Yoga 3x/week. Swimming/cycling 2x/week.",
            "sleep_target_hours": 8.0,
            "stress_management": "Maintain all practices. Celebrate achievements.",
            "key_milestones": "GOAL ACHIEVED! 1mg Risperidone at night only. All biomarkers normal. Comprehensive final assessment.",
            "progress_notes": ""
        }
    ]
    
    # Insert into database
    with database.get_db() as conn:
        cursor = conn.cursor()
        # Clear existing plan
        cursor.execute('DELETE FROM health_goals')
        
        for week_plan in plan:
            cursor.execute('''
                INSERT INTO health_goals 
                (week_number, week_start_date, medication_dose, medication_timing, 
                 target_biomarkers, diet_focus, exercise_plan, sleep_target_hours, 
                 stress_management, key_milestones, progress_notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                week_plan['week_number'],
                week_plan['week_start_date'],
                week_plan['medication_dose'],
                week_plan['medication_timing'],
                week_plan['target_biomarkers'],
                week_plan['diet_focus'],
                week_plan['exercise_plan'],
                week_plan['sleep_target_hours'],
                week_plan['stress_management'],
                week_plan['key_milestones'],
                week_plan['progress_notes'],
                'pending'
            ))
        
        conn.commit()
        print(f"Created 16-week health plan starting from {start_date.strftime('%Y-%m-%d')}")

if __name__ == '__main__':
    create_health_plan()

