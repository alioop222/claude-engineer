import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QProgressBar, QSlider, QSplitter,
                             QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsTextItem, QDockWidget)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QIcon, QColor, QPen
from modules.token_monitor import TokenMonitor

class Artifact:
    def __init__(self, name, function, x, y):
        self.name = name
        self.function = function
        self.x = x
        self.y = y
        self.connections = []

    def connect(self, other_artifact):
        self.connections.append(other_artifact)
        other_artifact.connections.append(self)

class ArtifactScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.artifacts = []

    def add_artifact(self, artifact):
        ellipse = QGraphicsEllipseItem(0, 0, 50, 50)
        ellipse.setPos(artifact.x, artifact.y)
        ellipse.setBrush(QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
        self.addItem(ellipse)

        text = QGraphicsTextItem(artifact.name)
        text.setPos(artifact.x, artifact.y + 60)
        self.addItem(text)

        self.artifacts.append((artifact, ellipse))

    def connect_artifacts(self, artifact1, artifact2):
        pos1 = artifact1[1].pos()
        pos2 = artifact2[1].pos()
        line = QGraphicsLineItem(pos1.x() + 25, pos1.y() + 25, pos2.x() + 25, pos2.y() + 25)
        self.addItem(line)

class ClaudeEngineerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token_monitor = TokenMonitor()
        self.artifacts = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Claude-Engineer Desktop')
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowIcon(QIcon('icon.png'))

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Sliding side menu (left side)
        side_menu = QWidget()
        side_menu.setFixedWidth(200)
        side_menu_layout = QVBoxLayout()
        side_menu_headers = ['Git', 'Env', 'Schema', 'Artifacts', 'Mode', 'Chats', 'Frameworks']
        for header in side_menu_headers:
            side_menu_layout.addWidget(QPushButton(header))
        side_menu.setLayout(side_menu_layout)

        # Right side split view (chat area and artifact display)
        right_splitter = QSplitter(Qt.Vertical)

        # Chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()

        # Token usage display
        self.token_usage_label = QLabel('Token Usage: 0%')
        self.token_usage_bar = QProgressBar()
        self.token_usage_bar.setRange(0, 100)

        # Chat display and input
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_input = QTextEdit()
        self.chat_input.setFixedHeight(100)
        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_message)

        chat_layout.addWidget(self.token_usage_label)
        chat_layout.addWidget(self.token_usage_bar)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_button)

        chat_widget.setLayout(chat_layout)

        # Artifact display area
        self.artifact_scene = ArtifactScene()
        self.artifact_view = QGraphicsView(self.artifact_scene)

        right_splitter.addWidget(chat_widget)
        right_splitter.addWidget(self.artifact_view)

        # Add widgets to main layout
        main_layout.addWidget(side_menu)
        main_layout.addWidget(right_splitter)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Artifact management panel
        artifact_dock = QDockWidget("Artifact Management", self)
        artifact_dock_widget = QWidget()
        artifact_dock_layout = QVBoxLayout()
        create_artifact_button = QPushButton("Create New Artifact")
        create_artifact_button.clicked.connect(self.create_artifact)
        artifact_dock_layout.addWidget(create_artifact_button)
        artifact_dock_widget.setLayout(artifact_dock_layout)
        artifact_dock.setWidget(artifact_dock_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, artifact_dock)

        # Set up timers
        self.token_timer = QTimer(self)
        self.token_timer.timeout.connect(self.update_token_usage)
        self.token_timer.start(60000)  # Update every minute

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_chat)
        self.autosave_timer.start(300000)  # Autosave every 5 minutes

        # Full screen toggle button
        full_screen_button = QPushButton('Toggle Full Screen')
        full_screen_button.clicked.connect(self.toggle_full_screen)
        chat_layout.addWidget(full_screen_button)

    def send_message(self):
        message = self.chat_input.toPlainText()
        if message:
            self.chat_display.append(f"You: {message}")
            self.chat_input.clear()
            # Here you would typically send the message to Claude and get a response
            # For now, we'll just echo the message and create a simulated artifact
            self.chat_display.append(f"Claude: You said: {message}")
            self.create_artifact_from_message(message)

    def create_artifact_from_message(self, message):
        artifact = Artifact(f"Artifact_{len(self.artifacts)}", message[:20], random.randint(0, 300), random.randint(0, 300))
        self.artifact_scene.add_artifact(artifact)
        self.artifacts.append(artifact)

        # Randomly connect to an existing artifact
        if len(self.artifacts) > 1:
            other_artifact = random.choice(self.artifacts[:-1])
            artifact.connect(other_artifact)
            self.artifact_scene.connect_artifacts(
                self.artifact_scene.artifacts[-1],
                next(a for a in self.artifact_scene.artifacts if a[0] == other_artifact)
            )

    def create_artifact(self):
        artifact = Artifact(f"Manual_Artifact_{len(self.artifacts)}", "User created", random.randint(0, 300), random.randint(0, 300))
        self.artifact_scene.add_artifact(artifact)
        self.artifacts.append(artifact)

    def update_token_usage(self):
        usage = self.token_monitor.get_token_usage()
        if usage is not None:
            percentage = self.token_monitor.get_usage_percentage()
            self.token_usage_label.setText(f'Token Usage: {percentage:.2f}%')
            self.token_usage_bar.setValue(int(percentage))

            if self.token_monitor.is_warning_needed():
                warning = self.token_monitor.format_warning_message()
                self.chat_display.append(f"System: {warning}")

    def autosave_chat(self):
        chat_history = self.chat_display.toPlainText()
        self.token_monitor.save_chat_history(chat_history)
        self.chat_display.append("Chat history autosaved.")

    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event):
        chat_history = self.chat_display.toPlainText()
        self.token_monitor.save_chat_history(chat_history)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ClaudeEngineerGUI()
    gui.show()
    sys.exit(app.exec_())