class AntiStatsPredictor:
    """
    İstatistikçi'nin Kabusu! Sapma Analizcisinin tam tersini yapar.
    Bir taraf teorik olasılıklardan belirgin şekilde sapmışsa,
    sapmanın DEVAM EDECEĞİNE inanır ve sapan tarafı tahmin eder.
    'Ortalamaya dönüş' fikrine karşı çıkar, 'sıcak el' mantığı güder.
    """
    # Sapma Analizcisi ile aynı teorik olasılıkları kullanabiliriz
    THEO_BANKER_PROB = 50.68
    THEO_PLAYER_PROB = 49.32

    def __init__(self, window_size=30, deviation_threshold=4.0, min_hands=15):
        # Parametreler Sapma Analizcisi ile aynı veya farklı olabilir
        self.window_size = max(10, window_size)
        self.deviation_threshold = max(1.0, deviation_threshold)
        self.min_hands_in_window = max(5, min_hands)

    def predict(self, history: list) -> str:
        """
        Verilen geçmişe göre bir sonraki hamleyi tahmin eder.
        Sapma yeterince büyükse, FAZLA performans gösteren tarafı tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)

        if window_len < self.min_hands_in_window:
            return "N/A"

        p_wins = window.count('P'); b_wins = window.count('B')
        actual_p_perc = (p_wins / window_len) * 100
        actual_b_perc = (b_wins / window_len) * 100
        p_deviation = actual_p_perc - self.THEO_PLAYER_PROB # P ne kadar fazla?
        b_deviation = actual_b_perc - self.THEO_BANKER_PROB # B ne kadar fazla?

        # Hangi taraf eşiği pozitif yönde aştıysa, o tarafın devam edeceğini tahmin et
        if p_deviation >= self.deviation_threshold:
            # Player fazla kazanmış ve momentumda, Player devam eder!
            return 'P'
        elif b_deviation >= self.deviation_threshold:
            # Banker fazla kazanmış ve momentumda, Banker devam eder!
            return 'B'
        else:
            # Belirgin bir sapma (momentum) yok
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Sapma Analizcisi ile benzer mantık: Sapma ne kadar büyükse güven o kadar yüksek.
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)
        if window_len < self.min_hands_in_window: return 0.0

        p_wins = window.count('P'); b_wins = window.count('B')
        actual_p_perc = (p_wins / window_len) * 100; actual_b_perc = (b_wins / window_len) * 100
        p_deviation = actual_p_perc - self.THEO_PLAYER_PROB
        b_deviation = actual_b_perc - self.THEO_BANKER_PROB

        deviation_magnitude = 0
        if prediction == 'P': deviation_magnitude = p_deviation # P ne kadar fazla sapmışsa
        elif prediction == 'B': deviation_magnitude = b_deviation # B ne kadar fazla sapmışsa

        # Sapma Analizcisi ile aynı güven formülünü kullanabiliriz
        base_confidence = 40.0
        confidence_increase = max(0, deviation_magnitude - self.deviation_threshold) * 5.0
        confidence = base_confidence + confidence_increase

        return max(30.0, min(90.0, confidence))

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Momentumun devam etme olasılığı ne kadar? Belki teorik olasılıktan biraz daha yüksek?
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0

        # Tahmin edilen tarafın son penceredeki gerçek yüzdesini olasılık olarak kullanabiliriz?
        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)
        if window_len < self.min_hands_in_window: return 50.0 # Emin değiliz

        prob = 50.0
        if prediction == 'P':
            p_wins = window.count('P')
            prob = (p_wins / window_len) * 100
        elif prediction == 'B':
            b_wins = window.count('B')
            prob = (b_wins / window_len) * 100

        # Olasılığı biraz daha makul sınırlarda tutalım
        return max(40.0, min(75.0, prob)) # %40-75 arası
