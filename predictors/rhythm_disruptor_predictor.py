class RhythmDisruptorPredictor:
    """
    Kısa (3'lü veya 4'lü) PBPB... gibi almaşık (alternating)
    ritimleri tespit edip, ritmin devamını kırmayı hedefler.
    """

    def predict(self, history: list) -> str:
        """
        Son 3 veya 4 ele bakarak almaşık bir ritim varsa,
        bu ritmi bozacak tahmini yapar. Yoksa 'N/A' döner.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        history_len = len(relevant_history)

        # Önce 4'lü ritmi kontrol et (daha güçlü bir işaret olabilir)
        if history_len >= 4:
            # Son 4 el: ...A B A B
            last_4 = relevant_history[-4:]
            # A!=B, B==B(kendi), A==A(kendi), B!=A olmalı
            if (last_4[0] != last_4[1] and
                    last_4[1] == last_4[3] and # 2. ve 4. aynı
                    last_4[0] == last_4[2]):   # 1. ve 3. aynı
                # Ritmin devamı 4. eleman ('B' gibi) olurdu, biz tam tersini ('A' gibi, yani 3. elemanı) tahmin edelim.
                # print("Disrupting 4-beat rhythm!") # Debug
                return last_4[2] # Ritmi bozmak için sondan bir öncekini tekrar et

        # 4'lü ritim yoksa veya yeterli el yoksa 3'lü ritmi kontrol et
        if history_len >= 3:
             # Son 3 el: ...A B A
            last_3 = relevant_history[-3:]
             # A!=B ve B!=A olmalı (zaten öyle) ve A==A olmalı
            if last_3[0] != last_3[1] and last_3[0] == last_3[2]:
                # Ritmin devamı (Zigzag gibi) B olurdu, biz tam tersini (A'yı) tahmin edelim.
                # print("Disrupting 3-beat rhythm!") # Debug
                return last_3[2] # Ritmi bozmak için sonuncuyu tekrar et

        # Belirgin bir 3'lü veya 4'lü almaşık ritim bulunamadı
        return "N/A"


    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        # Bu model oldukça spesifik durumlarda tetiklendiği için,
        # tetiklendiğinde nispeten daha yüksek bir güven verelim.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Belki 4'lü ritmi bozmak 3'lüden daha güvenlidir?
             relevant_history = [res for res in history if res in ('P', 'B')]
             if len(relevant_history) >= 4:
                 last_4 = relevant_history[-4:]
                 if (last_4[0] != last_4[1] and last_4[1] == last_4[3] and last_4[0] == last_4[2]):
                      return 70.0 # 4'lü ritim kırılması
             if len(relevant_history) >= 3:
                  last_3 = relevant_history[-3:]
                  if last_3[0] != last_3[1] and last_3[0] == last_3[2]:
                       return 60.0 # 3'lü ritim kırılması
             # Eğer predict N/A değilse buraya düşmemeli ama yedek
             return 50.0


    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Ritmi bozmak ne kadar olası? %50'den biraz daha düşük tutabiliriz.
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0
        else:
            # Belki 4'lü ritmin kırılması 3'lüden biraz daha olasıdır?
            relevant_history = [res for res in history if res in ('P', 'B')]
            if len(relevant_history) >= 4:
                last_4 = relevant_history[-4:]
                if (last_4[0] != last_4[1] and last_4[1] == last_4[3] and last_4[0] == last_4[2]):
                     return 48.0
            if len(relevant_history) >= 3:
                 last_3 = relevant_history[-3:]
                 if last_3[0] != last_3[1] and last_3[0] == last_3[2]:
                      return 45.0
            return 40.0 # Yedek
