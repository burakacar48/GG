from collections import Counter

class PatternMatcherPredictor:
    """
    Geçmişteki belirli bir uzunluktaki (n-gram) desenlerin
    tekrarlandığında hangi sonucun geldiğine bakarak tahmin yapar.
    """
    def __init__(self, n=3):
        # Aranacak desenin uzunluğu (n-gram)
        self.n = max(2, n) # En az 2'li desenlere bakalım

    def predict(self, history: list) -> str:
        """
        Verilen geçmişe göre bir sonraki hamleyi tahmin eder.
        En son n-gram desenini bulur, geçmişte bu desenden sonra
        en sık gelen sonucu ('P' veya 'B') tahmin eder.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]

        # Tahmin için en az n+1 eleman gerekli (n desen + 1 sonraki)
        if len(relevant_history) < self.n + 1:
            return "N/A"

        # Son n elemanı (aranacak desen) al
        last_pattern = tuple(relevant_history[-self.n:]) # Tuple yapıyoruz çünkü dict key olabilir

        # Geçmişte bu desenden sonra ne geldiğini sayalım
        next_elements = []
        # Aramayı sondan bir önceki n-gram'a kadar yapabiliriz
        for i in range(len(relevant_history) - self.n):
            current_pattern = tuple(relevant_history[i:i + self.n])
            if current_pattern == last_pattern:
                # Deseni bulduk, bir sonraki elemanı ekle
                next_element = relevant_history[i + self.n]
                next_elements.append(next_element)

        if not next_elements:
            # Desen geçmişte daha önce bulunamadı
            return "N/A"

        # En sık gelen sonraki elemanı bul
        counts = Counter(next_elements)
        most_common = counts.most_common(2) # En sık gelen 1 veya 2 elemanı al

        if len(most_common) == 1:
            # Sadece bir tür sonuç gelmiş (P veya B)
            return most_common[0][0]
        elif len(most_common) == 2:
            # İki tür sonuç da gelmiş, sayıları karşılaştır
            if most_common[0][1] > most_common[1][1]:
                # İlk sıradaki daha sık gelmiş
                return most_common[0][0]
            elif most_common[1][1] > most_common[0][1]:
                 # İkinci sıradaki daha sık gelmiş (Bu pratikte olmaz ama kontrol edelim)
                 return most_common[1][0]
            else:
                # Sayılar eşit, tahmin yapılamıyor
                return "N/A"
        else:
             # Hiçbir şey bulunamadı (pratikte olmaz)
             return "N/A"

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        if len(relevant_history) < self.n + 1: return 0.0

        last_pattern = tuple(relevant_history[-self.n:])
        next_elements = []
        for i in range(len(relevant_history) - self.n):
            if tuple(relevant_history[i:i + self.n]) == last_pattern:
                next_elements.append(relevant_history[i + self.n])

        if not next_elements: return 0.0

        counts = Counter(next_elements)
        total_found = len(next_elements)
        predicted_count = counts.get(prediction, 0)
        other_prediction = 'B' if prediction == 'P' else 'P'
        other_count = counts.get(other_prediction, 0)

        # Güven: Fark ne kadar büyükse ve toplam tekrar ne kadar fazlaysa o kadar yüksek
        # Basit formül: (Tahmin edilenin oranı - Diğerinin oranı) * 50 + 50, tekrar sayısına göre ayarla
        if total_found == 0: return 30.0 # Emin değiliz

        dominance_factor = abs(predicted_count - other_count) / total_found
        # Tekrar sayısı azsa güveni düşür (logaritmik etki)
        import math
        count_factor = min(1.0, math.log10(total_found + 1)) # +1 log(1)=0 olmasın diye

        confidence = 50.0 + (dominance_factor * 40.0) # Dominansa göre %50 +/- 40 arası
        confidence *= count_factor # Tekrar sayısına göre ayarla

        return max(25.0, min(95.0, confidence)) # Güveni %25-95 arasında tut


    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        if len(relevant_history) < self.n + 1: return 0.0

        last_pattern = tuple(relevant_history[-self.n:])
        next_elements = []
        for i in range(len(relevant_history) - self.n):
             if tuple(relevant_history[i:i + self.n]) == last_pattern:
                next_elements.append(relevant_history[i + self.n])

        if not next_elements: return 50.0 # Desen bulunamadıysa %50 diyelim

        total_found = len(next_elements)
        predicted_count = next_elements.count(prediction)

        probability = (predicted_count / total_found) * 100 if total_found > 0 else 50.0

        # Olasılığı biraz 50'ye çekelim (çok emin olmamak için)
        balanced_prob = 50.0 + (probability - 50.0) * 0.85

        return max(15.0, min(85.0, balanced_prob)) # Olasılığı %15-85 arasında tut
