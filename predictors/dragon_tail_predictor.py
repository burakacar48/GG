class DragonTailPredictor:
    """
    "Ejderha Takibi" Modeli: Belirli bir minimum uzunluktaki (genellikle 6+)
    kesintisiz P veya B serisini ("Ejderha") algılar ve kırılana kadar
    bu serinin devamını tahmin eder.
    """
    def __init__(self, min_dragon_length=6):
        # Ejderha olarak kabul edilecek minimum seri uzunluğu
        self.min_dragon_length = max(3, min_dragon_length) # En az 3 mantıklı olur

    def predict(self, history: list) -> str:
        """
        Geçmişe bakarak bir "Ejderha" serisi varsa ve devam ediyorsa,
        serinin bir sonraki adımını tahmin eder. Yoksa 'N/A' döner.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        history_len = len(relevant_history)

        # Tahmin için en az minimum ejderha uzunluğu kadar el olmalı
        if history_len < self.min_dragon_length:
            return "N/A"

        # Mevcut serinin ne olduğunu ve ne kadar uzun olduğunu bulalım
        current_streak_element = relevant_history[-1]
        current_streak_length = 0
        for i in range(history_len - 1, -1, -1):
            if relevant_history[i] == current_streak_element:
                current_streak_length += 1
            else:
                break # Seri bitti

        # Şu anki seri bir Ejderha mı? (Yeterince uzun mu?)
        if current_streak_length >= self.min_dragon_length:
            # Evet, bir ejderhanın kuyruğundayız! Takip et!
            # print(f"Following the Dragon ({current_streak_element})! Length: {current_streak_length}") # Debug
            return current_streak_element
        else:
            # Ya seri kırıldı ya da henüz Ejderha boyutuna ulaşmadı.
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Ejderha ne kadar uzunsa, güven o kadar yüksek olsun!
        relevant_history = [res for res in history if res in ('P', 'B')]
        current_streak_length = 0
        # ... (predict'teki gibi serinin uzunluğunu bul) ...
        if relevant_history:
             current_streak_element = relevant_history[-1]
             for i in range(len(relevant_history) - 1, -1, -1):
                 if relevant_history[i] == current_streak_element: current_streak_length += 1
                 else: break

        # Min uzunluktan sonraki her adım için güveni artıralım
        base_confidence = 65.0 # Ejderhayı yakaladık, temel güven yüksek!
        confidence_increase = max(0, current_streak_length - self.min_dragon_length) * 5.0
        confidence = base_confidence + confidence_increase

        return min(95.0, confidence) # Max %95 güven


    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Ejderhanın devam etme olasılığı genellikle %50'den biraz düşüktür
        # ama uzun serilerde bu kural bazen bozulur (veya öyle hissedilir).
        # Güvene benzer şekilde, seri uzadıkça olasılığı hafifçe artıralım.
        relevant_history = [res for res in history if res in ('P', 'B')]
        current_streak_length = 0
        # ... (predict'teki gibi serinin uzunluğunu bul) ...
        if relevant_history:
             current_streak_element = relevant_history[-1]
             for i in range(len(relevant_history) - 1, -1, -1):
                 if relevant_history[i] == current_streak_element: current_streak_length += 1
                 else: break

        base_probability = 50.0 # Başlangıç
        # Uzun serilerde hafif artış (momentuma inanç)
        probability_increase = max(0, current_streak_length - self.min_dragon_length) * 1.5
        probability = base_probability + probability_increase

        return max(45.0, min(65.0, probability)) # Olasılığı %45-65 arası tutalım
