class ConsensusMaverickPredictor:
    """
    Diğer modellerin tahminlerine bakar ve çoğunluğun TERSİNİ tahmin eder.
    Belirgin bir çoğunluk yoksa 'N/A' döner.
    """
    def __init__(self, threshold_percentage=70.0):
        # Çoğunluk olarak kabul edilecek minimum yüzde
        self.threshold = max(50.1, min(100.0, threshold_percentage)) # %50.1 ile %100 arası

    def predict(self, history: list, other_predictions: dict) -> str:
        """
        'other_predictions' sözlüğündeki diğer modellerin tahminlerine bakar.
        'history' bu model için doğrudan kullanılmaz.
        other_predictions formatı: {'ModelAdı': 'P', 'ModelAdı2': 'B', ...} (N/A'lar hariç)
        """
        # Sadece geçerli P veya B tahminlerini say
        valid_predictions = [pred for pred in other_predictions.values() if pred in ('P', 'B')]
        total_valid = len(valid_predictions)

        if total_valid == 0:
            # Diğer modellerden hiç geçerli tahmin gelmemiş
            return "N/A"

        p_count = valid_predictions.count('P')
        b_count = valid_predictions.count('B')

        p_percentage = (p_count / total_valid) * 100
        b_percentage = (b_count / total_valid) * 100

        # print(f"Maverick Check: P%={p_percentage:.1f}, B%={b_percentage:.1f}, Threshold={self.threshold}") # Debug

        if p_percentage >= self.threshold:
            # Çoğunluk P diyor, Maverick B diyor!
            return 'B'
        elif b_percentage >= self.threshold:
            # Çoğunluk B diyor, Maverick P diyor!
            return 'P'
        else:
            # Belirgin bir çoğunluk yok, Maverick kararsız
            return "N/A"

    def get_confidence(self, history: list, other_predictions: dict) -> float:
        """Tahminin güven oranını döndürür."""
        # Güven, çoğunluğun ne kadar 'ezici' olduğuna bağlı olabilir.
        prediction = self.predict(history, other_predictions) # Tekrar hesapla
        if prediction == "N/A":
            return 0.0

        valid_predictions = [pred for pred in other_predictions.values() if pred in ('P', 'B')]
        total_valid = len(valid_predictions)
        if total_valid == 0: return 0.0

        p_count = valid_predictions.count('P'); b_count = valid_predictions.count('B')
        p_percentage = (p_count / total_valid) * 100
        b_percentage = (b_count / total_valid) * 100

        # Çoğunluğun yüzdesi ne kadar yüksekse, tersine gitmenin 'riski' veya 'cesareti'
        # (dolayısıyla güveni?) o kadar yüksek olabilir? Ya da tam tersi?
        # Şimdilik, çoğunluk ne kadar güçlüyse, Maverick'in güveni o kadar artsın diyelim.
        majority_percentage = max(p_percentage, b_percentage)
        # Threshold'un üzerindeki her % puanı için güveni artıralım
        confidence_boost = max(0, majority_percentage - self.threshold) * 1.5
        confidence = 40.0 + confidence_boost

        return max(25.0, min(85.0, confidence)) # %25-85 arası


    def get_probability(self, history: list, other_predictions: dict) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Maverick'in olasılığı belirsizdir. Belki de çoğunluğun tersinin olasılığı?
        # Veya sabit %50'ye yakın bir değer? Şimdilik sabit verelim.
        prediction = self.predict(history, other_predictions)
        if prediction == "N/A":
            return 0.0
        else:
            # Sabit, çünkü gerçek olasılıkla ilgisi yok.
            return 45.0 # Çoğunluğa karşı olduğu için %50'den biraz düşük?
