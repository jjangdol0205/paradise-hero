@echo off
chcp 65001 >nul
cd /d "D:\드림컴퍼니\4사업부"
echo [%DATE% %TIME%] Starting Div4 Daily 19:30 KST Senior Radio Shorts & Naver Clip Pipeline... >> "D:\드림컴퍼니\4사업부\output\daily_automation.log"
python -u "D:\드림컴퍼니\4사업부\scripts\auto_youtube_moving_toon_manager.py" --count 1 >> "D:\드림컴퍼니\4사업부\output\daily_automation.log" 2>&1
echo [%DATE% %TIME%] Completed with exit code %ERRORLEVEL% >> "D:\드림컴퍼니\4사업부\output\daily_automation.log"
