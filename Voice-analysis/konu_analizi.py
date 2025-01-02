from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore

class KonuAnalizi:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Türkçe destekli Haystack tabanlı konu analizi sınıfını başlatır.

        Args:
            model_name (str): Kullanılacak embedding modelinin adı. Varsayılan 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'.
        """
        self.model_name = model_name
        # Modelin embedding boyutuna dikkat edin
        self.document_store = InMemoryDocumentStore(similarity="cosine", embedding_dim=384)
        self.retriever = None

    def model_yukle(self):
        """
        Modeli yükler ve konu başlıklarını indeksler.
        """
        konular = [
            "Spor dünyasındaki güncel gelişmeler",
            "Ekonomik reformlar ve finansal analizler",
            "Teknolojik yenilikler ve icatlar",
            "Halk sağlığı ve tıbbi gelişmeler",
            "Politik tartışmalar ve hükümet politikaları",
            "Eğitim reformları ve öğrenci başarıları"
        ]

        try:
            # Embedding Retriever oluştur
            self.retriever = EmbeddingRetriever(
                document_store=self.document_store,
                embedding_model=self.model_name,
                model_format="sentence_transformers"
            )

            # Konuları belge olarak ekle
            docs = [{"content": konu} for konu in konular]
            self.document_store.write_documents(docs)
            self.document_store.update_embeddings(self.retriever)

            # print("Model başarıyla yüklendi ve konular indekslendi.")
        except Exception as e:
            # print(f"Model veya indeksleme sırasında hata oluştu: {e}")
            pass

    def konu_tahmini(self, metin):
        """
        Metin üzerinden konu tahmini yapar.

        Args:
            metin (str): Analiz edilecek metin.

        Returns:
            list: Tahmin edilen konular ve olasılıkları.
        """
        if not self.retriever:
            # print("Model yüklü değil. Lütfen model_yukle() metodunu çağırın.")
            return None

        try:
            # Retriever kullanarak en benzer konuları bul
            tahminler = self.retriever.retrieve(query=metin, top_k=6)  # Tüm konuları alıyoruz

            # Cosine benzerliğini 0-100 arasında olasılık değeri olarak döndürme
            toplam_benzerlik = sum([(tahmin.score + 1) / 2 for tahmin in tahminler])  # Normalized toplam skor
            olasiliklar = []

            for tahmin in tahminler:
                # Her bir tahminin olasılığını hesapla
                olasilik = ((tahmin.score + 1) / 2) / toplam_benzerlik * 100
                olasiliklar.append((tahmin.content, round(olasilik, 2)))

            return olasiliklar
        except Exception as e:
            # print(f"Konu tahmini yapılırken hata oluştu: {e}")
            return None