import speech_recognition as sr

class SpeechToText:
    def konusan_metni_bul(self, dosya_yolu):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(dosya_yolu) as source:
                ses = recognizer.record(source)
            # Google Speech-to-Text kullanarak metne çevir
            metin = recognizer.recognize_google(ses, language="tr-TR")
            return metin, ""
        except Exception as e:
            return "", f"Hata: {e}"


    def kelime_say(self, metin):
        if not metin:
            return 0, "Metin bulunamadı, kelime sayımı yapılamıyor."
        kelimeler = metin.split()
        return len(kelimeler), ""