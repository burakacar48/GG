# predictors/visual_density_predictor.py
from typing import List # <<< typing modülünden List'i import et

class VisualDensityPredictor:
    """
    Matrise bakarak P ve B renklerinin oluşturduğu en büyük bitişik
    blokların boyutlarını karşılaştırır. Daha 'yoğun' (büyük bloğa sahip)
    rengin momentumunun devam edeceğini tahmin eder.
    """
    MATRIX_ROWS = 5
    MATRIX_COLS = 5
    MATRIX_SIZE = MATRIX_ROWS * MATRIX_COLS

    # <<< Tip ipucunu güncelle: list[list[str]] -> List[List[str]] >>>
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
                    matrix[r][c] = result if result in ('P', 'B') else '-' # Tie'ları sayma
        return matrix

    # <<< Tip ipucunu güncelle: list[list[str]] -> List[List[str]] >>>
    def _find_largest_block(self, matrix: List[List[str]], target: str) -> int:
        """
        Matriste belirli bir hedef (P veya B) için en büyük bitişik bloğun
        boyutunu bulan basit bir Depth First Search (DFS) algoritması.
        """
        rows, cols = self.MATRIX_ROWS, self.MATRIX_COLS
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        max_size = 0

        for r in range(rows):
            for c in range(cols):
                if matrix[r][c] == target and not visited[r][c]:
                    current_size = 0
                    stack = [(r, c)] # DFS için stack
                    visited[r][c] = True

                    while stack:
                        row, col = stack.pop()
                        current_size += 1
                        # Komşuları kontrol et (yukarı, aşağı, sol, sağ)
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nr, nc = row + dr, col + dc
                            if (0 <= nr < rows and 0 <= nc < cols and
                                    matrix[nr][nc] == target and not visited[nr][nc]):
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                    max_size = max(max_size, current_size)
        return max_size

    # <<< Tip ipucunu güncelle: list -> List >>>
    def predict(self, history: List[str]) -> str:
        """
        P ve B için en büyük blok boyutlarını karşılaştırır ve büyük olanı tahmin eder.
        """
        if len(history) < 5: return "N/A"
        matrix = self._get_matrix_from_history(history)
        valid_cells = sum(row.count('P') + row.count('B') for row in matrix)
        if valid_cells < 5: return "N/A"

        largest_p_block = self._find_largest_block(matrix, 'P')
        largest_b_block = self._find_largest_block(matrix, 'B')

        if largest_p_block > largest_b_block: return 'P'
        elif largest_b_block > largest_p_block: return 'B'
        else: return "N/A"

    # <<< Tip ipucunu güncelle: list -> List >>>
    def get_confidence(self, history: List[str]) -> float:
        """Tahminin güven oranını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0

        matrix = self._get_matrix_from_history(history)
        largest_p_block = self._find_largest_block(matrix, 'P')
        largest_b_block = self._find_largest_block(matrix, 'B')
        diff = abs(largest_p_block - largest_b_block)
        max_block = max(largest_p_block, largest_b_block)
        confidence = 35.0 + (diff * 5.0) + (max_block * 1.5)
        return max(25.0, min(90.0, confidence))

    # <<< Tip ipucunu güncelle: list -> List >>>
    def get_probability(self, history: List[str]) -> float:
        """Tahminin gerçekleşme olasılığını döndürür."""
        prediction = self.predict(history)
        if prediction == "N/A": return 0.0

        matrix = self._get_matrix_from_history(history)
        largest_p_block = self._find_largest_block(matrix, 'P')
        largest_b_block = self._find_largest_block(matrix, 'B')
        total_p = sum(row.count('P') for row in matrix)
        total_b = sum(row.count('B') for row in matrix)
        total_valid = total_p + total_b
        if total_valid == 0: return 50.0

        prob = 50.0
        if prediction == 'P':
            block_factor = largest_p_block / self.MATRIX_SIZE
            overall_ratio = total_p / total_valid
            prob = 50.0 + (block_factor * 30.0) + ((overall_ratio - 0.5) * 20.0)
        elif prediction == 'B':
            block_factor = largest_b_block / self.MATRIX_SIZE
            overall_ratio = total_b / total_valid
            prob = 50.0 + (block_factor * 30.0) + ((overall_ratio - 0.5) * 20.0)
        return max(20.0, min(80.0, prob))
