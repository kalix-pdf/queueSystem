import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QMessageBox, QLineEdit
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from queu import Ui_MainWindow
from login import Ui_LoginWindow
from form import Ui_GuestForm
from register import RegisterUi_MainWindow
from system_db.db_manager import DatabaseManager

from staff.index import Staff_MainWindow

class SharedFormatWindow(QMainWindow):
    def __init__(self, db, main_window, user_id):
        super().__init__()
        self.ui = Ui_GuestForm()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.user_id = user_id

        self.db = db
        self.conn = db.get_connection()
        self.cursor = db.get_cursor()

    def set_format_for(self, module_type, login_type):
        self.module_type = module_type
        self.login_type = login_type

        if module_type == "recordbtn":
            self.setWindowTitle(f"Records Section Module - {'Guest' if login_type == 'guest' else 'User'}")
            self.ui.title.setText("Records Section")
        elif module_type == "accountingbtn":
            self.setWindowTitle(f"Accounting Office Module - {'Guest' if login_type == 'guest' else 'User'}")
            self.ui.title.setText("Accounting Office")
        elif module_type == "admissionbtn":
            self.setWindowTitle(f"Admission Office Module - {'Guest' if login_type == 'guest' else 'User'}")
            self.ui.title.setText("Admission Office")
               
        if self.login_type == 'user':
            try:
                layout = self.ui.verticalLayout_11
                
                self.ui.nameinput.setReadOnly(True)
                self.ui.ageinput.setReadOnly(True)
                self.ui.contactinput.setReadOnly(True)

                self.cursor.execute("SELECT * FROM user WHERE id = ?", (self.user_id,))
                result = self.cursor.fetchone()

                self.user_name = result[1]
                self.user_age = result[3]
                self.user_contact = result[4]

                self.ui.nameinput.setText(self.user_name)
                self.ui.ageinput.setText(str(self.user_age))
                self.ui.contactinput.setText(str(self.user_contact))
                
                self.items = [(f"{self.user_name}", layout),
                         (f"{self.user_age}", layout)
                         ]
                
                for text, target_layout in self.items:
                    label = QtWidgets.QLabel(text)
                    target_layout.addWidget(label)
                    label.setStyleSheet("font-size: 12pt;")
            except Exception as e:
                print(e)
        
        self.ui.pushButton.clicked.connect(self.load_form)

    def load_form(self):        
        window_no = self.get_least_window()
        queue_no = self.generate_queue_number(window_no)

        layout = self.ui.verticalLayout_11
        windowlayout = self.ui.verticalLayout_8
        qlayout = self.ui.verticalLayout_10
    
        if self.login_type == 'guest':
        
            missing_fields = []

            name = self.ui.nameinput.text().strip()
            age = self.ui.ageinput.text().strip()
            purpose = self.ui.purposeinput.text().strip()
            contact = self.ui.contactinput.text().strip()

            if not name:
                missing_fields.append("Name")
                self.ui.nameinput.setStyleSheet("border: 1px solid red;")
            if not age:
                missing_fields.append("Age")
                self.ui.ageinput.setStyleSheet("border: 1px solid red;")
            if not purpose:
                missing_fields.append("Purpose")
                self.ui.purposeinput.setStyleSheet("border: 1px solid red;")
            if not contact or not contact.isdigit():
                missing_fields.append("Contact")
                self.ui.contactinput.setStyleSheet("border: 1px solid red;")

            if missing_fields:
                QMessageBox.warning(
                    self,
                    "Missing Fields",
                    f"Please fill out the following required field(s):\n- " + "\n- ".join(missing_fields)
                )
                return
            
            try:
                ageint = int(age)
                contactint = int(contact)
            except Exception as e:
                QMessageBox.warning(self, "Warning", "Contact Information and Age should be in Integer")
                return
            
            try:
                self.cursor.execute("INSERT INTO queue (name, service, user_type, age, purpose, queue_no, window_no, contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                    (name, self.module_type, self.login_type, ageint, purpose, queue_no, window_no, contactint ))
                
                self.conn.commit()
                QMessageBox.information(self, "Success", f"Queued as {queue_no} at Window {window_no}.")
                
                items = [
                    (f"{name}", layout),
                    (f"{age}", layout),
                    (f"{purpose}", layout),
                    (f"{contact}", layout),
                    (f"{window_no}", windowlayout),
                    (f"{queue_no}", qlayout),
                ]
                for text, target_layout in items:
                    label = QtWidgets.QLabel(text)
                    target_layout.addWidget(label)
                    
                    if target_layout in [windowlayout, qlayout]:
                        label.setAlignment(QtCore.Qt.AlignHCenter)
                        label.setStyleSheet("font-size: 14pt; font-weight: 600;")
                    else:
                        label.setStyleSheet("font-size: 12pt;")

                self.guest_info = {
                    'name': name,
                    'age': age,
                    'purpose': purpose,
                    'contact': contact,
                    'queue_no': queue_no,
                    'window_no': window_no,
                    'service_type': self.module_type
                }
                self.ui.nameinput.setReadOnly(True)
                self.ui.ageinput.setReadOnly(True)
                self.ui.purposeinput.setReadOnly(True)
                self.ui.contactinput.setReadOnly(True)

                self.main_window.refresh_queue(self.guest_info)

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to insert into database.\n\nError: {str(e)}")
        else:
            purpose = self.ui.purposeinput.text().strip()

            if not purpose:
                QMessageBox.warning(self, "Warning", "Purpose is Required! isa na nga lang yan ayaw mo pa sagutan!!!")
                return
            
            try:
                self.cursor.execute("INSERT INTO queue (name, service, user_type, age, purpose, queue_no, window_no, contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                    (self.user_name, self.module_type, self.login_type, self.user_age, purpose, queue_no, window_no, self.user_contact ))
                    
                self.conn.commit()

                items = [
                        (f"{window_no}", windowlayout),
                        (f"{queue_no}", qlayout),
                        (f"{purpose}", layout),
                        (f"{self.user_contact}", layout)
                    ]
                for text, target_layout in items:
                    label = QtWidgets.QLabel(text)
                    target_layout.addWidget(label)
                    if target_layout in [windowlayout, qlayout]:
                        label.setAlignment(QtCore.Qt.AlignHCenter)
                        label.setStyleSheet("font-size: 14pt; font-weight: 600;")
                    else:
                        label.setStyleSheet("font-size: 12pt;")

                self.user_info = {
                    'name': self.user_name,
                    'age': self.user_age,
                    'purpose': purpose,
                    'contact': self.user_contact,
                    'queue_no': queue_no,
                    'window_no': window_no,
                    'service_type': self.module_type
                } 

                self.ui.pushButton.setEnabled(False)
                self.main_window.refresh_queue(self.user_info)
                    
                QMessageBox.information(self, "Success", f"Queued as {queue_no} at Window {window_no}.")
            except Exception as e:
                print(e)
                

    def generate_queue_number(self, window_no):
        prefix_map = {
            "recordbtn": "RS",
            "accountingbtn": "AO",
            "admissionbtn": "AM"
        }
        prefix = prefix_map.get(self.module_type, "Q")

        self.cursor.execute(
            "SELECT queue_no FROM queue WHERE queue_no LIKE ? ORDER BY queue_no ASC",
            (f"{prefix}-%",)
        )
        result = self.cursor.fetchall()

        existing_numbers = set()
        for row in result:
            try:
                number_part = int(row[0].split("-")[1])
                existing_numbers.add(number_part)
            except (IndexError, ValueError):
                continue  
        new_no = 1
        while new_no in existing_numbers:
            new_no += 1

        return f"{prefix}-{new_no:03d}"

    
    def get_least_window(self):
        if self.module_type == 'recordbtn':
            available_windows = [1, 2]
        else:
            available_windows = [1, 2, 3]

        window_load = {}
        for win in available_windows:
            try:
                self.cursor.execute("SELECT COUNT(*) FROM queue WHERE window_no = ? and service = ?", (win, self.module_type))
                count = self.cursor.fetchone()[0]
            except Exception as e:
                print(f"Error counting queue for window {win}: {e}")
                count = 0

            window_load[win] = count
            
        
        return min(window_load, key=window_load.get)
       


class RegisterPage(QMainWindow):
    registration_successful = pyqtSignal(int)
    back_to_login = pyqtSignal()
    back_to_guest = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.ui = RegisterUi_MainWindow()
        self.ui.setupUi(self)

        self.db = db
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.ui.loginbtn.clicked.connect(self.go_back)
        self.ui.guestbtn.clicked.connect(self.guest)
        self.ui.registerbtn.clicked.connect(self.handle_registration)

    def guest(self):
        try:
            self.back_to_guest.emit()
            self.close()
        except Exception as e:
            print(e)

    def handle_registration(self):
        name = self.ui.fullnameinput.text().strip()
        age = self.ui.ageinput.text().strip()
        program = self.ui.sectioninput.text().strip()
        contact = self.ui.courseinput.text().strip()
        username = self.ui.usernameinput.text().strip()
        password = self.ui.passwordinput.text().strip()

        missing_fields = []

        if not name:
            missing_fields.append("Name")
            self.ui.fullnameinput.setStyleSheet("border: 1px solid red;")
        if not age:
            missing_fields.append("Age")
            self.ui.ageinput.setStyleSheet("border: 1px solid red;")
        if not program:
            missing_fields.append("Program")
            self.ui.sectioninput.setStyleSheet("border: 1px solid red;")
        if not contact or not contact.isdigit():
            missing_fields.append("Contact")
            self.ui.courseinput.setStyleSheet("border: 1px solid red;")
        if not username:
            missing_fields.append("Username")
            self.ui.usernameinput.setStyleSheet("border: 1px solid red;")
        if not password:
            missing_fields.append("Password")
            self.ui.passwordinput.setStyleSheet("border: 1px solid red;")

        if missing_fields:
            QMessageBox.warning(
                self,
                "Missing Fields",
                f"Please fill out the following required field(s):\n- " + "\n- ".join(missing_fields)
            )
            return
        
        try:
            ageint = int(age)
            contactint = int(contact)
        except Exception as e:
            QMessageBox.warning(self, "Warning", "Contact Information and Age should be in Integer")
            return

        try:
            self.cursor.execute("INSERT INTO user (fullname, username, age, contact, program, password) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, username, ageint, contactint, program, password))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Registration Complete!")

            user_id = self.cursor.lastrowid
            self.registration_successful.emit(user_id)
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error Occured", f"Error: {str(e)}")

    def go_back(self):
        self.back_to_login.emit()
        self.close()


class LoginPage(QMainWindow):
    login_successful = pyqtSignal(int)
    login_as_guest = pyqtSignal()
    register_successful = pyqtSignal(int)

    def __init__(self, db):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

        self.db = db
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.ui.Loginbutton.clicked.connect(self.authenticate_user)
        self.ui.guestbutton.clicked.connect(self.login_as_guest_func)
        self.ui.Registerbutton.clicked.connect(self.open_register_window)
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)

    def open_register_window(self):
        self.register_window = RegisterPage(self.db)
        self.register_window.registration_successful.connect(self.registration_complete)
        
        self.register_window.back_to_guest.connect(self.login_as_guest_func) 
        self.register_window.back_to_login.connect(self.show_again)
        self.register_window.show()
        self.close()
        

    def show_again(self):
        self.show()

    def show_again(self):
        self.show()

    def registration_complete(self, user_id):
        self.register_successful.emit(user_id)
        self.close()

    def authenticate_user(self):
        try:
            username = self.ui.username.text().strip()
            password = self.ui.password.text().strip()

            if not username or not password:
                QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
                return

            self.cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
            user = self.cursor.fetchone()

            if user:
                user_id = user[0]
                QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
                self.login_successful.emit(user_id)
                self.close()  
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
                return
        except Exception as e:
            print(e)
    
    def login_as_guest_func(self):
        self.login_as_guest.emit()
        self.close()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db = DatabaseManager()
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

        self.user_info = None

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

        self.staff_window = Staff_MainWindow()
        self.staff_window.queue_updated.connect(self.refresh_queue_from_staff)
        self.staff_window.show()

        self.load_queue(self.layout_per_service)


    def store_guest_info(self):
        try:
            service = self.user_info['service_type']
            window_no = self.user_info['window_no']
            
            self.cursor.execute("SELECT COUNT(*) FROM queue WHERE service = ? AND window_no = ?", (service, window_no))
            count = self.cursor.fetchone()[0]

            def get_ordinal(n):
                return f"{n}{'th' if 11<=n%100<=13 else {1:'st', 2:'nd', 3:'rd'}.get(n%10, 'th')}"
 
            if count == 2:
                QtWidgets.QMessageBox.information(
                        self,
                        "Queue Notification",
                        f"You are next in line!"
                )
                content = f"Your Queue No. is: {self.user_info['queue_no']}\nYou are {get_ordinal(count)} in the line at window {window_no}\nYou are next in the Line!"
            else:
                content = f"Your Queue No. is: {self.user_info['queue_no']}\nYou are {get_ordinal(count)} in the line at window {window_no}"
            
            label = QtWidgets.QLabel(content)
            label.setAlignment(QtCore.Qt.AlignHCenter)
            label.setStyleSheet("font-weight: 600; font-size: 11pt; text-decoration: underline;")

            if service == 'accountingbtn':
                self.delete_labels(self.verticalLayout_8)
                self.verticalLayout_8.insertWidget(0, label)
            elif service == 'admissionbtn':
                self.delete_labels(self.verticalLayout_25)
                self.verticalLayout_25.insertWidget(0, label)
            else:
                self.delete_labels(self.verticalLayout_5)
                self.verticalLayout_5.insertWidget(0, label)
        except Exception as e:
            print(e)

 
    def display_existing_guest_info(self):
        info = self.user_info
        msg = (
            f"Name: {info['name']}\n"
            f"Age: {info['age']}\n"
            f"Purpose: {info['purpose']}\n"
            f"Contact: {info['contact']}\n"
            f"Queue Number: {info['queue_no']}\n"
            f"Window Number: {info['window_no']}"
        )
        QMessageBox.information(self, "Your Info", msg)


    def TakeNumber_Clicked(self):
        if self.user_info:
            QMessageBox.information(self, "Info", "You have already taken a number!")
            self.display_existing_guest_info()
            return
        
        clicked_button = self.sender()
        self.target_module = clicked_button.objectName()
        self.open_login_window()

    def open_login_window(self):
        try:
            self.login_window = LoginPage(self.db)
            self.login_window.login_successful.connect(self.load_format)
            self.login_window.login_as_guest.connect(self.load_format_guest)
            self.login_window.register_successful.connect(self.load_format)
            self.login_window.show()
        except Exception as e:
            print(str(e))

    def load_format(self, user_id):
        self.login_type = "user"
        self.open_shared_window(user_id)

    def load_format_guest(self):
        self.login_type = "guest"
        self.open_shared_window(user_id = None)

    def open_shared_window(self, user_id):
        self.module_window = SharedFormatWindow(self.db, self, user_id)
        self.module_window.set_format_for(self.target_module.lower(), self.login_type)
        self.module_window.show()


    def delete_labels(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QLabel):
                layout.removeWidget(widget)
                widget.deleteLater()
    
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

                    if current_count == 0:
                        queue_label.setStyleSheet("background-color: #ffc107;")

                    if self.user_info:
                        if self.user_info['queue_no'] == str(queue_no):
                            queue_label.setStyleSheet("background-color: rgb(170, 255, 255);")
                    
                    layout_counts[key] = current_count + 1


    def refresh_queue(self, user_info):
        self.user_info = user_info

        if self.user_info:
            self.store_guest_info()

        self.load_queue(self.layout_per_service)

    def refresh_queue_from_staff(self):
        self.store_guest_info()
        self.load_queue(self.layout_per_service)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

