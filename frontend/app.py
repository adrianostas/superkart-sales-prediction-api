import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend service container
BACKEND_URL = "http://backend:7860"

# Set up page layout and title
st.set_page_config(
    page_title="Superkart Sales Predictor",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Superkart Product Sales Prediction")

# Interface split into two main tabs
tab1, tab2 = st.tabs(["Single Product Prediction", "Batch CSV Prediction"])

# ==========================================
# TAB 1: Single Product Prediction
# ==========================================
with tab1:
    st.subheader("Enter Product and Store Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Product Attributes**")
        product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.5, step=0.1)
        product_allocated_area = st.number_input("Product Allocated Area Ratio", min_value=0.00, max_value=1.00, value=0.05, step=0.005, format="%.4f")
        product_mrp = st.number_input("Product MRP ($)", min_value=0.0, max_value=500.0, value=140.0, step=1.0)
        product_sugar_content = st.selectbox("Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_type = st.selectbox(
            "Product Category", 
            [
                "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods", 
                "Fruits and Vegetables", "Hard Drinks", "Health and Hygiene", "Household", 
                "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods"
            ]
        )

    with col2:
        st.markdown("**Store Attributes**")
        store_id = st.selectbox("Store ID", ["OUT001", "OUT002", "OUT003", "OUT004", "OUT005"])
        store_est_year = st.number_input("Store Establishment Year", min_value=1980, max_value=2025, value=1999, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_city_type = st.selectbox("Store Location City Tier", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Food Mart", "Supermarket Type1", "Supermarket Type2", "Supermarket Type3"])

    # Build input payload
    payload = {
        "Product_Weight": product_weight,
        "Product_Allocated_Area": product_allocated_area,
        "Product_MRP": product_mrp,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Type": product_type,
        "Store_Id": store_id,
        "Store_Establishment_Year": store_est_year,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city_type,
        "Store_Type": store_type
    }

    if st.button("Predict Store Sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/sales", json=payload)
            if response.status_code == 200:
                predicted_sales = response.json().get("Predicted_Product_Store_Sales", 0.0)
                st.metric(label="Predicted Product Sales", value=f"${predicted_sales:,.2f}")
            else:
                st.error(f"Error from API (Status {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to Flask backend at {BACKEND_URL}. Ensure container is running.")

# ==========================================
# TAB 2: Batch CSV Prediction
# ==========================================
with tab2:
    st.subheader("Upload CSV File for Batch Prediction")
    uploaded_file = st.file_uploader("Upload a CSV file containing store and product features", type=["csv"])

    if uploaded_file is not None:
        if st.button("Generate Batch Predictions", type="primary"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{BACKEND_URL}/v1/sales/batch", files=files)
                
                if response.status_code == 200:
                    predictions_dict = response.json()
                    df_results = pd.DataFrame(list(predictions_dict.items()), columns=["Product_Id", "Predicted_Sales ($)"])
                    
                    st.success("Batch predictions completed successfully!")
                    st.dataframe(df_results, use_container_width=True)
                    
                    # Enable CSV output download
                    csv_bytes = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Predictions as CSV",
                        data=csv_bytes,
                        file_name="superkart_batch_predictions.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Batch processing error: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to Flask backend at {BACKEND_URL}. Details: {e}")
