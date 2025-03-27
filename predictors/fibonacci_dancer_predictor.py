class FibonacciDancerPredictor:
    """
    Mevcut el sayısının (Tie'lar hariç) bir Fibonacci sayısına
    denk gelip gelmediğine göre tahmin yapan model.
    Fibonacci sayılarında 'özel' bir tahmin (örn: son elin tersi),
    diğer ellerde 'normal' bir tahmin (örn: son eli tekrar et) yapar.
    """

    def __init__(self, max_fib_check=100):
        # Kontrol edilecek maksimum el sayısı için Fibonacci sayılarını üret
        self.fibonacci_numbers = self._generate_fibonacci_up_to(max_fib_check)
        # print(f"Fibonacci numbers to check: {self.fibonacci_numbers}") # Debug

    def _generate_fibonacci_up_to(self, limit):
        """Belirtilen limite kadar olan Fibonacci sayılarını içeren bir set döndürür."""
        fib_set = set()
        a, b = 0, 1
        while b <= limit: # Limit dahil
            fib_set.add(b)
            a, b = b, a + b
        # Genellikle Baccarat'ta ilk el önemli sayılmaz ama 1'i ekleyelim
        if 1 not in fib_set:
             fib_set.add(1)
        return fib_set

    def predict(self, history: list) -> str:
        """
        Mevcut P/B el sayısının Fibonacci olup olmadığına göre tahmin yapar.
        """
        relevant_history = [res for res in history if res in ('P', 'B')]
        current_hand_number = len(relevant_history) # Mevcut el sayısı (0'dan değil, 1'den başlar gibi düşünelim)

        # Tahmin için en az 1 önceki el gerekli
        if current_hand_number < 1:
            return "N/A"

        last_result = relevant_history[-1]

        # Mevcut el sayısı (bir sonraki elin numarası) Fibonacci mi?
        # Dikkat: Tahmin ettiğimiz el, mevcut el sayısının +1'i olacak.
        next_hand_number = current_hand_number + 1

        if next_hand_number in self.fibonacci_numbers:
            # Fibonacci Günü! Özel tahmin: Son elin tersini alalım (keyfi seçim)
            # print(f"Fibonacci Hand ({next_hand_number})! Predicting opposite of {last_result}") # Debug
            return 'B' if last_result == 'P' else 'P'
        else:
            # Normal gün. Normal tahmin: Son eli tekrar edelim (keyfi seçim)
            # print(f"Normal Hand ({next_hand_number}). Predicting same as {last_result}") # Debug
            return last_result

    def get_confidence(self, history: list) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        relevant_history = [res for res in history if res in ('P', 'B')]
        current_hand_number = len(relevant_history)
        next_hand_number = current_hand_number + 1

        # Fibonacci ellerinde güven biraz daha yüksek olsun (mistik güç! 😄)
        if next_hand_number in self.fibonacci_numbers:
            return 60.0
        else:
            # Normal ellerde daha standart bir güven
            return 45.0

    def get_probability(self, history: list) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A":
            return 0.0

        # Fibonacci'nin gerçek bir etkisi olmadığı varsayımıyla, %50'ye yakın tutalım.
        # Güven gibi hafif bir ayrım yapabiliriz.
        relevant_history = [res for res in history if res in ('P', 'B')]
        current_hand_number = len(relevant_history)
        next_hand_number = current_hand_number + 1

        if next_hand_number in self.fibonacci_numbers:
            return 52.0 # Hafifçe yüksek
        else:
            return 48.0 # Hafifçe düşük
