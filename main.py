import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
import webbrowser
import requests
from plyer import tts, stt

# CONFIGURACIÓN DE IA
GEMINI_API_KEY = "AIzaSyCxPZWWsjLv5HoZZZijr8cpN9F91pLyoek" 

class ChitoMobile(App):
    def build(self):
        self.always_listening = False
        self.keep_awake() # Evita que la pantalla se apague sola
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        self.status_label = Label(text="Chito Pro v1.1\nServicio de fondo activo", font_size='22sp', halign='center')
        layout.add_widget(self.status_label)
        
        self.mic_button = Button(text="HABLAR CON CHITO", size_hint=(1, 0.4))
        self.mic_button.bind(on_release=self.start_listening)
        layout.add_widget(self.mic_button)
        
        self.loop_button = Button(text="MODO SIEMPRE ACTIVO: OFF", size_hint=(1, 0.2))
        self.loop_button.bind(on_release=self.toggle_loop)
        layout.add_widget(self.loop_button)
        
        return layout

    def on_start(self):
        # EXCLUSIVO ANDROID: Arranca el servicio de escucha de fondo
        try:
            from jnius import autoclass
            # IMPORTANTE: El nombre del servicio debe coincidir con buildozer.spec
            # Kivy genera el nombre como: org.domain.appname.ServiceServicename
            Service = autoclass('org.alberto.chitoai.ServiceChitoservice')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            Service.start(mActivity, "")
            print("Servicio de fondo iniciado con éxito.")
        except Exception as e:
            print(f"No se pudo iniciar el servicio: {e}")

    def keep_awake(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity
            WindowManager = autoclass('android.view.WindowManager$LayoutParams')
            current_activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
        except: pass

    def toggle_loop(self, *args):
        self.always_listening = not self.always_listening
        self.loop_button.text = f"SIEMPRE ACTIVO: {'ON' if self.always_listening else 'OFF'}"
        if self.always_listening: self.start_listening()

    def talk(self, text):
        self.status_label.text = text
        try: tts.speak(text)
        except: pass
        if self.always_listening: Clock.schedule_once(self.start_listening, 4)

    def start_listening(self, *args):
        self.status_label.text = "Escuchando..."
        try:
            stt.start()
            Clock.schedule_once(self.check_results, 5)
        except: self.talk("Error de micro")

    def check_results(self, dt):
        if stt.results: self.process_command(stt.results[0].lower())
        elif self.always_listening: Clock.schedule_once(self.start_listening, 1)

    def process_command(self, command):
        # Comandos de Spotify
        if 'spotify' in command or 'música' in command:
            self.talk("Poniendo Spotify")
            webbrowser.open("spotify:")
            Clock.schedule_once(self.android_play_music, 4)
            return

        # Comandos de Radio
        if 'radio' in command or 'emisora' in command:
            estacion = command.replace('radio', '').replace('pon', '').strip()
            self.talk(f"Poniendo {estacion}")
            webbrowser.open(f"https://www.google.com/search?q=escuchar+{estacion}+en+directo")
            return

        self.talk(self.ask_ai(command))

    def android_play_music(self, dt):
        try:
            from jnius import autoclass
            KeyEvent = autoclass('android.view.KeyEvent')
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_MEDIA_BUTTON)
            intent.putExtra(Intent.EXTRA_KEY_EVENT, KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_MEDIA_PLAY))
            current_activity.sendOrderedBroadcast(intent, None)
            intent.putExtra(Intent.EXTRA_KEY_EVENT, KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_MEDIA_PLAY))
            current_activity.sendOrderedBroadcast(intent, None)
        except: pass

    def ask_ai(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            data = {"contents": [{"parts":[{"text": f"Responde breve en español: {prompt}"}]}]}
            response = requests.post(url, json=data, timeout=8)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except: return "Problema de conexión."

if __name__ == '__main__':
    ChitoMobile().run()
