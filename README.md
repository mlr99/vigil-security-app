# Vigil
 
Setup guide for running Vigil locally with MySQL.
 
## Requirements
 
- Python 3.10+
- Git
- MySQL Server 8.0+ (MySQL Workbench is optional but handy)
## Setup
 
All commands run from the `main_app` folder unless noted.
 
### 1. Create and activate a virtual environment
 
**Windows (PowerShell)**
 
```powershell
cd capstone-capstone-project-group-1/main_app
python -m venv venv
.\venv\Scripts\Activate.ps1
```
 
> If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.
 
**Mac / Linux**
 
```bash
cd capstone-capstone-project-group-1/main_app
python3 -m venv venv
source venv/bin/activate
```
 
### 2. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 3. Create the database
 
In MySQL Workbench or the `mysql` command line:
 
```sql
CREATE DATABASE vigil_db;
```
 
### 4. Add your database connection
 
Create a file named `.env` in `main_app/` with this line, replacing `YOUR_PASSWORD` with your MySQL root password:
 
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/vigil_db
```
 
`.env` is in `.gitignore`, so your password stays on your machine. Never commit it.
 
### 5. Build the tables and create the admin account
 
```bash
flask db upgrade
python seed_admin.py
```
 
### 6. Run the app
 
```bash
python app.py
```
 
Open http://127.0.0.1:5000 and log in with:
 
- **Username:** `admin`
- **Password:** `password`
## Updating after a pull
 
When someone changes the database models, run this after pulling:
 
```bash
flask db upgrade
```
 
If you change a model yourself, create a migration and commit it with your code:
 
```bash
flask db migrate -m "Short description of the change"
flask db upgrade
```
 
## Git workflow
 
```bash
git pull origin main          # always pull before starting work
git add -A
git commit -m "Describe your changes clearly"
git push origin main
```
 
Never commit `.env`, `venv/`, or `__pycache__/`.

## Testing Segment ##

To run tests make sure Pytest is installed (It should be installed if you ran the "pip install -r requirements.txt" from earlier in the readme document)
If you are currently in the directory ...project-group-1\main_app enter the command "cd .." in order to go back to the main project directory to run the tests.
and then in the terminal enter "pytest tests/"
this should automatically run through the test fodler and run all tests
 