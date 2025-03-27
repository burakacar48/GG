class StubbornSimplePredictor:
    """
    İnatçı Keçi (Basit Versiyon): Oyunun son iki P/B sonucuna göre tahmin yapar.
    - Son iki aynı ise (PP/BB) -> Tersini tahmin eder (B/P - Değişim).
    - Son iki farklı ise (PB/BP) -> İlkini tahmin eder (P/B - Düzeltme).
    """

    def predict(self, history: list) -> str:
        """
        Verilen geçmişin son iki P/B sonucuna göre tahmin yapar.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Tahmin için en az 2 önceki el gerekli
        if len(relevant_history) < 2:
            return "N/A" # Yeterli veri yok

        last_result = relevant_history[-1]
        second_last_result = relevant_history[-2]

        if last_result == second_last_result:
            # Son iki aynı (PP veya BB) -> Tersini tahmin et (İnatla Değişim!)
            return 'B' if last_result == 'P' else 'P'
        else:
            # Son iki farklı (PB veya BP) -> İlkini tahmin et (İnatla Düzeltme!)
            return second_last_result # PB -> P, BP -> B

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Bu modelin mantığı basit ve biraz keyfi olduğu için orta seviye sabit güven verelim.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Belki son iki elin aynı/farklı olmasına göre hafifçe değiştirilebilir?
            relevant_history = [res for res in history if res in ('P', 'B')]
            if len(relevant_history) >= 2:
                 if relevant_history[-1] == relevant_history[-2]:
                     return 55.0 # Aynıysa değişim tahmini biraz daha güvenli?
                 else:
                     return 50.0 # Farklıysa düzeltme tahmini?
            return 45.0 # Çok emin değiliz

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Güvene benzer şekilde, %50 civarı tutalım.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Basitçe %50 diyelim, çünkü mantık biraz keyfi.
            return 50.0
