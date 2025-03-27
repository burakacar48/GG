import random
import math

class MultiversePredictor:
    """
    Paralel Evren Bahisçisi (Basitleştirilmiş):
    Baccarat'ın temel P/B olasılıklarını alır, geçmişteki sapmalara göre
    hafifçe ayarlar ve daha olası görünen tarafı tahmin eder.
    Güven/Olasılık, iki taraf arasındaki olasılık farkına göre belirlenir.
    """

    # Tie'ları hesaba katmadan yaklaşık P/B oranları (8 deste için)
    BASE_P_PROB_NO_TIE = 49.32
    BASE_B_PROB_NO_TIE = 50.68

    def __init__(self, deviation_window=20, deviation_influence=0.15, quantum_leap_chance=0.05):
        # Olasılıkları ayarlamak için bakılacak geçmiş penceresi
        self.deviation_window = max(5, deviation_window)
        # Geçmişteki sapmanın temel olasılıkları ne kadar etkileyeceği (0 ile 1 arası)
        # 0.15 = Sapma farkının %15'i kadar olasılık kaydırılır.
        self.deviation_influence = max(0.0, min(0.5, deviation_influence))
        # Bazen düşük olasılıklı tarafı seçme şansı (Kuantum Sıçraması!)
        self.quantum_leap_chance = max(0.0, min(0.2, quantum_leap_chance))

    def predict(self, history: list) -> str:
        """
        Ayarlanmış olasılıklara göre P veya B tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.deviation_window:]
        window_len = len(window)

        # Mevcut penceredeki P/B oranları
        actual_p_prob = 0.0
        if window_len > 0:
            p_wins = window.count('P')
            actual_p_prob = (p_wins / window_len) * 100
        else:
            # Yeterli geçmiş yoksa, temel olasılığa daha yakın olalım
            actual_p_prob = self.BASE_P_PROB_NO_TIE

        # Sapmayı hesapla (P'nin teorikten ne kadar saptığı)
        deviation = actual_p_prob - self.BASE_P_PROB_NO_TIE

        # Temel olasılıkları sapmaya göre ayarla
        # Eğer P fazla geldiyse (deviation > 0), B'nin olasılığını artır, P'ninkini azalt.
        # Eğer B fazla geldiyse (deviation < 0), P'nin olasılığını artır, B'ninkini azalt.
        adjustment = deviation * self.deviation_influence
        adjusted_p_prob = self.BASE_P_PROB_NO_TIE - adjustment
        adjusted_b_prob = self.BASE_B_PROB_NO_TIE + adjustment

        # Olasılıkları 0-100 arasında tut (çok küçük ihtimal ama garanti olsun)
        adjusted_p_prob = max(0.1, min(99.9, adjusted_p_prob))
        adjusted_b_prob = max(0.1, min(99.9, adjusted_b_prob))

        # --- Kuantum Sıçraması! ---
        if random.random() < self.quantum_leap_chance:
             # Düşük olasılıklı olanı seçme şansı
             # print("Quantum Leap!") # Debug
             return 'P' if adjusted_p_prob < adjusted_b_prob else 'B'
        # --- Normal Tahmin ---
        else:
             # Daha yüksek olasılıklı olanı seç
             return 'P' if adjusted_p_prob >= adjusted_b_prob else 'B'


    def _get_adjusted_probs(self, history: list) -> tuple[float, float]:
        """Yardımcı fonksiyon: Ayarlanmış P ve B olasılıklarını hesaplar."""
        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.deviation_window:]
        window_len = len(window)
        actual_p_prob = self.BASE_P_PROB_NO_TIE # Başlangıç değeri
        if window_len > 0:
            p_wins = window.count('P')
            actual_p_prob = (p_wins / window_len) * 100

        deviation = actual_p_prob - self.BASE_P_PROB_NO_TIE
        adjustment = deviation * self.deviation_influence
        adjusted_p_prob = self.BASE_P_PROB_NO_TIE - adjustment
        adjusted_b_prob = self.BASE_B_PROB_NO_TIE + adjustment
        adjusted_p_prob = max(0.1, min(99.9, adjusted_p_prob))
        adjusted_b_prob = max(0.1, min(99.9, adjusted_b_prob))
        return adjusted_p_prob, adjusted_b_prob


    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Güven, iki ayarlanmış olasılık arasındaki farka göre belirlenir.
        adj_p, adj_b = self._get_adjusted_probs(history)
        diff = abs(adj_p - adj_b)

        # Fark ne kadar büyükse, o kadar güvenli.
        # Fark 0 (%50/%50) ise min güven, fark ~100 ise max güven.
        confidence = 20.0 + (diff * 0.7) # %20 taban + farkın %70'i kadar ekle

        return max(20.0, min(90.0, confidence)) # %20-90 arası


    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Tahmin edilen tarafın ayarlanmış olasılığını döndürür.
        prediction = self.predict(history) # Predict'i tekrar çağırmak ideal değil ama basitlik için
                                         # Not: Quantum leap olasılığı etkilemez, sadece seçimi değiştirir.
        if prediction == "N/A": # Bu modelde N/A dönmez ama kontrol edelim
            return 0.0

        adj_p, adj_b = self._get_adjusted_probs(history)

        if prediction == 'P':
            return adj_p
        elif prediction == 'B':
            return adj_b
        else:
             return 0.0
