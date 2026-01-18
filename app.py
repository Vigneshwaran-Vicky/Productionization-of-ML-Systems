import pandas as pd
import pickle
from flask import Flask, request, jsonify

# ================= LOAD MODELS =================
scaler_model = pickle.load(open('model/scaling.pkl', 'rb'))
rf_model = pickle.load(open('model/rf_model.pkl', 'rb'))

# ================= PREDICTION FUNCTION =================
def predict_price(input_data, model, scaler):
    df_input = pd.DataFrame([input_data])

    # 🔑 Reorder columns to match training
    df_input = df_input[scaler.feature_names_in_]

    X = scaler.transform(df_input)
    prediction = model.predict(X)
    return prediction[0]

# ================= FLASK APP =================
app = Flask(__name__)

# ================= HOME PAGE =================
@app.route('/', methods=['GET'])
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flight Price Prediction</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">

<style>
body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #667eea, #764ba2);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
}

.card {
    background: #ffffff;
    padding: 35px;
    max-width: 900px;
    width: 100%;
    border-radius: 18px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.15);
}

h1 {
    text-align: center;
    margin-bottom: 30px;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}

label {
    font-size: 14px;
    font-weight: 500;
}

select, input {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 14px;
}

select:focus, input:focus {
    outline: none;
    border-color: #667eea;
}

button {
    width: 100%;
    padding: 15px;
    margin-top: 30px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.25);
}

#result {
    margin-top: 25px;
    text-align: center;
    font-size: 22px;
    font-weight: 600;
    color: #667eea;
}
</style>
</head>

<body>

<div class="card">
<h1>✈ Flight Price Prediction</h1>

<form id="predictForm">
<div class="form-grid">

<div>
<label>Boarding City</label>
<select name="from">
<option>Aracaju</option>
<option>Brasilia</option>
<option>Campo_Grande</option>
<option>Florianopolis</option>
<option>Natal</option>
<option>Recife</option>
<option>Rio_de_Janeiro</option>
<option>Salvador</option>
<option>Sao_Paulo</option>
</select>
</div>

<div>
<label>Destination City</label>
<select name="Destination">
<option>Aracaju</option>
<option>Brasilia</option>
<option>Campo_Grande</option>
<option>Florianopolis</option>
<option>Natal</option>
<option>Recife</option>
<option>Rio_de_Janeiro</option>
<option>Salvador</option>
<option>Sao_Paulo</option>
</select>
</div>

<div>
<label>Flight Class</label>
<select name="flightType">
<option value="economic">Economic</option>
<option value="premium">Premium</option>
<option value="firstClass">First Class</option>
</select>
</div>

<div>
<label>Agency</label>
<select name="agency">
<option>FlyingDrops</option>
<option>Rainbow</option>
<option>CloudFy</option>
</select>
</div>

<div>
<label>Day</label>
<input type="number" name="day" min="1" max="31" value="5">
</div>

<div>
<label>Week No</label>
<input type="number" name="week_no" min="1" max="53" value="7">
</div>

<div>
<label>Week Day</label>
<input type="number" name="week_day" min="1" max="7" value="5">
</div>

</div>

<button type="submit">Predict Price</button>
</form>

<div id="result"></div>
</div>

<script>
document.getElementById("predictForm").addEventListener("submit", async function(e){
    e.preventDefault();
    const formData = new FormData(this);

    const response = await fetch("/predict", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    document.getElementById("result").innerHTML =
        "Estimated Flight Price: ₹ " + data.prediction;
});
</script>

</body>
</html>
"""

# ================= PREDICTION API =================
@app.route('/predict', methods=['POST'])
def predict():
    boarding = "from_" + request.form.get('from')
    destination = "destination_" + request.form.get('Destination')
    flight_class = "flightType_" + request.form.get('flightType')
    agency = "agency_" + request.form.get('agency')

    day = int(request.form.get('day'))
    week_no = int(request.form.get('week_no'))
    week_day = int(request.form.get('week_day'))

    boarding_city_list = [
        'from_Florianopolis (SC)','from_Sao_Paulo (SP)','from_Salvador (BH)',
        'from_Brasilia (DF)','from_Rio_de_Janeiro (RJ)','from_Campo_Grande (MS)',
        'from_Aracaju (SE)','from_Natal (RN)','from_Recife (PE)'
    ]

    destination_city_list = [
        'destination_Florianopolis (SC)','destination_Sao_Paulo (SP)','destination_Salvador (BH)',
        'destination_Brasilia (DF)','destination_Rio_de_Janeiro (RJ)','destination_Campo_Grande (MS)',
        'destination_Aracaju (SE)','destination_Natal (RN)','destination_Recife (PE)'
    ]

    class_list = ['flightType_economic','flightType_firstClass','flightType_premium']
    agency_list = ['agency_Rainbow','agency_CloudFy','agency_FlyingDrops']

    travel_dict = {}

    for c in boarding_city_list:
        travel_dict[c] = 1 if c[:-5] == boarding else 0

    for c in destination_city_list:
        travel_dict[c] = 1 if c[:-5] == destination else 0

    for c in class_list:
        travel_dict[c] = 1 if c == flight_class else 0

    for a in agency_list:
        travel_dict[a] = 1 if a == agency else 0

    travel_dict['day'] = day
    travel_dict['week_no'] = week_no
    travel_dict['week_day'] = week_day

    prediction = round(predict_price(travel_dict, rf_model, scaler_model), 2)

    return jsonify({'prediction': prediction})

# ================= RUN APP =================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
