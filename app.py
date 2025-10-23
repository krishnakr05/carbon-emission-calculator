from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load emission factors
with open("emission_factors.json") as f:
    EMISSION_FACTORS = json.load(f)


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.form.to_dict()
    total_emission = calculate_emission(data)
    return render_template("index.html", total=total_emission, data=data)


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.json
    total_emission = calculate_emission(data)
    return jsonify({
        "input": data,
        "total_emission_kgCO2": total_emission
    })


if __name__ == "__main__":
    app.run(debug=True)
