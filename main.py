import sqlite3
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QPushButton, QLineEdit, QHBoxLayout, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QTableWidgetItem, QTableWidget
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

# Класс для главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("4лаб")
        self.resize(800, 600)

        self.db = self.create_connection("posts.db")
        self.init_ui()

    def create_connection(self, db_name):
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT
            )
            """
        )
        connection.commit()
        return connection

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле для поиска
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по заголовку...")
        self.search_field.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_field)

        # Таблица
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.refresh_button)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_row)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_data()

    def load_data(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, user_id, title, body FROM posts")
        rows = cursor.fetchall()

        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "User ID", "Title", "Body"])

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def filter_data(self):
        filter_text = self.search_field.text().lower()
        cursor = self.db.cursor()
        cursor.execute("SELECT id, user_id, title, body FROM posts WHERE LOWER(title) LIKE ?", (f"%{filter_text}%",))
        rows = cursor.fetchall()

        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def add_row(self):
        dialog = AddRecordDialog(self.db, self)
        if dialog.exec_():
            self.load_data()

    def delete_row(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return

        row_id = self.table.item(selected_row, 0).text()
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM posts WHERE id = ?", (row_id,))
        self.db.commit()
        self.load_data()

class AddRecordDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Добавить запись")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.user_id_field = QLineEdit()
        self.title_field = QLineEdit()
        self.body_field = QLineEdit()

        layout.addRow("User ID:", self.user_id_field)
        layout.addRow("Title:", self.title_field)
        layout.addRow("Body:", self.body_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.add_row)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def add_row(self):
        user_id = self.user_id_field.text()
        title = self.title_field.text()
        body = self.body_field.text()

        if not user_id or not title or not body:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body)
        )
        self.db.commit()
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
