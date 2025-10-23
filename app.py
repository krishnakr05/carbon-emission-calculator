from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

# ------------------ App Setup ------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------ Models ------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    activities = db.relationship('Activity', backref='user', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car = db.Column(db.Float, default=0)
    bus = db.Column(db.Float, default=0)
    flight = db.Column(db.Float, default=0)
    electricity = db.Column(db.Float, default=0)
    gas = db.Column(db.Float, default=0)
    total_emission = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------ Login Loader ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ Database Creation ------------------
with app.app_context():
    db.create_all()

# ------------------ Helper Functions ------------------
EMISSION_FACTORS = {
    "car": 0.21,
    "bus": 0.10,
    "flight": 0.25,
    "electricity": 0.85,
    "gas": 2.3
}

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

# ------------------ Routes ------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Failed. Check email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
@login_required
def home():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.date.desc()).all()
    
    if request.method == 'POST':
        data = request.form
        total_emission = calculate_emission(data)
        emissionData = [
            float(data.get('car',0))*EMISSION_FACTORS['car'],
            float(data.get('bus',0))*EMISSION_FACTORS['bus'],
            float(data.get('flight',0))*EMISSION_FACTORS['flight'],
            float(data.get('electricity',0))*EMISSION_FACTORS['electricity'],
            float(data.get('gas',0))*EMISSION_FACTORS['gas']
        ]
        activity = Activity(
            user_id=current_user.id,
            car=float(data.get('car',0)),
            bus=float(data.get('bus',0)),
            flight=float(data.get('flight',0)),
            electricity=float(data.get('electricity',0)),
            gas=float(data.get('gas',0)),
            total_emission=total_emission
        )
        db.session.add(activity)
        db.session.commit()
        return render_template('index.html', total=total_emission, recommendation=get_recommendation(total_emission), data=data, activities=activities, emissionData=emissionData)
    
    return render_template('index.html', activities=activities)

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

@app.route('/history')
@login_required
def history():
    # Fetch all activities for the current user, ordered by date
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.date.asc()).all()

    # Prepare data for the chart
    dates = [act.date.strftime('%Y-%m-%d') for act in activities]
    emissions = [act.total_emission for act in activities]

    return render_template('history.html', activities=activities, dates=dates, emissions=emissions)

# ------------------ Run App ------------------
if __name__ == "__main__":
    app.run(debug=True)
