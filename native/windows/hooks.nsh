; ittybitty NSIS hooks -- kill backend before install/uninstall
!macro KillFleetProcesses
  DetailPrint "Stopping ittybitty processes..."
  ExecWait 'taskkill /F /IM ittybitty-backend.exe /T' $0
  ExecWait 'taskkill /F /IM ittybitty-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "ittybitty-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "ittybitty-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "ittybitty-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "ittybitty-native.exe"
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
