#!UTC/Encode to Python with Monkey Python Coddebuging Circus by Alan.R.G.Systemas
import sys, os
from functools import partial
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QMessageBox, QMenuBar, QLineEdit
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QSlider,  QDial, QAction
from PyQt5.QtCore import Qt, QTimer
from pulsectl import Pulse
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette
from mystyles import dial_estilo_minimalista_on, slider_estilo_minimalista_on, slider_estilo_minimalista_off, panel_colors

class MiAppMixer(QMainWindow):
    def __init__(self, parent=None):
        super(MiAppMixer, self).__init__(parent)
        versionado = "v.M01.060724"
        self.usdtdir = "0x104948b1A1AaD3437328aDDcc0A2E5A2679D4192" #USDT ADDRESS FOR DONATIONS BEP20, POLYGON OR OPTIMISM NETWORKS

        # Configuración de la ventana UI
        self.setWindowTitle("MiAppMixer "+ versionado)
        self.setMinimumSize(150,640)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.IconPath = os.path.join(scriptDir, 'icons')   
        self.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))

        # Se crea la barra de menues
        self.crear_barra_menu()

        # Se crea el layout_principal
        layout_principal = QVBoxLayout() 
        widget = QWidget()
        widget.setLayout(layout_principal)
        self.setCentralWidget(widget)      
        layout_panels = QHBoxLayout() 

        # Listar fuentes de audio disponibles en el systema (audio channels/sources) en un diccionario
        self.pulse = Pulse()
        self.fuentes = self.pulse.sink_input_list()
        # para debug
        #print("self.fuentes: ", self.fuentes)
        #for app in self.fuentes:
        #    print("lista de propiedades de las apps", app.proplist)
        #for app in self.fuentes:
        #    print(f"Properties for app index {app.index}:")
        #    for key, value in app.proplist.items():
        #        print(f"  {key}: {value}")

        # Establece un ancho de ventana minimo dependiendo de las fuentes de audio detectadas
        self.setMinimumWidth(150 * len(self.fuentes))

        # verifica existencia de fuentes de audio
        if self.fuentes:
            QMessageBox.information(self, f"Fuentes de Audio {versionado}", f"Fuentes de Audio: {self.fuentes}")
        else:
            QMessageBox.warning(self, "Sin Fuentes de Audio Detectadas", "No se Detectaron Aplicaciones de Audio Activas. Reproduce Audio para Controlar su Volumen.")

        # Botón Actuzalizar Fuentes de Audio
        btn_act_faudio = QPushButton("Actualizar Fuentes de Audio")
        btn_act_faudio.setStyleSheet("color: black;")
        btn_act_faudio.clicked.connect(self.actualizar_dinamicamente_fuentes_audio)        
        layout_principal.addWidget(btn_act_faudio)

        # diccionario de widgets de cada fuente
        self.labels = {}
        self.lineEdits = {}
        self.dials = {}
        self.sliders = {}
        self.muteButtons = {}
        self.vpanel_widget = {}

        # itera sobre las fuentes de audio y crea los paneles de control
        for i, fuente in enumerate(self.fuentes):
            self.vpanel_widget[i]=self.crear_panel_fuente_audio(i, fuente)    
            layout_panels.addWidget(self.vpanel_widget[i])
        layout_principal.addLayout(layout_panels)

        # actualiza el volumen inicial con los valores de cada fuente de audio
        self.volumen_inicial()

        # Actualizar dinamicamente la lista de fuentes de audio cada 5 segundos 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_dinamicamente_fuentes_audio)
        self.timer.start(5000)

    def crear_panel_fuente_audio(self, i, fuente):
        self.labels[i] = QLabel(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'))
        self.labels[i].setStyleSheet("color: black; background-color: lightgreen;")
        self.lineEdits[i] = QLineEdit(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'))
        self.lineEdits[i].setStyleSheet("color: black")
            
        self.dials[i] = QDial()
        self.dials[i].setFixedSize(70,70)
        self.dials[i].setRange(0, 100)
        self.dials[i].setStyleSheet(dial_estilo_minimalista_on)
        
        self.sliders[i] = QSlider(Qt.Vertical, minimum=0, maximum=100)
        self.sliders[i].setStyleSheet(slider_estilo_minimalista_on)
        self.sliders[i].setMinimumWidth(100)
        self.muteButtons[i] = QPushButton("Silenciar")
        self.muteButtons[i].setCheckable(True)
        self.muteButtons[i].setStyleSheet("color: black; background-color: lightgray;")

        # Conectores
        self.lineEdits[i].textChanged.connect(lambda text, i=i: self.actualizar_nombre_fuente(text, i))
        self.dials[i].valueChanged.connect(partial(self.actualizar_volumen, "dial", i))
        self.sliders[i].valueChanged.connect(partial(self.actualizar_volumen, "slide", i))
        self.muteButtons[i].clicked.connect(partial(self.toggleMute, i))

        # Centrado de controles en el panel mediante layouts y spacers
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        dial_layout_centering = QHBoxLayout()
        dial_layout_centering.addItem(spacer)
        dial_layout_centering.addWidget(self.dials[i])
        dial_layout_centering.addItem(spacer)
        slide_layout_centering = QHBoxLayout()
        slide_layout_centering.addItem(spacer)
        slide_layout_centering.addWidget(self.sliders[i])
        slide_layout_centering.addItem(spacer)

        # Agrega widgets de la fuente de audio al layout de su panel vertical
        self.vpanel_widget[i] = QWidget()
        self.vpanel_widget[i].setMaximumWidth(150)
        self.vpanel_widget[i].setStyleSheet(f"background-color: {panel_colors[i]};")
        vLayout = QVBoxLayout(self.vpanel_widget[i])
        vLayout.addWidget(self.labels[i])
        vLayout.addWidget(self.lineEdits[i])
        vLayout.addLayout(dial_layout_centering)
        vLayout.addLayout(slide_layout_centering)
        vLayout.addWidget(self.muteButtons[i])

        return self.vpanel_widget[i]

    def crear_barra_menu(self):
        """ Crea la barra de menú. """
        # Barra de menú 
        self.menuBar = QMenuBar(self)   
        self.layout().setMenuBar(self.menuBar)
        # Establecer estilo para la barra de menú
        self.menuBar.setStyleSheet("background-color: black; color: white;") # Ajusta el color de fondo y el color del texto de la barra de menú
        # Menú aplicación
        self.aplicacion = self.menuBar.addMenu('Aplicación')
        self.opcionayuda = QAction('Ayuda', self)
        self.opcionayuda.triggered.connect(self.en_construccion)
        self.aplicacion.addAction(self.opcionayuda)
        self.opciondonar = QAction('Donar', self)
        self.opciondonar.triggered.connect(self.donar)
        self.aplicacion.addAction(self.opciondonar)
        self.opcionreiniciar = QAction('Reiniciar', self)
        self.opcionreiniciar.triggered.connect(self.reiniciar_app)
        self.aplicacion.addAction(self.opcionreiniciar)
        self.opcionsalir = QAction('Salir', self)
        self.opcionsalir.triggered.connect(self.salir)
        self.aplicacion.addAction(self.opcionsalir)
        # Menú Configuración
        self.menuConfiguracion = self.menuBar.addMenu('Configuración')
           # Opción para configurar las horas de apertura y cierre de cada mercado
        self.opcionHorarios = QAction('Configurar Escala de Volúmen', self)
        self.opcionHorarios.triggered.connect(self.en_construccion)
        self.menuConfiguracion.addAction(self.opcionHorarios)
           # Opción para configurar los colores de los elementos de la aplicación
        self.opcionColores = QAction('Configurar Colores de la Aplicación', self)
        self.opcionColores.triggered.connect(self.en_construccion)
        self.menuConfiguracion.addAction(self.opcionColores)

    def volumen_inicial(self):
        for i, fuente in enumerate(self.fuentes):
            volumen = int(self.fuentes[i].volume.value_flat * 100)
            self.dials[i].setValue(volumen)
            self.sliders[i].setValue(volumen)
            if self.esta_silenciado(i):
                self.muteButtons[i].setChecked(True)
                self.panel_off(i)
            else:
                self.muteButtons[i].setChecked(False)
                self.panel_on(i)

    def toggleMute(self, index):
        silenciado = self.esta_silenciado(index)
        if silenciado:
            self.pulse.sink_input_mute(self.fuentes[index].index, 0)
            self.panel_on(index)
        else:
            self.pulse.sink_input_mute(self.fuentes[index].index, 1)
            self.panel_off(index)
        #actualiza los estados
        self.fuentes = self.pulse.sink_input_list()
    
    def panel_on(self, index):
        self.labels[index].setStyleSheet("color: black; background-color: lightgreen;")
        self.dials[index].setDisabled(False)
        self.dials[index].setStyleSheet(dial_estilo_minimalista_on)
        self.sliders[index].setDisabled(False)
        self.sliders[index].setStyleSheet(slider_estilo_minimalista_on)
        self.muteButtons[index].setText("Silenciar")
        self.muteButtons[index].setStyleSheet("color: black; background-color: gray;")
    
    def panel_off(self, index):
        self.labels[index].setStyleSheet("color: grey; background-color: red;")
        self.dials[index].setDisabled(True)
        self.sliders[index].setDisabled(True)
        self.sliders[index].setStyleSheet(slider_estilo_minimalista_off)
        self.muteButtons[index].setText("Restaurar")
        self.muteButtons[index].setStyleSheet("color: white; background-color: darkgray;")

    def actualizar_volumen(self, origen, index):
            if origen == "dial":
                nuevo_volumen = self.dials[index].value() / 100.0
                self.sliders[index].setValue(self.dials[index].value())
            if origen == "slide":
                nuevo_volumen = self.sliders[index].value() / 100.0
                self.dials[index].setValue(self.sliders[index].value())
            
            #se debe actualizar en ambos canales
            volumen_actual = self.fuentes[index].volume
            for i in range(len(volumen_actual.values)):
                volumen_actual.values[i] = nuevo_volumen
            self.pulse.volume_set(self.fuentes[index], volumen_actual)

    def actualizar_nombre_fuente(self, text, index):
        self.fuentes[index].name = text

    def esta_silenciado(self, index):
        silenciado = bool(self.fuentes[index].mute)
        return silenciado
    
    def actualizar_dinamicamente_fuentes_audio(self):
        """ Evalua cambios en las fuentes de audio y
        las actualiza dinamicamente... por ahora reiniciando la app 
        """
        evaluando = self.pulse.sink_input_list() 
        if len(self.fuentes) != len(evaluando):
            QMessageBox.information(self, "Aviso", f""" Se detectaron cambios en las fuentes de audio!
                Se debe reiniciar la applicación
                para conectar controladores
                de sonido en funcion de los
                cambios
            """)
            self.reiniciar_app()

    def donar(self):
        """ Crea la Ventana de Donación. """
        QMessageBox.information(self, "Donar...", f"""                    Ayude al software libre!!!                          
        
        Apoye a los programadores
        enviando su donación:
            # En Argentina via transferencia bancaria
              por app o billetera virtual al alias:
              buzos.hay.domar.mp
            # En Argentina y Resto del Mundo
              USDT por redes BEP20,  Polygon o Optimism
              {self.usdtdir}

        """)

    def en_construccion(self):
        """ Crea la Ventana que indica que la app esta en construcción. """
        QMessageBox.information(self, "...en construcción", f"""                  Paciencia!!!                          
        
        Implementando Metodos y Clases

        """)

    def reiniciar_app(self):
        """Reinicia la Aplicación."""
        # Flush the stdout to ensure all logs are printed before the app restarts
        print("reiniciando")
        sys.stdout.flush()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def salir(self):
        """ Sale de la Aplicación. """
        print("saliendo")
        sys.stdout.flush()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    #app.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
    window = MiAppMixer()
    window.show()
    sys.exit(app.exec_())
