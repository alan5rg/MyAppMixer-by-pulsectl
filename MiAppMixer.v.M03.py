#!UTC/Encode to Python with Monkey Python Coddebuging Circus by Alan.R.G.Systemas
'''
En beta test... implementar mejoras:
*Evaluar candidad de fuentes de audio disponibles y ademas sus nombres.
*Volumen independiente por canal o con los canales linkeado.
*ver colores de etiquetas.
*llevar a una biblioteca externa lo que tenga que ver con los esquemas de colores

v.M03.120724.Se implementa localizacion de la ventanas principal inferior izquierda.
             Se mejora la experiencia del usuario agregando opciones a los mensajes.
             Se mejora la experiencia del usuario al agregar botones para la configuración
             de la actualización automática o no de fuentes de audio en el sistema.

v.M02.110724.Se corrige y define el estilo personalizado del Creador de los botones.
             Se implementa selección de color personalizado del fondo de los paneles.
             Se deshabilitan los botones de color personalizado de fondo en modo Dark.

v.M02.100724.Se Implementa Scroll Automatico de Labels de Entradas!
             Se Evita que la app inicie si no hay fuentes de Audio en el Sistema.
             Se Documenta, Depura, Resume y Minimiza el Código en Parte.
             Se Implementa menú de configuración/esquema de colores
'''
import sys, os
from functools import partial
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QMessageBox, QMenuBar, QLineEdit
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QDesktopWidget
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QSlider,  QDial, QAction, QColorDialog 
from PyQt5.QtCore import Qt, QTimer 
from pulsectl import Pulse
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette
#mis estilos y clases
from styles.mystyles import dial_estilo_minimalista_on, slider_estilo_minimalista_on, slider_estilo_minimalista_off, panel_colors, slider_dimensiones
from styles.mystyles import boton_color_miestilo
from clases.scrollinglabel import ScrollingLabel

