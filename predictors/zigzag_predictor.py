class ZigzagPredictor:
    """
    Baccarat için basit bir Zigzag tahmin modeli.
    - Son iki farklı sonuç (Tie hariç) aynıysa (PP/BB), diğerini tahmin eder (B/P - Zig).
    - Son iki farklı sonuç farklıysa (PB/BP), son sonucu tekrar tahmin eder (B/P - Zag).
    """
    def predict(self, history: list) -> str:
        relevant_history = [res for res in history if res in ('P', 'B')]
        if len(relevant_history) < 2: return "N/A"
        last_result, second_last_result = relevant_history[-1], relevant_history[-2]
        if last_result == second_last_result: return 'B' if last_result == 'P' else 'P'
        else: return last_result

    def get_confidence(self, history: list) -> float:
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0
        relevant = [res for res in history if res in ('P', 'B')][-6:]
        if len(relevant) < 3: return 40.0
        correct_zigzags = 0; total_checks = 0
        for i in range(len(relevant) - 2):
            check_idx = i + 2; actual = relevant[check_idx]
            prev, second_prev = relevant[check_idx-1], relevant[check_idx-2]
            predicted = ('B' if prev == 'P' else 'P') if prev == second_prev else prev
            if predicted == actual: correct_zigzags += 1
            total_checks += 1
        base_confidence = 50.0
        if total_checks > 0: base_confidence = 40.0 + ((correct_zigzags / total_checks) * 100 * 0.5)
        if len(relevant) >= 2 and relevant[-1] != relevant[-2]: base_confidence += 5
        else: base_confidence -= 5
        return max(20.0, min(95.0, base_confidence))

    def get_probability(self, history: list) -> float:
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0
        relevant = [res for res in history if res in ('P', 'B')]
        if not relevant: return 50.0
        total_pb = len(relevant); count = relevant.count(prediction)
        probability = (count / total_pb) * 100
        balanced_prob = 50.0 + (probability - 50.0) * 0.8
        return max(10.0, min(90.0, balanced_prob))
