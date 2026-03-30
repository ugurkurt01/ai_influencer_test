import streamlit as st
import requests
import json

# --- GÜVENLİK VE AYARLAR ---
# API Key ve Endpoint ID'yi Streamlit'in kendi "Secrets" panelinden çekeceğiz
try:
    RUNPOD_API_KEY = st.secrets["RUNPOD_API_KEY"]
    ENDPOINT_ID = st.secrets["ENDPOINT_ID"]
    ACCESS_PASSWORD = st.secrets["ACCESS_PASSWORD"] # Paneli kilitlemek için
except:
    st.error("Lütfen Secrets ayarlarını yapın!")
    st.stop()

st.set_page_config(page_title="ai-influencer_test", page_icon="💃")

# --- BASİT GİRİŞ EKRANI ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    pwd = st.text_input("Giriş Şifresi:", type="password")
    if st.button("Giriş Yap"):
        if pwd == ACCESS_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()

# --- ANA PANEL ---
st.title("💃 AI Influencer Mobil Kontrol")
prompt = st.text_area("YKomut:", placeholder="Selin_woman drinking coffee in Paris...")

if st.button("Görseli Oluştur"):
    with st.spinner("Model hazırlanıyor..."):
        # Burada önceki JSON workflow okuma ve requests kodların yer alacak
        # (Workflow dosyasını da GitHub'a yüklemeyi unutma!)
        st.success("İstek gönderildi! (Test Modu)")
