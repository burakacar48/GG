import math

class StatisticalDeviationPredictor:
    """
    Son N eldeki P/B kazanma oranlarının teorik olasılıklardan
    sapmasına bakarak 'ortalamaya dönüş' prensibiyle tahmin yapar.
    Eğer bir taraf fazla kazandıysa, diğerini tahmin eder.
    """
    THEO_BANKER_PROB = 50.68 # Tie'lar hariç yaklaşık teorik Banker kazanma oranı
    THEO_PLAYER_PROB = 49.32 # Tie'lar hariç yaklaşık teorik Player kazanma oranı

    def __init__(self, window_size=30, deviation_threshold=4.0, min_hands=15):
        # İstatistikleri hesaplamak için bakılacak el sayısı
        self.window_size = max(10, window_size)
        # Tahmin yapmak için gereken minimum sapma (yüzde puanı)
        self.deviation_threshold = max(1.0, deviation_threshold)
        # Tahmin yapmak için pencerede gereken minimum el sayısı
        self.min_hands_in_window = max(5, min_hands)

    def predict(self, history: list) -> str:
        """
        Verilen geçmişe göre bir sonraki hamleyi tahmin eder.
        Sapma yeterince büyükse, az performans gösteren tarafı tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Penceredeki son ellere bak
        window = relevant_history[-self.window_size:]
        window_len = len(window)

        # Tahmin için yeterli el var mı?
        if window_len < self.min_hands_in_window:
            return "N/A"

        # Penceredeki P/B sayılarını hesapla
        p_wins = window.count('P')
        b_wins = window.count('B')

        # Gerçek yüzdeleri hesapla
        actual_p_perc = (p_wins / window_len) * 100
        actual_b_perc = (b_wins / window_len) * 100

        # Teorik değerlerden sapmaları hesapla
        p_deviation = actual_p_perc - self.THEO_PLAYER_PROB
        b_deviation = actual_b_perc - self.THEO_BANKER_PROB

        # Hangi tarafın fazla saptığına (pozitif yönde) bak
        if p_deviation >= self.deviation_threshold:
            # Player fazla kazanmış, Banker'ın gelmesini bekle (Ortalamaya dönüş)
            return 'B'
        elif b_deviation >= self.deviation_threshold:
            # Banker fazla kazanmış, Player'ın gelmesini bekle (Ortalamaya dönüş)
            return 'P'
        else:
            # Belirgin bir sapma yok
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)
        if window_len < self.min_hands_in_window: return 0.0

        p_wins = window.count('P'); b_wins = window.count('B')
        actual_p_perc = (p_wins / window_len) * 100
        actual_b_perc = (b_wins / window_len) * 100
        p_deviation = actual_p_perc - self.THEO_PLAYER_PROB
        b_deviation = actual_b_perc - self.THEO_BANKER_PROB

        # Güven, sapmanın büyüklüğüne göre artsın
        # Eğer 'B' tahmin ediliyorsa p_deviation'a, 'P' tahmin ediliyorsa b_deviation'a bak
        deviation_magnitude = 0
        if prediction == 'B':
            deviation_magnitude = p_deviation # Player ne kadar fazla saptıysa o kadar güvenli B tahmini
        elif prediction == 'P':
            deviation_magnitude = b_deviation # Banker ne kadar fazla saptıysa o kadar güvenli P tahmini

        # Sapmayı güven skoruna dönüştür (örnek formül)
        # Threshold'dan sonra her %1 sapma için güveni artıralım
        base_confidence = 40.0 # Minimum güven
        confidence_increase = max(0, deviation_magnitude - self.deviation_threshold) * 5.0 # Her % puan için +5
        confidence = base_confidence + confidence_increase

        return max(30.0, min(90.0, confidence)) # Güveni %30-90 arasında tut

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0 # veya 50.0?

        # Basitçe, tahmin edilen tarafın teorik olasılığını döndürelim
        if prediction == 'P':
            return self.THEO_PLAYER_PROB
        elif prediction == 'B':
            return self.THEO_BANKER_PROB
        else:
            return 0.0 # N/A durumu
