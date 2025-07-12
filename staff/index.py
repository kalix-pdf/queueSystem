import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit
from PyQt5 import QtWidgets, QtCore
from .queue_ui import Ui_MainWindow
from .login import Ui_LoginWindow
from .staffwindow import Staff_Ui_MainWindow
from PyQt5.QtCore import pyqtSignal
from system_db.db_manager import DatabaseManager
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QColor, QPixmap

class shared_Staff_Window(QMainWindow):
    def __init__(self, db, staff_id, main_window):
        super().__init__()
        self.ui = Staff_Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.main_window = main_window
        self.staff_id = staff_id

        self.db = db
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.ui.tabWidget.currentChanged.connect(self.handle_tab_change)
        self.ui.logoutbtn.clicked.connect(self.logout)
        self.display_staff_info()

    def logout(self):
        reply = QMessageBox.question(
            self, 
            "Logout Confirmation",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
        else:
            print("canceled")

    def display_staff_info(self):
        self.cursor.execute("SELECT * FROM staff WHERE id = ?", (self.staff_id,))
        staff = self.cursor.fetchone()
        image_path = staff[6]
        pixmap = QPixmap(image_path)
        self.ui.label_4.setPixmap(pixmap)

        items = [
            (f"{staff[1]}", self.ui.verticalLayout_10),
            (f"{staff[4]}", self.ui.verticalLayout_11),
            (f"{staff[5]}", self.ui.verticalLayout_12)
        ]
        for info, layout in items:
            label = QtWidgets.QLabel(info)
            layout.addWidget(label)
            label.setStyleSheet("font-size: 14pt; font-weight: 600;")


    def handle_tab_change(self, index):
        if self.ui.tabWidget.widget(index).objectName() == "tab_2":
            self.ui.window_no_layout.setText("Window No. 2")
            self.window_no = 2
            self.load_tab2_content()
        elif self.ui.tabWidget.widget(index).objectName() == "tab_3":
            self.ui.window_no_layout.setText("Window No. 3")
            self.window_no = 3
            self.load_tab3_content()
        elif self.ui.tabWidget.widget(index).objectName() == "tab":
            self.ui.window_no_layout.setText("Window No. 1")
            self.window_no = 1
            self.load_tab_content()

    def start_queue_refresh(self):
        self.timer = QTimer()
        if self.window_no == 1:
            self.timer.timeout.connect(self.load_tab_content)
        elif self.window_no == 2:
            self.timer.timeout.connect(self.load_tab2_content)
        elif self.window_no == 3:
            self.timer.timeout.connect(self.load_tab3_content)
        self.timer.start(3000)
    
    def load_window(self, module_type):
        self.module_type = module_type

        if module_type == "recordbtn":
            self.setWindowTitle(f"Records Section Module ")
            self.ui.title_office.setText("Records Section")
        elif module_type == "accountingbtn":
            self.setWindowTitle(f"Accounting Office Module")
            self.ui.title_office.setText("Accounting Office")
        elif module_type == "admissionbtn":
            self.setWindowTitle(f"Admission Office Module")
            self.ui.title_office.setText("Admission Office")


    def load_tab_content(self):
        self.cursor.execute("SELECT * FROM queue WHERE service = ? AND window_no = ?", (self.module_type, 1))
        result = self.cursor.fetchall()
        self.ui.table.setRowCount(0)

        for data in result:
            row = self.ui.table.rowCount()
            self.ui.table.insertRow(row)

            self.ui.table.setItem(row, 0, QTableWidgetItem(data[7]))
            self.ui.table.setItem(row, 1, QTableWidgetItem(data[1]))
            self.ui.table.setItem(row, 2, QTableWidgetItem(data[6]))
            self.ui.table.setItem(row, 3, QTableWidgetItem(data[9]))
            self.ui.table.setItem(row, 4, QTableWidgetItem(data[3]))

            btn = QPushButton("Mark as Done")
            btn.clicked.connect(lambda _, r=row, t=self.ui.table: self.markdone(r, t))
            self.ui.table.setCellWidget(row, 5, btn)

        self.start_queue_refresh()

    def load_tab2_content(self):
        self.cursor.execute("SELECT * FROM queue WHERE service = ? AND window_no = ?", (self.module_type, 2))
        result = self.cursor.fetchall()
        self.ui.table_2.setRowCount(0)

        for data in result:
            row = self.ui.table_2.rowCount()
            self.ui.table_2.insertRow(row)

            self.ui.table_2.setItem(row, 0, QTableWidgetItem(data[7]))
            self.ui.table_2.setItem(row, 1, QTableWidgetItem(data[1]))
            self.ui.table_2.setItem(row, 2, QTableWidgetItem(data[6]))
            self.ui.table_2.setItem(row, 3, QTableWidgetItem(data[9]))
            self.ui.table_2.setItem(row, 4, QTableWidgetItem(data[3]))

            btn = QPushButton("Mark as Done")
            btn.clicked.connect(lambda _, r=row, t=self.ui.table_2: self.markdone(r, t))
            self.ui.table_2.setCellWidget(row, 5, btn)

        self.start_queue_refresh()

    def load_tab3_content(self):
        self.cursor.execute("SELECT * FROM queue WHERE service = ? AND window_no = ?", (self.module_type, 3))
        result = self.cursor.fetchall()
        self.ui.table_3.setRowCount(0)

        for data in result:
            row = self.ui.table_3.rowCount()
            self.ui.table_3.insertRow(row)

            self.ui.table_3.setItem(row, 0, QTableWidgetItem(data[7]))
            self.ui.table_3.setItem(row, 1, QTableWidgetItem(data[1]))
            self.ui.table_3.setItem(row, 2, QTableWidgetItem(data[6]))
            self.ui.table_3.setItem(row, 3, QTableWidgetItem(data[9]))
            self.ui.table_3.setItem(row, 4, QTableWidgetItem(data[3]))

            btn = QPushButton("Mark as Done")
            btn.clicked.connect(lambda _, r=row, t=self.ui.table_3: self.markdone(r, t))
            self.ui.table_3.setCellWidget(row, 5, btn)

        self.start_queue_refresh()

    def markdone(self, row, table):
        queue_no_item = table.item(row, 0)

        if queue_no_item:
            queue_no = queue_no_item.text()
            self.cursor.execute("DELETE FROM queue WHERE queue_no = ?", (queue_no,))
            self.conn.commit()
            table.removeRow(row)
        
        self.main_window.refresh_queue()
        QMessageBox.information(self, "Mark as Done", f"Marked row {queue_no} as done.")

class LoginPage(QMainWindow):
    login_successful = pyqtSignal(int)

    def __init__(self, db):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

        self.db = db
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.ui.Loginbutton.clicked.connect(self.authenticate_user)
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)

    def authenticate_user(self):
        username = self.ui.username.text().strip()
        password = self.ui.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Warning", "Username and Password are required!")
            return
        
        self.cursor.execute("SELECT * FROM staff WHERE username = ? AND password = ?", (username, password))
        staff = self.cursor.fetchone()

        if staff:
            staff_id = staff[0]
            QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
            self.login_successful.emit(staff_id)
            self.close()  
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
            return

