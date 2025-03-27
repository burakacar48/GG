# view/main_window.py
import sys
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QProgressBar, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
try:
    from typing import List, Dict, Any
except ImportError:
    List = list; Dict = dict; Any = any

COLOR_BACKGROUND="#121212";COLOR_PANEL_BG="#1E1E1E";COLOR_SECTION_BG="#262626"
COLOR_BORDER="#333333";COLOR_TEXT_HEADER="#FFFFFF";COLOR_TEXT_NORMAL="#E0E0E0"
COLOR_TEXT_DIM="#BBBBBB";COLOR_TEXT_BUTTON="#FFFFFF";COLOR_PLAYER="#3D59AB"
COLOR_BANKER="#B22222";COLOR_TIE="#777777";COLOR_PROGRESS_CONF="#4CC9F0"
COLOR_PROGRESS_PROB="#FF9F1C";COLOR_KASA="#4CC9F0";COLOR_BAHIS="#FF9F1C"
COLOR_WIN="#2ECC71";COLOR_LOSS="#E74C3C"
COLOR_MATRIX_EMPTY_BG="#222222";COLOR_MATRIX_EMPTY_TEXT="#777777"
COLOR_PLAYER_HOVER="#5C7BC8";COLOR_PLAYER_PRESSED="#2E4A8A"
COLOR_BANKER_HOVER="#D44848";COLOR_BANKER_PRESSED="#9E1C1C"
COLOR_EMOJI_HOVER_BG="#333333";COLOR_EMOJI_PRESSED_BG="#444444"
MATRIX_ROWS=5;MATRIX_COLS=5
MATRIX_HISTORY_LEN=MATRIX_ROWS*MATRIX_COLS

