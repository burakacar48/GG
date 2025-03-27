# model/baccarat_model.py
from collections import deque
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Any # Tip ipuçları için

MATRIX_HISTORY_LEN = 25

class BaccaratModel(QObject):
    history_changed = pyqtSignal(list)
    # stats_updated sinyali artık kasa bilgilerini de içerecek
    stats_updated = pyqtSignal(dict)

    # Martingale Bahis Seviyeleri (Senin verdiğin liste)
    MARTINGALE_BETS = [4.00, 12.00, 32.00, 68.00, 144.00, 300.00, 620.00, 1300.00, 2660.00]
    # Not: Eğer liste biterse ne olacağına karar vermek lazım (örn: başa dön, max'ta kal, dur?)
    # Şimdilik max'ta kalacak şekilde ayarlayalım.

    def __init__(self, initial_balance=5000.0):
        super().__init__()
        # Geçmiş
        self.full_history_sequence: List[str] = []
        # Genel İstatistik Sayaçları
        self.total_hands_overall = 0
        self.player_wins_overall = 0
        self.banker_wins_overall = 0
        self.tie_wins_overall = 0
        # Kasa Yönetimi
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.initial_bet = self.MARTINGALE_BETS[0] # Listenin ilk elemanı
        self.current_bet = self.initial_bet
        self.martingale_level = 0 # Mevcut bahis seviyesinin index'i
        self.win_streak = 0
        self.loss_streak = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0

    # --- Ana Metodlar ---
    def add_result(self, actual_result: str, predicted_result: str):
        """
        Sonucu ekler, bahsi değerlendirir, kasayı günceller, sinyalleri tetikler.
        :param actual_result: Gerçekleşen sonuç ('P', 'B', 'T')
        :param predicted_result: O el için yapılan tahmin ('P', 'B', veya 'N/A')
        """
        if actual_result not in ('P', 'B', 'T'): return # Geçersiz sonuç

        # 1. Geçmişe Ekle
        self.full_history_sequence.append(actual_result)
        self.total_hands_overall += 1
        if actual_result == 'P': self.player_wins_overall += 1
        elif actual_result == 'B': self.banker_wins_overall += 1
        elif actual_result == 'T': self.tie_wins_overall += 1

        # 2. Bahsi Değerlendir (Tie durumunda bahis genellikle iade edilir - Push)
        # Sadece P veya B tahmini yapıldıysa ve sonuç Tie DEĞİLSE bahsi değerlendir.
        if predicted_result in ('P', 'B') and actual_result != 'T':
            bet_amount = self.current_bet
            won_bet = (predicted_result == actual_result)

            if won_bet:
                # Kazandık!
                # Banker kazancında %5 komisyon olduğunu varsayalım (yaklaşık Payout 0.95)
                # Player kazancında payout 1.0
                payout_multiplier = 0.95 if actual_result == 'B' else 1.0
                profit = bet_amount * payout_multiplier
                self.current_balance += profit
                # print(f"WIN! Bet: {bet_amount:.2f}, Won: {profit:.2f}, New Balance: {self.current_balance:.2f}") # Debug

                # Martingale resetle, serileri güncelle
                self.current_bet = self.initial_bet
                self.martingale_level = 0
                self.loss_streak = 0
                self.win_streak += 1
                self.max_win_streak = max(self.max_win_streak, self.win_streak)
            else:
                # Kaybettik!
                self.current_balance -= bet_amount
                # print(f"LOSS. Bet: {bet_amount:.2f}, New Balance: {self.current_balance:.2f}") # Debug

                # Martingale seviyesini artır, serileri güncelle
                self.martingale_level += 1
                # Bir sonraki bahsi belirle
                if self.martingale_level < len(self.MARTINGALE_BETS):
                    self.current_bet = self.MARTINGALE_BETS[self.martingale_level]
                else:
                    # Liste bitti, son bahiste kal veya başa dön? Şimdilik sonda kal.
                    self.current_bet = self.MARTINGALE_BETS[-1]
                    # Uyarı verebiliriz
                    # print("Warning: Martingale sequence limit reached!")
                self.win_streak = 0
                self.loss_streak += 1
                self.max_loss_streak = max(self.max_loss_streak, self.loss_streak)

        elif actual_result == 'T':
            # Beraberlikte bahis genellikle iade edilir (Push). Bakiye değişmez.
            # Martingale seviyesi ve seri değişmez. Bir sonraki bahis aynı kalır.
            # print("PUSH (Tie). Bet remains: {self.current_bet:.2f}") # Debug
            pass # Kasa/Martingale/Seri aynı kalır
        else:
             # Tahmin N/A ise veya geçersizse, bahis yapılmadı sayılır.
             # print("No bet placed (Prediction was N/A or invalid).") # Debug
             pass # Kasa/Martingale/Seri aynı kalır


        # 3. Sinyalleri Tetikle
        self._update_and_emit()

    def undo_last(self):
        """Son sonucu geri alır (Geçmişi ve Sayaçları). Kasa durumunu geri almak ZOR."""
        # DİKKAT: Martingale seviyesini, bahis miktarını ve kasayı doğru bir şekilde
        # geri almak çok karmaşık olabilir. Çünkü bir önceki durumun ne olduğunu
        # (kazanç mı kayıp mı, hangi seviyedeydi vb.) saklamamız gerekir.
        # ŞİMDİLİK, undo sadece geçmişi ve genel P/B/T sayaçlarını geri alsın.
        # Kasa ve Martingale durumu mevcut haliyle kalsın (basitleştirme).
        if self.full_history_sequence:
            popped_result = self.full_history_sequence.pop()
            if self.total_hands_overall > 0:
                 self.total_hands_overall -= 1
                 if popped_result == 'P' and self.player_wins_overall > 0: self.player_wins_overall -= 1
                 elif popped_result == 'B' and self.banker_wins_overall > 0: self.banker_wins_overall -= 1
                 elif popped_result == 'T' and self.tie_wins_overall > 0: self.tie_wins_overall -= 1
            # Kasa/Martingale/Seri durumunu geri ALMIYORUZ.
            self._update_and_emit() # Sadece güncel geçmiş ve stats'ı gönderir

    def clear_results(self):
        """Tüm geçmişi, sayaçları ve kasa durumunu sıfırlar."""
        self.full_history_sequence.clear()
        self.total_hands_overall = 0; self.player_wins_overall = 0
        self.banker_wins_overall = 0; self.tie_wins_overall = 0
        # Kasa ve Martingale'i de sıfırla
        self.current_balance = self.initial_balance
        self.current_bet = self.initial_bet
        self.martingale_level = 0
        self.win_streak = 0; self.loss_streak = 0
        self.max_win_streak = 0; self.max_loss_streak = 0
        self._update_and_emit() # Sıfırlanmış durumu gönder

    def _calculate_overall_statistics(self) -> dict:
        """Genel sayaçları ve MEVCUT kasa durumunu içeren sözlüğü döndürür."""
        total = self.total_hands_overall; p = self.player_wins_overall
        b = self.banker_wins_overall; t = self.tie_wins_overall
        pp = (p / total * 100) if total > 0 else 0; bp = (b / total * 100) if total > 0 else 0
        tp = (t / total * 100) if total > 0 else 0
        return {
            # Genel İstatistikler
            'total': total, 'player': p, 'banker': b, 'tie': t,
            'player_perc': pp, 'banker_perc': bp, 'tie_perc': tp,
            # Kasa Bilgileri
            'current_balance': self.current_balance,
            'current_bet': self.current_bet,
            'martingale_level': self.martingale_level,
            'win_streak': self.win_streak,
            'loss_streak': self.loss_streak,
            'max_win_streak': self.max_win_streak,
            'max_loss_streak': self.max_loss_streak,
        }

    def _update_and_emit(self):
        """TAM geçmiş listesini ve genel/kasa istatistiklerini yayınlar."""
        current_full_history = list(self.full_history_sequence)
        self.history_changed.emit(current_full_history)
        overall_stats_and_bankroll = self._calculate_overall_statistics()
        self.stats_updated.emit(overall_stats_and_bankroll)
