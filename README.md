# Collaborative Health Tracker

A web-based collaborative health tracking application that allows family members to track health files, add comments, generate reports, and interact with an AI assistant.

## Features

- 📊 **Health Data Tracking**: View health metrics in tabular format (weight, blood pressure, blood sugar, sleep, exercise)
- 🍽️ **Diet Plan Management**: Track meals, calories, and macronutrients
- 💪 **Exercise Plan Tracking**: Monitor workout routines and exercise schedules
- ✅ **To Do List**: Manage health and fitness related tasks with priorities and due dates
- 🤖 **AI Query Assistant**: Specialized AI assistant for Health, Food, Lifestyle, and Fitness queries
- 📈 **Health Reports**: Generate comprehensive AI-powered health reports
- ⌚ **Wearables Integration**: Support for Fitbit, Apple Watch, Garmin, and other health devices
- 💰 **Monthly Budget Tracker**: Set monthly budgets and track expenses
- 📝 **Expense Planner**: Add and manage expenses with categories including capital equipment
- 🔐 **Authentication System**: Secure CRUD operations - only authenticated users can create, update, or delete data
- 🗄️ **SQLite Database**: All data stored in a robust SQLite database
- 👁️ **Public Read Access**: Family members can view all data without authentication

## Deployment Instructions

### 🏆 Best 24/7 Always-On Options

**For FREE never-sleeping hosting:** Use **Koyeb** (see `DEPLOYMENT_24x7.md`)

**For paid reliable hosting:** Use **Railway.app** ($5/month) or **Render.com** ($7/month)

See `DEPLOYMENT_24x7.md` for detailed 24/7 deployment guide.

### Option 1: Deploy on Render.com (Recommended for Paid)

1. **Create a Render Account**
   - Go to https://render.com
   - Sign up for a free account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use Render's Git integration)

3. **Configure the Service**
   - **Name**: health-tracker (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free tier is sufficient

4. **Add Environment Variables** (if needed)
   - The OpenAI API key is hardcoded in the application

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - Your app will be available at: `https://health-tracker.onrender.com` (or your chosen name)

### Option 2: Deploy on Railway.app

1. **Create a Railway Account**
   - Go to https://railway.app
   - Sign up for a free account

2. **Create a New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" or "Empty Project"

3. **Configure the Project**
   - Add a new service → "GitHub Repo"
   - Select your repository
   - Railway will auto-detect Python

4. **Set Start Command**
   - In Settings → Deploy, set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

5. **Deploy**
   - Railway will automatically deploy
   - Your app will be available at: `https://your-project-name.up.railway.app`

### Option 3: Deploy on Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**
   ```bash
   fly auth login
   ```

3. **Initialize Fly App**
   ```bash
   fly launch
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

### Option 4: Deploy on Heroku

1. **Install Heroku CLI**
   - Download from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open your browser and go to: http://localhost:5000

## Project Structure

```
.
├── app.py                 # Flask backend application
├── database.py           # Database initialization and management
├── file_parser.py        # Excel file parsing and database population
├── templates/
│   └── index.html        # Frontend HTML/CSS/JavaScript
├── Content/              # Health files directory
├── health_tracker.db     # SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
├── Procfile             # Deployment configuration
├── runtime.txt          # Python version
├── WEARABLES_INTEGRATION.md  # Wearable devices integration guide
└── README.md            # This file
```

## API Endpoints

### File Management
- `GET /` - Main application page
- `GET /api/files` - Get list of all files
- `GET /api/files/<filename>` - Download a file

### Comments
- `GET /api/comments` - Get all comments - Public
- `POST /api/comments` - Add a new comment - **Requires Auth**
- `DELETE /api/comments/<comment_id>` - Delete a comment - **Requires Auth**

### AI Assistant
- `POST /api/ai/query` - Query the AI assistant
- `POST /api/reports/generate` - Generate a health report

### Authentication
- `POST /api/auth/login` - Login (requires username and password)
- `POST /api/auth/logout` - Logout
- `GET /api/auth/check` - Check authentication status

### Budget & Expenses
- `GET /api/budget` - Get budget for a month (query param: month=YYYY-MM) - Public
- `POST /api/budget` - Set or update monthly budget - **Requires Auth**
- `GET /api/expenses` - Get all expenses (query param: month=YYYY-MM) - Public
- `POST /api/expenses` - Add a new expense - **Requires Auth**
- `DELETE /api/expenses/<expense_id>` - Delete an expense - **Requires Auth**
- `GET /api/budget/summary` - Get budget summary with statistics - Public

## Authentication

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

**Important:** Change the default password after first login by modifying the database or updating the `database.py` file.

### Access Control:
- **Public (No Login Required):**
  - View files
  - View comments
  - View budgets and expenses
  - Use AI assistant
  - Generate reports

- **Authenticated Users Only (CRUD Operations):**
  - Add/edit/delete comments
  - Set/modify budgets
  - Add/delete expenses

## Notes

- The OpenAI API key is hardcoded in `app.py` for convenience
- All data is stored in `health_tracker.db` SQLite database
- Database is automatically initialized on first run
- All files in the `Content/` directory are accessible
- The application uses GPT-3.5-turbo for AI responses
- Budget tracking supports monthly budgets with expense categorization
- Capital equipment expenses can be marked separately for tracking
- Sessions expire after 24 hours of inactivity

## Support

For issues or questions, please check the deployment platform's documentation or contact support.

