import sqlite3

class Veritabani:
    def __init__(self):
        self.veritabani_adi = "kullanicilar.db"
        self.baglanti = sqlite3.connect(self.veritabani_adi)
        self.cursor = self.baglanti.cursor()
        self.tablo_olustur()

    def tablo_olustur(self):
        """Kullanıcılar tablosunu oluşturur."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                dosya_yolu TEXT NOT NULL
            )
            """
        )
        self.baglanti.commit()

    def kullanici_ekle(self, isim, dosya_yolu):
        """Yeni bir kullanıcı ekler."""
        self.cursor.execute(
            "INSERT INTO kullanicilar (isim, dosya_yolu) VALUES (?, ?)",
            (isim, dosya_yolu)
        )
        self.baglanti.commit()
    def kullanici_sil(self, isim):
        """Verilen isimdeki kullanıcıyı siler."""
        if self.kullanici_var_mi(isim):
            self.cursor.execute("DELETE FROM kullanicilar WHERE isim = ?", (isim,))
            self.baglanti.commit()
            return True
        else:
            return False

    def ses_kayitlarini_goster(self):
        """Tüm kullanıcı bilgilerini döndürür."""
        self.cursor.execute("SELECT * FROM kullanicilar")
        kayitlar = self.cursor.fetchall()
        return kayitlar  # Kayıtları bir liste olarak döndür

    def kullanici_sayisini_goster(self):
        """Toplam kullanıcı sayısını döndürür."""
        self.cursor.execute("SELECT COUNT(*) FROM kullanicilar")
        kullanici_sayisi = self.cursor.fetchone()[0]
        return kullanici_sayisi()
    def kullanici_sesleri(self):
        """Veritabanındaki tüm kullanıcıların ses dosyası bilgilerini alır."""
        self.cursor.execute("SELECT isim, dosya_yolu FROM kullanicilar")
        return self.cursor.fetchall()
    def kullanici_var_mi(self, isim):
        """Bir kullanıcı veritabanında mevcut mu kontrol eder."""
        self.cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE isim = ?", (isim,))
        return self.cursor.fetchone()[0] > 0

    def __del__(self):
        self.baglanti.close()
