class StreakBreakerPredictor:
    """
    Belirli bir uzunluktaki (streak_length) P veya B serisini algıladığında,
    serinin KIRILACAĞINI (yani tersini) tahmin eden model.
    """
    def __init__(self, streak_length=3):
        # Kırmayı düşünmek için gereken minimum seri uzunluğu
        self.streak_length = max(2, streak_length) # En az 2 olmalı

    def predict(self, history: list) -> str:
        """
        Verilen geçmişe göre bir sonraki hamleyi tahmin eder.
        Seri yeterince uzunsa tersini, değilse 'N/A' döndürür.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        if len(relevant_history) < self.streak_length:
            return "N/A" # Seri kırılması tahmini için yeterli veri yok

        # Son 'streak_length' kadar elemana bak
        last_streak_elements = relevant_history[-self.streak_length:]

        # Hepsi aynı mı diye kontrol et
        first_element = last_streak_elements[0]
        is_streak = all(elem == first_element for elem in last_streak_elements)

        if is_streak:
            # Seri varsa, serinin TERSİNİ tahmin et (kırılma)
            return 'B' if first_element == 'P' else 'P'
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
                    break # Seri bitti

        # Seri ne kadar uzunsa, kırılma ihtimali (ve güven) o kadar artsın (basit örnek)
        confidence = 40.0 + (max(0, current_streak_len - self.streak_length) * 10)
        return max(30.0, min(90.0, confidence)) # Güveni %30-90 arasında tut

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Seri kırılma olasılığı genellikle serinin devam etme olasılığından
        # biraz daha düşüktür, ancak seri uzadıkça artar.
        # Yine serinin uzunluğuna göre bir olasılık atayalım.
        current_streak_len = 0
        # ... (confidence'daki gibi serinin uzunluğunu bulma kodu) ...
        relevant_history = [res for res in history if res in ('P', 'B')] # Yeniden ekleyelim
        if relevant_history:
            last_val = relevant_history[-1]
            for i in range(len(relevant_history) - 1, -1, -1):
                if relevant_history[i] == last_val: current_streak_len += 1
                else: break

        probability = 45.0 + (max(0, current_streak_len - self.streak_length) * 5)
        return max(35.0, min(70.0, probability)) # Olasılığı %35-70 arasında tut
