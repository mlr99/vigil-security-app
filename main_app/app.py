from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Your database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/vigil_db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

@app.route("/")
def index():
    # This serves as the mandatory "goal/purpose" or about page
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/events")
def events():
    return render_template("events.html", events=[])

if __name__ == "__main__":
    app.run(debug=True)