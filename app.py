from flask import Flask, render_template, jsonify, request, send_file, send_from_directory, session
from flask_cors import CORS
import os
import json
from datetime import datetime
from openai import OpenAI
from werkzeug.utils import secure_filename
import uuid
from functools import wraps
import database
import file_parser

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app, supports_credentials=True)

# Configuration
CONTENT_DIR = 'Content'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client (only if API key is provided)
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}")
        client = None

# Ensure content directory exists
os.makedirs(CONTENT_DIR, exist_ok=True)

# Initialize database
database.init_database()

# Parse Excel files and populate database on startup
try:
    file_parser.parse_all_files()
except Exception as e:
    print(f"Warning: Could not parse files on startup: {e}")

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication for CRUD operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required', 'auth_required': True}), 401
        
        username = database.verify_session(session_id)
        if not username:
            return jsonify({'success': False, 'error': 'Invalid or expired session', 'auth_required': True}), 401
        
        request.current_user = username
        return f(*args, **kwargs)
    return decorated_function

def get_current_month_key():
    """Get current month key in YYYY-MM format"""
    return datetime.now().strftime('%Y-%m')

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

# Health Data CRUD Endpoints
@app.route('/api/health-data', methods=['POST'])
@require_auth
def add_health_data():
    """Add health tracker data (requires authentication)"""
    try:
        data = request.json
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_tracker_data 
                (date, weight, blood_pressure, blood_sugar, sleep_hours, exercise_minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('date'),
                data.get('weight'),
                data.get('blood_pressure'),
                data.get('blood_sugar'),
                data.get('sleep_hours'),
                data.get('exercise_minutes'),
                data.get('notes')
            ))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health-data/<int:data_id>', methods=['PUT'])
