import time
import random # Alternatif veya yedek için

class ChaosWalkerPredictor:
    """
    Baccarat'ın rastgeleliğine oynayan model.
    Tahminini sistem saatinin milisaniyesine göre yapar.
    Tek milisaniye -> P, Çift milisaniye -> B (veya tersi).
    """

    def predict(self, history: list) -> str:
        """
        Sistem saatinin milisaniyesine göre 'P' veya 'B' tahmini yapar.
        'history' parametresi bu model için kullanılmaz.
        """
        try:
            # Zamanı al ve milisaniyeyi (veya mikrosaniyeyi) kullan
            # time.time() saniye cinsinden float verir. Ondalık kısmını alalım.
            current_time = time.time()
            # Milisaniye veya mikrosaniye hassasiyetini almak için ondalık kısmı alıp büyütelim
            # ve integer'a çevirelim. Son rakamına bakalım.
            fractional_part_str = str(current_time - int(current_time))[2:] # "0." kısmını at
            if not fractional_part_str: # Tam saniye ise (çok nadir) rastgele seç
                 return random.choice(['P', 'B'])

            # Son rakamı al (yeterince rastgele olmalı)
            last_digit = int(fractional_part_str[-1])

            # Tek ise Player, Çift ise Banker (veya tam tersi, bu keyfi bir seçim)
            if last_digit % 2 != 0:
                return 'P'
            else:
                return 'B'

        except Exception:
            # Herhangi bir hata durumunda rastgele tahmin yap
            # print(f"ChaosWalker time error: {e}") # Hata ayıklama için
            return random.choice(['P', 'B'])


    def get_confidence(self, history: list) -> float:
        """
        Tahminin güven oranını döndürür.
        Rastgeleliğe dayandığı için düşük/orta sabit bir güven verelim.
        """
        # Belki zamanla hafifçe değişen bir şey yapılabilir ama şimdilik sabit.
        return 35.0 # Düşük ama sıfır değil

    def get_probability(self, history: list) -> float:
        """
        Tahminin gerçekleşme olasılığını döndürür.
        Tamamen rastgele olduğu varsayıldığı için %50 verelim.
        """
        return 50.0
