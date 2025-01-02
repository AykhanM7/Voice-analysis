import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

class SesOnIsleme:
    def __init__(self, dosya_adi):
        self.dosya_adi = dosya_adi
        self.ses_verisi = None
        self.ornekleme_hizi = None

    def yukle_ses(self):
        """Ses dosyasını yükler."""
        self.ses_verisi, self.ornekleme_hizi = librosa.load(self.dosya_adi, sr=None)

    def gorsellestir(self):
        """Ses dosyasının dalga formunu ve spektrogramını görselleştirir."""
        if self.ses_verisi is None or self.ornekleme_hizi is None:
            self.yukle()

        # Görselleştirme için bir figür oluştur
        plt.figure(figsize=(12, 8))

        # Dalga formu (waveform)
        plt.subplot(2, 1, 1)
        librosa.display.waveshow(self.ses_verisi, sr=self.ornekleme_hizi)
        plt.title('Dalga Formu')
        plt.xlabel('Zaman (saniye)')
        plt.ylabel('Genlik')

        # Spektrogram
        plt.subplot(2, 1, 2)
        S = librosa.feature.melspectrogram(y=self.ses_verisi, sr=self.ornekleme_hizi, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, sr=self.ornekleme_hizi, x_axis='time', y_axis='mel', fmax=8000, cmap='viridis')
        plt.colorbar(img, format='%+2.0f dB')
        plt.title('Mel Spektrogram')

        # Görüntüyü göster
        plt.tight_layout()
        plt.show()

