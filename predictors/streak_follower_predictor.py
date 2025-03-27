class StreakFollowerPredictor:
    """
    Belirli bir uzunluktaki (streak_length) P veya B serisini algıladığında,
    serinin devam edeceğini tahmin eden model.
    """
    def __init__(self, streak_length=3):
        # Takip etmeye başlamak için gereken minimum seri uzunluğu
        self.streak_length = max(2, streak_length) # En az 2 olmalı

    def predict(self, history: list) -> str:
        """
        Verilen geçmişe göre bir sonraki hamleyi tahmin eder.
        Seri yeterince uzunsa devamını, değilse 'N/A' döndürür.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        if len(relevant_history) < self.streak_length:
            return "N/A" # Seri takibi için yeterli veri yok

        # Son 'streak_length' kadar elemana bak
        last_streak_elements = relevant_history[-self.streak_length:]

        # Hepsi aynı mı diye kontrol et
        first_element = last_streak_elements[0]
        is_streak = all(elem == first_element for elem in last_streak_elements)

        if is_streak:
            # Seri varsa, serinin devamını (yani aynı elemanı) tahmin et
            return first_element
        else:
            # Yeterli uzunlukta bir seri yok
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        # Mevcut serinin gerçek uzunluğunu bul
        current_streak_len = 0
        if relevant_history:
            last_val = relevant_history[-1]
            for i in range(len(relevant_history) - 1, -1, -1):
                if relevant_history[i] == last_val:
                    current_streak_len += 1
                else:
                    break

        # Seri ne kadar uzunsa, güven o kadar artsın (basit örnek)
        # self.streak_length'den sonra her ek adım için güveni artıralım
        confidence = 50.0 + (max(0, current_streak_len - self.streak_length) * 8)
        return max(30.0, min(90.0, confidence)) # Güveni %30-90 arasında tut

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        if not relevant_history: return 50.0

        # Genel P/B oranını kullanabiliriz ama seri takibi için çok anlamlı değil.
        # Belki serinin uzunluğuna göre sabit bir olasılık verebiliriz?
        # Veya geçmişte benzer uzunluktaki serilerin ne kadar devam ettiğine bakılabilir (daha karmaşık)
        # Şimdilik, serinin uzunluğuna göre hafif artan bir olasılık verelim.
        current_streak_len = 0
        # ... (confidence'daki gibi serinin uzunluğunu bulma kodu) ...
        if relevant_history:
            last_val = relevant_history[-1]
            for i in range(len(relevant_history) - 1, -1, -1):
                if relevant_history[i] == last_val: current_streak_len += 1
                else: break

        probability = 50.0 + (max(0, current_streak_len - self.streak_length) * 3)
        return max(40.0, min(75.0, probability)) # Olasılığı %40-75 arasında tut
