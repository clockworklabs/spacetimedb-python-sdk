import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTextEdit, QLineEdit, QWidget
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QIcon


class ConsoleWindow(QMainWindow):
    """A window that displays the game output and accepts commands from the user."""

    instance = None
    last_print_was_prompt = False

    def __init__(self, game_controller):
        """Initialize the console window."""

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
        """Process the command entered by the user."""

        command = self.command_line_edit.text()

        self.print(command + "\n", is_command=True)

        # If the game controller has an active prompt, send the command to it
        # This will be either a create character prompt or a game prompt
        if self.game_controller.prompt:
            self.game_controller.prompt.command(command)

        self.command_line_edit.clear()

    def print(self, text, color="white", is_command=False):
        """Print text to the console window."""

        # Support custom colors
        qcolor = None
        if color == "room_name":
            qcolor = QColor(0, 255, 255)
        elif color == "exits":
            qcolor = QColor(0, 128, 128)
        else:
            qcolor = QColor(color)

        # Set the text color
        char_format = QTextCharFormat()
        char_format.setForeground(qcolor)

        # Set the font and move the cursor to the end of the document
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add some newlines based on if the last print was a prompt or not
        if self.last_print_was_prompt and not is_command:
            text = "\n\n" + text

        if self.last_print_was_prompt:
            text = text + "\n"

        # Insert the text and move the cursor to the end of the document
        cursor.insertText(text, char_format)

        # Scroll to the bottom of the document
        self.output_text_edit.ensureCursorVisible()

        # Set the last print flag
        self.last_print_was_prompt = False

    def prompt(self):
        """Print a prompt to the console window."""

        # Print the prompt
        self.print("> ")
        # Set the last print flag
        self.last_print_was_prompt = True

    def closeEvent(self, event) -> None:
        """Handle the window close event."""

        # Tell the game controller to exit
        self.game_controller.should_exit = True
