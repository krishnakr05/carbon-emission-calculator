# Carbon Emission Calculator

A web application to calculate your carbon footprint based on daily activities like travel, electricity, and gas usage. Users can register, log in, track their emissions over time, and view visual graphs of their carbon footprint.

---

## Features

- User registration and login system.
- Input daily activities: car, bus, flight, electricity, gas.
- Calculate total CO₂ emissions based on activity data.
- Recommendations to reduce carbon footprint.
- View activity history with a graph showing emissions over time.
- REST API endpoint to calculate emissions programmatically.

---

## Technologies Used

- **Frontend:** HTML, CSS, Bootstrap, Chart.js  
- **Backend:** Python, Flask, Flask-Login, Flask-Bcrypt  
- **Database:** SQLite with SQLAlchemy ORM  
- **Others:** JSON for emission factors  

---

## Usage

- Register: Create an account using your email and password.
- Login: Log in to access the calculator.
- Calculate Emissions: Enter your daily activities and click "Calculate".
- View History: Click "History" in the navbar to see all previous entries and a graph of emissions over time.
- Logout: Click "Logout" in the navbar.

## API
- Endpoint: /api/calculate
- Method: POST
