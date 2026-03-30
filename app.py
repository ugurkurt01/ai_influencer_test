# ... (önceki kodlar aynı)

if st.button("Görseli Oluştur ✨"):
    if not user_prompt:
        st.warning("Lütfen bir komut girin!")
    else:
        with st.spinner("Selin için GPU hazırlanıyor ve modeller yükleniyor... (Bu işlem ilk seferde 1-2 dk sürebilir)"):
            try:
                # 1. JSON Hazırlama (Aynı)
                with open("workflow_api.json", "r") as f:
                    workflow = json.load(f)
                
                for node_id, node_info in workflow.items():
                    if node_info.get("class_type") == "CLIPTextEncode":
                        node_info["inputs"]["text"] = f"score_9, score_8_up, {user_prompt}"
                        break

                # 2. İşi Başlat (/run kullanıyoruz, /runsync değil)
                run_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
                headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}", "Content-Type": "application/json"}
                payload = {"input": {"workflow": workflow}}

                run_response = requests.post(run_url, json=payload, headers=headers)
                job_data = run_response.json()
                job_id = job_data.get("id")

                if not job_id:
                    st.error(f"İş başlatılamadı: {job_data}")
                    st.stop()

                # 3. Sorgulama Döngüsü (Polling)
                status_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"
                
                while True:
                    status_response = requests.get(status_url, headers=headers)
                    status_data = status_response.json()
                    current_status = status_data.get("status")

                    if current_status == "COMPLETED":
                        output = status_data.get("output", {})
                        if "message" in output:
                            image_url = output["message"]
                            st.image(image_url, caption="İşte Selin!", use_container_width=True)
                            st.download_button("Görseli Kaydet", requests.get(image_url).content, "selin.png", "image/png")
                        else:
                            st.write("Sonuç:", output)
                        break
                    
                    elif current_status == "FAILED":
                        st.error(f"Üretim hatası: {status_data.get('error')}")
                        break
                    
                    else:
                        # IN_QUEUE veya IN_PROGRESS durumunda bekle
                        time.sleep(5) # 5 saniye bekle ve tekrar sor
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
