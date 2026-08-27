import os
import threading
import customtkinter as ctk
from tkinter import filedialog

# Diğer parçaları içe aktarıyoruz kanka
from kanka_storage import KankaMemoryManager, KankaZReportManager
from kanka_network import KankaNetworkEngine

class KankaUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Kanka AI v3.5 - Dinamik Proje Adlandırma Sürümü")
        self.geometry("1060x780")
        
        self.hafiza = KankaMemoryManager()
        self.network = KankaNetworkEngine(self)
        self.aktif_proje = "Günlük_Sohbet"
        self.gecici_sohbet_hafizasi = []
        
        ctk.set_appearance_mode("Dark")
        self.fg_color = "#121214"
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # SOL PANEL
        self.sol_panel = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1a1a1e")
        self.sol_panel.grid(row=0, column=0, sticky="nsew")
        self.sol_panel.grid_propagate(False)
        
        lbl = ctk.CTkLabel(self.sol_panel, text="📂 ARŞİV ODALARI", font=("Segoe UI", 13, "bold"), text_color="#8ec07c")
        lbl.pack(pady=(20, 5), padx=15, anchor="w")
        
        lbl_bilgi = ctk.CTkLabel(self.sol_panel, text="(İsim değiştirmek için çift tıkla)", font=("Segoe UI", 10, "italic"), text_color="#a89984")
        lbl_bilgi.pack(pady=(0, 10), padx=15, anchor="w")
        
        self.proje_butonlari = {}
        
        btn_pasif = ctk.CTkButton(self.sol_panel, text="💬 Günlük Sohbet (Pasif)", anchor="w", font=("Segoe UI", 12, "bold"), fg_color="#458588", text_color="#ffffff", hover_color="#076678", command=lambda: self.proje_degistir("Günlük_Sohbet"))
        btn_pasif.pack(fill="x", padx=10, pady=8)
        self.proje_butonlari["Günlük_Sohbet"] = btn_pasif
        
        # 🎮 Dinamik Proje Odaları Dizilimi
        for i in range(1, 6):
            p_kod_adi = f"Proje_{i}"
            p_gorunur_adi = self.hafiza.proje_haritasi.get(p_kod_adi, p_kod_adi)
            
            btn = ctk.CTkButton(self.sol_panel, text=f"🎮 {p_gorunur_adi}", anchor="w", font=("Segoe UI", 12), fg_color="transparent", text_color="#ffffff", hover_color="#2d2d34", command=lambda name=p_kod_adi: self.proje_degistir(name))
            btn.pack(fill="x", padx=10, pady=4)
            
            btn.bind("<Double-1>", lambda event, kod=p_kod_adi: self.proje_ismini_degistir_popup(kod))
            self.proje_butonlari[p_kod_adi] = btn
            
        self.btn_z_oku = ctk.CTkButton(self.sol_panel, text="📋 Odadaki Z-Raporunu Gör", font=("Segoe UI", 11, "bold"), fg_color="#d65d0e", hover_color="#af3a03", command=self.mevcut_z_raporunu_goster)
        self.btn_z_oku.pack(fill="x", padx=10, pady=(20, 4))
            
        self.alt_pan = ctk.CTkFrame(self.sol_panel, fg_color="transparent")
        self.alt_pan.pack(side="bottom", fill="x", padx=15, pady=25)
        
        lbl_t = ctk.CTkLabel(self.alt_pan, text="🌓 GÖRÜNÜM TEMASI:", font=("Segoe UI", 11, "bold"), text_color="#a89984")
        lbl_t.pack(anchor="w", pady=(0, 5))
        self.t_secici = ctk.CTkOptionMenu(self.alt_pan, values=["Karanlık Mod", "Aydınlık Mod"], font=("Segoe UI", 11), fg_color="#26262b", button_color="#32323c", command=self.tema_degistir)
        self.t_secici.pack(fill="x", pady=(0, 15))
        
        lbl_d = ctk.CTkLabel(self.alt_pan, text="🤖 YEREL BAĞLANTI:", font=("Segoe UI", 11, "bold"), text_color="#a89984")
        lbl_d.pack(anchor="w")
        self.lbl_onay = ctk.CTkLabel(self.alt_pan, text="🗹 Qwen-7B Aktif", font=("Segoe UI", 11, "bold"), text_color="#27ae60")
        self.lbl_onay.pack(anchor="w")
        # SAĞ PANEL
        self.sag_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.sag_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.sag_panel.grid_rowconfigure(0, weight=1)
        self.sag_panel.grid_columnconfigure(0, weight=1)
        
        self.metin_alani = ctk.CTkTextbox(self.sag_panel, corner_radius=12, fg_color="#1a1a1e", border_color="#2d2d34", border_width=1, font=("Consolas", 15), text_color="#e5e5e5")
        self.metin_alani.grid(row=0, column=0, sticky="nsew")
        self.metin_alani.configure(state="disabled")
        
        self.alt_isl = ctk.CTkFrame(self.sag_panel, fg_color="transparent")
        self.alt_isl.grid(row=1, column=0, pady=(15, 0), sticky="ew")
        self.alt_isl.grid_columnconfigure(1, weight=1)
        
        self.dosya_butonu = ctk.CTkButton(self.alt_isl, text="+", width=50, height=45, font=("Segoe UI", 22, "bold"), fg_color="#32323c", hover_color="#41414f", command=self.dosya_yukle)
        self.dosya_butonu.grid(row=0, column=0, padx=(0, 12), sticky="w")
        
        self.giris_kutusu = ctk.CTkEntry(self.alt_isl, height=45, font=("Segoe UI", 14), placeholder_text="Kankana oyun fikrini anlat veya geyik yap...", fg_color="#1a1a1e", border_color="#2d2d34")
        self.giris_kutusu.grid(row=0, column=1, padx=(0, 12), sticky="ew")
        self.giris_kutusu.bind("<Return>", lambda event: self.mesaj_gonder())
        
        self.gonder_butonu = ctk.CTkButton(self.alt_isl, text="Gönder", width=110, height=45, font=("Segoe UI", 13, "bold"), fg_color="#458588", hover_color="#076678", command=self.mesaj_gonder)
        self.gonder_butonu.grid(row=0, column=2, sticky="e")
        
        self.ekrana_yaz("🤖 Kanka AI v3.5: Dinamik Adlandırma Devrede! Geyikler uçucu, projeler kalıcı.\nİpucu: Oda adını değiştirmek için butonun üzerine çift tıkla kanka!\n")

    def proje_ismini_degistir_popup(self, kod_adi):
        """v3.5 Eklentisi: Kullanıcıdan pop-up ile yeni ismi alan tetikleyici."""
        mevcut_ad = self.hafiza.proje_haritasi.get(kod_adi, kod_adi)
        dialog = ctk.CTkInputDialog(text=f"'{mevcut_ad}' için yeni bir isim gir kanka:", title="Oda Adını Değiştir")
        yeni_ad = dialog.get_input()
        
        if yeni_ad:
            basarili, sonuc = self.hafiza.proje_adlandir(kod_adi, yeni_ad)
            if basarili:
                self.proje_butonlari[kod_adi].configure(text=f"🎮 {sonuc}")
                self.ekrana_yaz(f"✨ [SİSTEM]: Odasının adı başarıyla '{sonuc}' olarak güncellendi kanka!")
                if self.aktif_proje == kod_adi:
                    self.proje_degistir(kod_adi)
            else:
                self.ekrana_yaz(f"❌ [SİSTEM HATA]: {sonuc}")

    def tema_degistir(self, secim):
        if secim == "Karanlık Mod":
            ctk.set_appearance_mode("Dark")
            self.configure(fg_color="#121214")
            self.metin_alani.configure(fg_color="#1a1a1e", text_color="#e5e5e5", border_color="#2d2d34")
            self.giris_kutusu.configure(fg_color="#1a1a1e", text_color="#ffffff", border_color="#2d2d34")
        else:
            ctk.set_appearance_mode("Light")
            self.configure(fg_color="#f3f4f6")
            self.metin_alani.configure(fg_color="#ffffff", text_color="#1f2937", border_color="#e5e7eb")
            self.giris_kutusu.configure(fg_color="#ffffff", text_color="#000000", border_color="#d1d5db")

    def proje_degistir(self, pr_kod_adi):
        self.aktif_proje = pr_kod_adi
        for n, btn in self.proje_butonlari.items():
            if n == pr_kod_adi:
                btn.configure(fg_color="#458588" if pr_kod_adi=="Günlük_Sohbet" else "#26262b")
            else:
                btn.configure(fg_color="transparent")
                
        self.metin_alani.configure(state="normal")
        self.metin_alani.delete("1.0", "end")
        self.metin_alani.configure(state="disabled")
        
        if pr_kod_adi == "Günlük_Sohbet":
            self.ekrana_yaz("💬 Günlük Sohbet odasındayız. Burada konuşulanlar sisteme yük olmaz, kapanınca silinir kanka.\n")
        else:
            guncel_ad = self.hafiza.proje_haritasi.get(pr_kod_adi, pr_kod_adi)
            self.ekrana_yaz(f"📂 '{guncel_ad}' odasındayız kanka. Projenin kurumsal hafızası ve Z-Raporları yüklendi!\n")

    def mevcut_z_raporunu_goster(self):
        if self.aktif_proje == "Günlük_Sohbet":
            self.ekrana_yaz("⚠️ Günlük sohbet odasının bir Z-Raporu olmaz kanka, projelerden birini seç.")
            return
        guncel_ad = self.hafiza.proje_haritasi.get(self.aktif_proje, self.aktif_proje)
        icerik = KankaZReportManager.z_raporu_oku(guncel_ad)
        self.ekrana_yaz(f"\n📋 --- {guncel_ad} MEVCUT Z-RAPORU --- \n{icerik}\n----------------------------------\n")

    def ekrana_yaz(self, mesaj):
        self.metin_alani.configure(state="normal")
        self.metin_alani.insert("end", mesaj + "\n")
        self.metin_alani.configure(state="disabled")
        self.metin_alani.yview("end")

    def dosya_yukle(self):
        yol = filedialog.askopenfilename(title="Döküman Seç", filetypes=[("Kod Dosyaları", "*.txt *.py *.json *.gd")])
        if yol:
            dn = os.path.basename(yol)
            try:
                with open(yol, "r", encoding="utf-8") as f: icerik = f.read()
                msg = f"[DOSYA DAHİL EDİLDİ: {dn}]\n\n{icerik}\n\nAnaliz et kanka."
                self.ekrana_yaz(f"📁 Dosya '{dn}' oda bağlamına dahil ediliyor...")
                self.yapay_zekaya_sor(msg, gizli_mi=True)
            except Exception as e: self.ekrana_yaz(f"❌ Hata: {e}")

    def mesaj_gonder(self):
        msg = self.giris_kutusu.get()
        if not msg.strip(): return
        self.ekrana_yaz(f"👤 Sen: {msg}")
        self.giris_kutusu.delete(0, "end")
        self.yapay_zekaya_sor(msg)

    def yapay_zekaya_sor(self, msg, gizli_mi=False):
        is_parcacigi = threading.Thread(
            target=self.network._arka_plan_ollama_istegi, 
            args=(msg, gizli_mi), 
            daemon=True
        )
        is_parcacigi.start()

if __name__ == "__main__":
    app = KankaUygulamasi()
    app.mainloop()

