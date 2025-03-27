class AntiMirrorPredictor:
    """
    Ayakkabının başındaki ele bakarak tahmin yapar.
    Tahmin edilecek elin sırasına bakar ve ayakkabının başındaki
    aynı sıradaki elin sonucunun TERSİNİ tahmin eder.
    """
    def predict(self, history: list) -> str:
        """
        Tahmin edilecek elin index'ine bakar ve history'de o index'teki
        elemanın tersini tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        prediction_index = len(relevant_history) # Tahmin edilecek index

        # Geçmişte bu index'te bir el var mı?
        if prediction_index < len(relevant_history):
            try:
                mirrored_result = relevant_history[prediction_index]
                # Tersini döndür
                if mirrored_result == 'P':
                    return 'B'
                elif mirrored_result == 'B':
                    return 'P'
                else: # Beklenmedik bir durum (Tie olmamalı)
                    return "N/A"
            except IndexError:
                 return "N/A"
        else:
             # Bu index'te henüz bir el yok
             return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Mirror ile aynı mantık, sabit/düşük güven.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        return 30.0

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Mirror ile aynı mantık, %50.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        return 50.0
