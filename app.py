from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_pymongo import PyMongo
import os
import pickle
from gps import get_lat_lon, reverse_geocode, check_mangrove
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mangrove_db"
mongo = PyMongo(app)

with open("env_model.pkl", "rb") as f:
    env_model = pickle.load(f)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        name = request.form.get("Name")
        email = request.form.get("Email")
        mongo.db.users.insert_one({"name": name, "email": email})
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='GET':
        name=request.form.get("Name")
        email=request.form.get("Email")
        if mongo.db.find["name","email"]==True:
             print("You succesfully logged in!\n")
             return redirect(url_for("dashboard"))


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    mongo.db.users.insert_one({"name": name, "email": email, "points": 0})
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    user = mongo.db.users.find_one({"email": email})
    if user:
        return redirect(url_for("dashboard"))
    return "Invalid login", 401

@app.route("/dashboard")
def dashboard():
    reports = list(mongo.db.users.find())
    return render_template("dashboard.html", reports=reports)

@app.route("/complain", methods=["GET", "POST"])
def complain():
    if request.method == "POST":
        photo = request.files.get("photo")
        desc = request.form.get("desc")
        user_email = request.form.get("email")

        filename = None
        coords = None
        location = "Unknown"

        if photo:
            filename = photo.filename
            file_path = os.path.join(os.getcwd(), filename)
            photo.save(file_path)

            coords = get_lat_lon(file_path)
            if coords:
                lat, lon = coords
                location = reverse_geocode(lat, lon)
            else:
                location = "No GPS data"

        try:
            prediction = env_model.predict([[10, 20, 1]])[0]  
        except:
            prediction = "Unknown"

        mongo.db.complaints.insert_one({
            "user_email": user_email,
            "photo": filename,
            "description": desc,
            "coords": coords,
            "location": location,
            "ai_validation": str(prediction)
        })

        mongo.db.users.update_one(
            {"email": user_email},
            {"$inc": {"points": 10}}
        )

        return "Complaint submitted successfully!"
    return render_template("complain.html")

@app.route("/leaderboard")
def leaderboard():
    users = list(mongo.db.users.find().sort("points", -1))
    return render_template("leaderboard.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)
