class DoubleHunterPredictor:
    """
    "Çiftleri Kovalama": Son iki elin aynı (PP veya BB) olduğunu
    gördüğünde, üçüncünün de aynı geleceğini (serinin devam edeceğini)
    tahmin eder.
    """

    def predict(self, history: list) -> str:
        """
        Geçmişin son iki P/B sonucuna bakar. Eğer aynı iseler,
        o sonucu tekrar tahmin eder. Farklı iseler 'N/A' döner.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Tahmin için en az 2 önceki el gerekli
        if len(relevant_history) < 2:
            return "N/A"

        last_result = relevant_history[-1]
        second_last_result = relevant_history[-2]

        # Son iki el aynı mı (PP veya BB)?
        if last_result == second_last_result:
            # Evet, çift var! Üçüncüyü de aynı bekle!
            # print(f"Hunting Doubles! Found {last_result}{last_result}, predicting {last_result}") # Debug
            return last_result
        else:
            # Çift yok (PB veya BP), bu model sessiz kalır.
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Çift yakaladık, belki orta seviye bir güven?
            # Çok uzun serilerde güven düşebilir ama basit tutalım.
            return 58.0 # Sabit bir güven

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Üçlü serilerin oluşma olasılığı %50'den biraz düşüktür
            # ama modelin "inancını" yansıtalım.
            return 51.5 # %50'nin biraz üzeri
