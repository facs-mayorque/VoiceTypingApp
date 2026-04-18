import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import speech_recognition as sr
import pyperclip
import winsound
import threading
import time
import os
import json
from groq import Groq

CONFIG_FILE = "voice_app_config.json"

class VoiceApp:
    def __init__(self):
        self.load_config()

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.root.configure(bg='magenta')

        self.window_width = 80
        self.window_height = 20
        self.update_window_position()

        self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height, bg='magenta', highlightthickness=0)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)

        self.num_bars = 7
        self.bar_width = 2
        self.bar_spacing = 2
        self.base_height = 4
        self.bars = []
        self.height_pattern = [6, 8, 14, 18, 14, 8, 6]

        total_width = (self.num_bars * self.bar_width) + ((self.num_bars - 1) * self.bar_spacing)
        start_x = (self.window_width / 2) - (total_width / 2)
        center_y = self.window_height / 2

        for i in range(self.num_bars):
            x1 = start_x + (i * (self.bar_width + self.bar_spacing))
            x2 = x1 + self.bar_width
            y1 = center_y - (self.base_height / 2)
            y2 = center_y + (self.base_height / 2)
            bar = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="")
            self.bars.append(bar)

        self.root.withdraw()

        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.running = True
        self.settings_window = None

        keyboard.add_hotkey('esc', self.quit_app)
        keyboard.add_hotkey('ctrl+shift+c', lambda: self.root.after(0, self.open_settings))

        threading.Thread(target=self.key_monitor_loop, daemon=True).start()

        self.root.after(100, self.check_initial_setup)

    def load_config(self):
        self.config = {
            "api_key": "",
            "pos_x": None,
            "pos_y": None
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def update_window_position(self):
        if self.config["pos_x"] is None or self.config["pos_y"] is None:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.config["pos_x"] = int((screen_width / 2) - (self.window_width / 2))
            self.config["pos_y"] = screen_height - self.window_height - 90

        self.root.geometry(f'{self.window_width}x{self.window_height}+{self.config["pos_x"]}+{self.config["pos_y"]}')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.config["pos_x"] = self.root.winfo_x()
        self.config["pos_y"] = self.root.winfo_y()
        self.save_config()

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def check_initial_setup(self):
        if not self.config["api_key"]:
            self.open_settings()

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Configuración - Voice App")
        self.settings_window.geometry("300x180")
        self.settings_window.configure(bg="#f0f0f0")
        self.settings_window.attributes("-topmost", True)

        tk.Label(self.settings_window, text="⚙️ Configuración", font=("Segoe UI", 12, "bold"), bg="#f0f0f0").pack(pady=10)

        tk.Label(self.settings_window, text="Groq API Key:", bg="#f0f0f0", font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        api_entry = tk.Entry(self.settings_window, width=35, show="*")
        api_entry.insert(0, self.config["api_key"])
        api_entry.pack(padx=20, pady=5)

        def save_and_close():
            new_api = api_entry.get().strip()
            if not new_api:
                messagebox.showerror("Error", "La API Key es obligatoria.")
                return

            self.config["api_key"] = new_api
            self.save_config()
            self.groq_client = Groq(api_key=self.config["api_key"])

            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
            self.settings_window.destroy()

        tk.Button(self.settings_window, text="Guardar Cambios", command=save_and_close, bg="#007AFF", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5).pack(pady=15)

    def play_beep(self, start=True):
        freq = 1500 if start else 1000
        threading.Thread(target=winsound.Beep, args=(freq, 150), daemon=True).start()

    def key_monitor_loop(self):
        while self.running:
            is_holding = keyboard.is_pressed('ctrl') and keyboard.is_pressed('space')

            if is_holding and not self.is_listening:
                self.start_recording()
            elif not is_holding and self.is_listening:
                self.stop_recording()

            time.sleep(0.05)

    def update_ui(self, mode="listening"):
        if mode == "listening":
            self.root.deiconify()
            self.root.lift()
        elif mode in ["processing", "hidden"]:
            self.stop_animation()
            self.root.withdraw()

    def animate_bars(self):
        if not self.is_listening:
            return

        center_y = self.window_height / 2
        for i in range(self.num_bars):
            h = self.height_pattern[i]
            y1 = center_y - (h / 2)
            y2 = center_y + (h / 2)
            coords = self.canvas.coords(self.bars[i])
            self.canvas.coords(self.bars[i], coords[0], y1, coords[2], y2)

        self.height_pattern.append(self.height_pattern.pop(0))
        self.root.after(70, self.animate_bars)

    def stop_animation(self):
        center_y = self.window_height / 2
        for i in range(self.num_bars):
            y1 = center_y - (self.base_height / 2)
            y2 = center_y + (self.base_height / 2)
            coords = self.canvas.coords(self.bars[i])
            self.canvas.coords(self.bars[i], coords[0], y1, coords[2], y2)

    def start_recording(self):
        if not self.config.get("api_key"):
            self.root.after(0, self.open_settings)
            return

        self.is_listening = True
        self.play_beep(start=True)
        self.root.after(0, self.update_ui, "listening")
        self.root.after(0, self.animate_bars)

        self.audio_frames = []
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()

    def audio_capture_thread(self):
        try:
            with sr.Microphone() as source:
                self.sample_rate = source.SAMPLE_RATE
                self.sample_width = source.SAMPLE_WIDTH

                while self.is_listening:
                    buffer = source.stream.read(source.CHUNK)
                    self.audio_frames.append(buffer)
        except Exception as e:
            print(f"Error de audio: {e}")
            self.is_listening = False

    def stop_recording(self):
        if not self.is_listening:
            return
        self.is_listening = False
        self.play_beep(start=False)
        self.root.after(0, self.update_ui, "processing")
        threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        if not hasattr(self, 'audio_frames') or not self.audio_frames:
            self.root.after(0, self.update_ui, "hidden")
            return

        raw_audio_data = b''.join(self.audio_frames)

        try:
            if not hasattr(self, 'groq_client'):
                self.groq_client = Groq(api_key=self.config["api_key"])

            audio_obj = sr.AudioData(raw_audio_data, self.sample_rate, self.sample_width)
            wav_bytes = audio_obj.get_wav_data()

            transcription = self.groq_client.audio.transcriptions.create(
                file=("audio.wav", wav_bytes),
                model="whisper-large-v3",
                response_format="text",
                language="es"
            )
            raw_text = transcription.strip()

            if not raw_text:
                raise Exception("Audio vacío o incomprensible")

            system_prompt = """ERES UN MOTOR DE TRANSCRIPCIÓN Y FORMATEO. TIENES ESTRICTAMENTE PROHIBIDO CONVERSAR O RESPONDER AL USUARIO.

Tu única función es tomar el texto crudo y devolverlo con la puntuación y estructura perfectas.

REGLAS ABSOLUTAS:
1. PUNTUACIÓN Y ORTOGRAFÍA: Mantén las palabras exactas del usuario, pero corrige la ortografía, añade comas, puntos y usa signos de interrogación/exclamación (¿? / ¡!) si el contexto lo requiere.
2. COMANDOS DE PUNTUACIÓN: Si el usuario dice explícitamente la palabra "coma" escribe ",", si dice "punto" escribe ".", si dice "punto y aparte", escribe un punto y haz un doble salto de línea (\n\n).
3. DETECCIÓN INTELIGENTE DE LISTAS: Analiza la estructura de lo que dice el usuario. Si notas que está dictando una secuencia, elementos sueltos o una enumeración (ej: si dice "primero...", "segundo...", "por otro lado", "el punto uno es..."), organízalo automáticamente utilizando viñetas (bullet points) o listas numeradas. Dale un formato visualmente limpio.
4. DEVUELVE ÚNICA Y EXCLUSIVAMENTE EL TEXTO FINAL. Cero introducciones, cero explicaciones, cero confirmaciones."""

            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.1
            )

            final_text = completion.choices[0].message.content.strip()

            pyperclip.copy(final_text)
            time.sleep(0.05)
            keyboard.send('ctrl+v')

        except Exception as e:
            print(f"Error al procesar: {e}")

        self.root.after(0, self.update_ui, "hidden")

    def quit_app(self):
        self.running = False
        self.is_listening = False
        self.root.destroy()
        os._exit(0)

    def run(self):
        print("VoiceTypingApp iniciada.")
        print("- Ctrl + Espacio: dictar")
        print("- Ctrl + Shift + C: configuración")
        print("- ESC: salir")
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceApp()
    app.run()
