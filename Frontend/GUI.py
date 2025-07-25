
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QLabel, QVBoxLayout, QPushButton, QFrame, QSizePolicy, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import os
import sys

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure directories exist (optional, but good practice)
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Utility Functions
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "where's", "how's", "can you"]
    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip('.?!') + "?"
    else:
        new_query = new_query.rstrip('.?!') + "."
    return new_query.capitalize()

def SetMicrophoneStatus(command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
        file.write(command)

def GetMicrophoneStatus():
    with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(status)

def GetAssistantStatus():
    with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
        return file.read()

def ShowTextToScreen(text):
    with open(os.path.join(TempDirPath, "Responses.data"), "w", encoding='utf-8') as file:
        file.write(text)

def GraphicsDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)

# ChatSection Widget
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout for the chat section
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20) # Add padding around the content
        main_layout.setSpacing(15) # Spacing between widgets

        # Chat Text Edit
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #282c34; /* Darker background for chat area */
                border-radius: 10px;
                padding: 15px;
                color: #abb2bf; /* Light grey text */
                border: 1px solid #3e4451; /* Subtle border */
            }
        """)
        font = QFont("Arial", 12) # Use a modern font
        self.chat_text_edit.setFont(font)
        self.chat_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # Show scrollbar only when needed
        main_layout.addWidget(self.chat_text_edit, 1) # Make chat text edit expand

        # GIF Label
        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('jarvis.gif'))
        movie.setScaledSize(QSize(480, 270)) # Keep original size or adjust as needed
        self.gif_label.setMovie(movie)
        movie.start()
        self.gif_label.setAlignment(Qt.AlignCenter) # Center the GIF
        main_layout.addWidget(self.gif_label)

        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color:#61afef; font-size:16px; font-weight: bold;") # Accent color for status
        self.label.setAlignment(Qt.AlignCenter) # Center the status text
        main_layout.addWidget(self.label)

        self.setStyleSheet("background-color:#21252b;") # Main background for the section

        # Timers for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def loadMessages(self):
        try:
            with open(os.path.join(TempDirPath, "Responses.data"), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages:
                    # Clear previous content to avoid duplication if file is overwritten
                    # This assumes Responses.data is always the *current* message
                    # If it's a log, you'd append, but current logic overwrites.
                    self.chat_text_edit.clear() 
                    self.addMessage(message=messages, color='#abb2bf') # Use light grey for assistant text
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
                self.label.setText(file.read())
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor) # Scroll to bottom

# Initial Screen Widget
class InitialScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout for the initial screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter) # Center all content vertically

        # GIF Label
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('jarvis.gif'))
        movie.setScaledSize(QSize(640, 360))
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setAlignment(Qt.AlignCenter) # Center the GIF
        main_layout.addWidget(gif_label)

        # Microphone Icon Label
        self.icon_label = QLabel()
        self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
        self.icon_label.mousePressEvent = self.toggle_icon
        self.icon_label.setAlignment(Qt.AlignCenter) # Center the icon
        self.icon_label.setCursor(Qt.PointingHandCursor) # Indicate clickable
        self.icon_label.setStyleSheet("""
            QLabel {
                border: 2px solid #61afef; /* Accent border */
                border-radius: 35px; /* Make it circular */
                padding: 5px;
                background-color: #282c34; /* Dark background for icon */
            }
            QLabel:hover {
                background-color: #3e4451; /* Slightly lighter on hover */
            }
        """)
        main_layout.addWidget(self.icon_label)

        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color:#61afef; font-size:16px; font-weight: bold;") # Accent color for status
        self.label.setAlignment(Qt.AlignCenter) # Center the status text
        main_layout.addWidget(self.label)

        self.setStyleSheet("background-color:#21252b;") # Main background for the section
        self.toggled = True # Initial state for microphone

        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)

    def load_icon(self, path):
        pixmap = QPixmap(path).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Slightly larger, smooth scaling
        self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'))
            SetMicrophoneStatus("False")
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            SetMicrophoneStatus("True")
        self.toggled = not self.toggled

    def updateStatus(self):
        try:
            with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
                self.label.setText(file.read())
        except FileNotFoundError:
            pass

# Main Window and App
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint) # Keep frameless
        self.setMinimumSize(1024, 600) # Set a minimum size for better UI scaling

        # Central Widget and Stacked Widget
        central_widget = QWidget()
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0) # No margins for the central widget

        stacked_widget = QStackedWidget()
        self.initial_screen = InitialScreen()
        self.chat_screen = ChatSection()
        stacked_widget.addWidget(self.initial_screen)
        stacked_widget.addWidget(self.chat_screen)
        
        # Add top bar and stacked widget to the main layout
        top_bar = self.createTopBar(stacked_widget)
        main_v_layout.addWidget(top_bar)
        main_v_layout.addWidget(stacked_widget, 1) # Make stacked widget expand

        self.setCentralWidget(central_widget)

        # Global Stylesheet for the application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #21252b; /* Dark background */
                border: 1px solid #3e4451; /* Subtle border for the window */
                border-radius: 10px; /* Rounded corners for the window */
            }
            QPushButton {
                background-color: #3e4451; /* Darker button background */
                color: #abb2bf; /* Light grey text */
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4b5263; /* Slightly lighter on hover */
            }
            QPushButton#homeButton {
                background-color: #61afef; /* Blue accent for Home */
                color: white;
            }
            QPushButton#homeButton:hover {
                background-color: #529cdb;
            }
            QPushButton#chatButton {
                background-color: #98c379; /* Green accent for Chat */
                color: white;
            }
            QPushButton#chatButton:hover {
                background-color: #89b26a;
            }
            QPushButton#closeButton {
                background-color: #e06c75; /* Red accent for Close */
                color: white;
                font-weight: bold;
                padding: 5px 10px; /* Smaller padding for close button */
                border-radius: 5px;
            }
            QPushButton#closeButton:hover {
                background-color: #d15c6a;
            }
            QLabel#titleLabel {
                color: #61afef; /* Accent color for title */
                font-size: 20px;
                font-weight: bold;
                padding-left: 15px;
            }
        """)

    def createTopBar(self, stacked_widget):
        bar = QWidget()
        bar.setStyleSheet("background-color: #282c34; border-bottom: 1px solid #3e4451;") # Darker bar background with border
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 5, 0, 5) # Padding for the top bar
        layout.setSpacing(10) # Spacing between elements in the bar

        title = QLabel(f"{Assistantname} AI")
        title.setObjectName("titleLabel") # Set object name for specific styling
        layout.addWidget(title)
        layout.addStretch() # Pushes buttons to the right

        home_btn = QPushButton("Home")
        home_btn.setObjectName("homeButton") # Set object name for specific styling
        home_btn.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        layout.addWidget(home_btn)

        chat_btn = QPushButton("Chat")
        chat_btn.setObjectName("chatButton") # Set object name for specific styling
        chat_btn.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        layout.addWidget(chat_btn)

        close_btn = QPushButton("X")
        close_btn.setObjectName("closeButton") # Set object name for specific styling
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return bar

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    
    # Set a default font for the entire application
    app_font = QFont("Arial", 10)
    app.setFont(app_font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Create dummy files for testing if they don't exist
    if not os.path.exists(TempDirPath):
        os.makedirs(TempDirPath)
    if not os.path.exists(GraphicsDirPath):
        os.makedirs(GraphicsDirPath)
    
    # Create dummy Mic.data and Status.data if they don't exist
    mic_data_path = os.path.join(TempDirPath, "Mic.data")
    status_data_path = os.path.join(TempDirPath, "Status.data")
    responses_data_path = os.path.join(TempDirPath, "Responses.data")

    if not os.path.exists(mic_data_path):
        with open(mic_data_path, "w", encoding='utf-8') as f:
            f.write("True")
    if not os.path.exists(status_data_path):
        with open(status_data_path, "w", encoding='utf-8') as f:
            f.write("Listening...")
    if not os.path.exists(responses_data_path):
        with open(responses_data_path, "w", encoding='utf-8') as f:
            f.write("Hello! How can I help you today?")

    # Create dummy GIF and PNG files if they don't exist
    # Replace these with your actual paths or create simple placeholders
    dummy_gif_path = GraphicsDirectoryPath('jarvis.gif')
    dummy_mic_on_path = GraphicsDirectoryPath('Mic_on.png')
    dummy_mic_off_path = GraphicsDirectoryPath('Mic_off.png')

    if not os.path.exists(dummy_gif_path):
        # Create a very basic dummy GIF (requires Pillow and imageio for real GIF creation)
        # For a simple test, you might just need a placeholder file.
        # A real GIF would need to be provided by the user or created with a library.
        print(f"WARNING: {dummy_gif_path} not found. Please provide a 'jarvis.gif' in the Graphics directory.")
        # Create a blank image as a placeholder if no GIF is available
        try:
            from PIL import Image
            img = Image.new('RGB', (480, 270), color = 'gray')
            img.save(dummy_gif_path.replace('.gif', '.png')) # Save as PNG if GIF creation is complex
            print(f"Created a dummy PNG placeholder for {dummy_gif_path}")
        except ImportError:
            print("Pillow not installed. Cannot create dummy image. Please install Pillow (pip install Pillow) or provide your own image files.")
            # Create an empty file to prevent FileNotFoundError
            with open(dummy_gif_path, 'w') as f:
                f.write('')

    if not os.path.exists(dummy_mic_on_path):
        print(f"WARNING: {dummy_mic_on_path} not found. Please provide a 'Mic_on.png' in the Graphics directory.")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (70, 70), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((5, 5, 65, 65), fill='green', outline='white', width=2)
            draw.polygon([(35, 15), (25, 35), (45, 35)], fill='white') # Simple mic shape
            img.save(dummy_mic_on_path)
            print(f"Created a dummy PNG placeholder for {dummy_mic_on_path}")
        except ImportError:
            print("Pillow not installed. Cannot create dummy image. Please install Pillow (pip install Pillow) or provide your own image files.")
            with open(dummy_mic_on_path, 'w') as f:
                f.write('')

    if not os.path.exists(dummy_mic_off_path):
        print(f"WARNING: {dummy_mic_off_path} not found. Please provide a 'Mic_off.png' in the Graphics directory.")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (70, 70), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((5, 5, 65, 65), fill='red', outline='white', width=2)
            draw.line((10, 10, 60, 60), fill='white', width=3) # X over mic
            img.save(dummy_mic_off_path)
            print(f"Created a dummy PNG placeholder for {dummy_mic_off_path}")
        except ImportError:
            print("Pillow not installed. Cannot create dummy image. Please install Pillow (pip install Pillow) or provide your own image files.")
            with open(dummy_mic_off_path, 'w') as f:
                f.write('')

    GraphicalUserInterface()