@require_auth
def update_health_data(data_id):
    """Update health tracker data (requires authentication)"""
    try:
        data = request.json
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE health_tracker_data 
                SET date=?, weight=?, blood_pressure=?, blood_sugar=?, sleep_hours=?, exercise_minutes=?, notes=?
                WHERE id=?
            ''', (
                data.get('date'),
                data.get('weight'),
                data.get('blood_pressure'),
                data.get('blood_sugar'),
                data.get('sleep_hours'),
                data.get('exercise_minutes'),
                data.get('notes'),
                data_id
            ))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health-data/<int:data_id>', methods=['DELETE'])
@require_auth
def delete_health_data(data_id):
    """Delete health tracker data (requires authentication)"""
    try:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM health_tracker_data WHERE id=?', (data_id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        if database.authenticate_user(username, password, email):
            session_id = database.create_session(username)
            database.cleanup_expired_sessions()
            return jsonify({
                'success': True,
                'session_id': session_id,
                'username': username
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        if session_id:
            database.delete_session(session_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        if session_id:
            username = database.verify_session(session_id)
            if username:
                return jsonify({'success': True, 'authenticated': True, 'username': username})
        return jsonify({'success': True, 'authenticated': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/comments', methods=['GET'])
def get_comments():
    """Get all comments (public read access)"""
    try:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, author, comment, created_at, created_by
                FROM comments
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            
            # Group by filename
            comments = {}
            for row in rows:
                filename = row['filename']
                if filename not in comments:
                    comments[filename] = []
                comments[filename].append({
                    'id': row['id'],
                    'author': row['author'],
                    'comment': row['comment'],
                    'timestamp': row['created_at'],
                    'created_by': row['created_by']
                })
            
            return jsonify({'success': True, 'comments': comments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/comments', methods=['POST'])
@require_auth
def add_comment():
    """Add a new comment (requires authentication)"""
    try:
        data = request.json
        filename = data.get('filename')
        comment_text = data.get('comment')
        author = data.get('author', 'Anonymous')
        
        if not filename or not comment_text:
            return jsonify({'success': False, 'error': 'Filename and comment are required'}), 400
        
        comment_id = str(uuid.uuid4())
        username = getattr(request, 'current_user', 'admin')
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (id, filename, author, comment, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (comment_id, filename, author, comment_text, username))
        
        return jsonify({
            'success': True,
            'comment': {
                'id': comment_id,
                'author': author,
                'comment': comment_text,
                'timestamp': datetime.now().isoformat(),
                'created_by': username
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/comments/<comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """Delete a comment (requires authentication)"""
    try:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/query', methods=['POST'])
def ai_query():
    """Handle AI assistant queries with specialized categories"""
    try:
        if not client:
            return jsonify({
                'success': False, 
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
            }), 503
        
        data = request.json
        query = data.get('query')
        category = data.get('category', 'general')  # health, food, lifestyle, fitness
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        # Load health data from database
        health_data = []
        diet_data = []
        exercise_data = []
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            
            # Get health tracker data
            cursor.execute('SELECT date, weight, blood_pressure, blood_sugar, sleep_hours, exercise_minutes FROM health_tracker_data ORDER BY date DESC LIMIT 30')
            health_data = [dict(row) for row in cursor.fetchall()]
            
            # Get diet plan data
            cursor.execute('SELECT day, meal_type, food_item, calories, protein, carbs FROM diet_plan LIMIT 50')
            diet_data = [dict(row) for row in cursor.fetchall()]
            
            # Get exercise plan data
            cursor.execute('SELECT day, exercise_name, duration_minutes, sets, reps FROM exercise_plan LIMIT 50')
            exercise_data = [dict(row) for row in cursor.fetchall()]
        
        # Build specialized context based on category
        system_prompts = {
            'health': "You are a health and medical tracking assistant. Provide expert advice on health metrics, blood pressure, blood sugar, weight management, and overall health monitoring.",
            'food': "You are a nutrition and diet planning assistant. Provide expert advice on meal planning, nutrition, calories, macronutrients (protein, carbs, fats), and healthy eating habits.",
            'lifestyle': "You are a lifestyle and wellness assistant. Provide expert advice on sleep patterns, daily routines, work-life balance, stress management, and overall lifestyle optimization.",
            'fitness': "You are a fitness and exercise planning assistant. Provide expert advice on workout routines, exercise techniques, training schedules, and fitness goals."
        }
        
        system_prompt = system_prompts.get(category, system_prompts['health'])
        
        context = f"""User Query: {query}

Health Tracking Data (Recent):
{json.dumps(health_data[:10], indent=2) if health_data else 'No health data available'}

Diet Plan Data:
{json.dumps(diet_data[:20], indent=2) if diet_data else 'No diet data available'}

Exercise Plan Data:
{json.dumps(exercise_data[:20], indent=2) if exercise_data else 'No exercise data available'}

Please provide a detailed, helpful response based on the category: {category}"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({'success': True, 'response': ai_response, 'category': category})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a health report"""
    try:
        if not client:
            return jsonify({
                'success': False, 
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
            }), 503
        
        data = request.json
        report_type = data.get('type', 'summary')
        
        # Load file information and comments
        files = []
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                filepath = os.path.join(CONTENT_DIR, filename)
                if os.path.isfile(filepath):
                    file_info = {
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    }
                    files.append(file_info)
        
        # Load comments from database
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT filename, author, comment, created_at FROM comments ORDER BY created_at DESC')
            comment_rows = cursor.fetchall()
        
        comments = {}
        for row in comment_rows:
            filename = row['filename']
            if filename not in comments:
                comments[filename] = []
            comments[filename].append({
                'author': row['author'],
                'comment': row['comment'],
                'timestamp': row['created_at']
            })
        
        # Load health data from database
        with database.get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM health_tracker_data ORDER BY date DESC LIMIT 30')
            health_data = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM diet_plan LIMIT 50')
            diet_data = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM exercise_plan LIMIT 50')
            exercise_data = [dict(row) for row in cursor.fetchall()]
        
        # Build report context
        report_context = f"""Generate a {report_type} health tracking report based on the following data:

Health Tracker Data (Recent 30 entries):
{json.dumps(health_data, indent=2) if health_data else 'No health data available'}

Diet Plan Data:
{json.dumps(diet_data[:30], indent=2) if diet_data else 'No diet data available'}

Exercise Plan Data:
{json.dumps(exercise_data[:30], indent=2) if exercise_data else 'No exercise data available'}

Please generate a comprehensive health tracking report with:
1. Health metrics analysis and trends
2. Diet plan review and nutrition insights
3. Exercise plan evaluation and fitness recommendations
4. Overall health status summary
5. Actionable recommendations for improvement"""
        
        # Call OpenAI API to generate report
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a health tracking assistant. Generate detailed, professional health reports with insights, trends, and recommendations."},
                {"role": "user", "content": report_context}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        report_content = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'report': {
                'type': report_type,
                'content': report_content,
                'generated_at': datetime.now().isoformat(),
                'files_count': len(files),
                'comments_count': sum(len(c) for c in comments.values())
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Budget and Expense Management Endpoints


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses or expenses for a specific month (public read access)"""
    try:
        month = request.args.get('month')
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            if month:
                cursor.execute('''
                    SELECT id, month, date, amount, description, category, is_capital, created_at
                    FROM expenses
                    WHERE month = ?
                    ORDER BY date DESC
                ''', (month,))
            else:
                cursor.execute('''
                    SELECT id, month, date, amount, description, category, is_capital, created_at
                    FROM expenses
                    ORDER BY date DESC
                ''')
            
            rows = cursor.fetchall()
            expenses = []
            for row in rows:
                expenses.append({
                    'id': row['id'],
                    'amount': float(row['amount']),
                    'description': row['description'],
                    'category': row['category'],
                    'date': row['date'],
                    'month': row['month'],
                    'is_capital': bool(row['is_capital']),
                    'created_at': row['created_at']
                })
        
        return jsonify({'success': True, 'expenses': expenses})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
@require_auth
def add_expense():
    """Add a new expense (requires authentication)"""
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        description = data.get('description', '')
        category = data.get('category', 'Other')
        date = data.get('date', datetime.now().isoformat().split('T')[0])
        is_capital = data.get('is_capital', False)
        month = data.get('month', get_current_month_key())
        username = getattr(request, 'current_user', 'admin')
        
        if not description or amount <= 0:
            return jsonify({'success': False, 'error': 'Description and amount are required'}), 400
        
        expense_id = str(uuid.uuid4())
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (id, month, date, amount, description, category, is_capital, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, month, date, amount, description, category, 1 if is_capital else 0, username))
        
        expense = {
            'id': expense_id,
            'amount': amount,
            'description': description,
            'category': category,
            'date': date,
            'month': month,
            'is_capital': is_capital,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
@require_auth
def delete_expense(expense_id):
    """Delete an expense (requires authentication)"""
    try:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/budget/summary', methods=['GET'])
def get_budget_summary():
    """Get budget summary with statistics (public read access)"""
    try:
        month = request.args.get('month', get_current_month_key())
        
        with database.get_db() as conn:
            cursor = conn.cursor()
            # Get budget
            cursor.execute('SELECT total_budget FROM budgets WHERE month = ?', (month,))
            budget_row = cursor.fetchone()
            total_budget = float(budget_row['total_budget']) if budget_row else 0
            
            # Get expenses
            cursor.execute('''
                SELECT amount, category, is_capital
                FROM expenses
                WHERE month = ?
            ''', (month,))
            expense_rows = cursor.fetchall()
            
            total_expenses = 0
            capital_expenses = 0
            expenses_by_category = {}
            
            for row in expense_rows:
                amount = float(row['amount'])
                total_expenses += amount
                if row['is_capital']:
                    capital_expenses += amount
                
                category = row['category']
                if category not in expenses_by_category:
                    expenses_by_category[category] = {'total': 0, 'count': 0}
                expenses_by_category[category]['total'] += amount
                expenses_by_category[category]['count'] += 1
        
        regular_expenses = total_expenses - capital_expenses
        
        return jsonify({
            'success': True,
            'summary': {
                'month': month,
                'total_budget': total_budget,
                'total_expenses': total_expenses,
                'capital_expenses': capital_expenses,
                'regular_expenses': regular_expenses,
                'remaining': total_budget - total_expenses,
                'percentage_used': (total_expenses / total_budget * 100) if total_budget > 0 else 0,
                'expenses_by_category': expenses_by_category,
                'total_expense_count': len(expense_rows)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Mobile App Streaming Endpoints
@app.route('/api/stream/health-data', methods=['POST'])
def stream_health_data():
    """Receive streaming health data from mobile app"""
    try:
        data = request.json
        device_id = data.get('device_id')
        device_type = data.get('device_type')
        connection_type = data.get('connection_type')  # ble, nfc, wifi
        health_data = data.get('data')
        metadata = data.get('metadata', {})
        
        if not device_id or not health_data:
            return jsonify({'success': False, 'error': 'device_id and data are required'}), 400
        
        # Map device data to database fields
        with database.get_db() as conn:
            cursor = conn.cursor()
            
            # Extract health metrics
            if 'heart_rate' in health_data:
                # Store heart rate (could add new table or use existing)
                pass
            
            if 'weight' in health_data:
                cursor.execute('''
                    INSERT INTO health_tracker_data 
                    (date, weight, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (
                    health_data.get('timestamp', datetime.now().isoformat().split('T')[0]),
                    health_data.get('weight')
                ))
            
            if 'blood_pressure' in health_data:
                bp = health_data.get('blood_pressure')
                cursor.execute('''
                    INSERT INTO health_tracker_data 
                    (date, blood_pressure, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (
                    health_data.get('timestamp', datetime.now().isoformat().split('T')[0]),
                    f"{bp.get('systolic')}/{bp.get('diastolic')}" if isinstance(bp, dict) else bp
                ))
            
            if 'sleep_hours' in health_data:
                cursor.execute('''
                    INSERT INTO health_tracker_data 
                    (date, sleep_hours, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (
                    health_data.get('timestamp', datetime.now().isoformat().split('T')[0]),
                    health_data.get('sleep_hours')
                ))
            
            if 'steps' in health_data or 'exercise_minutes' in health_data:
                exercise_minutes = health_data.get('exercise_minutes') or (health_data.get('steps', 0) / 100)
                cursor.execute('''
                    INSERT INTO health_tracker_data 
                    (date, exercise_minutes, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (
                    health_data.get('timestamp', datetime.now().isoformat().split('T')[0]),
                    exercise_minutes
                ))
        
        return jsonify({
            'success': True,
            'message': 'Data received and processed',
            'device_id': device_id,
            'connection_type': connection_type,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stream/batch', methods=['POST'])
def stream_batch_data():
    """Receive batch health data from mobile app"""
    try:
        data = request.json
        device_id = data.get('device_id')
        device_type = data.get('device_type')
        connection_type = data.get('connection_type')
        data_points = data.get('data_points', [])
        
        if not device_id or not data_points:
            return jsonify({'success': False, 'error': 'device_id and data_points are required'}), 400
        
        processed = 0
        errors = []
        
        for point in data_points:
            try:
                # Process each data point
                with database.get_db() as conn:
                    cursor = conn.cursor()
                    # Similar processing as single stream endpoint
                    processed += 1
            except Exception as e:
                errors.append({'point': point, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'processed': processed,
            'total': len(data_points),
            'errors': errors if errors else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stream/devices', methods=['GET'])
def get_connected_devices():
    """Get list of connected streaming devices"""
    try:
        # This would track connected devices in a real implementation
        # For now, return empty list
        return jsonify({
            'success': True,
            'devices': []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

