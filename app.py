import streamlit as st
import pandas as pd
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

st.set_page_config(page_title="Park Smart - Balaji Cyber Point", page_icon="🚗", layout="centered")

# Updated Google Apps Script Deployment URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxkp-5emmvmM204ha8fUpvi7X6vdqk3Ig9D5BQoKW6D-z140si484P-8jui3iBozHxq/exec"
BASE_URL = "https://vehicle-qr-system-fdotykfal7vtgdekhavrhm.streamlit.app"

def load_data():
    try:
        response = requests.get(WEB_APP_URL, timeout=10)
        data = response.json()
        if isinstance(data, list) and len(data) > 1:
            headers = [str(c) for c in data[0]]
            df = pd.DataFrame(data[1:], columns=headers)
            return df
        elif isinstance(data, list) and len(data) == 1:
            headers = [str(c) for c in data[0]]
            return pd.DataFrame(columns=headers)
        else:
            return pd.DataFrame(columns=["QR_ID", "Owner_Name", "Phone_Number", "Vehicle_Number", "Sale_Date", "Price"])
    except Exception as e:
        return pd.DataFrame(columns=["QR_ID", "Owner_Name", "Phone_Number", "Vehicle_Number", "Sale_Date", "Price"])

# Query parameters check (for QR scanning)
query_params = st.query_params

if "qr" in query_params:
    # --- PUBLIC SCANNER VIEW ---
    qr_id = query_params["qr"]
    df = load_data()
    user_data = df[df["QR_ID"] == qr_id] if "QR_ID" in df.columns else pd.DataFrame()
    
    st.caption("Powered by **Balaji Cyber Point** 🌐")
    st.title("🚗 Park Smart - गाडी मालकाशी संपर्क")
    
    if not user_data.empty:
        owner_name = user_data.iloc[0]["Owner_Name"]
        phone = str(user_data.iloc[0]["Phone_Number"]).strip()
        v_num = user_data.iloc[0]["Vehicle_Number"]
        
        st.warning(f"⚠️ **गाडी क्रमांक: {v_num}** अडथळा ठरत आहे का?")
        st.info("गाडी मालकाला तातडीने कळवण्यासाठी खालील बटणावर क्लिक करा.")
        
        marathi_msg = f"नमस्कार,%20तुमची%20गाडी%20*{v_num}*%20अडथळा%20ठरत%20आहे.%20कृपया%20ती%20लवकरात%20लवकर%20बाजूला%20करावी."
        wa_url = f"https://wa.me/91{phone}?text={marathi_msg}"
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📞 डायरेक्ट कॉल करा", f"tel:{phone}", use_container_width=True)
        with col2:
            st.link_button("💬 WhatsApp वर मेसेज करा", wa_url, use_container_width=True, type="primary")
            
        st.divider()
        
        st.markdown("""
        <div style="border: 2px solid #25D366; padding:18px; border-radius:12px; text-align:center; margin-top:10px;">
            <h3 style="margin-bottom:8px;">🏪 बालाजी सायबर पॉईंट (Balaji Cyber Point)</h3>
            <p style="margin:5px 0; font-size: 15px;">ऑनलाइन अर्ज, पॅन कार्ड, आधार अपडेट, डिजिटल प्रिंटिंग आणि स्मार्ट QR सेवा!</p>
            <p style="color:#FF4B4B; font-weight:bold; margin-top:8px;">असाच स्मार्ट व्हेइकल QR कोड मिळवण्यासाठी आजच संपर्क करा!</p>
            <hr style="margin: 12px 0;">
            <p style="font-size: 16px; margin-bottom: 10px;"><b>📞 संपर्कासाठी कॉल करा / WhatsApp करा:</b> <br><a href="tel:8806789013" style="font-weight:bold; font-size:18px; text-decoration:none;">8806789013</a></p>
            <a href="https://wa.me/918806789013?text=Hello%20Balaji%20Cyber%20Point,%20mala%20Vehicle%20QR%20Sticker%20pahije." target="_blank" style="background-color:#25D366; color:white; padding:10px 18px; text-decoration:none; border-radius:8px; font-weight:bold; display:inline-block; margin-top:5px;">💬 Order Your Vehicle QR Code</a>
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
            
            submit = st.form_submit_button("Save Entry to Google Sheet")
            
        if submit:
            if qr_id and phone and v_num:
                payload = {
                    "qr_id": qr_id,
                    "owner_name": owner_name,
                    "phone": phone,
                    "v_num": v_num,
                    "sale_date": str(sale_date),
                    "price": price
                }
                
                res = requests.post(WEB_APP_URL, json=payload, timeout=10)
                
                if res.status_code == 200:
                    st.session_state['latest_qr'] = {
                        'qr_id': qr_id,
                        'v_num': v_num
                    }
                    st.success(f"Entry saved directly to Google Sheet for {v_num}!")
                    st.rerun()
                else:
                    st.error("Failed to connect with Google Sheet script!")
            else:
                st.error("Please fill required fields!")

        # ADVANCED GRAPHICAL STICKER GENERATOR
        if 'latest_qr' in st.session_state:
            latest = st.session_state['latest_qr']
            qr_link = f"{BASE_URL}/?qr={latest['qr_id']}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=12,
                border=1,
            )
            qr.add_data(qr_link)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#1E293B", back_color="white").convert('RGB')
            
            width = 500
            height = 630
            
            canvas = Image.new('RGB', (width, height), '#FFFFFF')
            draw = ImageDraw.Draw(canvas)
            
            draw.rectangle([(0, 0), (width, 90)], fill="#0F172A")
            draw.text((width//2, 32), "PARK SMART", fill="#F8FAFC", anchor="mm", font_size=32)
            draw.text((width//2, 68), "EMERGENCY VEHICLE CONTACT", fill="#38BDF8", anchor="mm", font_size=18)
            
            draw.rectangle([(40, 110), (width-40, 160)], fill="#FEF08A", outline="#EAB308", width=2)
            draw.text((width//2, 135), f"VEHICLE NO: {latest['v_num']}", fill="#854D0E", anchor="mm", font_size=22)
            
            qr_scaled = qr_img.resize((320, 320))
            canvas.paste(qr_scaled, ((width - 320)//2, 180))
            
            draw.rectangle([((width - 320)//2 - 10, 170), ((width + 320)//2 + 10, 510)], outline="#CBD5E1", width=3)
            
            draw.text((width//2, 528), "SCAN TO CONTACT VEHICLE OWNER", fill="#0F172A", anchor="mm", font_size=18)
            
            draw.rectangle([(0, 555), (width, height)], fill="#1E40AF")
            draw.text((width//2, 575), "TO ORDER THIS VEHICLE QR STICKER", fill="#FFFFFF", anchor="mm", font_size=16)
            draw.text((width//2, 600), "Call / WhatsApp: 8806789013 (Balaji Cyber Point)", fill="#93C5FD", anchor="mm", font_size=14)
            
            buf = BytesIO()
            canvas.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.divider()
            st.subheader(f"✨ Branded Vehicle Sticker for {latest['v_num']}")
            st.image(byte_im, width=320)
            
            st.download_button(
                label="📥 Download High-Res Branded Sticker (Ready to Print)",
                data=byte_im,
                file_name=f"{latest['v_num']}_Smart_Sticker.png",
                mime="image/png"
            )

        st.divider()
        st.header("📈 Sales Records (Live Google Sheet Data)")
        df_display = load_data()
        st.dataframe(df_display, use_container_width=True)
        
    else:
        st.info("👈 Enter Admin Password in sidebar to access sales portal.")
