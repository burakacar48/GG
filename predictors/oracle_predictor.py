# predictors/oracle_predictor.py
import math
from typing import List, Tuple # <<< typing modülünden List ve Tuple'ı import et

class OraclePredictor:
    """
    Baccarat Falcısı! Son 5x5 matrise bakarak 'uğurlu' veya
    'uğursuz' desenlere göre kehanette bulunur.
    """
    MATRIX_ROWS = 5
    MATRIX_COLS = 5
    MATRIX_SIZE = MATRIX_ROWS * MATRIX_COLS

    # <<< Tip ipucunu güncelle: list[list[str]] yerine List[List[str]] >>>
    def _get_matrix_from_history(self, history: List[str]) -> List[List[str]]:
        """Tam geçmiş listesini alır ve son 25 eli 5x5 matris olarak döndürür."""
        matrix = [['-' for _ in range(self.MATRIX_COLS)] for _ in range(self.MATRIX_ROWS)]
        history_for_matrix = history[-self.MATRIX_SIZE:]
        history_len = len(history_for_matrix)

        for r in range(self.MATRIX_ROWS):
            for c in range(self.MATRIX_COLS):
                index = history_len - self.MATRIX_SIZE + (r * self.MATRIX_COLS + c)
                if 0 <= index < history_len:
                    result = history_for_matrix[index]
                    matrix[r][c] = result if result in ('P','B','T') else '-'
        return matrix

    # <<< Tip ipucunu güncelle: list yerine List >>>
    def predict(self, history: List[str]) -> str:
        """
        Matrise bakarak fal yorumlar ve 'P', 'B' veya 'N/A' döndürür.
        """
        if len(history) < 5: return "N/A"
        matrix = self._get_matrix_from_history(history)
        p_signs = 0; b_signs = 0

        # --- Fal Yorumlama Kuralları ---
        diag1 = [matrix[i][i] for i in range(self.MATRIX_ROWS)]
        diag2 = [matrix[i][self.MATRIX_COLS - 1 - i] for i in range(self.MATRIX_ROWS)]
        if all(cell == 'P' for cell in diag1 if cell in ('P', 'B')): p_signs += 2
        if all(cell == 'B' for cell in diag2 if cell in ('P', 'B')): b_signs += 2
        center_p = 0; center_b = 0
        for r in range(1, 4):
            for c in range(1, 4):
                if matrix[r][c] == 'P': center_p += 1
                elif matrix[r][c] == 'B': center_b += 1
        if center_p > center_b and center_p >= 4: p_signs += 1
        if center_b > center_p and center_b >= 4: b_signs += 1
        last_row = matrix[self.MATRIX_ROWS - 1]
        first_col = [matrix[r][0] for r in range(self.MATRIX_ROWS)]
        if last_row.count('P') >= 3: p_signs += 1
        if first_col.count('B') >= 3: b_signs += 1

        # --- Kehanet Zamanı ---
        if p_signs > b_signs: return 'P'
        elif b_signs > p_signs: return 'B'
        else: return "N/A"

    # <<< Tip ipucunu güncelle: list yerine List >>>
    def get_confidence(self, history: List[str]) -> float:
        """Tahminin güven oranını döndürür."""
        matrix = self._get_matrix_from_history(history)
        p_signs = 0; b_signs = 0
        # ... (işaret hesaplamaları tekrar) ...
        diag1 = [matrix[i][i] for i in range(self.MATRIX_ROWS)]
        diag2 = [matrix[i][self.MATRIX_COLS - 1 - i] for i in range(self.MATRIX_ROWS)]
        if all(cell == 'P' for cell in diag1 if cell in ('P', 'B')): p_signs += 2
        if all(cell == 'B' for cell in diag2 if cell in ('P', 'B')): b_signs += 2
        center_p = 0; center_b = 0
        for r in range(1, 4):
            for c in range(1, 4):
                if matrix[r][c] == 'P': center_p += 1
                elif matrix[r][c] == 'B': center_b += 1
        if center_p > center_b and center_p >= 4: p_signs += 1
        if center_b > center_p and center_b >= 4: b_signs += 1
        last_row = matrix[self.MATRIX_ROWS - 1]
        first_col = [matrix[r][0] for r in range(self.MATRIX_ROWS)]
        if last_row.count('P') >= 3: p_signs += 1
        if first_col.count('B') >= 3: b_signs += 1
        # --- Hesaplama sonu ---

        sign_difference = abs(p_signs - b_signs)
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0
        else:
            confidence = 30.0 + (sign_difference * 15.0)
            return max(20.0, min(80.0, confidence))

    # <<< Tip ipucunu güncelle: list yerine List >>>
    def get_probability(self, history: List[str]) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        confidence = self.get_confidence(history)
        if confidence == 0.0: return 0.0
        probability = 50.0 + (confidence - 50.0) * 0.4
        return max(30.0, min(70.0, probability))
