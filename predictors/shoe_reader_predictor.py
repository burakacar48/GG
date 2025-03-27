class ShoeReaderPredictor:
    """
    Ayakkabı Okuyucu (Big Eye Boy Taklitçisi - Basit):
    Son N eldeki değişim (chop) sayısına bakarak ayakkabının
    "düzenli" mi (seri ağırlıklı) yoksa "karışık" mı (kesme ağırlıklı)
    olduğuna karar verir ve buna uygun başka bir modelin tahminini kullanır.
    """

    def __init__(self, window_size=15, chop_threshold_ratio=0.45,
                 orderly_model_name="Seri Takip (3)", # Düzenli ayakkabıda kullanılacak modelin adı
                 choppy_model_name="Kesme Takibi (Ping Pong)" # Karışık ayakkabıda kullanılacak modelin adı
                 ):
        self.window_size = max(5, window_size)
        # Eşik oranı: Pencerenin % kaçından fazlası değişim ise karışık sayılır
        self.chop_threshold_ratio = max(0.1, min(0.9, chop_threshold_ratio))
        self.orderly_model_key = orderly_model_name # main.py'deki dict key'i
        self.choppy_model_key = choppy_model_name   # main.py'deki dict key'i

    def _calculate_chops(self, history_window: list) -> int:
        """Verilen penceredeki P/B değişim sayısını hesaplar."""
        chops = 0
        for i in range(len(history_window) - 1):
            if history_window[i] != history_window[i+1]:
                chops += 1
        return chops

    def predict(self, history: list, current_predictions: dict) -> str:
        """
        Ayakkabı karakterini analiz eder ve uygun modelin tahminini döndürür.
        'current_predictions' o an diğer modellerin yaptığı tahminleri içerir.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)

        if window_len < 5: # Analiz için minimum el
            return "N/A"

        num_chops = self._calculate_chops(window)
        chop_ratio = num_chops / (window_len - 1) if window_len > 1 else 0 # Değişim oranı

        # Eşiği hesapla (en az 1 chop olmalı)
        threshold_count = max(1, int((window_len - 1) * self.chop_threshold_ratio))

        # print(f"Shoe Reader: Window={window_len}, Chops={num_chops}, Ratio={chop_ratio:.2f}, ThresholdCount={threshold_count}") # Debug

        chosen_model_key = None
        if num_chops < threshold_count:
            # Az değişim var -> Ayakkabı Düzenli (Seri Ağırlıklı)
            # print("Shoe Reader: Prefers Orderly Model") # Debug
            chosen_model_key = self.orderly_model_key
        else:
            # Çok değişim var -> Ayakkabı Karışık (Kesme Ağırlıklı)
            # print("Shoe Reader: Prefers Choppy Model") # Debug
            chosen_model_key = self.choppy_model_key

        # Seçilen modelin bu turdaki tahminini al
        prediction = current_predictions.get(chosen_model_key, "N/A") # Seçilen model tahmin yapmadıysa N/A

        # Güvenlik: Eğer seçilen model N/A dediyse, biz de N/A diyelim
        if prediction not in ('P', 'B'):
             return "N/A"

        return prediction

    def get_confidence(self, history: list, current_predictions: dict, chosen_model_confidence: float = 50.0) -> float:
        """Tahminin güven oranını döndürür."""
        # Güveni, seçilen altta yatan modelin güvenine göre ayarlayalım.
        # Ayrıca, ayakkabının ne kadar net bir şekilde düzenli/karışık olduğuna göre de modifiye edebiliriz.
        prediction = self.predict(history, current_predictions) # Tekrar hesaplama (ideal değil)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        window = relevant_history[-self.window_size:]
        window_len = len(window)
        if window_len < 5: return 0.0

        num_chops = self._calculate_chops(window)
        chop_ratio = num_chops / (window_len - 1) if window_len > 1 else 0
        threshold_count = max(1, int((window_len - 1) * self.chop_threshold_ratio))

        # Ayakkabının ne kadar 'net' olduğuna dair bir ölçüm (0-1 arası)
        # Eşikten ne kadar uzaklaştığına bakabiliriz.
        clarity_factor = 0.0
        mid_point_ratio = self.chop_threshold_ratio # Aslında threshold_count / (win_len-1) daha doğru
        if window_len > 1:
             mid_point_ratio = threshold_count / (window_len - 1)

        # Eşikten uzaklık (normalize edilmiş)
        clarity_factor = abs(chop_ratio - mid_point_ratio) / max(mid_point_ratio, 1.0 - mid_point_ratio) if mid_point_ratio > 0 and mid_point_ratio < 1 else 0.5
        clarity_factor = min(1.0, clarity_factor * 1.5) # Etkiyi biraz artır

        # Güven = Seçilen Modelin Güveni * (0.8 + ClarityFactor * 0.4)
        # Yani netlik arttıkça güven %80'den %120'ye kadar çıkabilir (sonra sınırlanır).
        final_confidence = chosen_model_confidence * (0.8 + clarity_factor * 0.4)

        return max(20.0, min(95.0, final_confidence)) # %20-95 arası


    def get_probability(self, history: list, current_predictions: dict, chosen_model_probability: float = 50.0) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        # Basitçe seçilen altta yatan modelin olasılığını döndürelim.
        prediction = self.predict(history, current_predictions)
        if prediction == "N/A":
            return 0.0
        else:
            # Belki netlik faktörüne göre hafifçe 50'ye çekilebilir ama şimdilik direkt döndürelim.
            return max(10.0, min(90.0, chosen_model_probability)) # %10-90 arası
