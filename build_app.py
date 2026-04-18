import subprocess
import sys

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    "--name", "VoiceTypingApp",
    "src/main.py"
]

subprocess.run(cmd, check=True)
print("\nCompilación completada. El ejecutable está en la carpeta dist/")
