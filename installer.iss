[Setup]
; Información básica de la app
AppName=VoiceTypingApp
AppVersion=1.0
AppPublisher=Facu
DefaultDirName={autopf}\VoiceTypingApp
DefaultGroupName=VoiceTypingApp
OutputDir=installer_output
OutputBaseFilename=Instalar_VoiceTypingApp
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\icon.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; Damos permisos de escritura al usuario en la carpeta de instalación 
; para que pueda guardar el archivo "voice_app_config.json" correctamente.
Name: "{app}"; Permissions: users-modify

[Files]
; IMPORTANTE: Esta ruta asume que primero compilaste el proyecto con pyinstaller
; y el archivo ejecutable resultante se llama "VoiceTypingApp.exe" dentro de la carpeta "dist\"
Source: "dist\VoiceTypingApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Añade un ícono en el Menú Inicio
Name: "{group}\VoiceTypingApp"; Filename: "{app}\VoiceTypingApp.exe"
; Añade un ícono en el Escritorio (si el usuario tilda la opción)
Name: "{commondesktop}\VoiceTypingApp"; Filename: "{app}\VoiceTypingApp.exe"; Tasks: desktopicon

[Run]
; Permite abrir la app automáticamente justo al terminar de instalar
Filename: "{app}\VoiceTypingApp.exe"; Description: "{cm:LaunchProgram,VoiceTypingApp}"; Flags: nowait postinstall skipifsilent
