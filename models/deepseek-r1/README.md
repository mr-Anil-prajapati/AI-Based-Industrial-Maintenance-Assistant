# Embedded Model Directory

Place the Windows-packaged GGUF model for the assistant here before building the installer.

Expected filename:

- `deepseek-r1-8b-q4.gguf`

The PyInstaller and Inno Setup packaging flow includes everything in this folder so the application can run offline without requiring Ollama or any network access.
