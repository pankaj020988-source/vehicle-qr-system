import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO

st.set_page_config(page_title="Vehicle QR System", page_icon="🚗", layout="centered")

DATA_FILE = "sales_data.csv"
BASE_URL = "https://vehicle-qr-system-fdotykfal7vtgdekhavrhm.streamlit.app"

# Load or initialize sales data
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["QR_ID", "Owner_Name", "Phone_Number", "Vehicle_Number", "Sale_Date", "Price"])
    df.to_csv(DATA_FILE, index=False)

# Query parameters check (for QR scanning)
query_params = st.query_params

if "qr" in query_params:
    # --- PUBLIC SCANNER VIEW (PRIVACY ENHANCED) ---
    qr_id = query_params["qr"]
    df = pd.read_csv(DATA_FILE)
    user_data = df[df["QR_ID"] == qr_id]
    
    st.title("🚗 Park Smart - Vehicle Contact")
    
    if not user_data.empty:
        owner_name = user_data.iloc[0]["Owner_Name"]
        phone = str(user_data.iloc[0]["Phone_Number"]).strip()
        v_num = user_data.iloc[0]["Vehicle_Number"]
        
        # Hide phone number (Ex: 80******51)
        masked_phone = phone[:2] + "******" + phone[-2:]
        
        st.warning(f"⚠️ Is Vehicle **{v_num}** causing an obstruction?")
        st.info("Click the button below to send an urgent notification directly to the owner via WhatsApp.")
        
        # Privacy badge
        st.caption(f"🔒 Registered Owner Contact: **{masked_phone}** (Protected)")
        
        # Pre-filled WhatsApp message URL
        msg = f"Hello,%20your%20vehicle%20*{v_num}*%20is%20causing%20an%20obstruction.%20Please%20move%20it%20as%20soon%20as%20possible."
        wa_url = f"https://wa.me/91{phone}?text={msg}"
        
        st.divider()
        st.link_button("💬 Alert Owner on WhatsApp", wa_url, use_container_width=True, type="primary")
        
        st.caption(" Note: Your phone number is kept private on this screen for safety.")
    else:
        st.error("Invalid QR Code or Unregistered Vehicle.")

else:
    # --- ADMIN DASHBOARD VIEW ---
    st.title("📊 Vehicle QR Sales Dashboard")
    
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":
        st.sidebar.success("Logged In!")
        
        st.header("➕ Add New Sale & Generate QR")
        
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
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                
                st.session_state['latest_qr'] = {
                    'qr_id': qr_id,
                    'v_num': v_num
                }
                st.success(f"Entry saved for {v_num}!")
            else:
                st.error("Please fill required fields!")

        # Display generated QR Code outside the form
        if 'latest_qr' in st.session_state:
            latest = st.session_state['latest_qr']
            qr_link = f"{BASE_URL}/?qr={latest['qr_id']}"
            qr_img = qrcode.make(qr_link)
            
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.divider()
            st.subheader(f"✨ Generated QR Code for {latest['qr_id']} ({latest['v_num']})")
            st.image(byte_im, width=220)
            
            st.download_button(
                label="📥 Download QR Code Image",
                data=byte_im,
                file_name=f"{latest['qr_id']}_{latest['v_num']}.png",
                mime="image/png"
            )

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
