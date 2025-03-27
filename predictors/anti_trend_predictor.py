class AntiTrendPredictor:
    """
    Başka bir modelin tahmininin tersini yapan 'Ters Köşe' modeli.
    Genellikle en popüler veya ilk modelin tersini hedefler.
    """

    def predict(self, history: list, primary_prediction: str = 'N/A') -> str:
        """
        Verilen 'birincil' tahminin tersini tahmin eder.
        'P', 'B' veya tahmin yapılamıyorsa 'N/A' döndürür.
        'history' parametresi bu model için doğrudan kullanılmaz ama standart arayüz için vardır.
        """
        if primary_prediction == 'P':
            return 'B'
        elif primary_prediction == 'B':
            return 'P'
        else: # Eğer birincil tahmin 'N/A' veya 'T' ise, ters köşe de 'N/A' döndürür.
            return 'N/A'

    def get_confidence(self, history: list, primary_confidence: float = 50.0) -> float:
        """
        Tahminin güven oranını döndürür.
        Basitçe, birincil modelin güveninin tersini (%100'den farkı) verebiliriz
        veya daha basit bir mantık kullanabiliriz. Şimdilik %50'den farkını alalım.
        """
        # Güveni %10-90 arasında tutalım
        confidence = 100.0 - primary_confidence
        return max(10.0, min(90.0, confidence))


    def get_probability(self, history: list, primary_probability: float = 50.0) -> float:
        """
        Tahminin gerçekleşme olasılığını döndürür.
        Benzer şekilde, birincil modelin olasılığının tersini verebiliriz.
        """
         # Olasılığı %10-90 arasında tutalım
        probability = 100.0 - primary_probability
        return max(10.0, min(90.0, probability))
