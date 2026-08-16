import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask application
app = Flask("Superkart Sales Predictor")

# Resolve model path relative to app.py location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "superkart_model.joblib")

# Load trained model
model = joblib.load(MODEL_PATH)

# Exact 15 encoded columns expected by the trained model
EXPECTED_COLUMNS = [
    'Product_Weight', 
    'Product_Allocated_Area', 
    'Product_MRP', 
    'Store_Establishment_Year', 
    'Store_Size', 
    'Store_Location_City_Type', 
    'Product_Type', 
    'Product_Sugar_Content_No Sugar', 
    'Product_Sugar_Content_Regular', 
    'Store_Id_OUT002', 
    'Store_Id_OUT003', 
    'Store_Id_OUT004', 
    'Store_Type_Food Mart', 
    'Store_Type_Supermarket Type1', 
    'Store_Type_Supermarket Type2'
]

def preprocess_input(df):
    """Preprocesses raw feature input into the 15 encoded features expected by the model."""
    df_proc = df.copy()

    size_map = {'Small': 0, 'Medium': 1, 'High': 2}
    city_map = {'Tier 3': 0, 'Tier 2': 1, 'Tier 1': 2}
    
    if 'Store_Size' in df_proc.columns:
        df_proc['Store_Size'] = df_proc['Store_Size'].map(size_map).fillna(1)
    if 'Store_Location_City_Type' in df_proc.columns:
        df_proc['Store_Location_City_Type'] = df_proc['Store_Location_City_Type'].map(city_map).fillna(0)

    prod_categories = [
        'Baking Goods', 'Breads', 'Breakfast', 'Canned', 'Dairy', 'Frozen Foods', 
        'Fruits and Vegetables', 'Hard Drinks', 'Health and Hygiene', 'Household', 
        'Meat', 'Others', 'Seafood', 'Snack Foods', 'Soft Drinks', 'Starchy Foods'
    ]
    prod_type_map = {cat: idx for idx, cat in enumerate(sorted(prod_categories))}
    if 'Product_Type' in df_proc.columns:
        df_proc['Product_Type'] = df_proc['Product_Type'].map(prod_type_map).fillna(-1)

    df_proc = pd.get_dummies(
        df_proc, 
        columns=['Product_Sugar_Content', 'Store_Id', 'Store_Type'], 
        drop_first=True, 
        errors='ignore'
    )

    df_proc = df_proc.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
    return df_proc


@app.get('/')
def home():
    """Welcome endpoint."""
    return "Welcome to the Superkart Sales Prediction API!"


@app.post('/v1/sales')
def predict_sales():
    """Endpoint for single product sales prediction from JSON payload."""
    data = request.get_json()
    input_df = pd.DataFrame([data])
    processed_df = preprocess_input(input_df)

    predicted_sales = float(model.predict(processed_df)[0])
    predicted_sales = round(predicted_sales, 2)

    return jsonify({'Predicted_Product_Store_Sales': predicted_sales})


@app.post('/v1/sales/batch')
def predict_sales_batch():
    """Endpoint for batch sales predictions via CSV file upload."""
    file = request.files['file']
    input_df = pd.read_csv(file)

    product_ids = input_df['Product_Id'].tolist() if 'Product_Id' in input_df.columns else [f"Item_{i}" for i in range(len(input_df))]

    processed_df = preprocess_input(input_df)
    predictions = model.predict(processed_df).tolist()
    predictions = [round(float(val), 2) for val in predictions]

    output_dict = dict(zip(product_ids, predictions))
    return jsonify(output_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
