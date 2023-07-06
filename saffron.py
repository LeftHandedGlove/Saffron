import sys
import os
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow,
    QFileDialog,
    QPushButton,
    QLabel,
    QToolBar,
    QAction,
    QStatusBar,
    QStyle
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

import spending_report_parser

class SaffronWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.define_backend()
        self.define_actions()
        self.define_visuals()
        self.show()

    def define_backend(self):
        self.finance_dir_parser = spending_report_parser.FinanceFolderParser()
        self.current_report = None

    def define_actions(self):
        self.define_select_finance_report_folder_action()

    def define_select_finance_report_folder_action(self):
        action_text = "Select Finance Report Folder"
        self.select_finance_report_folder_action = QAction(
            self.style().standardIcon(QStyle.SP_DirIcon), 
            action_text, 
            self
        )
        self.select_finance_report_folder_action.setStatusTip(action_text)
        self.select_finance_report_folder_action.triggered.connect(
            self.onSelectFinanceReportFolderClick
        )

    def onSelectFinanceReportFolderClick(self, signal):
        selected_directory = QFileDialog.getExistingDirectory(
            caption="Select Finance Report Directory",
            directory=os.path.join(os.path.basename(__file__), 'spending_reports')
        )
        self.current_report = self.finance_dir_parser.parse_folder(selected_directory)
        self.populate_entries_widgets()

    def populate_entries_widgets(self):
        report_entries = self.current_report.get_entires(
            sorted_by=spending_report_parser.Sorters.TRANSACTION_DATE
        )
        for entry in report_entries:
            pass
            
    def define_visuals(self):
        self.setWindowTitle("Saffron: Financial Finger-Pointer")
        self.setGeometry(50, 50, 800, 500)
        self.add_menubar()
        self.define_select_report_visuals()
        self.set_visuals_to_select_report_folder()
        
    def define_select_report_visuals(self):
        self.select_reports_folder_button = QPushButton(
            "Choose Reports Folder", 
            parent=self
        )
        self.select_reports_folder_button.clicked.connect(
            self.select_finance_report_folder_action.trigger
        )

    def set_visuals_to_select_report_folder(self):
        self.setCentralWidget(self.select_reports_folder_button)

    def add_menubar(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(self.select_finance_report_folder_action)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SaffronWindow()
    app.exec()

