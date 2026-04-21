import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import webbrowser
import requests
import json
from plyer import tts, stt

# CONFIGURACIÓN DE IA (GEMINI DIRECTO)
GEMINI_API_KEY = "AIzaSyCxPZWWsjLv5HoZZZijr8cpN9F91pLyoek" 

class ChitoMobile(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.status_label = Label(text="Hola, soy Chito. Pulsa para hablar.", font_size='20sp')
        layout.add_widget(self.status_label)
        self.mic_button = Button(text="Hablar con Chito", size_hint=(1, 0.3))
        self.mic_button.bind(on_release=self.start_listening)
        layout.add_widget(self.mic_button)
        return layout

    def talk(self, text):
        self.status_label.text = text
        try: tts.speak(text)
        except: pass

    def start_listening(self, *args):
        self.status_label.text = "Escuchando..."
        try:
            stt.start()
            Clock.schedule_once(self.check_results, 4)
        except: self.talk("Error de micro")

    def check_results(self, dt):
        if stt.results: self.process_command(stt.results[0].lower())
        else: self.talk("No te oí")

    def ask_ai(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts":[{"text": f"Eres Chito, un asistente breve y amable. Responde a: {prompt}"}]}]}
            response = requests.post(url, headers=headers, json=data)
            return response.json()['choices'][0]['message']['content'] # O similar según la API
        except: return "Error de conexión con mi cerebro."

    def process_command(self, command):
        if 'spotify' in command or 'música' in command:
            self.talk("Abriendo Spotify")
            webbrowser.open("spotify:")
        elif 'llama' in command:
            self.talk("Llamando...")
            webbrowser.open("tel:636769415")
        else:
            self.talk(self.ask_ai(command))

if __name__ == '__main__':
    ChitoMobile().run()
