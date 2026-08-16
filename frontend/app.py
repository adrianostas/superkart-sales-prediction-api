import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Superkart Sales Predictor", layout="wide")

BACKEND_URL = "http://127.0.0.1:7860"

st.title("🛒 Superkart Product Sales Prediction")

tab1, tab2 = st.tabs(["Single Product Prediction", "Batch CSV Prediction"])

with tab1:
    st.subheader("Enter Product and Store Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Product Attributes")
        weight = st.number_input("Product Weight", min_value=0.0, value=12.5, step=0.1)
        alloc_area = st.number_input("Product Allocated Area Ratio", min_value=0.0, max_value=1.0, value=0.05, step=0.001, format="%.4f")
        mrp = st.number_input("Product MRP ($)", min_value=0.0, value=140.0, step=1.0)
        sugar = st.selectbox("Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        category = st.selectbox("Product Category", [
            'Baking Goods', 'Breads', 'Breakfast', 'Canned', 'Dairy', 'Frozen Foods', 
            'Fruits and Vegetables', 'Hard Drinks', 'Health and Hygiene', 'Household', 
            'Meat', 'Others', 'Seafood', 'Snack Foods', 'Soft Drinks', 'Starchy Foods'
        ])

    with col2:
        st.write("#### Store Attributes")
        store_id = st.selectbox("Store ID", ["OUT001", "OUT002", "OUT003", "OUT004"])
        establishment_year = st.number_input("Store Establishment Year", min_value=1980, max_value=2025, value=1999, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        city_tier = st.selectbox("Store Location City Tier", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Food Mart", "Departmental Store", "Supermarket Type1", "Supermarket Type2"])

    if st.button("Predict Store Sales", type="primary"):
        payload = {
            "Product_Weight": weight,
            "Product_Allocated_Area": alloc_area,
            "Product_MRP": mrp,
            "Product_Sugar_Content": sugar,
            "Product_Type": category,
            "Store_Id": store_id,
            "Store_Establishment_Year": establishment_year,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_tier,
            "Store_Type": store_type
        }
        
        try:
            res = requests.post(f"{BACKEND_URL}/v1/sales", json=payload)
            if res.status_code == 200:
                pred = res.json().get("Predicted_Product_Store_Sales")
                st.success(f"**Predicted Sales:** ${pred:,.2f}")
            else:
                st.error(f"Error from API (Status {res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Could not connect to Flask backend at {BACKEND_URL}. Ensure container is running.")
