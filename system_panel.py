import sys
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QLabel, QMenu, QSystemTrayIcon, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QAction, QIcon

class StarkPanel(QWidget):
    def __init__(self):
        super().__init__()

        # CONSTANTS:
        self.NAME = "SYSTEM HUD"
        self.WIDGET_WIDTH = 420
        self.WIDGET_HEIGHT = 70

        self.VITALS_FONT_SIZE = 18
        self.LABEL_FONT_SIZE = 12

        self.setWindowTitle(self.NAME)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WIDGET_WIDTH, self.WIDGET_HEIGHT)
        
        # Position the panel at the top center of the screen
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(
            int((screen_geometry.width() - self.width()) / 1.2),
            20
        )
        
        self.old_pos = self.pos()
        self.edge_threshold = 50

        # Setup system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("utilities-system-monitor", QIcon.fromTheme("applications-system")))
        self.tray_icon.setToolTip(self.NAME)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Tray menu
        tray_menu = QMenu()
        restore_action = QAction("Restore Panel", self)
        quit_action = QAction("Exit", self)

        restore_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setVisible(True)

        # Create labels with custom styling
        self.cpu_value_label = QLabel("0%")
        self.cpu_text_label = QLabel("CPU")
        self.ram_value_label = QLabel("0%")
        self.ram_text_label = QLabel("RAM")

        self.net_up_label = QLabel("0000 KB/s")
        self.net_up_label.setMinimumWidth(90)

        self.net_down_label = QLabel("0000 KB/s")
        self.net_down_label.setMinimumWidth(90)

        # Set custom font and color for all labels
        self.setup_label_style(self.cpu_value_label, self.VITALS_FONT_SIZE, True)
        self.setup_label_style(self.cpu_text_label, self.LABEL_FONT_SIZE, False)
        self.setup_label_style(self.ram_value_label, self.VITALS_FONT_SIZE, True)
        self.setup_label_style(self.ram_text_label, self.LABEL_FONT_SIZE, False)
        self.setup_label_style(self.net_up_label, self.VITALS_FONT_SIZE, True)
        self.setup_label_style(self.net_down_label, self.VITALS_FONT_SIZE, True)

        # Create horizontal layout
        layout = QHBoxLayout()
        
        # Add CPU section
        cpu_section = QWidget()
        cpu_layout = QVBoxLayout(cpu_section)
        cpu_layout.addWidget(self.cpu_value_label, 0, Qt.AlignmentFlag.AlignCenter)
        cpu_layout.addWidget(self.cpu_text_label, 0, Qt.AlignmentFlag.AlignCenter)
        cpu_layout.setSpacing(5)
        cpu_layout.setContentsMargins(20, 5, 10, 5)
        
        # Add RAM section
        ram_section = QWidget()
        ram_layout = QVBoxLayout(ram_section)
        ram_layout.addWidget(self.ram_value_label, 0, Qt.AlignmentFlag.AlignCenter)
        ram_layout.addWidget(self.ram_text_label, 0, Qt.AlignmentFlag.AlignCenter)
        ram_layout.setSpacing(5)
        ram_layout.setContentsMargins(20, 5, 10, 5)
        
        # Add network section
        net_section = QWidget()
        net_layout = QVBoxLayout(net_section)

        # Create a sub-layout for the labels
        net_labels_layout = QHBoxLayout()
        net_labels_layout.addWidget(self.net_up_label, 0, Qt.AlignmentFlag.AlignCenter)
        net_labels_layout.addWidget(self.net_down_label, 0, Qt.AlignmentFlag.AlignCenter)

        # Create arrow labels
        self.net_up_arrow = QLabel("↑")
        self.net_down_arrow = QLabel("↓")

        # Style the arrows
        self.setup_label_style(self.net_up_arrow, self.LABEL_FONT_SIZE, False)
        self.setup_label_style(self.net_down_arrow, self.LABEL_FONT_SIZE, False)

        # Add arrows to a sub-layout
        net_arrows_layout = QHBoxLayout()
        net_arrows_layout.addWidget(self.net_up_arrow, 0, Qt.AlignmentFlag.AlignCenter)
        net_arrows_layout.addWidget(self.net_down_arrow, 0, Qt.AlignmentFlag.AlignCenter)

        # Add sub-layouts to the main network layout
        net_layout.addLayout(net_labels_layout)
        net_layout.addLayout(net_arrows_layout)

        net_layout.setSpacing(5)
        net_layout.setContentsMargins(20, 1, 20, 1)
        
        # Add sections to main layout
        layout.addWidget(cpu_section)
        layout.addWidget(ram_section)
        layout.addWidget(net_section)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(0)
        
        self.setLayout(layout)

        # Timer for updating stats
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

        # Initialize network counters
        self.last_bytes_sent = psutil.net_io_counters().bytes_sent
        self.last_bytes_recv = psutil.net_io_counters().bytes_recv

    def setup_label_style(self, label, font_size, is_value):
        font = QFont("Ubuntu Mono", font_size)
        font.setBold(True)
        label.setFont(font)
        if is_value:
            label.setStyleSheet("color: #00FF7F;")  # Bright green for values
        else:
            label.setStyleSheet("color: white;")  # White for descriptive text
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(20, 20, 20, 200)))
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        # Draw border
        pen = QPen(QColor(60, 60, 60, 150))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 20, 20)
        
        # Draw diagonal separator
        # painter.setPen(QPen(QColor(60, 60, 60, 150), 2))
        # separator_x = int(self.width() * 0.6)
        # painter.drawLine(separator_x, 10, separator_x + 30, self.height() - 10)

    def update_stats(self):
        # Update CPU usage
        cpu = psutil.cpu_percent()
        self.cpu_value_label.setText(f"{int(cpu)}%")

        # Update RAM usage
        ram = psutil.virtual_memory().percent
        self.ram_value_label.setText(f"{int(ram)}%")

        # Update network stats
        current = psutil.net_io_counters()
        up = (current.bytes_sent - self.last_bytes_sent) / 1024  # KB/s
        down = (current.bytes_recv - self.last_bytes_recv) / 1024  # KB/s

        self.last_bytes_sent = current.bytes_sent
        self.last_bytes_recv = current.bytes_recv

        # Format upload speed
        up_str = f"{int(up):04d}"
        down_str = f"{int(down):04d}"

        grey_index = -1
        if int(up_str) > 999:
            grey_index = -4
        elif int(up_str) > 99:
            grey_index = -3
        elif int(up_str) > 9:
            grey_index = -2
        elif int(up_str) >= 0:
            grey_index = -1

        # Apply styles to leading zeros and significant digits
        up_html = f"<span style='color: #001100;'>{up_str[:grey_index]}</span><span style='color: #00FF7F;'>{up_str[grey_index:]}</span> KB/s"

        grey_index = -1
        if int(down_str) > 999:
            grey_index = -4
        elif int(down_str) > 99:
            grey_index = -3
        elif int(down_str) > 9:
            grey_index = -2
        elif int(down_str) >= 0:
            grey_index = -1


        down_html = f"<span style='color: #001100;'>{down_str[:grey_index]}</span><span style='color: #00FF7F;'>{down_str[grey_index:]}</span> KB/s"

        self.net_up_label.setText(up_html)
        self.net_down_label.setText(down_html)

        # Enable rich text formatting for labels
        self.net_up_label.setTextFormat(Qt.TextFormat.RichText)
        self.net_down_label.setTextFormat(Qt.TextFormat.RichText)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # Snap to edges if close enough
        screen = QApplication.primaryScreen().availableGeometry()
        if abs(self.x()) < self.edge_threshold:
            self.move(0, self.y())
        elif abs((self.x() + self.width()) - screen.width()) < self.edge_threshold:
            self.move(screen.width() - self.width(), self.y())
        elif abs(self.y()) < self.edge_threshold:
            self.move(self.x(), 0)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        minimize_action = QAction("Minimize to Tray", self)
        always_on_top_action = QAction("Toggle Always on Top", self)
        exit_action = QAction("Exit", self)

        minimize_action.triggered.connect(self.minimize_to_tray)
        always_on_top_action.triggered.connect(self.toggle_always_on_top)
        exit_action.triggered.connect(QApplication.instance().quit)

        menu.addAction(minimize_action)
        menu.addAction(always_on_top_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        menu.exec(pos)

    def minimize_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            self.NAME, "Panel minimized to system tray", 
            QSystemTrayIcon.MessageIcon.Information, 2000
        )

    def toggle_always_on_top(self):
        flags = self.windowFlags()
        if flags & Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self.tray_icon.showMessage(self.NAME, "Always on top disabled", 
                                     QSystemTrayIcon.MessageIcon.Information, 1000)
        else:
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            self.tray_icon.showMessage(self.NAME, "Always on top enabled", 
                                     QSystemTrayIcon.MessageIcon.Information, 1000)
        self.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def closeEvent(self, event):
        # Override close event to minimize to tray instead of closing
        event.ignore()
        self.minimize_to_tray()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = StarkPanel()
    panel.show()
    sys.exit(app.exec())