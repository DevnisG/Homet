@echo off

powershell -command "Invoke-WebRequest -Uri http://localhost:5123/api/hardware/off -Method POST"

timeout /t 3

powershell -command "Stop-Process -Name LHM -Force"

exit

