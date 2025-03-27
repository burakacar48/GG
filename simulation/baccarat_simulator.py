import random
from collections import deque
from typing import List, Tuple, Optional # Tip ipuçları için

class BaccaratSimulator:
    """
    Baccarat oyunu için bir simülasyon motoru.
    Ayakkabı oluşturma, karıştırma, yakma kartı, kesme kartı ve
    standart Baccarat kurallarına göre el dağıtma işlemlerini yapar.
    """
    CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 0, 'J': 0, 'Q': 0, 'K': 0}
    CARD_PIP_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}

    def __init__(self, num_decks: int = 8, cut_card_depth_approx: int = 14):
        """
        Simülatörü başlatır.
        :param num_decks: Ayakkabıdaki deste sayısı.
        :param cut_card_depth_approx: Kesme kartının ayakkabının SONUNDAN itibaren
                                      yaklaşık olarak kaç kart önce yerleştirileceği.
                                      Standart olarak ~14 kart kala (1 desteye yakın).
        """
        self.num_decks = num_decks
        self.cut_card_depth = cut_card_depth_approx
        self.shoe = deque()
        self.initial_shoe_size_after_burn = 0 # Yakma sonrası kart sayısı (index takibi için)
        self.cards_dealt_count = 0 # Dağıtılan kart sayısı
        self.cut_card_position_index = -1 # Kesme kartının *tam olarak* arkasındaki kartın index'i
        self.cut_card_reached = False
        self.play_one_more_hand_after_cut = False
        self.shuffle_and_reset()

    def _create_shoe(self) -> List[str]:
        """Belirtilen sayıda deste ile bir kart listesi oluşturur."""
        suits = ['H', 'D', 'C', 'S']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        deck = [rank for rank in ranks for _ in suits]
        full_shoe = deck * self.num_decks
        return full_shoe

    def _burn_cards(self):
        """Yakma kartı kurallarını uygular."""
        if not self.shoe: return

        first_card_rank = self.shoe.popleft()
        burn_value = self.CARD_PIP_VALUES.get(first_card_rank, 0)
        num_to_burn = 0

        if burn_value == 1: num_to_burn = 1
        elif burn_value == 10: num_to_burn = 10 # T, J, Q, K pip değeri 10
        elif 2 <= burn_value <= 9: num_to_burn = burn_value

        # print(f"Burning: First card was {first_card_rank}, burning {num_to_burn} cards.")
        for _ in range(num_to_burn):
            if self.shoe: self.shoe.popleft()
            else: break

    def _place_cut_card(self):
        """Kesme kartının pozisyonunu belirler (sondan X kart önce)."""
        # Ayakkabıda kalan kart sayısından kesme derinliğini çıkar.
        # Bu, kesme kartının hemen arkasındaki kartın index'i olur (0-bazlı).
        self.cut_card_position_index = max(0, len(self.shoe) - self.cut_card_depth -1) # -1 çünkü 0-bazlı index
        # print(f"Cut card placed effectively after index {self.cut_card_position_index} (approx. {self.cut_card_depth} cards from end)")

    def shuffle_and_reset(self):
        """Yeni bir ayakkabı oluşturur, karıştırır, yakar ve kesme kartını yerleştirir."""
        # print("\n--- SHUFFLING NEW SHOE ---")
        shoe_list = self._create_shoe()
        random.shuffle(shoe_list)
        self.shoe = deque(shoe_list)
        self._burn_cards() # Önce yak
        self.initial_shoe_size_after_burn = len(self.shoe) # Yakma sonrası boyutu sakla
        self._place_cut_card() # Sonra kesme kartını yerleştir (pozisyonunu belirle)
        self.cards_dealt_count = 0 # Dağıtılan kart sayacını sıfırla
        self.cut_card_reached = False
        self.play_one_more_hand_after_cut = False

    def _deal_card(self) -> Optional[str]:
        """Ayakkabıdan bir kart çeker, sayacı artırır ve kesme kartını kontrol eder."""
        if not self.shoe:
            self.cut_card_reached = True # Ayakkabı bittiyse de kesme kartı geçmiş sayılır
            return None

        # Kesme kartına ulaşıldı mı?
        # Eğer dağıtılan kart sayısı kesme kartı pozisyonunu geçtiyse.
        if not self.cut_card_reached and self.cards_dealt_count > self.cut_card_position_index:
            # print(f"CUT CARD REACHED at card {self.cards_dealt_count + 1} (Position was after index {self.cut_card_position_index})!")
            self.cut_card_reached = True
            # Kural 2 & 3: Bu eli bitir, bir el daha oyna.
            # Bu bayrak deal_hand sonunda kontrol edilecek.
            self.play_one_more_hand_after_cut = True

        card = self.shoe.popleft()
        self.cards_dealt_count += 1 # Dağıtılan kart sayısını artır
        # print(f"Dealt card #{self.cards_dealt_count}: {card}") # Debug
        return card

    def _get_baccarat_value(self, cards: List[str]) -> int:
        """Verilen kart listesinin Baccarat değerini (0-9) hesaplar."""
        total = sum(self.CARD_VALUES.get(card, 0) for card in cards)
        return total % 10

    def needs_shuffle(self) -> bool:
        """Ayakkabının karıştırılması gerekip gerekmediğini kontrol eder."""
        # Eğer kesme kartına ulaşıldıysa VE 'son bir el oyna' bayrağı False ise karıştır.
        return self.cut_card_reached and not self.play_one_more_hand_after_cut

    def deal_hand(self) -> Optional[str]:
        """
        Bir el Baccarat oynar ve sonucu ('P', 'B', 'T') döndürür.
        Ayakkabı karıştırılması gerekiyorsa veya bittiyse None döner.
        """
        if self.needs_shuffle():
            # print("Shuffle required before next hand.")
            return None # Karıştırılması lazım

        # Eğer bu el, kesme kartından sonraki "son el" ise, işareti ayarla
        is_last_hand = self.play_one_more_hand_after_cut
        if is_last_hand:
            self.play_one_more_hand_after_cut = False # Bayrağı indir, bu el sondu.

        player_hand: List[str] = []
        banker_hand: List[str] = []

        # İlk iki kartı dağıt
        for _ in range(2):
            p_card = self._deal_card()
            if p_card is None: return None # Ayakkabı bitti
            player_hand.append(p_card)

            b_card = self._deal_card()
            if b_card is None: return None # Ayakkabı bitti
            banker_hand.append(b_card)

        player_score = self._get_baccarat_value(player_hand)
        banker_score = self._get_baccarat_value(banker_hand)

        # Doğal (Natural) kontrolü
        is_player_natural = player_score >= 8
        is_banker_natural = banker_score >= 8

        if is_player_natural or is_banker_natural:
            # print(f"Natural! P:{player_score} B:{banker_score}") # Debug
            if player_score > banker_score: return 'P'
            elif banker_score > player_score: return 'B'
            else: return 'T'

        # Player için üçüncü kart kuralı
        player_draws = False
        if player_score <= 5:
            p_third_card = self._deal_card()
            if p_third_card is None: return None # Ayakkabı bitti
            player_hand.append(p_third_card)
            player_score = self._get_baccarat_value(player_hand)
            player_draws = True
            player_third_card_value = self.CARD_VALUES.get(p_third_card, 0) # Banker kuralı için
        # else: Player 6 veya 7 ile durur

        # Banker için üçüncü kart kuralı
        banker_draws = False
        if not player_draws: # Eğer Player üçüncü kart çekmediyse (6 veya 7 ile durduysa)
            if banker_score <= 5:
                b_third_card = self._deal_card()
                if b_third_card is None: return None
                banker_hand.append(b_third_card)
                banker_score = self._get_baccarat_value(banker_hand)
                banker_draws = True
            # else: Banker 6 veya 7 ile durur
        else: # Eğer Player üçüncü kart çektiyse
            if banker_score <= 2:
                banker_draws = True
            elif banker_score == 3 and player_third_card_value != 8:
                banker_draws = True
            elif banker_score == 4 and player_third_card_value in (2, 3, 4, 5, 6, 7):
                banker_draws = True
            elif banker_score == 5 and player_third_card_value in (4, 5, 6, 7):
                banker_draws = True
            elif banker_score == 6 and player_third_card_value in (6, 7):
                banker_draws = True
            # else: Banker 7 ile durur veya diğer durumlarda durur

            if banker_draws:
                b_third_card = self._deal_card()
                if b_third_card is None: return None
                banker_hand.append(b_third_card)
                banker_score = self._get_baccarat_value(banker_hand)

        # print(f"Final Hands: P={player_hand} ({player_score}), B={banker_hand} ({banker_score})") # Debug

        # Sonucu belirle
        if player_score > banker_score: return 'P'
        elif banker_score > player_score: return 'B'
        else: return 'T'

    # Simülasyonu çalıştırmak için örnek bir metod (opsiyonel)
    def run_simulation(self, num_hands=100):
        """Belirtilen sayıda el oynar ve sonuçları listeler."""
        results = []
        for i in range(num_hands):
            result = self.deal_hand()
            if result is None:
                print(f"Simulation stopped after {i} hands due to shuffle needed or empty shoe.")
                break
            results.append(result)
            print(f"Hand {i+1}: {result}")
        return results

# Test için:
if __name__ == '__main__':
    simulator = BaccaratSimulator(num_decks=8, cut_card_depth_approx=14)
    # simulator.run_simulation(num_hands=70) # Tüm ayakkabıyı oynamaya çalış

    # Tek tek el oynama örneği
    for i in range(80): # Maksimum 80 el oyna
        hand_result = simulator.deal_hand()
        if hand_result is None:
            print(f"\nShuffle needed after hand {i}. Resetting shoe...")
            simulator.shuffle_and_reset()
            # İstersen karıştırma sonrası ilk eli de oyna
            # hand_result = simulator.deal_hand()
            # if hand_result: print(f"Hand {i+1} (after shuffle): {hand_result}")
            # else: print("Shoe empty even after shuffle?"); break
            break # Şimdilik duralım
        else:
             print(f"Hand {i+1}: {hand_result}")
