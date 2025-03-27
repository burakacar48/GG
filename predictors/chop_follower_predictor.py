class ChopFollowerPredictor:
    """
    "Kesme/Sekme Takibi" (Ping Pong): Sürekli P-B-P-B gibi
    almaşık giden bir düzeni ("chop") algılar ve bu düzenin
    devam edeceğini tahmin eder. Yani son sonucun tersini tahmin eder.
    """

    def predict(self, history: list) -> str:
        """
        Son iki el farklıysa (P-B veya B-P), bu sekme düzeninin
        devam edeceğini varsayarak son elin TERSİNİ tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Tahmin için en az 1 önceki el gerekli (sonuca bakmak için)
        # Ama mantık 2 ele dayandığı için 2 diyelim.
        if len(relevant_history) < 2:
            return "N/A" # Sekme kontrolü için yeterli veri yok

        last_result = relevant_history[-1]
        second_last_result = relevant_history[-2]

        # Sekme durumu var mı? (Son iki el farklı mı?)
        if last_result != second_last_result:
            # Evet, sekme var (P-B veya B-P). Sekmenin devamını tahmin et.
            # Yani son sonucun tersini.
            # print(f"Following the Chop! Last was {last_result}, predicting opposite.") # Debug
            return 'B' if last_result == 'P' else 'P'
        else:
            # Sekme yok (PP veya BB), bu model yorum yapmaz.
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Sekme ne kadar uzun süredir devam ediyorsa, güven o kadar artabilir.
        relevant_history = [res for res in history if res in ('P', 'B')]
        chop_length = 0
        if len(relevant_history) >= 2:
            # Sondan başlayarak ne kadar süredir P-B-P-B gittiğine bak
            for i in range(len(relevant_history) - 1, 0, -1):
                if relevant_history[i] != relevant_history[i-1]:
                    chop_length += 1
                else:
                    break # Sekme bitti
            # Eğer son iki farklıysa, chop_length en az 1'dir. İlk farklılık 1 sayılır.
            # Gerçek sekme uzunluğu için +1 ekleyebiliriz.
            if relevant_history[-1] != relevant_history[-2]:
                 chop_length += 1 # Mevcut son farklılığı da say

        # Sekme uzunluğuna göre güveni ayarla
        base_confidence = 50.0
        confidence_increase = max(0, chop_length - 2) * 6.0 # İlk 2'den sonraki her sekme için +6
        confidence = base_confidence + confidence_increase

        return min(85.0, confidence) # Max %85 güven

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Sekmenin devam etme olasılığı genellikle %50 civarındadır.
        # Güvene benzer şekilde hafifçe ayarlayalım.
        relevant_history = [res for res in history if res in ('P', 'B')]
        chop_length = 0
        # ... (confidence'daki gibi chop_length hesaplama) ...
        if len(relevant_history) >= 2:
            for i in range(len(relevant_history) - 1, 0, -1):
                if relevant_history[i] != relevant_history[i-1]: chop_length += 1
                else: break
            if relevant_history[-1] != relevant_history[-2]: chop_length += 1

        base_probability = 50.0
        probability_increase = max(0, chop_length - 2) * 2.0
        probability = base_probability + probability_increase

        return max(45.0, min(60.0, probability)) # Olasılığı %45-60 arası tutalım
