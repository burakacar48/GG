# main.py
import sys
import time
import os
import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
try:
    from typing import List, Dict, Tuple, Any, Optional
except ImportError:
    List = list; Dict = dict; Tuple = tuple; Any = any; Optional = None

from view.main_window import BaccaratView
from model.baccarat_model import BaccaratModel
from predictors.zigzag_predictor import ZigzagPredictor
from predictors.anti_trend_predictor import AntiTrendPredictor
from predictors.streak_follower_predictor import StreakFollowerPredictor
from predictors.streak_breaker_predictor import StreakBreakerPredictor
from predictors.pattern_matcher_predictor import PatternMatcherPredictor
from predictors.statistical_deviation_predictor import StatisticalDeviationPredictor
from predictors.anti_stats_predictor import AntiStatsPredictor
from predictors.chaos_walker_predictor import ChaosWalkerPredictor
from predictors.mirror_predictor import MirrorPredictor
from predictors.anti_mirror_predictor import AntiMirrorPredictor
from predictors.lazy_predictor import LazyPredictor
from predictors.fibonacci_dancer_predictor import FibonacciDancerPredictor
from predictors.oracle_predictor import OraclePredictor
from predictors.stubborn_simple_predictor import StubbornSimplePredictor
from predictors.rhythm_disruptor_predictor import RhythmDisruptorPredictor
from predictors.consensus_maverick_predictor import ConsensusMaverickPredictor
from predictors.visual_density_predictor import VisualDensityPredictor
from predictors.multiverse_predictor import MultiversePredictor
from predictors.dragon_tail_predictor import DragonTailPredictor
from predictors.chop_follower_predictor import ChopFollowerPredictor
from predictors.double_hunter_predictor import DoubleHunterPredictor
from predictors.shoe_reader_predictor import ShoeReaderPredictor
from simulation.baccarat_simulator import BaccaratSimulator
from view.stats_dialog import StatsDialog

# Simülasyon Logger Sınıfı
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

# Model tahminlerini izlemek için sınıf
class ModelPredictionTracker:
    """
    Her model için yapılan son tahminleri ve sonuçları izleyen yardımcı sınıf.
    Bu sayede hangi modelin son 'n' elde doğru tahmin yaptığını kolaylıkla belirleyebiliriz.
    """
    
    def __init__(self, history_len=5):
        """
        Args:
            history_len: Her model için saklanacak maksimum tahmin sayısı
        """
        self.history_len = history_len
        # Her model için tahmin geçmişini sakla: {model_name: [(prediction, actual_result, correct), ...]}
        self.model_history = {}
        
    def register_model(self, model_name: str):
        """Yeni bir model kaydeder"""
        if model_name not in self.model_history:
            self.model_history[model_name] = []
    
    def record_prediction(self, model_name: str, prediction: str, actual_result: str):
        """
        Bir modelin tahminini ve gerçekleşen sonucu kaydeder
        
        Args:
            model_name: Modelin adı
            prediction: Modelin tahmini ('P', 'B', 'N/A')
            actual_result: Gerçekleşen sonuç ('P', 'B', 'T')
        """
        if model_name not in self.model_history:
            self.register_model(model_name)
        
        # Eğer prediction veya actual_result geçersizse kaydetme
        if prediction not in ('P', 'B') or actual_result not in ('P', 'B', 'T'):
            return
            
        # Beraberliği (Tie) kaydetme (genelde bahis iade edilir)
        if actual_result == 'T':
            return
            
        # Tahminin doğru olup olmadığını belirle
        correct = (prediction == actual_result)
        
        # Eski kayıtları sınırla (maksimum history_len kadar)
        if len(self.model_history[model_name]) >= self.history_len:
            self.model_history[model_name].pop(0)
            
        # Kaydı ekle
        self.model_history[model_name].append((prediction, actual_result, correct))
    
    def get_last_n_predictions(self, model_name: str, n: int):
        """
        Bir modelin son n tahminini döndürür
        
        Args:
            model_name: Modelin adı
            n: İstenen tahmin sayısı
            
        Returns:
            [(prediction, actual_result, correct), ...] listesi
        """
        if model_name not in self.model_history:
            return []
            
        history = list(self.model_history[model_name])
        return history[-n:] if n <= len(history) else history
    
    def get_recent_accuracy(self, model_name: str, n: int):
        """
        Bir modelin son n tahmindeki doğruluk oranını döndürür
        
        Args:
            model_name: Modelin adı
            n: Dikkate alınacak son tahmin sayısı
            
        Returns:
            Doğruluk oranı (0.0-1.0 arası)
        """
        predictions = self.get_last_n_predictions(model_name, n)
        
        if not predictions:
            return 0.0
            
        correct_count = sum(1 for _, _, correct in predictions if correct)
        return correct_count / len(predictions)
    
    def has_consistent_predictions(self, model_name: str, n: int):
        """
        Bir modelin son n tahminin tutarlı olup olmadığını kontrol eder 
        (hepsi doğru mu?)
        
        Args:
            model_name: Modelin adı
            n: Kontrol edilecek son tahmin sayısı
            
        Returns:
            True if all last n predictions were correct, False otherwise
        """
        predictions = self.get_last_n_predictions(model_name, n)
        
        if len(predictions) < n:
            return False
            
        return all(correct for _, _, correct in predictions)

