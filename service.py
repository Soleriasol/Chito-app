from time import sleep
from jnius import autoclass
from plyer import tts

# Este archivo no tiene botones, solo lógica de fondo
def background_listener():
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService
    
    # Notificación permanente (Obligatoria para que Android no nos mate)
    notification = autoclass('android.app.Notification$Builder')
    # ... (Configuración de notificación simplificada)
    
    print("CHITO: Servicio de fondo iniciado.")
    
    while True:
        # Aquí es donde pondríamos el motor de escucha constante
        # Por ahora, simplemente mantenemos el proceso vivo
        sleep(1)

if __name__ == '__main__':
    background_listener()
