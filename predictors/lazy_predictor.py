class LazyPredictor:
    """
    Tahmin yapmaya 'üşenen' model. Sadece çok belirgin ve tek bir
    durumda (örneğin uzun bir seri) tahmin yapar, aksi halde 'N/A' döner.
    """
    def __init__(self, trigger_streak_length=5, follow_streak=True):
        # Tahmin yapmayı tetikleyecek seri uzunluğu
        self.trigger_streak_length = max(3, trigger_streak_length)
        # Eğer seri tetiklenirse, seriyi mi takip etsin (True) yoksa kırsın mı (False)?
        self.follow_streak = follow_streak

    def predict(self, history: list) -> str:
        """
        Sadece belirlenen uzunlukta bir seri varsa tahmin yapar.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Tetikleme uzunluğu kadar el var mı?
        if len(relevant_history) < self.trigger_streak_length:
            return "N/A" # Daha erken konuşmaya gerek yok

        # Son 'trigger_streak_length' elemana bak
        last_elements = relevant_history[-self.trigger_streak_length:]

        # Hepsi aynı mı?
        first_element = last_elements[0]
        is_trigger_streak = all(elem == first_element for elem in last_elements)

        if is_trigger_streak:
            # Evet, tembel model uyandı! Şimdi ne diyecek?
            if self.follow_streak:
                # Seriyi takip et
                return first_element
            else:
                # Seriyi kır
                return 'B' if first_element == 'P' else 'P'
        else:
            # Belirgin durum yok, tembelliğe devam...
            return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Madem konuştuk, biraz güvenimiz olsun ama abartmayalım.
            # Belki serinin trigger'dan ne kadar uzun olduğuna göre artabilir?
            relevant_history = [res for res in history if res in ('P', 'B')]
            current_streak_len = 0
            if relevant_history:
                last_val = relevant_history[-1]
                for i in range(len(relevant_history) - 1, -1, -1):
                    if relevant_history[i] == last_val: current_streak_len += 1
                    else: break
            # Trigger uzunluğundan sonraki her adım için hafif artış
            extra_streak = max(0, current_streak_len - self.trigger_streak_length)
            confidence = 60.0 + (extra_streak * 5)
            return min(85.0, confidence) # Max %85 güven

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Konuştuğuna göre olasılık fena değildir diye düşünelim.
            # Yine serinin uzunluğuna göre hafif ayar yapılabilir.
            # Şimdilik nispeten yüksek sabit bir değer verelim.
             relevant_history = [res for res in history if res in ('P', 'B')]
             current_streak_len = 0
             # ... (confidence'daki gibi serinin uzunluğunu bulma kodu) ...
             if relevant_history:
                last_val = relevant_history[-1]
                for i in range(len(relevant_history) - 1, -1, -1):
                    if relevant_history[i] == last_val: current_streak_len += 1
                    else: break
             extra_streak = max(0, current_streak_len - self.trigger_streak_length)
             probability = 55.0 + (extra_streak * 2)
             return min(70.0, probability) # Max %70 olasılık
