panel_colors = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#FFCCFF', '#CCFFFF', '#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#FFCCFF', '#CCFFFF']  # Colores para los paneles

dial_estilo_minimalista_on = ("""
            QDial {
                background-color: #346792;
                border: 2px solid #5c5c5c;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
            QDial::handle {
                background-color: blue;
                border: 1px solid #5c5c5c;
                width: 16px; /* Ajusta el tamaño del handle */
                height: 16px;
                border-radius: 8px; /* Para hacer el handle circular */
                margin: -8px; /* Asegúrate de centrar el handle */
            }
            QDial::groove {
                background: green;
                border: 1px solid #5c5c5c;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
            QDial::chunk {
                background: red;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
        """)

slider_estilo_minimalista_on = ("""
            QSlider::groove:vertical {
                background: #f0f0f0;
                width: 40px;
            }
            QSlider::handle:vertical {
                background: #9da9b5;
                border: 1px solid #19232d;
                height: 10px;
                margin: 0 -5px; /* Expand handle width outside the groove */
                border-radius: 4px; /* Half of the width/height to make it circular */
            }
            QSlider::sub-page:vertical {
                background: #455364;
            }
            QSlider::add-page:vertical {
                background: #346792;
            }
            QSlider::tick:vertical {
                background: black; /* Color de los ticks */
                width: 2px;
                height: 2px;
            }
        """)

slider_estilo_minimalista_off = ("""
            QSlider::groove:vertical {
                background: #f0f0f0;
                width: 40px;
            }
            QSlider::handle:vertical {
                background: #455364;
                border: 1px solid #5c5c5c;
                height: 10px;
                margin: 0 -5px; /* Expand handle width outside the groove */
                border-radius: 4px; /* Half of the width/height to make it circular */
            }
            QSlider::sub-page:vertical {
                background: #455364;
            }
            QSlider::add-page:vertical {
                background: #455364;
            }
            QSlider::tick:vertical {
                background: black; /* Color de los ticks */
                width: 2px;
                height: 2px;
            }
        """)

slider_dimensiones = ("""
            QSlider::groove:vertical {
                width: 40px;
            }
            QSlider::handle:vertical {
                height: 10px;
                margin: 0 -5px; /* Expand handle width outside the groove */
                border-radius: 4px; /* Half of the width/height to make it circular */
            }
            QSlider::tick:vertical {
                width: 2px;
                height: 2px;
            }
        """)