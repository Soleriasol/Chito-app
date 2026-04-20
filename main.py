import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
import webbrowser
import time
import random
from plyer import tts, stt
from google import genai
from google.genai import types

# CONFIGURACIÓN DE IA (GEMINI)
GEMINI_API_KEY = "AIzaSyCxPZWWsjLv5HoZZZijr8cpN9F91pLyoek" 
client = genai.Client(api_key=GEMINI_API_KEY)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.1, 0.6, 0.8, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

class ChitoMobile(App):
    def build(self):
        self.title = 'Chito Assistant'
        Window.clearcolor = (0.05, 0.05, 0.1, 1) # Fondo oscuro premium
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        # Header / Status
        self.status_label = Label(
            text="Hola, soy Chito\n¿En qué puedo ayudarte?", 
            font_size='22sp', 
            halign='center',
            color=(0.9, 0.9, 1, 1),
            line_height=1.2
        )
        layout.add_widget(self.status_label)
        
        # Main Microphone Button
        self.mic_button = RoundedButton(
            text="HABLAR CON CHITO",
            size_hint=(1, 0.4),
            font_size='24sp',
            bold=True
        )
        self.mic_button.bind(on_release=self.start_listening)
        layout.add_widget(self.mic_button)
        
        # Footer
        footer = Label(
            text="Asistente Personal Inteligente",
            font_size='12sp',
            color=(0.4, 0.4, 0.6, 1),
            size_hint_y=None,
            height=40
        )
        layout.add_widget(footer)
        
        return layout

    def talk(self, text):
        print(f"Chito: {text}")
        self.status_label.text = text
        try:
            tts.speak(text)
        except Exception as e:
            print(f"Error TTS: {e}")

    def start_listening(self, *args):
        self.status_label.text = "Escuchando...\n(Habla ahora)"
        self.mic_button.disabled = True
        try:
            stt.start()
            # Intentamos verificar resultados cada segundo durante un máximo de 7 segundos
            self.stt_attempts = 0
            Clock.schedule_interval(self.check_stt_polling, 1.0)
        except Exception as e:
            self.talk("No he podido activar el micrófono.")
            self.mic_button.disabled = False

    def check_stt_polling(self, dt):
        self.stt_attempts += 1
        results = stt.results
        
        if results:
            # Tenemos resultados, paramos el polling
            command = results[0].lower()
            Clock.unschedule(self.check_stt_polling)
            self.mic_button.disabled = False
            self.process_command(command)
            return False # Detiene el intervalo
        
        if self.stt_attempts >= 8: # Timeout
            Clock.unschedule(self.check_stt_polling)
            self.mic_button.disabled = False
            self.talk("No te he escuchado bien.")
            return False
            
        return True # Continúa el intervalo

    def ask_ai(self, prompt):
        try:
            system_prompt = (
                "Eres Chito, un asistente personal móvil cercano. "
                "Tus respuestas deben ser breves, naturales y sin markdown. "
                "Responde como si estuviéramos hablando en persona."
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    # Actualizado según verify_search_genai.py
                    tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]
                )
            )
            return response.text.replace("*", "").strip()
        except Exception as e:
            print(f"Error IA: {e}")
            return "Perdona, mi cerebro está desconectado ahora mismo."

    def process_command(self, command):
        print(f"Usuario: {command}")
        
        # Lista completa de contactos sincronizada
        contacts = {
            "Mamá": "+34636769415",
            "Papá": "+34680511331",
            "Mi niña": "+34666486471",
            "Alansio": "+34690906807",
            "Alicia": "+34600713634",
            "Oso": "+34650443200",
            "Soler": "+34659712796",
            "Oliva": "+34686656233",
            "Abuela": "+34390172663",
            "Abuelo": "+34617250062",
            "cristian": "+34641334097",
            "Javier": "+34640828440"
        }

        # Lógica de WhatsApp (Android Intent)
        if any(word in command for word in ['mensaje', 'whatsapp', 'escribe', 'wasap']):
            for name, number in contacts.items():
                if name.lower() in command:
                    self.talk(f"Abriendo WhatsApp para {name}")
                    webbrowser.open(f"whatsapp://send?phone={number}")
                    return

        # Lógica de Llamada (Android Intent)
        if any(word in command for word in ['llama', 'llamada', 'teléfono']):
            for name, number in contacts.items():
                if name.lower() in command:
                    self.talk(f"Llamando a {name}")
                    webbrowser.open(f"tel:{number}")
                    return

        # Lógica de Spotify
        if any(word in command for word in ['spotify', 'música', 'reproduce', 'pon', 'escuchar']):
            query = ""
            for word in ['pon la canción', 'pon el álbum', 'pon', 'busca', 'reproduce', 'escuchar']:
                if word in command:
                    potential_query = command.split(word)[-1].strip()
                    if potential_query and potential_query not in ['música', 'canción']:
                        query = potential_query
                        break
            
            if query:
                self.talk(f"Buscando {query} en Spotify.")
                self.android_search_spotify(query)
            else:
                self.talk("Abriendo Spotify y dándole al play.")
                webbrowser.open("spotify:")
                Clock.schedule_once(lambda dt: self.android_play_music(), 4)
            return

        # Si no es un comando directo, IA (Gemini)
        respuesta = self.ask_ai(command)
        self.talk(respuesta)

    def android_play_music(self):
        try:
            from jnius import autoclass
            KeyEvent = autoclass('android.view.KeyEvent')
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity
            
            # Media Button Intent para Play
            intent = Intent(Intent.ACTION_MEDIA_BUTTON)
            
            # Press
            ev_down = KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_MEDIA_PLAY)
            intent.putExtra(Intent.EXTRA_KEY_EVENT, ev_down)
            current_activity.sendOrderedBroadcast(intent, None)
            
            # Release
            ev_up = KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_MEDIA_PLAY)
            intent.putExtra(Intent.EXTRA_KEY_EVENT, ev_up)
            current_activity.sendOrderedBroadcast(intent, None)
        except:
            print("No es Android o falta jnius")

    def android_search_spotify(self, query):
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity

            intent = Intent(MediaStore.INTENT_ACTION_MEDIA_PLAY_FROM_SEARCH)
            intent.putExtra(MediaStore.EXTRA_MEDIA_FOCUS, "vnd.android.cursor.item/*")
            intent.putExtra(MediaStore.QUERY, query)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            current_activity.startActivity(intent)
        except:
            webbrowser.open(f"spotify:search:{query}")

if __name__ == '__main__':
    ChitoMobile().run()
