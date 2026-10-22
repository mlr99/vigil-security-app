Vigil — First-Time Developer Setup Guide
Follow these steps when pulling the project to get your local environment and MySQL database running.

1. Prerequisites
Ensure you have the following installed on your machine:

Python 3.10+

Git

MySQL Server 8.0+ & MySQL Workbench

2. Quick-Start Setup
Step 1: Open Directory & Virtual Environment
Navigate into capstone-capstone-project-group-1/main_app and activate your virtual environment:

On Windows (PowerShell):

PowerShell
cd capstone-capstone-project-group-1/main_app
python -m venv venv
.\venv\Scripts\Activate.ps1
On Mac / Linux (Terminal):

Bash

cd capstone-capstone-project-group-1/main_app
python3 -m venv venv
source venv/bin/activate
Step 2: Install Dependencies
Install all required Python packages:

Bash

pip install -r requirements.txt
Step 3: Prevent Accidental Commits (.gitignore)
Run these commands once to ensure your machine automatically ignores .env and Python cache files so they never get pushed to GitHub:

On Windows (PowerShell):

PowerShell
Add-Content -Path .gitignore -Value "`n.env`n__pycache__/`n*.pyc"

On Mac / Linux (Terminal):

Bash

printf "\n.env\n__pycache__/\n*.pyc\n" >> .gitignore

Step 4: Create Database in MySQL
Open MySQL Workbench or your terminal MySQL client and create an empty database named vigil_db:

SQL
CREATE DATABASE vigil_db;
Step 5: Configure Environment Variables (.env)
Create a file named .env inside the main_app/ folder. Replace YOUR_MYSQL_PASSWORD with your local MySQL root password.

Windows (PowerShell command):

PowerShell
Set-Content -Path .env -Value "DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/vigil_db"
Mac / Linux (Terminal command):

Bash
echo "DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/vigil_db" > .env
Note: .env is git-ignored so each machine retains its local credentials. Do not force-commit .env to GitHub.

Step 6: Initialize Database & Seed Admin
Run the Alembic migrations to generate the database tables, then seed the default admin account:

Bash
flask db upgrade
python seed_admin.py
Default Account Credentials:

Username: admin

Password: password

Step 7: Launch the Application
Start the local development server:

Bash
python app.py
Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser and log in with admin / password.

3. Git Workflow Guidelines
To ensure Mac and Windows environments synchronize without conflicts:

Bash
git pull origin main
git add -A
git commit -m "Describe your changes clearly"
git push origin main
Never commit .env or __pycache__/ folders.

Always run git pull origin main before starting new work.