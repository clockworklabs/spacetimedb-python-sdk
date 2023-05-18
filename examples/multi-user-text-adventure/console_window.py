import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTextEdit, QLineEdit, QWidget
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QIcon

class ConsoleWindow(QMainWindow):
    instance = None
    last_print_was_prompt = False

    def __init__(self, game_controller):
        super().__init__()

        ConsoleWindow.instance = self

        self.game_controller = game_controller

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.output_text_edit)

        self.command_line_edit = QLineEdit()
        
        layout.addWidget(self.command_line_edit)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.command_line_edit.returnPressed.connect(self.process_command)

        self.setWindowTitle("SpacetimeMUD")

        # Get the path to the current module
        module_path = os.path.dirname(os.path.abspath(__file__))

        self.setWindowIcon(QIcon(os.path.join(module_path, "logo.png")))

    def process_command(self):
        command = self.command_line_edit.text()

        self.print(command + "\n", is_command = True)
        
        if self.game_controller.prompt:
            self.game_controller.prompt.command(command)        

        self.command_line_edit.clear()

    def print(self, text, color = "white", is_command = False):
        char_format = QTextCharFormat()

        qcolor = None
        if(color == "room_name"):
            qcolor = QColor(0, 255, 255)
        elif(color == "exits"):
            qcolor = QColor(0, 128, 128)
        else:
            qcolor = QColor(color)

        char_format.setForeground(qcolor)

        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if self.last_print_was_prompt and not is_command:
            text = '\n\n' + text
        
        if self.last_print_was_prompt:
            text = text + '\n'

        cursor.insertText(text, char_format)
        self.output_text_edit.ensureCursorVisible()

        self.last_print_was_prompt = False

    def prompt(self):
        self.print("> ")
        self.last_print_was_prompt = True

    def closeEvent(self, event) -> None:
        self.game_controller.should_exit = True