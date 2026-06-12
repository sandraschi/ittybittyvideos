; roughcut NSIS hooks -- kill backend before install/uninstall
!macro KillFleetProcesses
  DetailPrint "Stopping roughcut processes..."
  ExecWait 'taskkill /F /IM roughcut-backend.exe /T' $0
  ExecWait 'taskkill /F /IM roughcut-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "roughcut-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "roughcut-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "roughcut-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "roughcut-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
