import requests
from kanka_storage import KankaZReportManager

class KankaNetworkEngine:
    """Modüler Eklenti: Arka plan LLM isteklerini ve API yönetimini üstlenir."""
    def __init__(self, uygulama_ref):
        self.app = uygulama_ref  # UI güncellemeleri için ana arayüz referansı

    def _arka_plan_ollama_istegi(self, msg, gizli_mi):
        # Oda türüne göre dinamik geçmiş hazırlığı
        gecmis = self.app.hafiza.model_icin_gecmis_hazirla(self.app.aktif_proje)
        
        # Eğer günlük sohbetteysek uçucu hafızayı da ekle
        if self.app.aktif_proje == "Günlük_Sohbet":
            gecmis.extend(self.app.gecici_sohbet_hafizasi[-10:])
            
        gecmis.append({"role": "user", "content": msg})
        
        url = "http://localhost:11434/api/chat"
        payload = {"model": "qwen2.5-coder:7b", "messages": gecmis, "stream": False}
        try:
            req = requests.post(url, json=payload, timeout=None)

            if req.status_code == 200:
                res = req.json()
                cevap = res['message']['content']
                self.app.ekrana_yaz(f"🤖 Kanka AI: {cevap}\n")
                
                if self.app.aktif_proje == "Günlük_Sohbet":
                    # Günlük sohbeti sadece RAM'de tut, diske yazma
                    if not gizli_mi:
                        self.app.gecici_sohbet_hafizasi.append({"role": "user", "content": msg})
                        self.app.gecici_sohbet_hafizasi.append({"role": "assistant", "content": cevap})
                else:
                    # Gerçek projedeysek normal logu yaz
                    if not gizli_mi: 
                        self.app.hafiza.gunluk_kaydet(self.app.aktif_proje, msg, cevap)
                    else: 
                        self.app.hafiza.gunluk_kaydet(self.app.aktif_proje, "[Dosya eklendi]", "[Analiz edildi]")
                    
                    # Z-Raporu tetikleyicisi kontrolü
                    if KankaZReportManager.z_raporu_guncelle(self.app.aktif_proje, msg, cevap):
                        self.app.ekrana_yaz("✨ [SİSTEM]: Kritik karar tespit edildi ve Z-Raporu Arşivine kaydedildi! 📋")
            else:
                self.app.ekrana_yaz("⚠️ Ollama motoru açık mı kanka?")
        except Exception as e:
            self.app.ekrana_yaz(f"\n⚠️ Yerel modele bağlanılamadı kanka! (Detay: {e})\n")