class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = BaccaratModel(initial_balance=5000.0)
        self.view = BaccaratView()
        self.simulator = BaccaratSimulator(num_decks=8, cut_card_depth_approx=14)

        # Model parametreleri
        streak_len = 3; pattern_len = 3; dev_window = 30; dev_thresh = 4.0
        lazy_trigger = 5; fib_limit = 100; maverick_thresh = 70.0
        multi_window = 20; multi_influence = 0.15; multi_leap = 0.05
        dragon_min_len = 6; shoe_window = 15; shoe_thresh_ratio = 0.45
        orderly_model = f"Seri Takip ({streak_len})"
        choppy_model = "Kesme Takibi (Ping Pong)"
        
        # Tahmin modelleri sözlüğü
        self.predictors: Dict[str, Any] = {
            "Zigzag": ZigzagPredictor(), 
            orderly_model: StreakFollowerPredictor(streak_length=streak_len),
            f"Seri Kırıcı ({streak_len})": StreakBreakerPredictor(streak_length=streak_len),
            f"Ejderha Takibi ({dragon_min_len}+)": DragonTailPredictor(min_dragon_length=dragon_min_len),
            choppy_model: ChopFollowerPredictor(), 
            "Çiftleri Kovalama": DoubleHunterPredictor(),
            f"Desen ({pattern_len}-gram)": PatternMatcherPredictor(n=pattern_len),
            f"Sapma Analizi (W{dev_window}, T{dev_thresh}%)": StatisticalDeviationPredictor(window_size=dev_window, deviation_threshold=dev_thresh),
            f"Anti-Stats (Kabus!) (W{dev_window}, T{dev_thresh}%)": AntiStatsPredictor(window_size=dev_window, deviation_threshold=dev_thresh),
            "Kaos Yürüyüşçüsü (Saat)": ChaosWalkerPredictor(), 
            "Ayna (Başlangıç)": MirrorPredictor(),
            "Anti-Ayna (Başlangıç)": AntiMirrorPredictor(),
            f"Tembel Model (Seri>{lazy_trigger-1})": LazyPredictor(trigger_streak_length=lazy_trigger, follow_streak=True),
            f"Fibonacci Dansçısı (<{fib_limit})": FibonacciDancerPredictor(max_fib_check=fib_limit),
            "Baccarat Falcısı": OraclePredictor(), 
            "İnatçı Keçi (Basit)": StubbornSimplePredictor(),
            "Ahenk Bozucu": RhythmDisruptorPredictor(), 
            "Görsel Yoğunluk (Momentum)": VisualDensityPredictor(),
            "Paralel Evren Bahisçisi": MultiversePredictor(deviation_window=multi_window, deviation_influence=multi_influence, quantum_leap_chance=multi_leap),
            f"Ayakkabı Okuyucu (W{shoe_window})": ShoeReaderPredictor(window_size=shoe_window, chop_threshold_ratio=shoe_thresh_ratio, orderly_model_name=orderly_model, choppy_model_name=choppy_model),
            f"Konsensüs Kaçağı ({maverick_thresh}%)": ConsensusMaverickPredictor(threshold_percentage=maverick_thresh),
            "Ters Köşe (Anti-Zigzag)": AntiTrendPredictor()
         }
        
        # Meta modeller (diğer modellerin tahminlerini kullananlar)
        self.meta_model_names = {
            f"Ayakkabı Okuyucu (W{shoe_window})", 
            f"Konsensüs Kaçağı ({maverick_thresh}%)",
            "Ters Köşe (Anti-Zigzag)"
        }
        
        # Tahmin izleyici oluştur
        self.prediction_tracker = ModelPredictionTracker(history_len=10)
        # Modelleri kaydet
        for name in self.predictors:
            self.prediction_tracker.register_model(name)
        
        # Logger başlat
        self.logger = SimulationLogger()
        self.hand_count = 0
        
        # İstatistik ve durum bilgileri
        self.predictor_stats = { name: {'correct': 0, 'total': 0, 'last_prediction': 'N/A'} 
                                for name in self.predictors }
        self.last_run_results: Dict[str, Dict[str, Any]] = {}
        self.last_predictions: Dict[str, str] = {name: 'N/A' for name in self.predictors}
        self.stats_dialog_instance = None
        self.last_best_model = None

        # Simülasyon ayarları
        self.is_simulating = False
        self.simulation_timer = QTimer()
        self.simulation_timer.setInterval(150)
        self.simulation_timer.timeout.connect(self.run_single_simulation_step)
        self._connect_signals()

    def _connect_signals(self):
        self.view.player_clicked.connect(lambda: self.handle_add_result('P'))
        self.view.banker_clicked.connect(lambda: self.handle_add_result('B'))
        self.view.tie_clicked.connect(lambda: self.handle_add_result('T'))
        self.view.undo_clicked.connect(self.handle_undo)
        self.view.clear_clicked.connect(self.handle_clear)
        self.view.stats_clicked.connect(self.show_statistics_window)
        try:
            sim_button = getattr(self.view, 'sim_btn', None)
            if sim_button:
                sim_button.clicked.connect(self.handle_simulation_toggle)
            else:
                print("Warning: View object has no 'sim_btn' attribute for simulation.")
        except Exception as e:
            print(f"Error connecting simulation button: {e}")
        self.model.history_changed.connect(self.view.update_matrix_display)
        self.model.stats_updated.connect(self.view.update_statistics)
        self.model.history_changed.connect(self.run_predictions)

    def handle_simulation_toggle(self):
        sim_button = getattr(self.view, 'sim_btn', None)
        if not self.is_simulating:
            self.is_simulating = True
            if sim_button: sim_button.setText("⏹️")
            print("Simulation Started.")
            self.simulation_timer.start()
        else:
            self.is_simulating = False
            self.simulation_timer.stop()
            if sim_button: sim_button.setText("▶️")
            print("Simulation Stopped.")
            
            # Simülasyon durduğunda sonuçları kaydet
            self.logger.finalize(
                total_hands=self.hand_count, 
                final_balance=self.model.current_balance,
                initial_balance=self.model.initial_balance
            )
            print(f"Simülasyon sonuçları {self.logger.log_file} dosyasına kaydedildi.")

    def run_single_simulation_step(self):
        if not self.is_simulating:
             self.simulation_timer.stop()
             sim_button = getattr(self.view, 'sim_btn', None)
             if sim_button: sim_button.setText("▶️")
             return
        result = self.simulator.deal_hand()
        if result is None:
            # self.handle_simulation_toggle() # Otomatik durdurma yerine sadece sıfırla ve devam et
            print("--- Ayakkabı Bitti. Yeni Ayakkabı Karıştırılıyor ---")
            self.simulator.shuffle_and_reset()
        elif result == 'T': pass
        elif result in ('P', 'B'): self.handle_add_result(result)
        else:
             print(f"Warning: Simulator returned unexpected result: {result}")
             self.handle_simulation_toggle()

    def handle_add_result(self, actual_result: str):
        # Get the best model's prediction
        best_model_name, best_model_data = self.find_best_model_prediction()
        predicted_result_for_bet = best_model_data.get('prediction', 'N/A') if best_model_data else 'N/A'
        
        # Logger için el sayısını artır
        self.hand_count += 1
        
        is_tie = (actual_result == 'T')
        if not is_tie:
            # Update stats for all models
            for name, last_pred in self.last_predictions.items():
                if last_pred in ('P', 'B'):
                    stat = self.predictor_stats[name]
                    stat['total'] += 1
                    correct = (last_pred == actual_result)
                    if correct: 
                        stat['correct'] += 1
                        print(f"Model {name} correctly predicted {actual_result}")
                    stat['last_prediction'] = last_pred
                    
                    # Record prediction in tracker
                    if self.prediction_tracker:
                        self.prediction_tracker.record_prediction(name, last_pred, actual_result)
            
            # Print which model was used for prediction (if any)
            if best_model_name:
                print(f"Used model for prediction: {best_model_name} ({predicted_result_for_bet})")
                if predicted_result_for_bet == actual_result:
                    print(f"✓ Correct prediction from {best_model_name}!")
                else:
                    print(f"✗ Wrong prediction from {best_model_name}")
        
        # Tüm tahminleri topla
        all_predictions = {name: pred for name, pred in self.last_predictions.items() if pred in ('P', 'B')}

        # Sonucu logla
        self.logger.log_hand_result(
            hand_number=self.hand_count,
            actual_result=actual_result,
            predicted_result=predicted_result_for_bet,
            best_model=best_model_name,
            all_predictions=all_predictions,
            balance=self.model.current_balance,
            bet_amount=self.model.current_bet
        )
        
        self.model.add_result(actual_result, predicted_result_for_bet)
        if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
            self.stats_dialog_instance.update_data(self.predictor_stats)

    def handle_undo(self):
        if self.is_simulating:
             print("Cannot undo while simulation is running.")
             return
        self.model.undo_last()

    def clear_predictors(self):
        """Tüm tahmin modellerinin istatistiklerini ve tahmin geçmişini sıfırlar"""
        # İstatistik resetleme
        self.predictor_stats = {name: {'correct': 0, 'total': 0, 'last_prediction': 'N/A'} 
                               for name in self.predictors}
        self.last_run_results = {}
        self.last_predictions = {name: 'N/A' for name in self.predictors}
        
        # Tahmin izleyiciyi sıfırla
        if self.prediction_tracker:
            # Yeni bir izleyici oluştur
            self.prediction_tracker = ModelPredictionTracker(history_len=10)
            for name in self.predictors:
                self.prediction_tracker.register_model(name)
                
        # En son kullanılan modeli sıfırla
        self.last_best_model = None

    def handle_clear(self):
        if self.is_simulating:
             print("Stopping simulation before clearing.")
             self.handle_simulation_toggle()
        
        # Reset all predictors
        self.clear_predictors()
        
        # Reset the model and simulator
        self.model.clear_results()
        self.simulator.shuffle_and_reset()
        
        # Logger'ı da sıfırla
        self.logger = SimulationLogger()
        self.hand_count = 0
        
        print("History cleared, stats reset, and simulator reset.")
        
        # Update stats dialog if open
        if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
            self.stats_dialog_instance.update_data(self.predictor_stats)

    def find_best_model_prediction(self) -> Tuple[str, Dict[str, Any]]:
        """
        Son 2 elde doğru tahmin yapan ve aynı tahminde bulunan modelleri bulur.
        Eğer böyle bir model grubu bulunursa, en yüksek güven oranına sahip olanın
        tahminini döndürür.
        """
        # 1. Tahmin izleyiciyi kullanarak son 2 elde tutarlı şekilde doğru 
        # tahmin yapan modelleri bul
        consistent_correct_models = []
        
        if self.prediction_tracker:
            min_predictions = 2  # En az kaç tahminin doğru olması gerektiği
            
            for name, stats in self.predictor_stats.items():
                # Meta modelleri atla
                if name in self.meta_model_names:
                    continue
                
                # Mevcut tahmini al
                current_pred_data = self.last_run_results.get(name, {})
                current_prediction = current_pred_data.get('prediction', 'N/A')
                
                # Sadece geçerli tahmini olan modelleri kontrol et
                if current_prediction not in ('P', 'B'):
                    continue
                
                # Son min_predictions elde tutarlı şekilde doğru tahmin yapmış mı?
                if self.prediction_tracker.has_consistent_predictions(name, min_predictions):
                    # Yeterince tutarlı tahmin var, modeli listeye ekle
                    consistent_correct_models.append((name, current_pred_data))
                    print(f"Model {name} was correct in last {min_predictions} predictions")
        
        # Eğer tahmin izleyici yoksa veya tutarlı model bulunamadıysa, 
        # başarı oranlarına göre değerlendir
        if not consistent_correct_models:
            # Get top 3 models by success rate
            top_models = []
            
            for name, stats in self.predictor_stats.items():
                # Skip meta models
                if name in self.meta_model_names:
                    continue
                
                # Get current prediction for this model
                current_pred_data = self.last_run_results.get(name, {})
                current_prediction = current_pred_data.get('prediction', 'N/A')
                
                # Only consider models with current predictions
                if current_prediction not in ('P', 'B'):
                    continue
                
                # Model must have at least 5 predictions
                total = stats.get('total', 0)
                correct = stats.get('correct', 0)
                
                if total >= 5:
                    win_rate = correct / total
                    top_models.append((name, current_pred_data, win_rate))
            
            # Sort by win rate and get top 3
            if top_models:
                top_models.sort(key=lambda x: x[2], reverse=True)
                top_3_models = top_models[:min(3, len(top_models))]
                
                # Convert to format that's compatible with consistent_correct_models
                consistent_correct_models = [(name, data) for name, data, _ in top_3_models]
        
        # Tahmin yapacak model bulunamadı
        if not consistent_correct_models:
            return None, None
        
        # Check if all models agree on the same prediction
        predictions = [model[1].get('prediction') for model in consistent_correct_models]
        unique_predictions = set(predictions)
        
        # If there's only one type of prediction, all models agree
        if len(unique_predictions) == 1 and list(unique_predictions)[0] in ('P', 'B'):
            # Sort by confidence and return the highest
            consistent_correct_models.sort(key=lambda x: x[1].get('confidence', 0), reverse=True)
            best_model = consistent_correct_models[0]
            
            print(f"Top models agree on {list(unique_predictions)[0]}: {[model[0] for model in consistent_correct_models]}")
            return best_model
        
        # Models don't agree on a prediction, don't make one
        print(f"Top models disagree: {[f'{model[0]}:{model[1].get('prediction')}' for model in consistent_correct_models]}")
        return None, None

    def run_predictions(self, history):
        if not history:
            self.last_predictions = {name: 'N/A' for name in self.predictors}
            self.last_run_results = {}
            self.view.update_prediction_display("N/A", 0.0, 0.0)
            if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
                 self.stats_dialog_instance.update_data(self.predictor_stats)
            return

        current_run_results: Dict[str, Dict[str, Any]] = {}

        # Adım 1: Tüm Modelleri Çalıştır (Meta modellerle özel işlemler)
        for name, predictor in self.predictors.items():
            prediction = 'N/A'; confidence = 50.0; probability = 50.0
            try:
                if isinstance(predictor, AntiTrendPredictor):
                    zigzag_pred = current_run_results.get("Zigzag", {}).get('prediction', 'N/A')
                    zigzag_conf = current_run_results.get("Zigzag", {}).get('confidence', 50.0)
                    zigzag_prob = current_run_results.get("Zigzag", {}).get('probability', 50.0)
                    prediction = predictor.predict(history, zigzag_pred)
                    if prediction != 'N/A':
                         confidence = predictor.get_confidence(history, zigzag_conf)
                         probability = predictor.get_probability(history, zigzag_prob)
                elif isinstance(predictor, ConsensusMaverickPredictor):
                     basic_preds_dict = {k: v['prediction'] for k,v in current_run_results.items() if k not in self.meta_model_names}
                     prediction = predictor.predict(history, basic_preds_dict)
                     if prediction != 'N/A':
                          confidence = predictor.get_confidence(history, basic_preds_dict)
                          probability = predictor.get_probability(history, basic_preds_dict)
                elif isinstance(predictor, ShoeReaderPredictor):
                     basic_results_dict = {k: v for k,v in current_run_results.items() if k not in self.meta_model_names}
                     chosen_model_key = None
                     relevant_history = [res for res in history if res in ('P', 'B')]
                     window = relevant_history[-predictor.window_size:]
                     window_len = len(window)
                     if window_len >= 5:
                          num_chops = predictor._calculate_chops(window)
                          threshold_count = max(1, int((window_len - 1) * predictor.chop_threshold_ratio))
                          if num_chops < threshold_count: chosen_model_key = predictor.orderly_model_key
                          else: chosen_model_key = predictor.choppy_model_key

                     if chosen_model_key:
                          chosen_model_result = basic_results_dict.get(chosen_model_key)
                          if chosen_model_result and chosen_model_result['prediction'] != 'N/A':
                               prediction = chosen_model_result['prediction']
                               confidence = predictor.get_confidence(history, basic_results_dict, chosen_model_result['confidence'])
                               probability = predictor.get_probability(history, basic_results_dict, chosen_model_result['probability'])
                          else: prediction = 'N/A'
                     else: prediction = 'N/A'
                else: # Temel modeller
                    prediction = predictor.predict(history)
                    if prediction != 'N/A':
                        try: confidence = predictor.get_confidence(history)
                        except AttributeError: pass
                        try: probability = predictor.get_probability(history)
                        except AttributeError: pass
            except Exception as e:
                print(f"Error running predictor {name}: {e}")
                prediction = 'N/A'
            current_run_results[name] = {'prediction': prediction, 'confidence': confidence, 'probability': probability}

        # Adım 2: Tüm sonuçları sakla
        self.last_run_results = current_run_results.copy()
        self.last_predictions = {name: data['prediction'] for name, data in current_run_results.items()}

        # Adım 3: Son 2 elde doğru tahmin yapan modelleri belirle
        best_model_name, best_model_data = self.find_best_model_prediction()
        
        # Adım 4: Ana tahmin ekranını güncelle
        if best_model_name and best_model_data:
            display_prediction = best_model_data.get('prediction', 'N/A')
            display_confidence = best_model_data.get('confidence', 0.0)
            display_probability = best_model_data.get('probability', 0.0)
            print(f"Consistent model found: {best_model_name} - Prediction: {display_prediction}, Confidence: {display_confidence:.1f}%")
        else:
            # Hiçbir model son 2 elde doğru tahmin yapmadı - tahmin gösterme
            display_prediction = 'N/A'
            display_confidence = 0.0
            display_probability = 0.0
            print("No consistent correct model found - not showing any prediction")
            
        self.view.update_prediction_display(display_prediction, display_confidence, display_probability)

    def show_statistics_window(self):
        if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
            self.stats_dialog_instance.raise_()
            self.stats_dialog_instance.activateWindow()
            self.stats_dialog_instance.update_data(self.predictor_stats)
        else:
            self.stats_dialog_instance = StatsDialog(self.view)
            self.stats_dialog_instance.update_data(self.predictor_stats)
            self.stats_dialog_instance.show()
    
    def run_batch_simulation(self, num_hands=1000, log_file="batch_sim_log.txt"):
        """
        Belirli sayıda eli otomatik olarak simüle eder ve sonuçları kaydeder
        """
        # Batch modu için yeni bir logger oluştur
        self.logger = SimulationLogger(log_file=log_file)
        self.hand_count = 0
        
        # Başlangıç durumunu sıfırla
        self.handle_clear()
        
        print(f"Batch simülasyon başlatılıyor: {num_hands} el...")
        
        # Simülasyonu çalıştır
        for i in range(num_hands):
            result = self.simulator.deal_hand()
            if result is None:
                print(f"Ayakkabı bitti, yenileniyor... ({i+1}/{num_hands})")
                self.simulator.shuffle_and_reset()
                continue
                
            if result in ('P', 'B'):
                self.handle_add_result(result)
            
            # Her 100 elde bir bilgi ver
            if (i+1) % 100 == 0:
                print(f"Simülasyon ilerliyor: {i+1}/{num_hands}")
        
        # Sonuçları kaydet
        self.logger.finalize(
            total_hands=self.hand_count,
            final_balance=self.model.current_balance,
            initial_balance=self.model.initial_balance
        )
        
        print(f"Batch simülasyon tamamlandı. {self.hand_count} el oynandı.")
        print(f"Sonuçlar {log_file} dosyasına kaydedildi.")
        
        # İstatistikleri ekranda göster
        profit = self.model.current_balance - self.model.initial_balance
        print(f"Kâr/Zarar: ₺{profit:.2f} ({(profit/self.model.initial_balance)*100:.1f}%)")
        print(f"Max Kazanç Serisi: {self.model.max_win_streak}, Max Kayıp Serisi: {self.model.max_loss_streak}")

    def run(self):
        self.view.show()
        self.model._update_and_emit() # Başlangıç kasa bilgisini gönder
        self.run_predictions(self.model.full_history_sequence)
        sys.exit(self.app.exec())

if __name__ == '__main__':
    controller = ApplicationController()
    
    # Eğer komut satırı argümanları varsa
    if len(sys.argv) > 1:
        # Toplu simülasyon modu için argüman kontrolü
        if sys.argv[1] == '--simulate' or sys.argv[1] == '-s':
            num_hands = 1000  # Varsayılan
            if len(sys.argv) > 2:
                try:
                    num_hands = int(sys.argv[2])
                except ValueError:
                    print(f"Geçersiz el sayısı. Varsayılan değer kullanılıyor: {num_hands}")
            
            log_file = f"sim_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            controller.run_batch_simulation(num_hands=num_hands, log_file=log_file)
        else:
            controller.run()
    else:
        controller.run()
