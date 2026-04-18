# VoiceTypingApp (MacOS Style for Windows)

Asistente de dictado minimalista con inteligencia artificial que formatea texto, detecta preguntas y organiza listas/viñetas automáticamente. Inspirado en la estética de Apple, vive como una onda animada flotante en tu pantalla.

## Características

- **Transcripción en tiempo real** con Whisper Large v3 (Groq)
- **Formateo inteligente** con Llama 3.3-70b: puntuación, listas, viñetas automáticas
- **Interfaz minimalista** tipo Pure-Wave, sin bordes, transparente
- **Arrastrable**: reposicioná la onda donde quieras, la posición se guarda
- **Sin consola**: funciona silenciosamente en segundo plano

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal |
| Groq API (Whisper-large-v3) | Transcripción de voz a texto |
| Groq API (Llama-3.3-70b) | Formateo y corrección del texto |
| Tkinter | Interfaz gráfica flotante |
| keyboard | Atajos globales del sistema |
| SpeechRecognition | Captura de audio del micrófono |
| pyperclip | Portapapeles (copiar y pegar) |

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/VoiceTypingApp.git
cd VoiceTypingApp

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python src/main.py
```

## Configuración

Al iniciar por primera vez, la app pedirá tu **Groq API Key**.

- Obtené tu clave gratis en: https://console.groq.com
- También podés abrirla en cualquier momento con `Ctrl + Shift + C`

La clave se guarda localmente en `voice_app_config.json` (no se sube a GitHub).

## Uso

| Atajo | Acción |
|---|---|
| `Ctrl + Espacio` (mantener) | Dictar — soltá para procesar |
| `Ctrl + Shift + C` | Abrir configuración |
| `ESC` | Cerrar la aplicación |

El texto transcrito y formateado se pega automáticamente donde tengas el cursor.

## Compilar a .exe (Windows)

```bash
pyinstaller --noconsole --onefile src/main.py --name VoiceTypingApp
```

El ejecutable quedará en la carpeta `dist/`.

## Estructura del Proyecto

```
VoiceTypingApp/
├── src/
│   └── main.py          # Código fuente principal
├── .gitignore
├── requirements.txt
└── README.md
```

## Notas de Seguridad

El archivo `voice_app_config.json` (donde se guarda tu API Key) está incluido en `.gitignore` y **nunca se sube al repositorio**.
