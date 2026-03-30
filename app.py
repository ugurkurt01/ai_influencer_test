import streamlit as st
import requests
import json
import time

# --- GÜVENLİK VE AYARLAR ---
try:
    RUNPOD_API_KEY = st.secrets["RUNPOD_API_KEY"]
    ENDPOINT_ID = st.secrets["ENDPOINT_ID"]
    ACCESS_PASSWORD = st.secrets["ACCESS_PASSWORD"]
except:
    st.error("Lütfen Streamlit Cloud panelinden 'Secrets' ayarlarını yapın!")
    st.stop()

st.set_page_config(page_title="Selin AI Control", page_icon="💃")

# --- GİRİŞ KONTROLÜ ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Selin AI Erişim")
    pwd = st.text_input("Giriş Şifresi:", type="password")
    if st.button("Giriş Yap"):
        if pwd == ACCESS_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()

# --- ANA PANEL ---
st.title("💃 Selin AI Kontrol Paneli")
user_prompt = st.text_area("Selin ne yapsın?", placeholder="Örn: Selin_woman walking in a flower garden, smiling...")

if st.button("Görseli Oluştur ✨"):
    if not user_prompt:
        st.warning("Lütfen bir komut girin!")
    else:
        with st.spinner("Selin hazırlanıyor... Bu işlem 1 dakika sürebilir."):
            try:
                # 1. JSON Workflow'u oku
                with open("workflow_api.json", "r") as f:
                    workflow = json.load(f)
                
                # 2. Prompt'u JSON içine yerleştir
                # NOT: JSON dosyanızdaki CLIPTextEncode ID'sini kontrol edin (Genelde '6' dır)
                prompt_node_found = False
                for node_id, node_info in workflow.items():
                    if node_info.get("class_type") == "CLIPTextEncode":
                        node_info["inputs"]["text"] = f"score_9, score_8_up, {user_prompt}"
                        prompt_node_found = True
                        break
                
                if not prompt_node_found:
                    st.error("JSON içinde 'CLIPTextEncode' düğümü bulunamadı!")
                    st.stop()

                # 3. RunPod API'ye Gönder
                url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
                headers = {
                    "Authorization": f"Bearer {RUNPOD_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {"input": {"workflow": workflow}}

                response = requests.post(url, json=payload, headers=headers, timeout=120)
                result = response.json()

                # 4. Yanıtı İşle
                if result.get("status") == "COMPLETED":
                    # RunPod ComfyUI API genellikle çıktıları bir URL veya base64 olarak döner
                    # Template'inize göre output yapısı değişebilir
                    output_data = result.get("output", {})
                    
                    if "message" in output_data: # Çoğu hazır template bu formatı kullanır
                        image_url = output_data["message"]
                        st.image(image_url, caption="İşte Selin!", use_container_width=True)
                        
                        # İndirme Butonu
                        img_res = requests.get(image_url)
                        st.download_button("Görseli Kaydet", img_res.content, "selin_output.png", "image/png")
                    else:
                        st.write("Görsel üretildi ama format farklı. Yanıt:", output_data)
                else:
                    st.error(f"Üretim başarısız: {result.get('status')} - {result}")
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
