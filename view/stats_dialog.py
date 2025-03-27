# view/stats_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt

# Stil Renkleri (Görünümü ana pencereyle uyumlu hale getirmek için)
COLOR_BACKGROUND = "#121212"
COLOR_PANEL_BG = "#1E1E1E"
COLOR_TEXT_HEADER = "#FFFFFF"
COLOR_TEXT_NORMAL = "#E0E0E0"
COLOR_BORDER = "#333333"
COLOR_SECTION_BG = "#262626"

class StatsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model İstatistikleri")
        self.setMinimumSize(550, 300) # Başlangıç boyutu

        # Koyu tema ayarları
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
            QTableWidget {{
                background-color: {COLOR_PANEL_BG};
                color: {COLOR_TEXT_NORMAL};
                gridline-color: {COLOR_BORDER};
                border: 1px solid {COLOR_BORDER};
                font-family: Arial;
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {COLOR_SECTION_BG};
                color: {COLOR_TEXT_HEADER};
                padding: 4px;
                border: 1px solid {COLOR_BORDER};
                font-weight: bold;
            }}
            QTableCornerButton::section {{
                 background-color: {COLOR_SECTION_BG};
                 border: 1px solid {COLOR_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4) # Sütun sayısı
        self.table_widget.setHorizontalHeaderLabels([
            "Model Adı", "Son Tahmin", "Başarı (%)", "Doğru / Toplam"
        ])
        # Düzenlemeyi engelle
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Satır seçimi
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Başlıkları boyutlandır
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Esnet
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Başarı sütunu içeriğe göre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # D/T sütunu içeriğe göre


        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def update_data(self, stats_data: dict):
        """
        Tabloyu verilen istatistik verileriyle günceller.
        stats_data format: {'PredictorName': {'correct': 0, 'total': 0, 'last_prediction': 'N/A'}, ...}
        """
        self.table_widget.setRowCount(0) # Önceki verileri temizle

        for name, stats in stats_data.items():
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            correct = stats.get('correct', 0)
            total = stats.get('total', 0)
            last_pred = stats.get('last_prediction', 'N/A')

            success_rate = (correct / total * 100) if total > 0 else 0.0
            ratio_str = f"{correct} / {total}"

            # Hücre öğelerini oluştur
            name_item = QTableWidgetItem(name)
            last_pred_item = QTableWidgetItem(last_pred)
            success_item = QTableWidgetItem(f"{success_rate:.1f}%")
            ratio_item = QTableWidgetItem(ratio_str)

            # Hizalama (isteğe bağlı)
            last_pred_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            success_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            ratio_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Öğeleri tabloya ekle
            self.table_widget.setItem(row_position, 0, name_item)
            self.table_widget.setItem(row_position, 1, last_pred_item)
            self.table_widget.setItem(row_position, 2, success_item)
            self.table_widget.setItem(row_position, 3, ratio_item)

        # self.table_widget.resizeColumnsToContents() # Stretch yerine bunu kullanabilirsiniz
