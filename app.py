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

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of all files in Content directory"""
    try:
        files = []
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                filepath = os.path.join(CONTENT_DIR, filename)
                if os.path.isfile(filepath):
                    file_info = {
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        'type': filename.split('.')[-1] if '.' in filename else 'unknown'
                    }
                    files.append(file_info)
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file from Content directory"""
    try:
        safe_filename = secure_filename(filename)
        return send_from_directory(CONTENT_DIR, safe_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        if database.authenticate_user(username, password):
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
    """Handle AI assistant queries"""
    try:
        if not client:
            return jsonify({
                'success': False, 
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
            }), 503
        
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        # Load file information and comments for context
        files = []
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                filepath = os.path.join(CONTENT_DIR, filename)
                if os.path.isfile(filepath):
                    files.append(filename)
        
        # Load comments from database
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT filename, author, comment FROM comments ORDER BY created_at DESC LIMIT 50')
            comment_rows = cursor.fetchall()
        
        comments = {}
        for row in comment_rows:
            filename = row['filename']
            if filename not in comments:
                comments[filename] = []
            comments[filename].append({
                'author': row['author'],
                'comment': row['comment']
            })
        
        # Build context for AI
        context = f"""You are a health tracking assistant. The user has the following files in their health tracker:
{', '.join(files)}

"""
        
        if comments:
            context += "Comments on files:\n"
            for filename, file_comments in comments.items():
                context += f"\n{filename}:\n"
                for comment in file_comments[-5:]:  # Last 5 comments per file
                    context += f"  - {comment['author']}: {comment['comment']}\n"
        
        context += f"\nUser query: {query}\n\nPlease provide a helpful response."
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful health tracking assistant. Provide clear, concise, and helpful responses about health tracking, diet plans, exercise routines, and medical information."},
                {"role": "user", "content": context}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({'success': True, 'response': ai_response})
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
        
        # Build report context
        report_context = f"""Generate a {report_type} health tracking report based on the following information:

Files tracked:
"""
        for file_info in files:
            report_context += f"- {file_info['name']} (Last modified: {file_info['modified']})\n"
        
        if comments:
            report_context += "\nComments and notes:\n"
            for filename, file_comments in comments.items():
                report_context += f"\n{filename}:\n"
                for comment in file_comments:
                    report_context += f"  - [{comment['timestamp']}] {comment['author']}: {comment['comment']}\n"
        
        report_context += "\nPlease generate a comprehensive health tracking report with insights, recommendations, and status summary."
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