class MiAppMixer(QMainWindow):
    def __init__(self, parent=None):
        super(MiAppMixer, self).__init__(parent)
        versionado = "v.M03.120724"
        self.usdtdir = "0x104948b1A1AaD3437328aDDcc0A2E5A2679D4192" #USDT ADDRESS FOR DONATIONS BEP20, POLYGON OR OPTIMISM NETWORKS
        
        # evaluamos el tamaño de tu monitor
        pantalla = QDesktopWidget().screenGeometry()
        self.anchopantalla = pantalla.width()
        self.altopantalla = pantalla.height()
        
        # Configuración de la ventana UI
        self.setWindowTitle("MiAppMixer "+ versionado)
        anchominimo=150
        altominimo=480
        self.setMinimumSize(anchominimo,altominimo)
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.IconPath = os.path.join(scriptDir, 'icons')   
        self.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))
        self.esquemaColores={"mystyles": True, "paletaOscura": False} # Mi Estilo/Estilo del Creador
        #self.esquemaColores={"mystyles": False, "paletaOscura": True}

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
        anchodinamico = 150 * len(self.fuentes)
        self.setMinimumWidth(150 * len(self.fuentes))
        # coloca la ventana del mixer en laparte inferior izquierda
        self.move(self.anchopantalla-anchodinamico,self.altopantalla-altominimo)
        
        # inicializa la actualizacion dinamica de fuentes de audio en True
        self.act_din_faudio = True

        # verifica existencia de fuentes de audio
        # mensaje solo para debug
        #if self.fuentes:
        #    QMessageBox.information(self, f"Fuentes de Audio {versionado}", f"Fuentes de Audio: {self.fuentes}")
        #else:
        if  len(self.fuentes) == 0:
            #self.move(int(self.ancho/2-self.width()/2),int(self.alto/2-self.height()/2))
            msg = QMessageBox(QMessageBox.Warning, "(!) Sin Fuentes de Audio Detectadas", """No se Detectaron Aplicaciones de Audio Activas.
Reproduce Audio para Controlar su Volumen.""")
            msg.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))
            # botones personalizados
            yes_button = QPushButton("Intentar de Nuevo")
            no_button = QPushButton("Salir")
            msg.addButton(yes_button, QMessageBox.YesRole)
            msg.addButton(no_button, QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_button:
                self.reiniciar_app()
            elif msg.clickedButton() == no_button:
                self.salir()

        # Botón Actuzalizar Fuentes de Audio
        self.btn_act_faudio = QPushButton("Actualizar Fuentes de Audio")
        self.btn_act_faudio.setDisabled(True) #el programa inicia en actualización automática
        if self.esquemaColores["mystyles"] == True:
            self.btn_act_faudio.setStyleSheet(boton_color_miestilo)
        
        self.btn_act_faudio.clicked.connect(partial(self.actualizar_dinamicamente_fuentes_audio, "manual"))
        layout_principal.addWidget(self.btn_act_faudio)

        #Boton actualizacion automatica de fuente de audio
        self.btn_act_din_faudio = QPushButton("Desactivar Actualización Dinámica")
        self.btn_act_din_faudio.setCheckable(True)
        self.btn_act_din_faudio.clicked.connect(self.actualizacion_dinamica_faudio)
        self.btn_act_din_faudio.setStyleSheet(boton_color_miestilo)
        layout_principal.addWidget(self.btn_act_din_faudio)

        # Ajusta la velocidad del scroll de las etiquetas de las fuentes de audio
        self.speedscroll = 150 #menor valor mayor velocidad

        # diccionarios de widgets de cada fuente
        self.vPanel_Widgets = {}
        self.colorButtons = {}
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

        # Actualizar dinamicamente la lista de fuentes de audio cada 10 segundos 
        self.timer = QTimer(self)
        self.timer.timeout.connect(partial(self.actualizar_dinamicamente_fuentes_audio, "auto"))
        self.timer.start(10000)

    def actualizacion_dinamica_faudio(self):
        if self.act_din_faudio:
            self.act_din_faudio = False
            self.btn_act_faudio.setDisabled(False)
        else:
            self.act_din_faudio = True
            self.btn_act_faudio.setDisabled(True)
        if self.btn_act_din_faudio.isChecked():
            self.btn_act_din_faudio.setText("Activar Actualización Dinámica")
        else:
            self.btn_act_din_faudio.setText("Desactivar Actualización Dinámica")

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
        self.colorButtons[i] = QPushButton("Color del Panel")
        
        self.labels[i] = ScrollingLabel(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'), self.speedscroll)
        self.lineEdits[i] = QLineEdit(fuente.proplist.get('application.name', 'Unknown') + " - " + fuente.proplist.get('media.name', 'Unknown'))
            
        self.dials[i] = QDial()
        self.dials[i].setFixedSize(70,70)
        self.dials[i].setRange(0, 100)
        
        self.sliders[i] = QSlider(Qt.Vertical, minimum=0, maximum=100)
        self.sliders[i].setMinimumWidth(100)
        self.muteButtons[i] = QPushButton("Silenciar")
        self.muteButtons[i].setCheckable(True)

        # Conectores
        self.colorButtons[i].clicked.connect(partial(self.colorFondopanel,i))
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
            self.colorButtons[i].setStyleSheet(boton_color_miestilo)
            self.muteButtons[i].setStyleSheet(boton_color_miestilo)
        vLayout = QVBoxLayout(self.vPanel_Widgets[i])
        vLayout.addWidget(self.colorButtons[i])
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
        if self.esquemaColores["mystyles"] == True:
            self.mystylesPaletayqueso(index, "on")
        if self.esquemaColores["paletaOscura"] == True:
            self.paletaOscura(index)

    def panel_off_style(self, index):
        self.labels[index].setStyleSheet("color: grey; background-color: red;")
        self.dials[index].setDisabled(True)
        self.sliders[index].setDisabled(True)
        self.muteButtons[index].setText("Restaurar")
        if self.esquemaColores["mystyles"] == True:
            self.mystylesPaletayqueso(index, "off")
        if self.esquemaColores["paletaOscura"] == True:
            self.paletaOscura(index)

    def mystylesPaletayqueso(self, index, estado_panel):
        self.vPanel_Widgets[index].setStyleSheet(f"background-color: {panel_colors[index]};")
        self.colorButtons[index].setStyleSheet(boton_color_miestilo)
        self.btn_act_faudio.setStyleSheet(boton_color_miestilo)
        self.btn_act_din_faudio.setStyleSheet(boton_color_miestilo)
        self.lineEdits[index].setStyleSheet("color: black")
        if estado_panel == "on":
            self.dials[index].setStyleSheet(dial_estilo_minimalista_on)
            self.sliders[index].setStyleSheet(slider_estilo_minimalista_on)
            self.muteButtons[index].setStyleSheet("color: black; background-color: gray;")
        if estado_panel == "off":
            self.sliders[index].setStyleSheet(slider_estilo_minimalista_off)
            self.muteButtons[index].setStyleSheet("color: white; background-color: darkgray;")

    def paletaOscura(self, index):
        style = qdarkstyle.load_stylesheet(palette=DarkPalette)
        app.setStyleSheet(style)
        self.btn_act_faudio.setStyleSheet(style)
        self.btn_act_din_faudio.setStyleSheet(style)
        self.vPanel_Widgets[index].setStyleSheet(style)
        self.colorButtons[index].setStyleSheet(style)
        self.muteButtons[index].setStyleSheet(style)
        self.lineEdits[index].setStyleSheet(style)
        self.dials[index].setStyleSheet(style)
        self.sliders[index].setStyleSheet(style)
        self.sliders[index].setStyleSheet(slider_dimensiones)
        app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))

    def ponePaletaoscura(self):
        self.esquemaColores={"mystyles": False, "paletaOscura": True}
        self.volumen_inicial()
        for i , fuentes in enumerate(self.fuentes):
            self.colorButtons[i].setDisabled(True)

    def poneMipaleta(self):
        self.esquemaColores={"mystyles": True, "paletaOscura": False}
        self.volumen_inicial()
        for i , fuentes in enumerate(self.fuentes):
            self.colorButtons[i].setDisabled(False)

    def colorFondopanel(self, index):
        index = int(index)
        if index >= len(panel_colors):
            panel_colors.append('#555753')
        colorSeleccionado = QColorDialog.getColor(QColor(panel_colors[index]), self, 'Color del Panel')
        if colorSeleccionado.isValid():
            panel_colors[index] = colorSeleccionado.name() #lo pasamos a hexa y lo guardamos
            self.vPanel_Widgets[index].setStyleSheet(f"background-color: {panel_colors[index]};")

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

    def actualizar_dinamicamente_fuentes_audio(self, origen):
        """ Evalua cambios en las fuentes de audio y
        las actualiza dinamicamente... por ahora reiniciando la app,
        pero al menos avisa,y el que avisa no traiciona!
        """
        evaluando = self.pulse.sink_input_list() 
        if len(self.fuentes) == len(evaluando) and origen == "manual":        
            #print("origen:",origen, "act.dinamica:",self.act_din_faudio)
            msg = QMessageBox(QMessageBox.Information, "Información...", f""" No se detectaron cambios en las fuentes de audio!
                
                Espere la actualización automática o vuelva
                a intentar más tarde...
            """)            
            msg.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))
            msg.exec_()
        if len(self.fuentes) != len(evaluando) and (self.act_din_faudio or origen=="manual"):
            #print("origen:",origen, "act.dinamica:",self.act_din_faudio)
            msg = QMessageBox(QMessageBox.Warning, "Alerta!", f""" Se detectaron cambios en las fuentes de audio!
                
                Se debe reiniciar la applicación para reconectar
                los controladores de sonido en funcion de dichos
                cambios.
                    Este mensaje volverá a aparecer cada diez
                segundos mientras la cantidad de fuentes de audio 
                difiera de la cantidad de paneles de control
                a menos que desactive la actualizacion dinámica
            """)
            msg.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))
            # botones personalizados
            yes_button = QPushButton("Ok, Reiniciar app")
            no_button = QPushButton("Ignorar por ahora...")
            msg.addButton(yes_button, QMessageBox.YesRole)
            msg.addButton(no_button, QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_button:
                print("Se presionó Reiniciar app")
                self.reiniciar_app()
            elif msg.clickedButton() == no_button:
                print("Se presionó Ignorar por ahora...")

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
