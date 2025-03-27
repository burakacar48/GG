class MirrorPredictor:
    """
    Ayakkabının başındaki ele bakarak tahmin yapar.
    Tahmin edilecek elin sırasına (Tie'lar hariç) bakar ve
    ayakkabının başındaki aynı sıradaki elin sonucunu tahmin eder.
    """
    def predict(self, history: list) -> str:
        """
        Tahmin edilecek elin index'ine bakar ve history'de o index'teki
        (Tie'lar hariç) elemanı tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        # Tahmin edeceğimiz elin relevant_history içindeki sırası (0-bazlı index)
        prediction_index = len(relevant_history)

        # Eğer geçmişte bu index'te bir el varsa (yani en az o kadar el oynanmışsa)
        if prediction_index < len(relevant_history): # Bu kontrol hala tam doğru değil, index'in varlığını kontrol etmeli
             # Düzeltme: relevant_history'nin o index'e sahip olup olmadığını kontrol etmeliyiz.
             if 0 <= prediction_index < len(relevant_history):
                 mirrored_result = relevant_history[prediction_index]
                 return mirrored_result
             else:
                 # Bu index geçmişte yok (örneğin ilk birkaç el)
                 return "N/A"
        else:
             # Geçmiş, tahmin edeceğimiz index'e henüz ulaşmamış.
             # Bu durum, history'nin tam listeyi içerdiği varsayımıyla
             # aslında olmamalı, ama güvenlik için ekleyelim.
              if 0 <= prediction_index < len(relevant_history): # Tekrar kontrol edelim
                    mirrored_result = relevant_history[prediction_index]
                    return mirrored_result
              else:
                   return "N/A"

         # Mantıksal Hata Düzeltmesi:
         # 'prediction_index' bir sonraki elin index'idir.
         # Geçmişte bu index'e karşılık gelen elemanı arıyoruz.
         # Yani relevant_history[prediction_index] değerini okumalıyız.
         # Bunun için listenin yeterince uzun olması lazım.
        if prediction_index < len(relevant_history): # Bu, mevcut listede o index var demek.
             try:
                 mirrored_result = relevant_history[prediction_index]
                 return mirrored_result
             except IndexError:
                 # Eğer index list sınırları dışındaysa (olmamalı ama kontrol)
                 return "N/A"
        else:
             # Listenin kendisi o kadar uzun değil, yani o index'te bir el yok.
             return "N/A"


    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Bu model batıl inanca dayalı olduğu için sabit veya düşük bir güven verelim.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        # Belki ayna deseni şu ana kadar ne kadar tuttu diye bakılabilir (karmaşık)
        # Şimdilik sabit verelim.
        return 30.0

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Yine batıl inanç, %50 diyelim.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0 # veya 50.0?
        return 50.0
