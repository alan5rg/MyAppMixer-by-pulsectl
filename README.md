Versiones:

v.M03.120724.Se implementa localizacion de la ventanas principal inferior izquierda.
             Se mejora la experiencia del usuario agregando opciones a los mensajes.
             Se mejora la experiencia del usuario al agregar botones para la configuración
             de la actualización automática o no de fuentes de audio en el sistema.

v.M02.110724.Se corrige y define el estilo personalizado del Creador de los botones.
             Se implementa selección de color personalizado del fondo de los paneles.
             Se deshabilitan los botones de color personalizado de fondo en modo Dark.

v.M02.100724.Se Implementa Scroll Automático de Labels de Entradas!
             Se Evita que la app inicie si no hay fuentes de Audio en el Sistema.
             Se Documenta, Depura, Resume y Minimiza el Código en Parte.
             Se Implementa menú de configuración/esquema de colores

-----------------------

Funcionalidad Principal:

Controlar el volumen de todas las fuentes de audio disponibles en el sistema
mediante paneles independientes en una app minimalista.


Funcionalidades:

Enumera las fuentes de audio disponibles (aplicaciones que utilizan audio).

Crea paneles para cada fuente con:
  Etiqueta (nombre de la fuente).
  Campo de texto editable (para cambiar el nombre de las fuentes).
  Controles de dial y deslizador para ajustar el volumen.
  Botón de silencio.

Actualiza los niveles de volumen en función de la interacción del usuario (diales, deslizadores, silencio).

Actualiza los nombres de las fuentes en función de la entrada del usuario en el campo de texto.

Actualiza la lista de fuentes periódicamente (actualmente mediante el reinicio de la aplicación).

Proporciona una barra de menú con opciones para:
  Ayuda (actualmente en construcción).
  Donar (muestra un mensaje de donación).
  Reiniciar (reinicia la aplicación).
  Salir (cierra la aplicación).
