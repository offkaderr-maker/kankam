import os
import json
from datetime import datetime, timedelta

ANA_DIZIN = os.path.dirname(os.path.abspath(__file__))
HAFIZA_KLASORU = os.path.join(ANA_DIZIN, "kanka_hafizasi")
if not os.path.exists(HAFIZA_KLASORU): 
    os.makedirs(HAFIZA_KLASORU)

class KankaZReportManager:
    """Modüler Eklenti: Projelerin kurumsal hafızasını ve Z-Raporlarını yönetir."""
    @staticmethod
    def z_raporu_guncelle(pr_adi, kullanici_mesaji, kanka_cevabi):
        if pr_adi == "Günlük_Sohbet":
            return False
            
        tetikleyiciler = ["z-raporu", "arşive ekle", "kritik karar", "karar", "not et", "unutma"]
        metin_norm = (kullanici_mesaji + " " + kanka_cevabi).lower()
        
        if any(kelime in metin_norm for kelime in tetikleyiciler):
            proje_klasor = os.path.join(HAFIZA_KLASORU, pr_adi)
            if not os.path.exists(proje_klasor): os.makedirs(proje_klasor)
            
            yol = os.path.join(proje_klasor, "z_report.md")
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            blok = f"\n### 📌 Kritik Karar & Hafıza ({tarih})\n"
            blok += f"**Kullanıcı Talebi:** {kullanici_mesaji}\n"
            cevab_ozet = "\n".join(kanka_cevabi.split("\n")[:8])
            blok += f"**Alınan Karar / Çözüm:**\n{cevab_ozet}\n"
            blok += f"{'-'*40}\n"
            
            with open(yol, "a", encoding="utf-8") as f:
                f.write(blok)
            return True
        return False

    @staticmethod
    def z_raporu_oku(pr_adi):
        if pr_adi == "Günlük_Sohbet":
            return ""
        yol = os.path.join(HAFIZA_KLASORU, pr_adi, "z_report.md")
        if os.path.exists(yol):
            with open(yol, "r", encoding="utf-8") as f:
                return f.read()
        return "Henüz bu proje için kritik bir karar alınmadı kanka."

class KankaMemoryManager:
    def __init__(self):
        self.kalici_bilgi_olustur()
        for i in range(1, 6): 
            self.kirli_hafizayi_temizle(f"Proje_{i}")
        
    def kalici_bilgi_olustur(self):
        yolu = os.path.join(HAFIZA_KLASORU, "kanka_kimdir.json")
        if not os.path.exists(yolu):
            veri = {
                "kullanici_adi": "Kanka", 
                "hedef": "Godot 4.x ile sıfırdan oyun geliştirmeyi, kas hafızası edinmeyi...", 
                "ogretmen_tarzi": "Salağa/cahile anlatır gibi sabırla öğretmek."
            }
            with open(yolu, "w", encoding="utf-8") as f: 
                json.dump(veri, f, ensure_ascii=False, indent=4)
            
    def gunluk_kaydet(self, pr_adi, msg, cevap):
        if pr_adi == "Günlük_Sohbet":
            return
            
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        veri = {"tarih": tarih, "kullanici": msg, "kanka": cevap}
        
        proje_klasor = os.path.join(HAFIZA_KLASORU, pr_adi)
        if not os.path.exists(proje_klasor): os.makedirs(proje_klasor)
        
        yol = os.path.join(proje_klasor, "chat_history.json")
        
        if os.path.exists(yol) and os.path.getsize(yol) > 0:
            with open(yol, "r", encoding="utf-8") as f: gecmis = json.load(f)
        else: 
            gecmis = []
        
        gecmis.append(veri)
        if len(gecmis) > 16: 
            gecmis = self.hafizayi_rafine_et(gecmis)
        with open(yol, "w", encoding="utf-8") as f: 
            json.dump(gecmis, f, ensure_ascii=False, indent=4)
        
    def hafizayi_rafine_et(self, gecmis):
        rafine = [{"tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kullanici": "[Sistem]: RAM hafiflet.", "kanka": "[Sistem]: Kararlar kilitlendi."}]
        rafine.extend(gecmis[-12:])
        return rafine
        
    def kirli_hafizayi_temizle(self, pr_adi):
        yol = os.path.join(HAFIZA_KLASORU, pr_adi, "chat_history.json")
        if os.path.exists(yol) and os.path.getsize(yol) > 0:
            with open(yol, "r", encoding="utf-8") as f: kayitlar = json.load(f)
            simdi = datetime.now()
            guncel = []
            for k in kayitlar:
                try:
                    k_tar = datetime.strptime(k["tarih"], "%Y-%m-%d %H:%M:%S")
                    if simdi - k_tar < timedelta(days=7): guncel.append(k)
                except: 
                    guncel.append(k)
            with open(yol, "w", encoding="utf-8") as f: 
                json.dump(guncel, f, ensure_ascii=False, indent=4)
            
    def model_icin_gecmis_hazirla(self, pr_adi):
        with open(os.path.join(HAFIZA_KLASORU, "kanka_kimdir.json"), "r", encoding="utf-8") as f: 
            kimlik = json.load(f)
        
        z_raporu_icerik = KankaZReportManager.z_raporu_oku(pr_adi)
        
        talimat = (
            f"Kullanıcıya kanka de. Hedef: {kimlik['hedef']} Tarz: {kimlik['ogretmen_tarzi']} "
            f"Kural: Godot 4.x ve GDScript kullan. Kodları aşama aşama ver. Türkçe açıklamalar ekle.\n"
            f"⚠️ PROJE KURUMSAM HAFIZASI VE Z-RAPORU KARARLARI (Bunları Asla Unutma):\n{z_raporu_icerik}"
        )
        
        gecmis = [{"role": "system", "content": talimat}]
        
        if pr_adi == "Günlük_Sohbet":
            return gecmis
            
        yol = os.path.join(HAFIZA_KLASORU, pr_adi, "chat_history.json")
        if os.path.exists(yol) and os.path.getsize(yol) > 0:
            with open(yol, "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
                for k in kayitlar:
                    gecmis.append({"role": "user", "content": k["kullanici"]})
                    gecmis.append({"role": "assistant", "content": k["kanka"]})
        return gecmis
