import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO

st.set_page_config(page_title="Park Smart - Balaji Cyber Point", page_icon="🚗", layout="centered")

DATA_FILE = "sales_data.csv"
BASE_URL = "https://vehicle-qr-system-fdotykfal7vtgdekhavrhm.streamlit.app"

# Load or initialize sales data
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["QR_ID", "Owner_Name", "Phone_Number", "Vehicle_Number", "Sale_Date", "Price"])
    df.to_csv(DATA_FILE, index=False)

# Query parameters check (for QR scanning)
query_params = st.query_params

if "qr" in query_params:
    # --- PUBLIC SCANNER VIEW (WITH BRANDING) ---
    qr_id = query_params["qr"]
    df = pd.read_csv(DATA_FILE)
    user_data = df[df["QR_ID"] == qr_id]
    
    # Header Branding
    st.caption("Powered by **Balaji Cyber Point** 🌐")
    st.title("🚗 Park Smart - गाडी मालकाशी संपर्क")
    
    if not user_data.empty:
        owner_name = user_data.iloc[0]["Owner_Name"]
        phone = str(user_data.iloc[0]["Phone_Number"]).strip()
        v_num = user_data.iloc[0]["Vehicle_Number"]
        
        st.warning(f"⚠️ **गाडी क्रमांक: {v_num}** अडथळा ठरत आहे का?")
        st.info("गाडी मालकाला तातडीने कळवण्यासाठी खालील बटणावर क्लिक करा.")
        
        # Marathi WhatsApp pre-filled text
        marathi_msg = f"नमस्कार,%20तुमची%20गाडी%20*{v_num}*%20अडथळा%20ठरत%20आहे.%20कृपया%20ती%20लवकरात%20लवकर%20बाजूला%20करावी."
        wa_url = f"https://wa.me/91{phone}?text={marathi_msg}"
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📞 डायरेक्ट कॉल करा", f"tel:{phone}", use_container_width=True)
        with col2:
            st.link_button("💬 WhatsApp वर मेसेज करा", wa_url, use_container_width=True, type="primary")
            
        st.divider()
        
        # Footer Business Promotion Card
        st.markdown("""
        <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; text-align:center;">
            <h4>🏪 बालाजी सायबर पॉईंट (Balaji Cyber Point)</h4>
            <p style="margin:5px 0;">ऑनलाइन अर्ज, पॅन कार्ड, आधार अपडेट, डिजिटल प्रिंटिंग आणि स्मार्ट QR सेवा!</p>
            <p><b>स्मार्ट व्हेइकल QR कोड मिळवण्यासाठी आजच संपर्क करा!</b></p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("हा QR कोड नोंदणीकृत नाही किंवा चुकीचा आहे.")

else:
    # --- ADMIN DASHBOARD VIEW ---
    st.title("📊 Vehicle QR Sales Dashboard")
    st.caption("BALAJI CYBER POINT - ADMIN PORTAL")
    
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":
        st.sidebar.success("Logged In!")
        
        st.header("➕ Add New Sale & Generate QR")
        
        # Form sathi Data processing
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
                
                # Session State madhe QR details store kara
                st.session_state['latest_qr'] = {
                    'qr_id': qr_id,
                    'v_num': v_num
                }
                st.success(f"Entry saved for {v_num}!")
            else:
                st.error("Please fill required fields!")

        # FORM CHYA BAHER QR Code dakhva ani Download Button dya
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
