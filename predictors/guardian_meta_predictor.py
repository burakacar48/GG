import sys
# Diğer predictor sınıflarını import etmek GEREKEBİLİR, eğer risk analizinde
# doğrudan o sınıfların METODLARINI değil de sadece İSİMLERİNİ kullanacaksak GEREKMEYEBİLİR.
# Şimdilik sadece isimlerini kullanacağız.
from .statistical_deviation_predictor import StatisticalDeviationPredictor # Örnek

class GuardianMetaPredictor:
    """
    Vasi Meta-Tahminci: Risk analizi yapar. Risk yüksekse N/A döner.
    Risk düşük/orta ise, o ana kadar en başarılı temel modelin tahminini kullanır.
    """
    # Risk Eşikleri (Örnek - Ayarlanabilir)
    RISK_HIGH_DEVIATION_THRESHOLD_FACTOR = 1.8 # Normal sapma eşiğinin katı
    RISK_HIGH_MODEL_CONFLICT_RATIO = 0.65 # Modellerin %65'ten azı aynı fikirdeyse riskli
    RISK_MIN_PREDICTIONS_FOR_BEST = 10 # En iyi modeli seçmek için gereken min tahmin sayısı

    # Meta ve özel modelleri başarı sıralamasında dikkate almamak için isimleri
    # Not: Bu isimler main.py'deki anahtarlarla eşleşmeli!
    META_MODEL_NAMES_PREFIXES = [
        "Ayakkabı Okuyucu", "Konsensüs Kaçağı", "Ters Köşe", "Vasi Meta-Tahminci" # Kendisini de ekle
    ]

    def __init__(self, risk_params=None): # Opsiyonel risk parametreleri
        if risk_params:
            self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR = risk_params.get('deviation_factor', self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR)
            self.RISK_HIGH_MODEL_CONFLICT_RATIO = risk_params.get('conflict_ratio', self.RISK_HIGH_MODEL_CONFLICT_RATIO)
            self.RISK_MIN_PREDICTIONS_FOR_BEST = risk_params.get('min_preds', self.RISK_MIN_PREDICTIONS_FOR_BEST)
        # print(f"Guardian Initialized: DevFactor={self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR}, Conflict={self.RISK_HIGH_MODEL_CONFLICT_RATIO}, MinPreds={self.RISK_MIN_PREDICTIONS_FOR_BEST}")


    def _assess_risk(self, history: list, current_run_results: dict, predictor_stats: dict, predictors: dict) -> str:
        """Mevcut duruma göre risk seviyesini belirler: 'High', 'Medium', 'Low'."""
        risk_level = 'Low' # Başlangıçta düşük
        reasons = [] # Risk nedenleri (debug için)

        relevant_history = [res for res in history if res in ('P', 'B')]
        history_len = len(relevant_history)

        # 1. Aşırı Sapma Kontrolü
        # Sapma Analizcisi'nin parametrelerini alalım (varsa)
        sapma_predictor_instance = None
        sapma_threshold = 4.0 # Varsayılan
        sapma_window = 30   # Varsayılan
        for name, predictor in predictors.items():
             if isinstance(predictor, StatisticalDeviationPredictor):
                  sapma_predictor_instance = predictor
                  sapma_threshold = predictor.deviation_threshold
                  sapma_window = predictor.window_size
                  break

        if history_len >= sapma_window:
             window = relevant_history[-sapma_window:]
             p_wins = window.count('P')
             actual_p_perc = (p_wins / sapma_window) * 100
             deviation = abs(actual_p_perc - StatisticalDeviationPredictor.THEO_PLAYER_PROB)
             high_risk_threshold = sapma_threshold * self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR
             if deviation >= high_risk_threshold:
                  risk_level = 'High'
                  reasons.append(f"Aşırı Sapma ({deviation:.1f}% > {high_risk_threshold:.1f}%)")

        # 2. Model Çatışması Kontrolü
        valid_predictions = [data['prediction'] for data in current_run_results.values() if data['prediction'] in ('P', 'B')]
        total_valid = len(valid_predictions)
        if total_valid > 3: # En az birkaç model fikir belirtmişse
             p_count = valid_predictions.count('P')
             b_count = valid_predictions.count('B')
             max_count = max(p_count, b_count)
             consensus_ratio = max_count / total_valid
             if consensus_ratio < self.RISK_HIGH_MODEL_CONFLICT_RATIO:
                  # Yeterli çoğunluk yok, riskli olabilir
                  if risk_level != 'High': risk_level = 'Medium' # Zaten High değilse Medium yap
                  reasons.append(f"Model Çatışması (Ratio: {consensus_ratio:.2f} < {self.RISK_HIGH_MODEL_CONFLICT_RATIO:.2f})")


        # 3. Diğer Riskler (Eklenebilir: Uzun kaybetme serisi, Martingale uyarısı vb.)

        # if reasons: print(f"Guardian Risk Assessment: {risk_level} - Reasons: {', '.join(reasons)}") # Debug
        return risk_level


    def _find_best_performing_model(self, predictor_stats: dict) -> str | None:
        """En iyi başarı oranına sahip temel modeli bulur."""
        best_model_name = None
        best_rate = -1.0 # Başlangıç

        for name, stats in predictor_stats.items():
            # Meta modelleri ve özel durumları atla
            is_meta = False
            for prefix in self.META_MODEL_NAMES_PREFIXES:
                 if name.startswith(prefix):
                      is_meta = True
                      break
            if is_meta: continue

            total = stats.get('total', 0)
            correct = stats.get('correct', 0)

            # Yeterli sayıda tahmin yapılmış mı?
            if total >= self.RISK_MIN_PREDICTIONS_FOR_BEST:
                success_rate = (correct / total) * 100
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_model_name = name
                # Eşitlik durumunda ne yapmalı? Şimdilik ilk bulunan kalır.

        # if best_model_name: print(f"Guardian found best model: {best_model_name} ({best_rate:.1f}%)") # Debug
        return best_model_name

    # --- Ana Tahmin Metodları ---

    def predict(self, history: list, current_run_results: dict, predictor_stats: dict, predictors: dict) -> str:
        """Risk seviyesine göre ya N/A ya da en iyi modelin tahminini döndürür."""
        risk_level = self._assess_risk(history, current_run_results, predictor_stats, predictors)

        if risk_level == 'High':
            # print("Guardian says: TOO RISKY, predict N/A") # Debug
            return "N/A" # Yüksek risk, tahmin yok!
        else:
            best_model_name = self._find_best_performing_model(predictor_stats)
            if best_model_name:
                # print(f"Guardian chooses: {best_model_name}'s prediction") # Debug
                # En iyi modelin bu turdaki tahminini döndür
                return current_run_results.get(best_model_name, {'prediction': 'N/A'})['prediction']
            else:
                 # Henüz yeterli istatistiğe sahip bir model yoksa
                 # print("Guardian: No reliable model found yet, predict N/A") # Debug
                 return "N/A"

    def get_confidence(self, history: list, current_run_results: dict, predictor_stats: dict, predictors: dict) -> float:
        """Tahminin güven oranını döndürür."""
        risk_level = self._assess_risk(history, current_run_results, predictor_stats, predictors)
        if risk_level == 'High':
            return 0.0

        best_model_name = self._find_best_performing_model(predictor_stats)
        if best_model_name:
            best_model_confidence = current_run_results.get(best_model_name, {'confidence': 50.0})['confidence']
            # Orta riskte güveni biraz düşür
            if risk_level == 'Medium':
                # print("Guardian: Medium risk, reducing confidence slightly.") # Debug
                return max(10.0, best_model_confidence * 0.85) # %15 düşür
            else: # Low risk
                return best_model_confidence
        else:
            return 20.0 # Henüz iyi model yoksa düşük güven

    def get_probability(self, history: list, current_run_results: dict, predictor_stats: dict, predictors: dict) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        risk_level = self._assess_risk(history, current_run_results, predictor_stats, predictors)
        if risk_level == 'High':
            return 0.0

        best_model_name = self._find_best_performing_model(predictor_stats)
        if best_model_name:
            best_model_probability = current_run_results.get(best_model_name, {'probability': 50.0})['probability']
             # Orta riskte olasılığı 50'ye yaklaştır
            if risk_level == 'Medium':
                 # print("Guardian: Medium risk, adjusting probability towards 50%.") # Debug
                 return 50.0 + (best_model_probability - 50.0) * 0.7 # Farkın %70'i
            else: # Low risk
                 return best_model_probability
        else:
             return 50.0 # Henüz iyi model yoksa %50