class BaccaratView(QWidget):
    player_clicked = pyqtSignal()
    banker_clicked = pyqtSignal()
    tie_clicked = pyqtSignal()
    undo_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()
    stats_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BACCARAT TAHMİN UYGULAMASI")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint) # Hep üstte
        self.matrix_labels: List[List[QLabel]] = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        self._apply_styles()
        header_widget = QWidget(); header_widget.setFixedHeight(60); header_widget.setStyleSheet(f"background-color: {COLOR_PANEL_BG};")
        header_layout = QHBoxLayout(header_widget); header_layout.setContentsMargins(40, 0, 0, 0)
        title_label = QLabel("BACCARAT TAHMİN UYGULAMASI"); title_label.setObjectName("TitleLabel")
        header_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignVCenter); main_layout.addWidget(header_widget)
        content_widget = QWidget(); content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20); content_layout.setSpacing(20)
        left_panel = self._create_left_panel(); right_panel = self._create_right_panel()
        content_layout.addWidget(left_panel, 280); content_layout.addWidget(right_panel, 460)
        main_layout.addWidget(content_widget); self.setLayout(main_layout)

    def _apply_styles(self):
         self.setStyleSheet(f"""
            QWidget{{background-color:{COLOR_BACKGROUND};color:{COLOR_TEXT_NORMAL};font-family:Arial;}}
            QPushButton{{color:{COLOR_TEXT_BUTTON};border:1px solid {COLOR_BORDER};border-radius:8px;padding:5px 10px;font-size:14px;font-weight:bold;background-color:{COLOR_SECTION_BG};}}
            QPushButton:hover{{background-color:#3a3a3a;border:1px solid #555555;}}
            QPushButton:pressed{{background-color:#2f2f2f;border:1px solid #444444;}}
            QLabel{{color:{COLOR_TEXT_NORMAL};font-size:14px;background-color:transparent;}}
            QLabel#SmallStatusLabel{{font-size:11px; color:{COLOR_TEXT_DIM};}}
            QProgressBar{{border:none;border-radius:8px;background-color:{COLOR_BORDER};text-align:center;height:16px;}}
            QProgressBar::chunk{{border-radius:8px;}}
            QFrame#SectionFrame{{background-color:{COLOR_SECTION_BG};border-radius:8px;}}
            QWidget#LeftPanel,QWidget#RightPanel{{background-color:{COLOR_PANEL_BG};border-radius:8px;}}
            QLabel#TitleLabel{{color:{COLOR_TEXT_HEADER};font-size:22px;font-weight:bold;}}
            QLabel#SectionTitleLabel{{color:{COLOR_TEXT_HEADER};font-size:16px;font-weight:bold;alignment:AlignCenter;}}
            QLabel#ValueLabel{{font-weight:bold;alignment:AlignRight;}}
            QLabel#MatrixLabel{{font-size:20px;font-weight:bold;border-radius:4px;border:1px solid {COLOR_BORDER};}}
            QPushButton#EmojiButton{{font-size:24px;background-color:transparent;border:none;border-radius:5px;padding:5px;}}
            QPushButton#EmojiButton:hover{{background-color:{COLOR_EMOJI_HOVER_BG};}}
            QPushButton#EmojiButton:pressed{{background-color:{COLOR_EMOJI_PRESSED_BG};}}""")

    def _create_styled_frame(self): frame = QFrame(); frame.setObjectName("SectionFrame"); return frame

    def _create_left_panel(self):
        panel = QWidget(); panel.setObjectName("LeftPanel"); panel.setFixedWidth(280)
        layout = QVBoxLayout(panel); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(20)
        controls_frame = self._create_styled_frame(); controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(10, 10, 10, 10); controls_layout.setSpacing(15)
        controls_title = QLabel("KONTROLLER"); controls_title.setObjectName("SectionTitleLabel"); controls_layout.addWidget(controls_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        pb_layout = QHBoxLayout(); pb_layout.setSpacing(10)
        self.player_btn = QPushButton("PLAYER"); self.player_btn.setFixedSize(110, 50); self.player_btn.setStyleSheet(f"QPushButton{{background-color:{COLOR_PLAYER};border-radius:25px;font-size:18px;color:{COLOR_TEXT_BUTTON};border:none;}} QPushButton:hover{{background-color:{COLOR_PLAYER_HOVER};}} QPushButton:pressed{{background-color:{COLOR_PLAYER_PRESSED};}}")
        self.banker_btn = QPushButton("BANKER"); self.banker_btn.setFixedSize(100, 50); self.banker_btn.setStyleSheet(f"QPushButton{{background-color:{COLOR_BANKER};border-radius:25px;font-size:18px;color:{COLOR_TEXT_BUTTON};border:none;}} QPushButton:hover{{background-color:{COLOR_BANKER_HOVER};}} QPushButton:pressed{{background-color:{COLOR_BANKER_PRESSED};}}")
        pb_layout.addWidget(self.player_btn); pb_layout.addWidget(self.banker_btn); controls_layout.addLayout(pb_layout)
        self.player_btn.clicked.connect(self.player_clicked.emit); self.banker_btn.clicked.connect(self.banker_clicked.emit)
        action_layout = QHBoxLayout(); action_layout.setSpacing(10); action_layout.addStretch()
        undo_btn = QPushButton("↩️"); self.sim_btn = QPushButton("▶️"); clear_btn = QPushButton("🗑️"); stats_btn = QPushButton("📊")
        for btn in [undo_btn, self.sim_btn, clear_btn, stats_btn]: btn.setObjectName("EmojiButton"); btn.setFixedSize(40, 40); action_layout.addWidget(btn)
        action_layout.addStretch(); controls_layout.addLayout(action_layout)
        undo_btn.clicked.connect(self.undo_clicked.emit); clear_btn.clicked.connect(self.clear_clicked.emit); stats_btn.clicked.connect(self.stats_clicked.emit)
        layout.addWidget(controls_frame)

        stats_frame = self._create_styled_frame(); stats_layout = QVBoxLayout(stats_frame); stats_layout.setContentsMargins(10, 10, 10, 10); stats_layout.setSpacing(10)
        stats_title = QLabel("MASA İSTATİSTİKLERİ"); stats_title.setObjectName("SectionTitleLabel"); stats_layout.addWidget(stats_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        def create_stat_row(lt, vt, vc=COLOR_TEXT_NORMAL): row=QHBoxLayout(); l=QLabel(lt); v=QLabel(vt); v.setObjectName("ValueLabel"); v.setStyleSheet(f"color:{vc};"); row.addWidget(l); row.addWidget(v); return row, v
        total_layout, self.total_hands_value = create_stat_row("Toplam El:", "0")
        player_layout, self.player_wins_value = create_stat_row("Player Kazanma:", "0 (%0.0)", COLOR_PLAYER)
        banker_layout, self.banker_wins_value = create_stat_row("Banker Kazanma:", "0 (%0.0)", COLOR_BANKER)
        stats_layout.addLayout(total_layout); stats_layout.addLayout(player_layout); stats_layout.addLayout(banker_layout); layout.addWidget(stats_frame)

        kasa_frame = self._create_styled_frame(); kasa_layout = QVBoxLayout(kasa_frame)
        kasa_layout.setContentsMargins(10, 10, 10, 5); kasa_layout.setSpacing(5)
        kasa_title = QLabel("KASA & BAHİS"); kasa_title.setObjectName("SectionTitleLabel"); kasa_layout.addWidget(kasa_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        kasa_row_layout, self.kasa_value = create_stat_row("Toplam Kasa:", "₺0.00", COLOR_KASA)
        bahis_row_layout, self.bahis_value = create_stat_row("Mevcut Bahis:", "₺0.00", COLOR_BAHIS)
        kasa_layout.addLayout(kasa_row_layout); kasa_layout.addLayout(bahis_row_layout)
        self.status_label = QLabel("Martingale: 0 | Seri: W0"); self.status_label.setObjectName("SmallStatusLabel")
        kasa_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        streak_layout = QHBoxLayout()
        self.max_win_streak_label = QLabel("Max Kazanç S: 0"); self.max_win_streak_label.setObjectName("SmallStatusLabel"); self.max_win_streak_label.setStyleSheet(f"color: {COLOR_WIN};")
        self.max_loss_streak_label = QLabel("Max Kayıp S: 0"); self.max_loss_streak_label.setObjectName("SmallStatusLabel"); self.max_loss_streak_label.setStyleSheet(f"color: {COLOR_LOSS};")
        streak_layout.addWidget(self.max_win_streak_label); streak_layout.addStretch(); streak_layout.addWidget(self.max_loss_streak_label)
        kasa_layout.addLayout(streak_layout)
        layout.addWidget(kasa_frame)

        layout.addStretch(); return panel

    def _create_right_panel(self):
        panel = QWidget(); panel.setObjectName("RightPanel"); panel.setFixedWidth(460)
        layout = QVBoxLayout(panel); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(20)
        tahmin_frame = self._create_styled_frame(); tahmin_layout = QVBoxLayout(tahmin_frame)
        tahmin_layout.setContentsMargins(10, 10, 10, 10); tahmin_layout.setSpacing(15)
        tahmin_title = QLabel("TAHMİN EKRANI"); tahmin_title.setObjectName("SectionTitleLabel"); tahmin_layout.addWidget(tahmin_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        tahmin_content_layout = QHBoxLayout(); tahmin_content_layout.setSpacing(20)
        self.pred_box = QLabel("-"); self.pred_box.setFixedSize(140, 85); self.pred_box.setAlignment(Qt.AlignmentFlag.AlignCenter); self.pred_box.setStyleSheet(f"background-color:{COLOR_SECTION_BG};color:{COLOR_TEXT_DIM};font-size:30px;font-weight:bold;border-radius:8px;")
        tahmin_content_layout.addWidget(self.pred_box)
        details_layout = QVBoxLayout(); details_layout.setSpacing(10)
        conf_layout = QHBoxLayout(); conf_label = QLabel("Güven Oranı:")
        self.conf_bar = QProgressBar(); self.conf_bar.setValue(0); self.conf_bar.setStyleSheet(f"QProgressBar::chunk{{background-color:{COLOR_PROGRESS_CONF};}}"); self.conf_bar.setTextVisible(False)
        self.conf_value = QLabel("%0.0"); self.conf_value.setObjectName("ValueLabel"); self.conf_value.setStyleSheet(f"color:{COLOR_TEXT_HEADER};min-width:40px;")
        conf_layout.addWidget(conf_label); conf_layout.addWidget(self.conf_bar); conf_layout.addWidget(self.conf_value); details_layout.addLayout(conf_layout)
        prob_layout = QHBoxLayout(); prob_label = QLabel("Kazanma İhtimali:")
        self.prob_bar = QProgressBar(); self.prob_bar.setValue(0); self.prob_bar.setStyleSheet(f"QProgressBar::chunk{{background-color:{COLOR_PROGRESS_PROB};}}"); self.prob_bar.setTextVisible(False)
        self.prob_value = QLabel("%0.0"); self.prob_value.setObjectName("ValueLabel"); self.prob_value.setStyleSheet(f"color:{COLOR_TEXT_HEADER};min-width:40px;")
        prob_layout.addWidget(prob_label); prob_layout.addWidget(self.prob_bar); prob_layout.addWidget(self.prob_value); details_layout.addLayout(prob_layout)
        tahmin_content_layout.addLayout(details_layout); tahmin_layout.addLayout(tahmin_content_layout); layout.addWidget(tahmin_frame)
        matrix_frame = self._create_styled_frame(); matrix_outer_layout = QVBoxLayout(matrix_frame); matrix_outer_layout.setContentsMargins(10, 10, 10, 10); matrix_outer_layout.setSpacing(15)
        matrix_title = QLabel("SON SONUÇLAR"); matrix_title.setObjectName("SectionTitleLabel"); matrix_outer_layout.addWidget(matrix_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        matrix_container = QWidget(); matrix_container.setStyleSheet(f"background-color:{COLOR_PANEL_BG};border-radius:5px;")
        matrix_grid_layout = QGridLayout(matrix_container); matrix_grid_layout.setContentsMargins(0, 0, 0, 0); matrix_grid_layout.setSpacing(0)
        self.matrix_labels = []; cell_width = 72; cell_height = 44
        for r in range(MATRIX_ROWS):
            row_labels = []
            for c in range(MATRIX_COLS): cell = QLabel("-"); cell.setObjectName("MatrixLabel"); cell.setFixedSize(cell_width, cell_height); cell.setAlignment(Qt.AlignmentFlag.AlignCenter); matrix_grid_layout.addWidget(cell, r, c); row_labels.append(cell)
            self.matrix_labels.append(row_labels)
        self.update_matrix_display([])
        matrix_outer_layout.addWidget(matrix_container, alignment=Qt.AlignmentFlag.AlignHCenter); layout.addWidget(matrix_frame)
        layout.addStretch(); return panel

    def update_matrix_display(self, full_history: List[str]):
        history_for_matrix = full_history[-MATRIX_HISTORY_LEN:]
        history_len = len(history_for_matrix)
        for r in range(MATRIX_ROWS):
            for c in range(MATRIX_COLS):
                label = self.matrix_labels[r][c]; index = history_len - (MATRIX_ROWS*MATRIX_COLS) + (r*MATRIX_COLS + c)
                if 0 <= index < history_len:
                    result = history_for_matrix[index]
                    if result=='P': bg,tc,t = COLOR_PLAYER,COLOR_TEXT_BUTTON,"P"
                    elif result=='B': bg,tc,t = COLOR_BANKER,COLOR_TEXT_BUTTON,"B"
                    elif result=='T': bg,tc,t = COLOR_TIE,COLOR_TEXT_BUTTON,"T"
                    else: bg,tc,t = COLOR_MATRIX_EMPTY_BG,COLOR_MATRIX_EMPTY_TEXT,"?"
                else: bg,tc,t = COLOR_MATRIX_EMPTY_BG,COLOR_MATRIX_EMPTY_TEXT,"-"
                label.setText(t); label.setStyleSheet(f"background-color:{bg};color:{tc};border:1px solid {COLOR_BORDER};font-size:20px;font-weight:bold;border-radius:4px;")

    def update_statistics(self, stats: Dict[str, Any]):
        self.total_hands_value.setText(str(stats.get('total',0)))
        pp=stats.get('player_perc',0.0); bp=stats.get('banker_perc',0.0)
        self.player_wins_value.setText(f"{stats.get('player',0)} ({pp:.1f}%)")
        self.banker_wins_value.setText(f"{stats.get('banker',0)} ({bp:.1f}%)")
        balance = stats.get('current_balance', 0.0)
        bet = stats.get('current_bet', 0.0)
        level = stats.get('martingale_level', 0)
        win_streak = stats.get('win_streak', 0)
        loss_streak = stats.get('loss_streak', 0)
        max_win = stats.get('max_win_streak', 0)
        max_loss = stats.get('max_loss_streak', 0)
        locale_currency_format = "₺{:,.2f}"
        self.kasa_value.setText(locale_currency_format.format(balance))
        self.bahis_value.setText(locale_currency_format.format(bet))
        seri_text = f"W{win_streak}" if win_streak > 0 else f"L{loss_streak}"
        self.status_label.setText(f"Martingale: {level} | Seri: {seri_text}")
        self.max_win_streak_label.setText(f"Max Kazanç S: {max_win}")
        self.max_loss_streak_label.setText(f"Max Kayıp S: {max_loss}")

    def update_prediction_display(self, prediction: str, confidence: float, probability: float):
        pt="N/A"; ps=f"background-color:{COLOR_SECTION_BG};color:{COLOR_TEXT_DIM};font-size:30px;font-weight:bold;border-radius:8px;"
        if prediction=='P': pt="PLAYER"; ps=f"background-color:{COLOR_PLAYER};color:{COLOR_TEXT_BUTTON};font-size:30px;font-weight:bold;border-radius:8px;"
        elif prediction=='B': pt="BANKER"; ps=f"background-color:{COLOR_BANKER};color:{COLOR_TEXT_BUTTON};font-size:30px;font-weight:bold;border-radius:8px;"
        self.pred_box.setText(pt); self.pred_box.setStyleSheet(ps)
        cv=max(0,min(100,int(confidence))); pv=max(0,min(100,int(probability)))
        self.conf_bar.setValue(cv); self.conf_value.setText(f"%{confidence:.1f}")
        self.prob_bar.setValue(pv); self.prob_value.setText(f"%{probability:.1f}")