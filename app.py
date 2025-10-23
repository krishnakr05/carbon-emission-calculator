from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load emission factors
with open("emission_factors.json") as f:
    EMISSION_FACTORS = json.load(f)

# Database model for user activity
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car = db.Column(db.Float, default=0)
    bus = db.Column(db.Float, default=0)
    flight = db.Column(db.Float, default=0)
    electricity = db.Column(db.Float, default=0)
    gas = db.Column(db.Float, default=0)
    total_emission = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Helper function
def calculate_emission(data):
    total = 0.0
    for category, value in data.items():
        try:
            value = float(value)
            factor = EMISSION_FACTORS.get(category, 0)
            total += value * factor
        except ValueError:
            continue
    
    return round(total, 2)



def get_recommendation(total_emission):
    if total_emission > 100:
        return "Consider using public transport, reducing flights, and conserving electricity."
    elif total_emission > 50:
        return "Good, but you can still reduce energy consumption and travel emissions."
    else:
        return "Excellent! Keep up your eco-friendly habits."

# Routes
@app.route("/")
def home():
    activities = Activity.query.order_by(Activity.date.desc()).limit(5).all()
    return render_template("index.html", activities=activities)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.form.to_dict()
    total_emission = calculate_emission(data)
    recommendation = get_recommendation(total_emission)

    # Save to database
    activity = Activity(
        car=data.get('car',0),
        bus=data.get('bus',0),
        flight=data.get('flight',0),
        electricity=data.get('electricity',0),
        gas=data.get('gas',0),
        total_emission=total_emission
    )
    db.session.add(activity)
    db.session.commit()

    activities = Activity.query.order_by(Activity.date.desc()).limit(5).all()
    # inside /calculate route after calculating total_emission and saving activity
    emissionData = [
        float(data.get('car', 0)) * 0.21,
        float(data.get('bus', 0)) * 0.10,
        float(data.get('flight', 0)) * 0.25,
        float(data.get('electricity', 0)) * 0.85,
        float(data.get('gas', 0)) * 2.3
    ]

    return render_template(
        "index.html",
        total=total_emission,
        recommendation=recommendation,
        data=data,
        activities=activities,
        emissionData=emissionData
    )


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.json
    total_emission = calculate_emission(data)
    recommendation = get_recommendation(total_emission)
    return jsonify({
        "input": data,
        "total_emission_kgCO2": total_emission,
        "recommendation": recommendation
    })

if __name__ == "__main__":
    app.run(debug=True)
