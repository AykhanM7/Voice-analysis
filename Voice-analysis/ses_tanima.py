import numpy as np
import librosa
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from veritabani import Veritabani

class SesTanima:
    def __init__(self):
        self.veritabani = Veritabani()
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.model_egit()

    def mfcc_ozellik_cikarimi(self, dosya_adi):
        try:
            audio_data, sampling_rate = librosa.load(dosya_adi, sr=None)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sampling_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_var = np.var(mfccs, axis=1)

            # Ekstra özellikler: chroma, spectral contrast, tonnetz
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sampling_rate)
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sampling_rate)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sampling_rate)

            # Bu yeni özellikleri mevcut MFCC özelliklerine ekleyelim
            chroma_mean = np.mean(chroma, axis=1)
            spectral_contrast_mean = np.mean(spectral_contrast, axis=1)
            tonnetz_mean = np.mean(tonnetz, axis=1)

            return np.concatenate((mfcc_mean, mfcc_var, chroma_mean, spectral_contrast_mean, tonnetz_mean))
        except Exception as e:
            # print(f"MFCC çıkarımı sırasında hata oluştu: {e}")
            return None

    def veri_hazirla(self):
        kullanicilar = self.veritabani.kullanici_sesleri()
        if not kullanicilar:
            # print("Veritabanında kullanıcı yok.")
            return None, None

        X = []
        y = []

        for i, (isim, dosya_adi) in enumerate(kullanicilar):
            mfcc_vektor = self.mfcc_ozellik_cikarimi(dosya_adi)
            if mfcc_vektor is not None:
                X.append(mfcc_vektor)
                y.append(isim)

        # Verilerin karıştırılması
        veriler = list(zip(X, y))
        np.random.shuffle(veriler)  # Karıştırma işlemi
        X, y = zip(*veriler)

        return np.array(X), np.array(y)

    def model_egit(self):
        # print("Veri hazırlanıyor...")
        X, y = self.veri_hazirla()
        if X is None or y is None:
            # print("Veri hazırlanamadı, model eğitimi başarısız oldu.")
            return

        # Veri setini eğitim ve test olarak ayırma
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.scaler.fit(X_train)
        X_train = self.scaler.transform(X_train)
        X_test = self.scaler.transform(X_test)
        self.is_fitted = True

        # print("Model eğitiliyor...")

        # Modeli doğrudan eğitim verileri ile eğitme
        self.model = SVC(class_weight='balanced', probability=True)
        self.model.fit(X_train, y_train)

        # Modeli değerlendir
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

    def kullanici_tahmini(self, dosya_adi):
        mfcc_vektor = self.mfcc_ozellik_cikarimi(dosya_adi)
        if mfcc_vektor is None:
            # print("MFCC çıkarımı yapılamadı.")
            return None

        if not self.is_fitted:
            # print("Scaler henüz fit edilmedi. Modeli yeniden eğitmeniz gerekebilir.")
            return None

        try:
            mfcc_vektor = self.scaler.transform(mfcc_vektor.reshape(1, -1))  # 1D to 2D reshape
            tahmin = self.model.predict(mfcc_vektor)
            tahmin_olasiliklari = self.model.predict_proba(mfcc_vektor)
            tahmin_olasiligi = tahmin_olasiliklari[0][self.model.classes_ == tahmin[0]][0]
            # print(f"Tahmin Edilen Kullanıcı: {tahmin[0]}, Olasılık: {tahmin_olasiligi:.2f}")
            return str(tahmin[0])
        except Exception as e:
            # print(f"Tahmin sırasında hata oluştu: {e}")
            return None, None

    def ses_tanima_ve_goster(self, dosya_adi):
        tahmin = self.kullanici_tahmini(dosya_adi)
        if tahmin:
            return f"Tahmin Edilen Kullanıcı: {tahmin}"
        else:
            return "Kullanıcı tanınamadı."