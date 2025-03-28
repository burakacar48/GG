import sys
import math
from collections import deque  # Son N eldeki performansı takip etmek için
from .statistical_deviation_predictor import StatisticalDeviationPredictor # Örnek

class GuardianMetaPredictor:
    """
    Geliştirilmiş Vasi Meta-Tahminci: Daha kapsamlı risk analizi yapar,
    geçmiş performansları daha akıllı değerlendirir ve modellerin tahminlerini
    ağırlıklandırarak birleştirir.
    """
    # Risk Eşikleri
    RISK_HIGH_DEVIATION_THRESHOLD_FACTOR = 2.5  # 1.8'den 2.5'e yükseltildi
    RISK_HIGH_MODEL_CONFLICT_RATIO = 0.55      # 0.65'ten 0.55'e düşürüldü
    RISK_MIN_PREDICTIONS_FOR_BEST = 4          # 6'dan 4'e düşürüldü
    
    # Yeni parametreler
    RECENT_PERFORMANCE_WINDOW = 20  # 30'dan 20'ye düşürüldü
    OVERALL_WEIGHT = 0.5           # Genel performansın ağırlığı
    RECENT_WEIGHT = 0.5            # Son ellerdeki performansın ağırlığı
    SUCCESS_STREAK_BONUS = 0.1     # Başarı serisini ödüllendirme katsayısı
    MIN_MODELS_FOR_CONSENSUS = 3   # Fikir birliği için gereken min model sayısı
    
    # Meta ve özel modelleri başarı sıralamasında dikkate almamak için isimleri
    META_MODEL_NAMES_PREFIXES = [
        "Ayakkabı Okuyucu", "Konsensüs Kaçağı", "Ters Köşe", "Vasi Meta-Tahminci"
    ]

    def __init__(self, risk_params=None):
        # Temel risk parametreleri
        if risk_params:
            self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR = risk_params.get('deviation_factor', self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR)
            self.RISK_HIGH_MODEL_CONFLICT_RATIO = risk_params.get('conflict_ratio', self.RISK_HIGH_MODEL_CONFLICT_RATIO)
            self.RISK_MIN_PREDICTIONS_FOR_BEST = risk_params.get('min_preds', self.RISK_MIN_PREDICTIONS_FOR_BEST)
            
            # Yeni parametreler için de kontrol et
            self.RECENT_PERFORMANCE_WINDOW = risk_params.get('recent_window', self.RECENT_PERFORMANCE_WINDOW)
            self.OVERALL_WEIGHT = risk_params.get('overall_weight', self.OVERALL_WEIGHT)
            self.RECENT_WEIGHT = risk_params.get('recent_weight', self.RECENT_WEIGHT)
        
        # Ayakkabı karakteristiğini izleme
        self.shoe_choppy_score = 0.5  # 0: Düzenli, 1: Karışık
        
        # Model performans hafızası
        self.model_performance_memory = {}  # model_name -> [win/loss geçmişi]
        
        # Son tahminlerin tutulacağı sözlük
        self.last_predictions = {}  # model_name -> last_prediction
        
        # Risk profili için geçmiş
        self.risk_history = deque(maxlen=10)  # Son 10 risk seviyesi

    def _record_model_performance(self, model_name, actual_result, prediction):
        """Bir modelin performansını kaydeder."""
        if model_name not in self.model_performance_memory:
            self.model_performance_memory[model_name] = deque(maxlen=self.RECENT_PERFORMANCE_WINDOW)
            
        # Sadece P ve B için değerlendirme yap (Tie'lar hariç)
        if actual_result in ('P', 'B') and prediction in ('P', 'B'):
            success = (prediction == actual_result)
            self.model_performance_memory[model_name].append(success)

    def update_model_performances(self, actual_result, predictor_stats):
        """Tüm modellerin performansını günceller."""
        for model_name, stats in predictor_stats.items():
            last_pred = stats.get('last_prediction', 'N/A')
            if last_pred != 'N/A':
                self._record_model_performance(model_name, actual_result, last_pred)

    def _assess_shoe_characteristic(self, history):
        """Ayakkabının düzenli mi yoksa karışık mı olduğunu değerlendirir."""
        relevant_history = [res for res in history if res in ('P', 'B')]
        if len(relevant_history) < 20:
            return 0.5  # Yeterli veri yoksa orta değer
            
        window = relevant_history[-20:]
        chops = 0
        for i in range(len(window) - 1):
            if window[i] != window[i+1]:
                chops += 1
                
        # Chop oranı (değişim oranı)
        chop_ratio = chops / (len(window) - 1) if len(window) > 1 else 0.5
        
        # Ayakkabı karakteristiğini güncelle (biraz yumuşatma uygula)
        self.shoe_choppy_score = (self.shoe_choppy_score * 0.7) + (chop_ratio * 0.3)
        
        return self.shoe_choppy_score

    def _assess_risk(self, history, current_run_results, predictor_stats, predictors):
        """Mevcut duruma göre risk seviyesini belirler: 'High', 'Medium', 'Low'."""
        risk_level = 'Low'
        risk_score = 0  # 0-100 arası risk puanı (0: Düşük, 100: Yüksek)
        reasons = []
        
        # Çok erken aşamada tahmin yapmaya izin ver
        if len(history) < 10:  # Başlangıçta her zaman düşük risk
            return 'Low', 10, ["Başlangıç Aşaması"]
        
        relevant_history = [res for res in history if res in ('P', 'B')]
        history_len = len(relevant_history)

        # 1. Aşırı Sapma Kontrolü
        sapma_threshold = 4.0
        sapma_window = 30
        
        for name, predictor in predictors.items():
            if isinstance(predictor, StatisticalDeviationPredictor):
                sapma_threshold = predictor.deviation_threshold
                sapma_window = predictor.window_size
                break

        if history_len >= sapma_window:
            window = relevant_history[-sapma_window:]
            p_wins = window.count('P')
            actual_p_perc = (p_wins / sapma_window) * 100
            deviation = abs(actual_p_perc - StatisticalDeviationPredictor.THEO_PLAYER_PROB)
            high_risk_threshold = sapma_threshold * self.RISK_HIGH_DEVIATION_THRESHOLD_FACTOR
            
            # Risk puanını güncelle
            deviation_risk = min(100, (deviation / high_risk_threshold) * 70)
            risk_score += deviation_risk
            
            if deviation >= high_risk_threshold:
                reasons.append(f"Aşırı Sapma ({deviation:.1f}% > {high_risk_threshold:.1f}%)")

        # 2. Model Çatışması Kontrolü
        valid_predictions = [data['prediction'] for data in current_run_results.values() 
                            if data['prediction'] in ('P', 'B')]
        total_valid = len(valid_predictions)
        
        if total_valid >= self.MIN_MODELS_FOR_CONSENSUS:
            p_count = valid_predictions.count('P')
            b_count = valid_predictions.count('B')
            max_count = max(p_count, b_count)
            consensus_ratio = max_count / total_valid if total_valid > 0 else 0
            
            # Risk puanını güncelle
            conflict_risk = min(100, ((1 - consensus_ratio) / (1 - self.RISK_HIGH_MODEL_CONFLICT_RATIO)) * 60)
            risk_score += conflict_risk * 0.8  # Biraz daha az ağırlık
            
            if consensus_ratio < self.RISK_HIGH_MODEL_CONFLICT_RATIO:
                reasons.append(f"Model Çatışması (Ratio: {consensus_ratio:.2f} < {self.RISK_HIGH_MODEL_CONFLICT_RATIO:.2f})")

        # 3. Uzun süreli model başarısızlığı kontrolü
        best_models = self._find_top_models(predictor_stats, 3)
        if best_models:
            best_model_accuracy = best_models[0][1]
            if best_model_accuracy < 45.0 and total_valid > 10:
                risk_score += 50
                reasons.append(f"Düşük Model Başarısı ({best_model_accuracy:.1f}%)")

        # 4. Ayakkabı geçiş dönemlerini tespit et
        shoe_characteristic = self._assess_shoe_characteristic(history)
        if 0.4 < shoe_characteristic < 0.6:
            risk_score += 30
            reasons.append("Ayakkabı Karakteristiği Belirsiz (Geçiş Dönemi)")

        # Risk seviyesi eşiklerini düşür (daha fazla tahmin için)
        if risk_score >= 85:  # 70'ten 85'e yükseltildi
            risk_level = 'High'
        elif risk_score >= 45:  # 35'ten 45'e yükseltildi
            risk_level = 'Medium'
        
        # Risk geçmişini güncelle
        self.risk_history.append(risk_score)
        
        return risk_level, risk_score, reasons

    def _find_top_models(self, predictor_stats, top_n=3):
        """En iyi N model ve başarı oranlarını döndürür."""
        models_performance = []
        
        for name, stats in predictor_stats.items():
            # Meta modelleri atla
            if any(name.startswith(prefix) for prefix in self.META_MODEL_NAMES_PREFIXES):
                continue
                
            total = stats.get('total', 0)
            correct = stats.get('correct', 0)
            
            # Yeterli tahmin yapılmış mı?
            if total >= self.RISK_MIN_PREDICTIONS_FOR_BEST:
                success_rate = (correct / total) * 100
                
                # Son performansı da değerlendir
                recent_performance = list(self.model_performance_memory.get(name, []))
                recent_correct = sum(recent_performance)
                recent_total = len(recent_performance)
                
                # Ağırlıklı başarı oranı
                if recent_total > 0:
                    recent_rate = (recent_correct / recent_total) * 100
                    weighted_rate = (success_rate * self.OVERALL_WEIGHT) + (recent_rate * self.RECENT_WEIGHT)
                else:
                    weighted_rate = success_rate
                
                # Başarı serisi için bonus
                consecutive_success = 0
                for result in reversed(recent_performance):
                    if result:
                        consecutive_success += 1
                    else:
                        break
                
                streak_bonus = min(10, consecutive_success * self.SUCCESS_STREAK_BONUS)
                final_score = weighted_rate + streak_bonus
                
                models_performance.append((name, final_score))
        
        # Performansa göre sırala ve en iyi N taneyi döndür
        return sorted(models_performance, key=lambda x: x[1], reverse=True)[:top_n]

    def _get_weighted_consensus(self, current_run_results, predictor_stats):
        """Modellerin tahminlerini ağırlıklı olarak birleştirir."""
        p_weight = 0
        b_weight = 0
        
        top_models = self._find_top_models(predictor_stats, 5)
        
        for model_name, score in top_models:
            model_pred = current_run_results.get(model_name, {}).get('prediction', 'N/A')
            if model_pred == 'P':
                p_weight += score
            elif model_pred == 'B':
                b_weight += score
        
        # Eğer toplam ağırlık çok düşükse consensus yok
        if p_weight + b_weight < 100:
            return "N/A"
            
        # En az 10 puanlık bir fark olsun
        if abs(p_weight - b_weight) < 10:
            return "N/A"
            
        return 'P' if p_weight > b_weight else 'B'

    def predict(self, history, current_run_results, predictor_stats, predictors):
        """Geliştirilmiş tahmin stratejisi."""
        # Risk analizi yap
        risk_level, risk_score, risk_reasons = self._assess_risk(history, current_run_results, predictor_stats, predictors)
        
        # Yüksek risk durumunda bile bazı tahminler yapabilelim
        if risk_level == 'High':
            # Yüksek riskte bile en iyi modeli kullan
            # Ama sadece çok başarılı bir model varsa
            top_models = self._find_top_models(predictor_stats, 1)
            if top_models and top_models[0][1] > 60.0:  # %60'tan fazla başarılı ise
                best_model_name = top_models[0][0]
                best_model_pred = current_run_results.get(best_model_name, {}).get('prediction', 'N/A')
                if best_model_pred in ('P', 'B'):
                    return best_model_pred
            
            # Konsensus kontrolü - eğer modellerin büyük çoğunluğu aynı fikirde ise
            p_count = 0
            b_count = 0
            for name, result in current_run_results.items():
                if result['prediction'] == 'P':
                    p_count += 1
                elif result['prediction'] == 'B':
                    b_count += 1
            
            total_valid = p_count + b_count
            if total_valid >= 8:  # En az 8 geçerli tahmin varsa
                consensus_ratio = max(p_count, b_count) / total_valid if total_valid > 0 else 0
                if consensus_ratio > 0.75:  # %75'ten fazla model aynı tahminde bulunuyorsa
                    return 'P' if p_count > b_count else 'B'
                
            return "N/A"  # Diğer durumlarda tahmin yok
        
        if risk_level == 'Medium':
            # Orta riskte sadece en iyi modeli kullan
            top_models = self._find_top_models(predictor_stats, 1)
            if top_models:
                best_model_name = top_models[0][0]
                return current_run_results.get(best_model_name, {}).get('prediction', 'N/A')
            else:
                return "N/A"
        else:  # Low risk
            # Düşük riskte, ayakkabı karakteristiğine göre karar ver
            shoe_characteristic = self._assess_shoe_characteristic(history)
            
            if shoe_characteristic < 0.4:  # Düzenli ayakkabı
                # Seri takip eden modellere daha fazla güven
                orderly_models = ["Seri Takip", "Ejderha Takibi", "Tembel Model", "Fibonacci Dansçısı"]
                top_models = self._find_top_models(predictor_stats, 3)
                
                for model_name, _ in top_models:
                    if any(orderly in model_name for orderly in orderly_models):
                        return current_run_results.get(model_name, {}).get('prediction', 'N/A')
                
                # Orderly model yoksa ağırlıklı consensus'a bak
                return self._get_weighted_consensus(current_run_results, predictor_stats)
                
            elif shoe_characteristic > 0.6:  # Karışık ayakkabı
                # Kesme/değişim takip eden modellere daha fazla güven
                choppy_models = ["Kesme Takibi", "Çiftleri Kovalama", "Zigzag", "Ahenk Bozucu"]
                top_models = self._find_top_models(predictor_stats, 3)
                
                for model_name, _ in top_models:
                    if any(choppy in model_name for choppy in choppy_models):
                        return current_run_results.get(model_name, {}).get('prediction', 'N/A')
                
                # Choppy model yoksa ağırlıklı consensus'a bak
                return self._get_weighted_consensus(current_run_results, predictor_stats)
                
            else:  # Kararsız/geçiş durumu
                # Ağırlıklı consensus kullan
                return self._get_weighted_consensus(current_run_results, predictor_stats)

    def get_confidence(self, history, current_run_results, predictor_stats, predictors):
        """Tahminin güven oranını döndürür."""
        risk_level, risk_score, _ = self._assess_risk(history, current_run_results, predictor_stats, predictors)
        
        if risk_level == 'High':
            # Yüksek riskte tahmin yapıyorsak bile düşük güven göster
            prediction = self.predict(history, current_run_results, predictor_stats, predictors)
            if prediction == "N/A":
                return 0.0
            return 35.0  # Sabit düşük güven
            
        # Tahmini tekrar yap (ideal değil ama kodu basit tutmak için)
        prediction = self.predict(history, current_run_results, predictor_stats, predictors)
        if prediction == "N/A":
            return 0.0
            
        # Hazır tahmin değerlerini topla
        p_confidence = 0.0
        b_confidence = 0.0
        p_count = 0
        b_count = 0
        
        for name, result in current_run_results.items():
            if result['prediction'] == 'P':
                p_confidence += result['confidence']
                p_count += 1
            elif result['prediction'] == 'B':
                b_confidence += result['confidence']
                b_count += 1
                
        # Ortalama güven değerlerini hesapla
        avg_p_confidence = p_confidence / p_count if p_count > 0 else 0
        avg_b_confidence = b_confidence / b_count if b_count > 0 else 0
        
        # Tahminin güvenini hesapla
        confidence = avg_p_confidence if prediction == 'P' else avg_b_confidence
        
        # Risk seviyesine göre güveni ayarla
        if risk_level == 'Medium':
            confidence *= 0.8  # %20 azalt
            
        # Son tahminlerin başarısına göre güveni ayarla
        if prediction in ('P', 'B'):
            # Consensus gücüne göre güveni ayarla
            predictions_list = [res['prediction'] for res in current_run_results.values() 
                               if res['prediction'] in ('P', 'B')]
            count_for_prediction = predictions_list.count(prediction)
            total_predictions = len(predictions_list)
            
            if total_predictions > 0:
                consensus_strength = count_for_prediction / total_predictions
                confidence_boost = (consensus_strength - 0.5) * 20  # -10 ile +10 arası
                confidence += confidence_boost
        
        return max(20.0, min(95.0, confidence))

    def get_probability(self, history, current_run_results, predictor_stats, predictors):
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history, current_run_results, predictor_stats, predictors)
        if prediction == "N/A":
            return 0.0
            
        # Yüksek risk durumunda tahmin yapıyorsak bile düşük olasılık göster
        risk_level, _, _ = self._assess_risk(history, current_run_results, predictor_stats, predictors)
        if risk_level == 'High':
            return 45.0  # Sabit düşük olasılık
            
        # Benzer model tahminlerini topla
        p_probability = 0.0
        b_probability = 0.0
        p_count = 0
        b_count = 0
        
        for name, result in current_run_results.items():
            if result['prediction'] == 'P':
                p_probability += result['probability']
                p_count += 1
            elif result['prediction'] == 'B':
                b_probability += result['probability']
                b_count += 1
                
        # Ortalama olasılık değerlerini hesapla
        avg_p_probability = p_probability / p_count if p_count > 0 else 0
        avg_b_probability = b_probability / b_count if b_count > 0 else 0
        
        # Tahminin olasılığını hesapla
        probability = avg_p_probability if prediction == 'P' else avg_b_probability
        
        # Ayakkabı karakteristiğine göre olasılığı ayarla
        shoe_characteristic = self._assess_shoe_characteristic(history)
        
        # Tahmin eden modellerin başarı oranlarına göre olasılığı ayarla
        supporting_models = []
        
        for name, result in current_run_results.items():
            if result['prediction'] == prediction:
                total = predictor_stats.get(name, {}).get('total', 0)
                correct = predictor_stats.get(name, {}).get('correct', 0)
                if total > 0:
                    success_rate = (correct / total) * 100
                    supporting_models.append((name, success_rate))
        
        if supporting_models:
            avg_success_rate = sum(rate for _, rate in supporting_models) / len(supporting_models)
            # Ağırlıklı olasılık hesabı
            probability = (probability * 0.7) + (avg_success_rate * 0.3)
            
        return max(10.0, min(90.0, probability))
