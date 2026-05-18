import sys
from PyQt6.QtWidgets import QApplication, QDialog
from windows.login_window import LoginWindow
from windows.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    login_win = LoginWindow()
    if login_win.exec() == QDialog.DialogCode.Accepted:
        user_info = login_win.user_info
        
        main_win = MainWindow(user_info)
        main_win.show()
        
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()