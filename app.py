import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Vehicle QR System", page_icon="🚗", layout="centered")

DATA_FILE = "sales_data.csv"

# Load or initialize sales data
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["QR_ID", "Owner_Name", "Phone_Number", "Vehicle_Number", "Sale_Date", "Price"])
    df.to_csv(DATA_FILE, index=False)

# Query parameters check (for QR scanning)
query_params = st.query_params

if "qr" in query_params:
    # --- PUBLIC SCANNER VIEW ---
    qr_id = query_params["qr"]
    df = pd.read_csv(DATA_FILE)
    user_data = df[df["QR_ID"] == qr_id]
    
    st.title("🚗 Park Smart - Vehicle Contact")
    
    if not user_data.empty:
        owner_name = user_data.iloc[0]["Owner_Name"]
        phone = str(user_data.iloc[0]["Phone_Number"])
        v_num = user_data.iloc[0]["Vehicle_Number"]
        
        st.warning(f"⚠️ Vehicle No: **{v_num}** is obstructing your way?")
        st.info("Please contact the owner below to move the vehicle safely.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📞 Call Owner", f"tel:{phone}", use_container_width=True)
        with col2:
            st.link_button("💬 WhatsApp Owner", f"https://wa.me/91{phone}?text=Hello,%20your%20vehicle%20{v_num}%20is%20causing%20an%20obstruction.", use_container_width=True)
    else:
        st.error("Invalid QR Code or Unregistered Vehicle.")

else:
    # --- ADMIN DASHBOARD VIEW ---
    st.title("📊 Vehicle QR Sales Dashboard")
    
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":  # Tumhi tumcha password badlu shakta
        st.sidebar.success("Logged In!")
        
        st.header("➕ Add New Sale")
        with st.form("add_sale_form"):
            qr_id = st.text_input("QR Code ID (Ex: QR-101)")
            owner_name = st.text_input("Customer Name")
            phone = st.text_input("Mobile Number (10 Digits)")
            v_num = st.text_input("Vehicle Number (Ex: MH06AB1234)")
            sale_date = st.date_input("Sale Date")
            price = st.number_input("Selling Price (₹)", value=149)
            
            submit = st.form_submit_button("Save Entry")
            
            if submit:
                if qr_id and phone and v_num:
                    df = pd.read_csv(DATA_FILE)
                    new_data = pd.DataFrame([[qr_id, owner_name, phone, v_num, str(sale_date), price]], 
                                           columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=False)
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"Successfully added {qr_id} for {v_num}!")
                else:
                    st.error("Please fill required fields!")
        
        st.divider()
        st.header("📈 Sales Records")
        df_display = pd.read_csv(DATA_FILE)
        st.dataframe(df_display, use_container_width=True)
        
        st.download_button(
            label="📥 Download Excel/CSV Data",
            data=df_display.to_csv(index=False).encode('utf-8'),
            file_name='vehicle_qr_sales.csv',
            mime='text/csv',
        )
    else:
        st.info("👈 Enter Admin Password in sidebar to access sales portal.")
