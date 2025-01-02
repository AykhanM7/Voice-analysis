import librosa
import numpy as np
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class DuyguAnalizi:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()

    def duygu_tahmini(self, dosya_yolu):
        """
        Ses dosyasından duygu analizi yapar ve duygu olasılıklarını döner.
        """
        try:
            # Ses dosyasını yükle
            y, sr = librosa.load(dosya_yolu, sr=None)

            # Ses özelliklerini çıkar (MFCC, Enerji, Tempo, Frekans vb.)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            enerji = np.mean(librosa.feature.rms(y=y).flatten())
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            frekans = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr).flatten())
            pitch = np.mean(librosa.yin(y=y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')))

            # Sesin durumu (Hız, Frekans, Enerji vs. ile duygu tahmini)
            if enerji > 0.02 and tempo > 120:
                return {"Heyecanlı": 90, "Mutlu": 80, "İlgili": 60, "Sakin": 20, "Üzgün": 5, "Öfkeli": 5}, ""
            elif frekans > 1000 and tempo > 150:
                return {"Heyecanlı": 85, "Mutlu": 70, "İlgili": 50, "Sakin": 5, "Öfkeli": 5, "Üzgün": 5}, ""
            elif tempo < 90 and enerji < 0.02:
                return {"Üzgün": 90, "Kırgın": 80, "Tedirgin": 60, "Sakin": 40, "Heyecanlı": 5}, ""
            else:
                return {"Sakin": 70, "İlgili": 50, "Mutlu": 40, "Heyecanlı": 30, "Üzgün": 10}, ""
        except Exception as e:
            return {}, f"Ses duygu analizi sırasında hata: {e}"

    def metinden_duygu_tahmini(self, metin):
        """
        Metinden duygu analizi yapar ve duygu olasılıklarını döner.
        """
        try:
            if not metin:
                return {"Bilinmiyor": 100}, ""

            # TextBlob ile duygu analizi (Polarite ve subjektiflik)
            blob = TextBlob(metin)
            polarite = blob.sentiment.polarity
            subjektiflik = blob.sentiment.subjectivity

            # VADER ile duygu analizi
            vader_result = self.vader_analyzer.polarity_scores(metin)

            # Metin duygu tahmini ve olasılık hesaplama
            if polarite > 0.2 or vader_result['compound'] > 0.2:
                return {"Mutlu": 80, "Heyecanlı": 70, "İlgili": 60, "Pozitif": 85, "Sakin": 10}, ""
            elif polarite < -0.2 or vader_result['compound'] < -0.2:
                return {"Üzgün": 85, "Kırgın": 70, "Negatif": 90, "Sakin": 10, "Tedirgin": 30}, ""
            elif subjektiflik > 0.5:
                return {"İlgili": 80, "Heyecanlı": 60, "Pozitif": 50, "Mutlu": 40, "Sakin": 20}, ""
            else:
                return {"Nötr": 100, "Sakin": 50, "İlgili": 40, "Mutlu": 20, "Üzgün": 10}, ""
        except Exception as e:
            return {}, f"Metin duygu analizi sırasında hata: {e}"

    def birlestirilmis_duygu_tahmini(self, dosya_yolu, metin):
        """
        Hem ses hem de metin duygu analizini birleştirir ve duygu olasılıklarını döner.
        """
        try:
            sesten_duygu, hata_ses = self.duygu_tahmini(dosya_yolu)
            metinden_duygu, hata_metin = self.metinden_duygu_tahmini(metin)

            if hata_ses:
                return {}, hata_ses
            if hata_metin:
                return {}, hata_metin

            # Ses ve metin duygu tahminlerinin ortalaması ile birleşik duygu tahmini
            birlesik_duygu = {}
            for duygu in set(sesten_duygu.keys()).union(metinden_duygu.keys()):
                # Ses ve metin olasılıklarının ortalamasını al
                birlesik_duygu[duygu] = (sesten_duygu.get(duygu, 0) + metinden_duygu.get(duygu, 0)) / 2

            return birlesik_duygu, ""
        except Exception as e:
            return {}, f"Birleşik duygu analizi sırasında hata: {e}"
