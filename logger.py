# logger.py
import os
import datetime
from typing import Dict, List, Any, Optional

class SimulationLogger:
    """
    Simülasyon sonuçlarını ve tahmin performansını kaydeden logger sınıfı
    """
    
    def __init__(self, log_file="log.txt"):
        self.log_file = log_file
        self.results = []
        self.bet_history = []
        self.win_streak = 0
        self.loss_streak = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0
        self.prediction_success = {}  # Her model için tahmin başarısı
        
        # Log dosyasını başlat
        self._init_log_file()
    
    def _init_log_file(self):
        """Log dosyasını başlangıç bilgileriyle oluşturur"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=== BACCARAT SİMÜLASYON SONUÇLARI ===\n")
            f.write(f"Başlangıç: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
    
    def log_hand_result(self, hand_number: int, actual_result: str, predicted_result: str, 
                        best_model: Optional[str], all_predictions: Dict[str, str],
                        balance: float, bet_amount: float):
        """Her el sonucunu kaydeder"""
        # Sonucu listeye ekle
        result_data = {
            'hand': hand_number,
            'actual': actual_result,
            'predicted': predicted_result,
            'best_model': best_model,
            'all_predictions': all_predictions,
            'balance': balance,
            'bet': bet_amount
        }
        self.results.append(result_data)
        
        # Sonucu log dosyasına yaz
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"El #{hand_number}: Sonuç={actual_result}, Tahmin={predicted_result or 'N/A'}")
            
            if best_model:
                f.write(f" (Model: {best_model})")
            
            # Bahis sonucunu yaz
            if predicted_result in ('P', 'B') and actual_result != 'T':
                is_win = predicted_result == actual_result
                result_str = "KAZANÇ" if is_win else "KAYIP"
                
                # Seri takibi
                if is_win:
                    self.win_streak += 1
                    self.loss_streak = 0
                    if self.win_streak > self.max_win_streak:
                        self.max_win_streak = self.win_streak
                else:
                    self.loss_streak += 1
                    self.win_streak = 0
                    if self.loss_streak > self.max_loss_streak:
                        self.max_loss_streak = self.loss_streak
                
                streak_info = f"W{self.win_streak}" if is_win else f"L{self.loss_streak}"
                f.write(f" - {result_str} | {streak_info} | Bakiye: ₺{balance:.2f} | Bahis: ₺{bet_amount:.2f}")
                
                # Bahis geçmişine ekle
                self.bet_history.append(1 if is_win else 0)
            
            f.write("\n")
            
            # Tüm modellerin tahminleri
            model_predictions = []
            for model, prediction in all_predictions.items():
                if prediction in ('P', 'B'):
                    correct = prediction == actual_result if actual_result != 'T' else None
                    
                    # Model başarı istatistiklerini güncelle
                    if model not in self.prediction_success:
                        self.prediction_success[model] = {'correct': 0, 'total': 0}
                    
                    if actual_result != 'T' and prediction in ('P', 'B'):
                        self.prediction_success[model]['total'] += 1
                        if correct:
                            self.prediction_success[model]['correct'] += 1
                    
                    if correct is not None:
                        result_mark = "✓" if correct else "✗"
                        model_predictions.append(f"{model}: {prediction} {result_mark}")
            
            if model_predictions:
                f.write("  Model Tahminleri:\n")
                for pred in model_predictions:
                    f.write(f"    {pred}\n")
            
            f.write("\n")
    
    def log_streak_summary(self):
        """Seri kayıtlarını özetler"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n=== SERİ ÖZETİ ===\n")
            f.write(f"Maksimum Kazanç Serisi: {self.max_win_streak}\n")
            f.write(f"Maksimum Kayıp Serisi: {self.max_loss_streak}\n")
            
            # En uzun kayıp serisi analizi
            if len(self.bet_history) > 0:
                longest_loss_series = self._find_longest_series(self.bet_history, 0)
                f.write(f"En uzun kayıp serisi analizi: {longest_loss_series} el\n")
    
    def log_model_performance(self):
        """Model performanslarını kaydeder"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n=== MODEL BAŞARI ORANLARI ===\n")
            
            # Başarı oranına göre sırala
            sorted_models = sorted(
                self.prediction_success.items(),
                key=lambda x: (x[1]['correct'] / x[1]['total'] if x[1]['total'] > 0 else 0),
                reverse=True
            )
            
            for model, stats in sorted_models:
                if stats['total'] > 0:
                    success_rate = (stats['correct'] / stats['total']) * 100
                    f.write(f"{model}: {stats['correct']}/{stats['total']} ({success_rate:.1f}%)\n")
    
    def log_simulation_summary(self, total_hands: int, final_balance: float, initial_balance: float):
        """Simülasyon sonuçlarını özetler"""
        profit = final_balance - initial_balance
        profit_percentage = (profit / initial_balance) * 100 if initial_balance > 0 else 0
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n=== SİMÜLASYON ÖZET ===\n")
            f.write(f"Toplam El: {total_hands}\n")
            f.write(f"Başlangıç Bakiye: ₺{initial_balance:.2f}\n")
            f.write(f"Son Bakiye: ₺{final_balance:.2f}\n")
            f.write(f"Kâr/Zarar: ₺{profit:.2f} ({profit_percentage:.1f}%)\n")
            
            # Bahis performansı
            if len(self.bet_history) > 0:
                win_count = sum(self.bet_history)
                total_bets = len(self.bet_history)
                win_rate = (win_count / total_bets) * 100 if total_bets > 0 else 0
                
                f.write(f"Toplam Bahis: {total_bets}\n")
                f.write(f"Kazanılan Bahis: {win_count} ({win_rate:.1f}%)\n")
                f.write(f"Kaybedilen Bahis: {total_bets - win_count} ({100 - win_rate:.1f}%)\n")
    
    def log_recommendations(self):
        """Performans analizine dayalı öneriler kaydeder"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n=== İYİLEŞTİRME ÖNERİLERİ ===\n")
            
            # Öneriler
            if self.max_loss_streak > 10:
                f.write("! Martingale seviyelerini artırmayı düşünün, yüksek kayıp serisi yaşandı.\n")
            
            # En başarılı modelleri belirle
            if self.prediction_success:
                best_models = sorted(
                    [(model, stats['correct']/stats['total'] if stats['total'] > 20 else 0) 
                     for model, stats in self.prediction_success.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                if best_models and best_models[0][1] > 0.55:
                    f.write(f"+ En başarılı model: {best_models[0][0]} ({best_models[0][1]*100:.1f}%)\n")
                    f.write("  Bu modele daha fazla ağırlık vermeyi düşünün.\n")
            
            # Son 20 bahis analizi
            if len(self.bet_history) >= 20:
                recent_win_rate = sum(self.bet_history[-20:]) / 20 * 100
                if recent_win_rate < 40:
                    f.write("! Son 20 elde kazanma oranı düşük (%{:.1f}).\n".format(recent_win_rate))
                    f.write("  Model seçim kriterlerini gözden geçirmeyi düşünün.\n")
    
    def _find_longest_series(self, history: List[int], target: int) -> int:
        """Belirli bir değerin listedeki en uzun serisini bulur"""
        max_length = 0
        current_length = 0
        
        for result in history:
            if result == target:
                current_length += 1
                max_length = max(max_length, current_length)
            else:
                current_length = 0
        
        return max_length
    
    def finalize(self, total_hands: int, final_balance: float, initial_balance: float):
        """Loglama işlemini sonlandırır ve özet bilgileri kaydeder"""
        self.log_streak_summary()
        self.log_model_performance()
        self.log_simulation_summary(total_hands, final_balance, initial_balance)
        self.log_recommendations()
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Bitiş: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
