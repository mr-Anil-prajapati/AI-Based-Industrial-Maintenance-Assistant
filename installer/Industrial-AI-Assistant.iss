#define MyAppName "Industrial AI Maintenance Assistant"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Industrial AI Assistant"
#define MyAppExeName "IndustrialAIAssistant.exe"

[Setup]
AppId={{F5938D3D-8E62-4E7D-8B40-4D526B4BC4D7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Industrial AI Maintenance Assistant
DefaultGroupName={#MyAppName}
OutputDir=..\build\installer
OutputBaseFilename=Industrial-AI-Assistant-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\IndustrialAIAssistant\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
