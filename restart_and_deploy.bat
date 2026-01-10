@echo off
echo ============================================================
echo RESTART REMINDER
echo ============================================================
echo.
echo Docker Desktop has been installed successfully!
echo.
echo IMPORTANT: You must RESTART your computer for Docker to work.
echo.
echo After restart:
echo   1. Docker Desktop will auto-start
echo   2. Open PowerShell in this directory
echo   3. Run: .\deploy.ps1
echo   4. Dashboard will open at http://localhost:8501
echo.
echo ============================================================
echo.
echo Press any key to open the POST_RESTART.md guide...
pause >nul
start POST_RESTART.md
echo.
echo Ready to restart? Press any key when you're ready...
pause >nul
shutdown /r /t 60 /c "Restarting for Docker Desktop installation. You have 60 seconds to save your work."
echo.
echo Restart scheduled in 60 seconds. Save your work!
echo To cancel: shutdown /a
echo.
pause
