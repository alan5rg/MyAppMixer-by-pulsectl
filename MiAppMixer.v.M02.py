#!UTC/Encode to Python with Monkey Python Coddebuging Circus by Alan.R.G.Systemas
'''
En beta test... implementar mejoras:
Es muy molesto que cada vez que en el sistema aparece o desaparece una fuente de audio aparezca un cartel. Cambiar!
Volumen independiente por canal o con los canales linkeado.
ver personalizado de color fondo paneles.
ver colores de fuentes de botones y etiquetas.

v.M02.100724.Se Implementa Scroll Automatico de Labels de Entradas!
             Se Evita que la app inicie si no hay fuentes de Audio en el Sistema.
             Se Documenta, Depura, Resume y Minimiza el Código en Parte.
             Se Implementa menú de configuración/esquema de colores
'''
import sys, os
from functools import partial
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QMessageBox, QMenuBar, QLineEdit
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QSlider,  QDial, QAction
from PyQt5.QtCore import Qt, QTimer
from pulsectl import Pulse
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette
#mis estilos y clases
from styles.mystyles import dial_estilo_minimalista_on, slider_estilo_minimalista_on, slider_estilo_minimalista_off, panel_colors, slider_dimensiones
from clases.scrollinglabel import ScrollingLabel

class MiAppMixer(QMainWindow):
    def __init__(self, parent=None):
        super(MiAppMixer, self).__init__(parent)
        versionado = "v.M02.100724"
        self.usdtdir = "0x104948b1A1AaD3437328aDDcc0A2E5A2679D4192" #USDT ADDRESS FOR DONATIONS BEP20, POLYGON OR OPTIMISM NETWORKS

        # Configuración de la ventana UI
        self.setWindowTitle("MiAppMixer "+ versionado)
        self.setMinimumSize(150,640)
        self.esquemaColores={"mystyles": True, "paletaOscura": False} # Mi Estilo/Estilo del Creador
        #self.esquemaColores={"mystyles": False, "paletaOscura": True}

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
        layout_paneles = QHBoxLayout() 

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

        # Establece un ancho de ventana minimo dinamico que depende
        #  de las fuentes de audio detectadas
        self.setMinimumWidth(150 * len(self.fuentes))

        # verifica existencia de fuentes de audio
        # mensaje solo para debug
        #if self.fuentes:
        #    QMessageBox.information(self, f"Fuentes de Audio {versionado}", f"Fuentes de Audio: {self.fuentes}")
        #else:
        if  len(self.fuentes) == 0:
            QMessageBox.warning(self, "Sin Fuentes de Audio Detectadas", """No se Detectaron Aplicaciones de Audio Activas.
Reproduce Audio para Controlar su Volumen.""")
            self.salir()

        # Botón Actuzalizar Fuentes de Audio
        btn_act_faudio = QPushButton("Actualizar Fuentes de Audio")
        btn_act_faudio.setStyleSheet("color: black;")
        btn_act_faudio.clicked.connect(self.actualizar_dinamicamente_fuentes_audio)        
        layout_principal.addWidget(btn_act_faudio)

        # Ajusta la velocidad del scroll de las etiquetas de las fuentes de audio
        self.speedscroll = 150 #menor valor mayor velocidad

        # diccionarios de widgets de cada fuente
        #self.vpanel_widget = {}
        self.vPanel_Widgets = {}
        self.labels = {}
        self.lineEdits = {}
        self.dials = {}
        self.sliders = {}
        self.muteButtons = {}
        
        # itera sobre las fuentes de audio y crea los paneles verticales de control
        for i, fuente in enumerate(self.fuentes):
            layout_paneles.addWidget(self.crear_panel_fuente_audio(i, fuente))
        layout_principal.addLayout(layout_paneles)

        # actualiza el volumen inicial con los valores de cada fuente de audio
        self.volumen_inicial()

        # Actualizar dinamicamente la lista de fuentes de audio cada 5 segundos 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_dinamicamente_fuentes_audio)
        self.timer.start(5000)

    #---------------------Widget Panel de Fuente de Audio Generico
    def crear_panel_fuente_audio(self, i, fuente):
        """Crea Un Panel para una fuente de audio con todos los controles

        Args:
            i (int): indice en la lista de fuentes de audio
            fuente (str): nombre de la fuente de audio

        Returns:
            QWidget(): Crea y Devuelve un QWidget con el layout que continen todos los controles,
            cada uno identificado con el indice como elemento del diccionario que le corresponde
        """
        self.labels[i] = ScrollingLabel(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'), self.speedscroll)
        self.lineEdits[i] = QLineEdit(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'))
            
        self.dials[i] = QDial()
        self.dials[i].setFixedSize(70,70)
        self.dials[i].setRange(0, 100)
        
        self.sliders[i] = QSlider(Qt.Vertical, minimum=0, maximum=100)
        self.sliders[i].setMinimumWidth(100)
        self.muteButtons[i] = QPushButton("Silenciar")
        self.muteButtons[i].setCheckable(True)
        self.muteButtons[i].setStyleSheet("color: black; background-color: lightgray;")

        # Conectores
        self.lineEdits[i].textChanged.connect(lambda text, i=i: self.actualizar_nombre_fuente(text, i))
        self.dials[i].valueChanged.connect(partial(self.actualizar_volumen, "dial", i))
        self.sliders[i].valueChanged.connect(partial(self.actualizar_volumen, "slide", i))
        self.muteButtons[i].clicked.connect(partial(self.silenciar_fuente, i))

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

        # Crea el widget panel vertical de la fuente de audio y agrega todos los elementos
        self.vPanel_Widgets[i] = QWidget()
        self.vPanel_Widgets[i].setMaximumWidth(150)
        if self.esquemaColores["mystyles"] == True:
            self.mystylesPaletayqueso(i, "manzana")
            self.lineEdits[i].setStyleSheet("color: black") 
        vLayout = QVBoxLayout(self.vPanel_Widgets[i])
        vLayout.addWidget(self.labels[i])
        vLayout.addWidget(self.lineEdits[i])
        vLayout.addLayout(dial_layout_centering)
        vLayout.addLayout(slide_layout_centering)
        vLayout.addWidget(self.muteButtons[i])

        return self.vPanel_Widgets[i]

    #------------------------Barra de Menú de la app
    def crear_barra_menu(self):
        """ Crea la barra de menú. """
        # Barra de menú 
        self.menuBar = QMenuBar(self)   
        self.layout().setMenuBar(self.menuBar)
        # Establecer estilo para la barra de menú
        #self.menuBar.setStyleSheet("background-color: black; color: white;") # Ajusta el color de fondo y el color del texto de la barra de menú
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
           # Opción para configurar la escala del salto de volumen
        self.confEscala = QAction('Configurar Escala de Volúmen', self)
        self.confEscala.triggered.connect(self.en_construccion)
        self.menuConfiguracion.addAction(self.confEscala)
           # Submenu para configurar los Esquemas de Colores de la Aplicación
        self.coloresUI = self.menuConfiguracion.addMenu('Esquema de Colores')
           # Opciones de estilo
        self.miEstilo = QAction('Esquema Basado en Estilo del Creador', self)
        self.estiloOscuro = QAction('Esquema Estilo Oscuro qdarkstyle', self)
        self.miEstilo.triggered.connect(self.poneMipaleta)
        self.estiloOscuro.triggered.connect(self.ponePaletaoscura)
        self.coloresUI.addAction(self.miEstilo)
        self.coloresUI.addAction(self.estiloOscuro)

    #----------Verifica Niveles de Volumen de las Fuentes de Audio
    #----------y los refleja en los controles, tambien verifica si
    #----------la fuente esta silenciada o no y aplica estilos
    def volumen_inicial(self):
        for index, fuente in enumerate(self.fuentes):
            volumen = int(self.fuentes[index].volume.value_flat * 100)
            self.dials[index].setValue(volumen)
            self.sliders[index].setValue(volumen)
            if bool(self.fuentes[index].mute):
                self.muteButtons[index].setChecked(True)
                self.panel_off_style(index)
            else:
                self.muteButtons[index].setChecked(False)
                self.panel_on_style(index)

    #---Acción al Presionar el Boton Silenciar de cualquier Panel de Fuente de Audio
    def silenciar_fuente(self, index):
        if bool(self.fuentes[index].mute):
            self.pulse.sink_input_mute(self.fuentes[index].index, 0)
            self.panel_on_style(index)
        else:
            self.pulse.sink_input_mute(self.fuentes[index].index, 1)
            self.panel_off_style(index)
        #actualiza los estados
        self.fuentes = self.pulse.sink_input_list()
    
    #-------Configuracion de Estilos de los Paneles de las Fuentes de Audio
    def panel_on_style(self, index):
        self.labels[index].setStyleSheet("color: black; background-color: lightgreen;")
        self.dials[index].setDisabled(False)
        self.sliders[index].setDisabled(False)
        self.muteButtons[index].setText("Silenciar")
        self.muteButtons[index].setStyleSheet("color: black; background-color: gray;")
        if self.esquemaColores["mystyles"] == True:
            self.mystylesPaletayqueso(index, "on")
        if self.esquemaColores["paletaOscura"] == True:
            self.paletaOscura(index)

    def panel_off_style(self, index):
        self.labels[index].setStyleSheet("color: grey; background-color: red;")
        self.dials[index].setDisabled(True)
        self.sliders[index].setDisabled(True)
        self.muteButtons[index].setText("Restaurar")
        self.muteButtons[index].setStyleSheet("color: white; background-color: darkgray;")
        if self.esquemaColores["mystyles"] == True:
            self.mystylesPaletayqueso(index, "off")
        if self.esquemaColores["paletaOscura"] == True:
            self.paletaOscura(index)

    def mystylesPaletayqueso(self, index, estado_panel):
        self.vPanel_Widgets[index].setStyleSheet(f"background-color: {panel_colors[index]};")
        self.lineEdits[index].setStyleSheet("color: black")
        if estado_panel == "on":
            self.dials[index].setStyleSheet(dial_estilo_minimalista_on)
            self.sliders[index].setStyleSheet(slider_estilo_minimalista_on)
        if estado_panel == "off":
            self.sliders[index].setStyleSheet(slider_estilo_minimalista_off)

    def paletaOscura(self, index):
        app.setStyleSheet("")
        app.setStyle('Fusion')
        style = qdarkstyle.load_stylesheet(palette=DarkPalette)
        app.setStyleSheet(style)
        self.vPanel_Widgets[index].setStyleSheet(style)
        self.lineEdits[index].setStyleSheet(style)
        self.dials[index].setStyleSheet(style)
        self.sliders[index].setStyleSheet(style)
        self.sliders[index].setStyleSheet(slider_dimensiones)
        app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))

    def ponePaletaoscura(self):
        print("¿paleta oscura? qdarkstyle debería hacer todo por mí")
        self.esquemaColores={"mystyles": False, "paletaOscura": True}
        self.volumen_inicial()

    def poneMipaleta(self):
        self.esquemaColores={"mystyles": True, "paletaOscura": False}
        self.volumen_inicial()

    #------------Acción Volumen al Mover un dial o slider
    def actualizar_volumen(self, origen, index):
            if origen == "dial":
                nuevo_volumen = self.dials[index].value() / 100.0
                self.sliders[index].setValue(self.dials[index].value())
            if origen == "slide":
                nuevo_volumen = self.sliders[index].value() / 100.0
                self.dials[index].setValue(self.sliders[index].value())
            #se debe actualizar en ambos canales implementar volumen por canal!!!
            volumen_actual = self.fuentes[index].volume
            for i in range(len(volumen_actual.values)):
                volumen_actual.values[i] = nuevo_volumen
            self.pulse.volume_set(self.fuentes[index], volumen_actual)

    def actualizar_nombre_fuente(self, text, index):
        self.fuentes[index].name = text

    def actualizar_dinamicamente_fuentes_audio(self):
        """ Evalua cambios en las fuentes de audio y
        las actualiza dinamicamente... por ahora reiniciando la app 
        """
        evaluando = self.pulse.sink_input_list() 
        if len(self.fuentes) != len(evaluando):
            '''
            QMessageBox.information(self, "Aviso", f""" Se detectaron cambios en las fuentes de audio!
                Se debe reiniciar la applicación
                para conectar controladores
                de sonido en funcion de los
                cambios
            """)
            '''
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
        sys.stdout.flush()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def salir(self):
        """ Sale de la Aplicación. """
        sys.stdout.flush()
        self.close()
        app.exit()
        sys.exit(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    #app.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
    window = MiAppMixer()
    window.show()
    sys.exit(app.exec_())