class Staff_MainWindow(QMainWindow, Ui_MainWindow):
    queue_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db = DatabaseManager()
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.Recordbtn.clicked.connect(self.TakeNumber_Clicked)
        self.Accountingbtn.clicked.connect(self.TakeNumber_Clicked)
        self.Admissionbtn.clicked.connect(self.TakeNumber_Clicked)

        self.layout_per_service = {
            'recordbtn': {
                1: self.verticalLayout_13,
                2: self.verticalLayout_14
            },
            'accountingbtn': {
                1: self.verticalLayout_20,
                2: self.verticalLayout_21,
                3: self.verticalLayout_22
            },
            'admissionbtn': {
                1: self.verticalLayout_31,
                2: self.verticalLayout_32,
                3: self.verticalLayout_33
            }
        }

        self.load_queue(self.layout_per_service)

    def TakeNumber_Clicked(self):
        clicked_button = self.sender()
        self.target_module = clicked_button.objectName()
        self.open_login_window()

    def open_login_window(self):
        self.loginWindow = LoginPage(self.db)
        self.loginWindow.login_successful.connect(self.load_staff_window)
        self.loginWindow.show()

    def load_staff_window(self, staff_id):
        self.staff_window = shared_Staff_Window(self.db, staff_id, self)
        self.staff_window.load_window(self.target_module.lower())
        self.staff_window.show()

    def delete_labels(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QLabel):
                layout.removeWidget(widget)
                widget.deleteLater()
    
    def start_queue_refresh(self):
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.load_queue(self.layout_per_service))
        self.timer.start(2000)

    #display queue frame, frame 3, frame 6
    def load_queue(self, layouts_per_services):
        
        self.delete_labels(self.verticalLayout_13)
        self.delete_labels(self.verticalLayout_14)
        self.delete_labels(self.verticalLayout_20)
        self.delete_labels(self.verticalLayout_21)
        self.delete_labels(self.verticalLayout_22)
        self.delete_labels(self.verticalLayout_31)
        self.delete_labels(self.verticalLayout_32)
        self.delete_labels(self.verticalLayout_33)

        self.cursor.execute("SELECT service, queue_no, window_no FROM queue ORDER BY timestamp ASC")
        result = self.cursor.fetchall()        

        MAX_DISPLAY = 5 

        layout_counts = {}

        for service, queue_no, window_no in result:
            if service in layouts_per_services and window_no in layouts_per_services[service]:
                target_layout = layouts_per_services[service][window_no]

                key = (service, window_no)
                current_count = layout_counts.get(key, 0)

                if current_count < MAX_DISPLAY:
                    queue_label = QtWidgets.QLabel(str(queue_no))
                    target_layout.addWidget(queue_label)
                    layout_counts[key] = current_count + 1


        for service_layout in layouts_per_services.values():
            for layout in service_layout.values():
                if layout.count() > 0:
                    first_widget = layout.itemAt(0).widget()
                    if first_widget:
                        first_widget.setStyleSheet("""
                    background-color: #ffc107;
                """)
        
        self.start_queue_refresh()
        
                        
    def refresh_queue(self):
        self.queue_updated.emit()
        self.load_queue(self.layout_per_service)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Staff_MainWindow()
    window.show()
    sys.exit(app.exec_())

