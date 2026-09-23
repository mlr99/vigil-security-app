from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/events")
def events():
    return render_template("events.html", events=[])

if __name__ == "__main__":
    app.run(debug=True)