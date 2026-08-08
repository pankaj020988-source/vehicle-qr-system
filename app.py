import streamlit as st
import pandas as pd
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
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
    # --- PUBLIC SCANNER VIEW (WITH BRANDING & CONTACT) ---
    qr_id = query_params["qr"]
    df = pd.read_csv(DATA_FILE)
    user_data = df[df["QR_ID"] == qr_id]
    
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
        
        # Footer Business Promotion Card with Direct Phone Number
        st.markdown("""
        <div style="background-color:#f0f2f6; padding:18px; border-radius:12px; text-align:center; border: 1px solid #dcdfe6;">
            <h3 style="color:#1e3d59; margin-bottom:5px;">🏪 बालाजी सायबर पॉईंट (Balaji Cyber Point)</h3>
            <p style="margin:5px 0; font-size: 15px;">ऑनलाइन अर्ज, पॅन कार्ड, आधार अपडेट, डिजिटल प्रिंटिंग आणि स्मार्ट QR सेवा!</p>
            <p style="color:#d9534f; font-weight:bold; margin-top:8px;">असाच स्मार्ट व्हेइकल QR कोड मिळवण्यासाठी आजच संपर्क करा!</p>
            <hr style="margin: 10px 0;">
            <p style="font-size: 16px; margin-bottom: 8px;"><b>📞 संपर्कासाठी कॉल करा / WhatsApp करा:</b> <a href="tel:8007365051" style="color:#007bff; font-weight:bold;">8007365051</a></p>
            <a href="https://wa.me/918007365051?text=Hello%20Balaji%20Cyber%20Point,%20mala%20Vehicle%20QR%20Sticker%20pahije." target="_blank" style="background-color:#25D366; color:white; padding:8px 16px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">💬 Order Your Vehicle QR Code</a>
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

        # FORM CHYA BAHER QR Code Professional Image Design
        if 'latest_qr' in st.session_state:
            latest = st.session_state['latest_qr']
            qr_link = f"{BASE_URL}/?qr={latest['qr_id']}"
            
            # Base QR Code Creation
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_link)
            qr.make(fit=True)
            qr_raw = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # Add Header & Footer Banner to Image for Professional Look
            width, height = qr_raw.size
            new_height = height + 100
            canvas = Image.new('RGB', (width, new_height), 'white')
            
            draw = ImageDraw.Draw(canvas)
            # Paste QR Code in Center
            canvas.paste(qr_raw, (0, 45))
            
            # Draw Header and Footer Text
            draw.text((width//2, 12), "PARK SMART - VEHICLE QR", fill="black", anchor="mm")
            draw.text((width//2, 30), f"NO: {latest['v_num']}", fill="red", anchor="mm")
            draw.text((width//2, new_height - 35), "SCAN TO CONTACT OWNER", fill="black", anchor="mm")
            draw.text((width//2, new_height - 15), "Balaji Cyber Point (8007365051)", fill="blue", anchor="mm")
            
            buf = BytesIO()
            canvas.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.divider()
            st.subheader(f"✨ Professional QR Sticker Image for {latest['v_num']}")
            st.image(byte_im, width=260)
            
            st.download_button(
                label="📥 Download Professional QR Sticker Image",
                data=byte_im,
                file_name=f"{latest['qr_id']}_{latest['v_num']}_sticker.png",
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
