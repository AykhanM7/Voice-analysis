import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from ses_on_isleme import SesOnIsleme
from ses_tanima import SesTanima
from speech_to_text import SpeechToText
from duygu_analizi import DuyguAnalizi
from konu_analizi import KonuAnalizi
from veritabani import Veritabani
import sounddevice as sd
import numpy as np
import wave
import os

class SesKayitUygulamasi:
    def __init__(self, master):
        self.master = master
        self.master.title("Ses Analiz Uygulaması")
        self.master.geometry("1000x600")
        self.master.config(bg='#f0f0f0')
        self.tahmin_kullan = False  # Kullanıcı tahmin kontrolü için bayrak
        self.recording_data = []  # Kayıt için veri saklama alanı
        self.is_recording = False
        self.stream = None


        # Başlık
        self.baslik_label = tk.Label(master, text="Ses Analiz Uygulaması", font=("Arial", 24, "bold"), bg='#f0f0f0')
        self.baslik_label.pack(pady=20)

        # Butonlar için Frame
        self.button_frame = tk.Frame(master, bg='#f0f0f0')
        self.button_frame.pack(pady=50)

        # Butonları oluştur
        self.create_button("Sesinizi Kaydedip Analiz Yapın", "#4CAF50", self.ses_kaydet_ve_isle, 0, 0)
        self.create_button("Kaydetmeden Analiz Yap", "#FF9800", self.kaydetmeden_isle, 0, 1)
        self.create_button("Kullanıcıları Göster", "#008CBA", self.ses_kayitlarini_goster, 1, 0)
        self.create_button("Kullanıcıları Sil", "#f44336", self.kullanici_sil, 1, 1)
        self.create_button("Çıkış Yap", "#9E9E9E", self.master.quit, 2, 0)

        # Sonuçlar kısmı
        self.sonuc_frame = tk.Frame(master)
        self.sonuc_frame.pack(pady=20)
        self.sonuc_text = tk.Text(self.sonuc_frame, font=("Arial", 12), bg='#f0f0f0', wrap=tk.WORD, height=15, width=100)
        self.sonuc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.sonuc_frame, command=self.sonuc_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sonuc_text.config(yscrollcommand=self.scrollbar.set)

        # Butonları saklamak için
        self.mikrofonu_durdur_button = None
        self.analiz_yap_button = None
        self.yeniden_baslat_button = None
        self.geri_don_button = None
        self.myrecording = None

    def create_button(self, text, bg_color, command, row, column):
        button = tk.Button(self.button_frame, text=text, font=("Arial", 14), width=25, height=2, bg=bg_color, fg="white", command=command)
        button.grid(row=row, column=column, padx=20, pady=10)
        return button
    
    def ses_kaydet_ve_isle(self):
        self.hide_buttons()
        self.console_temizle()

        # Yeni butonları göster
        self.mikrofonu_durdur_button = self.create_button("Mikrofonu Durdur", "#FF5722", self.mikrofonu_durdur, 0, 0)
        self.analiz_yap_button = self.create_button("Analiz Yap", "#FF9800", self.analiz_yap, 0, 1)
        self.yeniden_baslat_button = self.create_button("Yeniden Başlat", "#FFC107", self.yeniden_baslat, 1, 0)
        self.geri_don_button = self.create_button("Geri Dön", "#FFC107", self.geri_don, 1, 1)
        self.ses_kayit_baslat()

    def ses_kayit_baslat(self):
        """
        Ses kaydını başlatır ve kullanıcıyı bilgilendirir.
        """
        try:
            self.sonuc_text.insert(tk.END, "Ses kaydı başlatıldı. Kaydı durdurmak için 'Mikrofonu Durdur' butonuna basın...\n")
            self.recording_data = []
            self.is_recording = True
            self.stream = sd.InputStream(
                samplerate=44100,
                channels=2,
                dtype='int16',
                callback=self.audio_callback
            )
            self.stream.start()
        except Exception as e:
            self.sonuc_text.insert(tk.END, f"Ses kaydı başlatılırken bir hata oluştu: {e}\n")

    def mikrofonu_durdur(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            self.sonuc_text.insert(tk.END, "Ses kaydı durduruldu.\n")
            # Kaydedilen tüm veriyi birleştir
            if self.recording_data:
                self.myrecording = np.concatenate(self.recording_data, axis=0)
            else:
                messagebox.showerror("Hata", "Kayıt sırasında ses alınamadı!")
                self.myrecording = None
        else:
            messagebox.showerror("Hata", "Ses kaydı zaten durduruldu.")

    def analiz_yap(self):
        if not hasattr(self, 'myrecording') or self.myrecording is None:
            messagebox.showerror("Hata", "Ses kaydını durdurmadan analiz yapılamaz!")
            return

        self.tahmin_kullan = True
        veritabani = Veritabani()
        
        while True:
            kullanici_adi = simpledialog.askstring("Kullanıcı Adı", "Kaydedilecek sesin kullanıcı adını girin:", parent=self.master)
            if not kullanici_adi:
                messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
                return
            
            if veritabani.kullanici_var_mi(kullanici_adi):
                messagebox.showwarning("Uyarı", f"{kullanici_adi} adlı kullanıcı zaten mevcut. Lütfen başka bir kullanıcı adı girin.")
            else:
                break

        dosya_adi = self.ses_kaydet(self.myrecording, 44100, kullanici_adi)
        if dosya_adi:
            self.ses_isle(dosya_adi)
            
    def yeniden_baslat(self):
        self.sonuc_text.insert(tk.END, "Ses kaydı yeniden başlatılıyor...\n")
        self.ses_kaydet_ve_isle()

    def geri_don(self):
        self.hide_buttons()
        self.create_button("Sesinizi Kaydedip Analiz Yapın", "#4CAF50", self.ses_kaydet_ve_isle, 0, 0)
        self.create_button("Kaydetmeden Analiz Yap", "#FF9800", self.kaydetmeden_isle, 0, 1)
        self.create_button("Kullanıcıları Göster", "#008CBA", self.ses_kayitlarini_goster, 1, 0)
        self.create_button("Kullanıcıları Sil", "#f44336", self.kullanici_sil, 1, 1)
        self.create_button("Çıkış Yap", "#9E9E9E", self.master.quit, 2, 0)



   
    def kaydetmeden_isle(self):
        self.hide_buttons()
        self.console_temizle()

        # Butonları göster
        self.mikrofonu_durdur_button = self.create_button("Mikrofonu Durdur", "#FF5722", self.mikrofonu_durdur, 0, 0)
        self.analiz_yap_button = self.create_button("Analiz Yap", "#FF9800", self.analiz_yap_kaydetmeden, 0, 1)
        self.yeniden_baslat_button = self.create_button("Yeniden Başlat", "#FFC107", self.yeniden_baslat_kaydetmeden, 1, 0)
        self.geri_don_button = self.create_button("Geri Dön", "#FFC107", self.geri_don, 1, 1)
        self.ses_kayit_baslat()

    def analiz_yap_kaydetmeden(self):
        """
        Geçici dosyaya kaydedilmeden ses analizi yapar.
        """
        if not hasattr(self, 'myrecording') or self.myrecording is None:
            messagebox.showerror("Hata", "Ses kaydını durdurmadan analiz yapılamaz!")
            return

        self.tahmin_kullan = False
        dosya_adi = "temp_kayit.wav"

        try:
            # Geçici dosyayı kaydet
            self.ses_kaydet_temp(self.myrecording, 44100, dosya_adi)
            self.ses_isle(dosya_adi)
            self.sonuc_text.insert(tk.END, "Ses başarıyla analiz edildi.\n")
        except Exception as e:
            messagebox.showerror("Hata", f"Ses analizi sırasında bir hata oluştu: {e}")


    def yeniden_baslat_kaydetmeden(self):
        self.sonuc_text.insert(tk.END, "Ses kaydı yeniden başlatılıyor...\n")
        self.kaydetmeden_isle()

    def ses_kaydet_temp(self, myrecording, fs, dosya_adi):
        """
        Geçici bir ses dosyasını kaydeder.
        """
        # Boş veya geçersiz `myrecording` verisi kontrolü
        if myrecording is None or len(myrecording) == 0:
            messagebox.showerror("Hata", "Kaydedilecek ses verisi yok!")
            return

        try:
            with wave.open(dosya_adi, 'wb') as wf:
                wf.setnchannels(2)  # Stereo
                wf.setsampwidth(2)  # 16-bit (2 byte)
                wf.setframerate(fs)
                wf.writeframes(myrecording.tobytes())

            self.sonuc_text.insert(tk.END, f"Ses kaydı başarıyla geçici olarak kaydedildi: {dosya_adi}\n")
        except Exception as e:
            messagebox.showerror("Hata", f"Ses kaydedilirken bir hata oluştu: {e}")
  
    def ses_kaydet(self, myrecording, fs, kullanici_adi):
        """
        Ses kaydını belirli bir kullanıcı adıyla dosya olarak kaydeder ve veritabanına ekler.
        """
        # Kayıt için dosya adı oluşturulması
        dosya_adi = f"data/{kullanici_adi}_kayit.wav"
        os.makedirs(os.path.dirname(dosya_adi), exist_ok=True)

        # `myrecording` geçerlilik kontrolü
        if myrecording is None or len(myrecording) == 0:
            messagebox.showerror("Hata", "Kaydedilecek geçerli bir ses verisi bulunamadı!")
            return None

        try:
            # WAV dosyasını kaydetme işlemi
            with wave.open(dosya_adi, 'wb') as wf:
                wf.setnchannels(2)  # Stereo
                wf.setsampwidth(2)  # 16-bit (2 byte)
                wf.setframerate(fs)  # Örnekleme frekansı
                wf.writeframes(myrecording.tobytes())

            # Başarılı işlem mesajı
            self.sonuc_text.insert(tk.END, f"Ses kaydı başarıyla kaydedildi: {dosya_adi}\n")

            # Veritabanına kullanıcı ekleme işlemi
            try:
                veritabani = Veritabani()
                veritabani.kullanici_ekle(kullanici_adi, dosya_adi)
            except Exception as e:
                self.sonuc_text.insert(tk.END, f"Veritabanına kullanıcı eklenirken bir hata oluştu: {e}\n")
                return None

            # Başarı durumunda dosya adını döndür
            return dosya_adi

        except Exception as e:
            # Hata durumunda mesaj göster ve None döndür
            messagebox.showerror("Hata", f"Ses kaydedilirken bir hata oluştu: {e}")
            return None
    def ses_isle(self, dosya_adi):
        try:
            ses_on_isleme = SesOnIsleme(dosya_adi)
            ses_on_isleme.yukle_ses()
            ses_on_isleme.gorsellestir()

            metin = self.metin_donusumu(dosya_adi)

            duygu = self.duygu_analizi(dosya_adi, metin)

            kullanici_tahmini = self.kullanici_tahmini(dosya_adi)
            self.sonuc_text.insert(tk.END, f"Kullanıcı Tahmini: {kullanici_tahmini}\n")
            if metin:
                self.konu_analizi(metin)

            self.sonuc_text.config(state=tk.DISABLED)
        except Exception as e:
            self.sonuc_text.insert(tk.END, f"Bir hata oluştu: {e}\n")
            self.sonuc_text.config(state=tk.DISABLED)

        self.geri_don()

    def metin_donusumu(self, dosya_adi):
        speech_to_text = SpeechToText()
        metin, hata_mesaji = speech_to_text.konusan_metni_bul(dosya_adi)

        if metin:
            self.sonuc_text.insert(tk.END, f"Dönüştürülen Metin: {metin}\n")
            kelime_sayisi, kelime_hata = speech_to_text.kelime_say(metin)
            self.sonuc_text.insert(tk.END, f"Kelime Sayısı: {kelime_sayisi}\n")
        else:
            self.sonuc_text.insert(tk.END, f"Metin dönüşümü başarısız oldu: {hata_mesaji}\n")
        
        if kelime_hata:
            self.sonuc_text.insert(tk.END, kelime_hata + "\n")
        
        return metin


    def duygu_analizi(self, dosya_adi, metin):
        duygu_analizi = DuyguAnalizi()
        sesten_duygu, hata_ses = duygu_analizi.duygu_tahmini(dosya_adi)
        self.sonuc_text.insert(tk.END, f"Sesten Duygu Tahmini: {sesten_duygu}\n")
        
        if hata_ses:
            self.sonuc_text.insert(tk.END, f"Hata (Ses): {hata_ses}\n")

        if metin:
            metinden_duygu, hata_metin = duygu_analizi.metinden_duygu_tahmini(metin)
            self.sonuc_text.insert(tk.END, f"Metinden Duygu Tahmini: {metinden_duygu}\n")
            if hata_metin:
                self.sonuc_text.insert(tk.END, f"Hata (Metin): {hata_metin}\n")

            birlesik_duygu, hata_birlesik = duygu_analizi.birlestirilmis_duygu_tahmini(dosya_adi, metin)
            self.sonuc_text.insert(tk.END, f"Birleşik Duygu Tahmini: {birlesik_duygu}\n")
            if hata_birlesik:
                self.sonuc_text.insert(tk.END, f"Hata (Birleşik): {hata_birlesik}\n")


    def konu_analizi(self, metin):
        konu_analizi = KonuAnalizi()
        konu_analizi.model_yukle()
        tahminler = konu_analizi.konu_tahmini(metin)
        if tahminler:
            for konu, skor in tahminler:
                self.sonuc_text.insert(tk.END, f"Konu: {konu}, Skor: {skor}\n")
        else:
            self.sonuc_text.insert(tk.END, "Konu tahmini yapılamadı.\n")
    def kullanici_tahmini(self, dosya_adi):
        if not self.tahmin_kullan:
            ses_tanima = SesTanima()
            return ses_tanima.kullanici_tahmini(dosya_adi)
        else:
            return "Kullanıcı eklediğiniz için tahmin yapılmadı"  # Bayrak aktifse tahmini atla

    def ses_kayitlarini_goster(self):
        try:
            veritabani = Veritabani()
            kayitlar = veritabani.ses_kayitlarini_goster()

            self.console_temizle()

            if not kayitlar:
                self.sonuc_text.insert(tk.END, "Henüz kayıtlı kullanıcı yok.\n")
            else:
                self.sonuc_text.insert(tk.END, "Kayıtlı Kullanıcılar:\n")
                for kayit in kayitlar:
                    self.sonuc_text.insert(tk.END, f"ID: {kayit[0]}, İsim: {kayit[1]}, Dosya Yolu: {kayit[2]}\n")

            self.sonuc_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Hata: {e}")

    def kullanici_sil(self):
        kullanici_adi = simpledialog.askstring("Kullanıcı Adı Sil", "Silmek istediğiniz kullanıcı adını girin:", parent=self.master)

        if not kullanici_adi:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
            return

        veritabani = Veritabani()
        if veritabani.kullanici_var_mi(kullanici_adi):
            if veritabani.kullanici_sil(kullanici_adi):
                messagebox.showinfo("Başarılı", f"{kullanici_adi} adlı kullanıcı silindi.")
            else:
                messagebox.showerror("Hata", "Kullanıcı silinirken bir hata oluştu!")
        else:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı!")

    def hide_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.grid_forget()

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording_data.append(indata.copy())  # Gelen ses verilerini kaydet

    def console_temizle(self):
        self.sonuc_text.config(state=tk.NORMAL)
        self.sonuc_text.delete(1.0, tk.END)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SesKayitUygulamasi(root)
    root.mainloop() 