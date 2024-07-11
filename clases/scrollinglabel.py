#import sys
from PyQt5.QtWidgets import QLabel #,QApplication, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

class ScrollingLabel(QLabel):
    """Scroll automatico del texto en una etiqueta

        Args: ScroollingLabel(str, int): str("string a scrollear), int(velocidad)
        """
    def __init__(self, text, speed, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.text = text
        self.step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(speed)  # Ajusta la velocidad del desplazamiento aquí

    def update_text(self):
        display_text = self.text[self.step:] + self.text[:self.step]
        self.setText(display_text)
        self.step = (self.step + 1) % len(self.text)
'''
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        scrolling_label = ScrollingLabel("Este es un texto largo que se desplazará automáticamente.")
        layout.addWidget(scrolling_label)

        self.setLayout(layout)
        self.setWindowTitle('Texto Desplazándose Horizontalmente')
        self.setGeometry(100, 100, 600, 100)  # Ajusta el tamaño de la ventana según sea necesario

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
'''