# main.py
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
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
from predictors.guardian_meta_predictor import GuardianMetaPredictor
from simulation.baccarat_simulator import BaccaratSimulator
from view.stats_dialog import StatsDialog

class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = BaccaratModel(initial_balance=5000.0)
        self.view = BaccaratView()
        self.simulator = BaccaratSimulator(num_decks=8, cut_card_depth_approx=14)

        streak_len = 3; pattern_len = 3; dev_window = 30; dev_thresh = 4.0
        lazy_trigger = 5; fib_limit = 100; maverick_thresh = 70.0
        multi_window = 20; multi_influence = 0.15; multi_leap = 0.05
        dragon_min_len = 6; shoe_window = 15; shoe_thresh_ratio = 0.45
        orderly_model = f"Seri Takip ({streak_len})"
        choppy_model = "Kesme Takibi (Ping Pong)"
        guardian_risk_params = {'deviation_factor': 1.8,'conflict_ratio': 0.65,'min_preds': 6}

        self.predictors: Dict[str, Any] = {
            "Zigzag": ZigzagPredictor(), orderly_model: StreakFollowerPredictor(streak_length=streak_len),
            f"Seri Kırıcı ({streak_len})": StreakBreakerPredictor(streak_length=streak_len),
            f"Ejderha Takibi ({dragon_min_len}+)": DragonTailPredictor(min_dragon_length=dragon_min_len),
            choppy_model: ChopFollowerPredictor(), "Çiftleri Kovalama": DoubleHunterPredictor(),
            f"Desen ({pattern_len}-gram)": PatternMatcherPredictor(n=pattern_len),
            f"Sapma Analizi (W{dev_window}, T{dev_thresh}%)": StatisticalDeviationPredictor(window_size=dev_window, deviation_threshold=dev_thresh),
            f"Anti-Stats (Kabus!) (W{dev_window}, T{dev_thresh}%)": AntiStatsPredictor(window_size=dev_window, deviation_threshold=dev_thresh),
            "Kaos Yürüyüşçüsü (Saat)": ChaosWalkerPredictor(), "Ayna (Başlangıç)": MirrorPredictor(),
            "Anti-Ayna (Başlangıç)": AntiMirrorPredictor(),
            f"Tembel Model (Seri>{lazy_trigger-1})": LazyPredictor(trigger_streak_length=lazy_trigger, follow_streak=True),
            f"Fibonacci Dansçısı (<{fib_limit})": FibonacciDancerPredictor(max_fib_check=fib_limit),
            "Baccarat Falcısı": OraclePredictor(), "İnatçı Keçi (Basit)": StubbornSimplePredictor(),
            "Ahenk Bozucu": RhythmDisruptorPredictor(), "Görsel Yoğunluk (Momentum)": VisualDensityPredictor(),
            "Paralel Evren Bahisçisi": MultiversePredictor(deviation_window=multi_window, deviation_influence=multi_influence, quantum_leap_chance=multi_leap),
            f"Ayakkabı Okuyucu (W{shoe_window})": ShoeReaderPredictor(window_size=shoe_window, chop_threshold_ratio=shoe_thresh_ratio, orderly_model_name=orderly_model, choppy_model_name=choppy_model),
            f"Konsensüs Kaçağı ({maverick_thresh}%)": ConsensusMaverickPredictor(threshold_percentage=maverick_thresh),
            "Ters Köşe (Anti-Zigzag)": AntiTrendPredictor(),
            "Vasi Meta-Tahminci": GuardianMetaPredictor(risk_params=guardian_risk_params)
         }
        self.meta_model_names = {
            f"Ayakkabı Okuyucu (W{shoe_window})", f"Konsensüs Kaçağı ({maverick_thresh}%)",
            "Ters Köşe (Anti-Zigzag)", "Vasi Meta-Tahminci"
        }
        self.predictor_stats = { name: {'correct': 0, 'total': 0, 'last_prediction': 'N/A'} for name in self.predictors }
        self.last_run_results: Dict[str, Dict[str, Any]] = {}
        self.last_predictions: Dict[str, str] = {name: 'N/A' for name in self.predictors}
        self.stats_dialog_instance = None

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
        guardian_result_data = self.last_run_results.get("Vasi Meta-Tahminci", {})
        predicted_result_for_bet = guardian_result_data.get('prediction', 'N/A')
        is_tie = (actual_result == 'T')
        if not is_tie:
            for name, last_pred in self.last_predictions.items():
                if last_pred in ('P', 'B'):
                    stat = self.predictor_stats[name]
                    stat['total'] += 1
                    if last_pred == actual_result: stat['correct'] += 1
                    stat['last_prediction'] = last_pred
        self.model.add_result(actual_result, predicted_result_for_bet)
        if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
            self.stats_dialog_instance.update_data(self.predictor_stats)

    def handle_undo(self):
        if self.is_simulating:
             print("Cannot undo while simulation is running.")
             return
        self.model.undo_last()

    def handle_clear(self):
        if self.is_simulating:
             print("Stopping simulation before clearing.")
             self.handle_simulation_toggle()
        self.predictor_stats = { name: {'correct': 0, 'total': 0, 'last_prediction': 'N/A'} for name in self.predictors }
        self.last_run_results = {}
        self.last_predictions = {name: 'N/A' for name in self.predictors}
        self.model.clear_results()
        self.simulator.shuffle_and_reset()
        print("History cleared, stats reset, and simulator reset.")
        if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
            self.stats_dialog_instance.update_data(self.predictor_stats)

    def run_predictions(self, history):
        if not history:
            self.last_predictions = {name: 'N/A' for name in self.predictors}
            self.last_run_results = {}
            self.view.update_prediction_display("N/A", 0.0, 0.0)
            if self.stats_dialog_instance and self.stats_dialog_instance.isVisible():
                 self.stats_dialog_instance.update_data(self.predictor_stats)
            return

        current_run_results: Dict[str, Dict[str, Any]] = {}
        guardian_predictor_instance = self.predictors.get("Vasi Meta-Tahminci")
        guardian_name = "Vasi Meta-Tahminci"

        # Adım 1: Tüm Modelleri Çalıştır (Vasi hariç)
        for name, predictor in self.predictors.items():
            if predictor == guardian_predictor_instance: continue

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

        # Adım 2: Vasi Meta-Tahminci'yi Çalıştır
        final_prediction = 'N/A'; final_confidence = 0.0; final_probability = 0.0
        if guardian_predictor_instance and guardian_name:
             try:
                 prediction = guardian_predictor_instance.predict(history, current_run_results, self.predictor_stats, self.predictors)
                 if prediction != 'N/A':
                      final_prediction = prediction
                      final_confidence = guardian_predictor_instance.get_confidence(history, current_run_results, self.predictor_stats, self.predictors)
                      final_probability = guardian_predictor_instance.get_probability(history, current_run_results, self.predictor_stats, self.predictors)
             except Exception as e:
                  print(f"Error running predictor {guardian_name}: {e}")
                  final_prediction = 'N/A'
             current_run_results[guardian_name] = {'prediction': final_prediction, 'confidence': final_confidence, 'probability': final_probability}
        else: # Vasi yoksa Zigzag'ı kullan
             zigzag_data = current_run_results.get("Zigzag", {})
             final_prediction = zigzag_data.get('prediction', 'N/A')
             final_confidence = zigzag_data.get('confidence', 0.0)
             final_probability = zigzag_data.get('probability', 0.0)
             if guardian_name in self.predictors:
                 current_run_results[guardian_name] = {'prediction': 'N/A', 'confidence': 0.0, 'probability': 0.0}

        # Adım 3: Tüm sonuçları sakla
        self.last_run_results = current_run_results.copy()
        self.last_predictions = {name: data['prediction'] for name, data in current_run_results.items()}

        # Adım 4: Ana ekranda gösterilecek tahmini belirle (Vasi'nin dediği!)
        display_prediction = final_prediction
        display_confidence = final_confidence
        display_probability = final_probability

        # Adım 5: Ana tahmin ekranını güncelle
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

    def run(self):
        self.view.show()
        self.model._update_and_emit() # Başlangıç kasa bilgisini gönder
        self.run_predictions(self.model.full_history_sequence)
        sys.exit(self.app.exec())

if __name__ == '__main__':
    controller = ApplicationController()
    controller.run()