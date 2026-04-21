[app]
title = Chito AI
package.name = chitoai
package.domain = org.alberto
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1.0

# Requerimientos optimizados (Sin google-genai para evitar errores de Código 1)
requirements = python3,kivy,plyer,requests,urllib3,pyjnius,openssl,certifi,chardet,idna

orientation = portrait
fullscreen = 0

# PERMISOS CRÍTICOS PARA ASISTENTE DE VOZ
android.permissions = INTERNET, RECORD_AUDIO, FOREGROUND_SERVICE, WAKE_LOCK, CALL_PHONE, VIBRATE, MODIFY_AUDIO_SETTINGS

# SERVICIOS DE FONDO (Esto permite que Chito viva cuando cierras la app)
services = ChitoService:service.py

# Versión de Android soportada (API 31 es necesaria para servicios de fondo modernos)
android.api = 31
android.minapi = 21
android.sdk = 31

# Icono y Presplash (Puedes cambiarlos después con tus imágenes)
# android.presplash_color = #0D0D1A

[buildozer]
log_level = 2
warn_on_root = 1
