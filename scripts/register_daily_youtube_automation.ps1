# register_daily_youtube_automation.ps1
# Registers daily autonomous Moving-Toon 3-episode staggered upload & Community/Shorts manager at 05:50 KST
$ErrorActionPreference = "Stop"
$TaskName = "DreamCompany_Div4_Daily_MovingToon_YouTube"
$BatPath = "D:\드림컴퍼니\4사업부\scripts\run_daily_youtube_moving_toon.bat"

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatPath`"" -WorkingDirectory "D:\드림컴퍼니\4사업부"
$Trigger = New-ScheduledTaskTrigger -Daily -At "05:50AM"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "4사업부 (@김쌤의영웅라디오) 기념사진관 캐릭터 순정 영상툰 일일 3편 시간차 예약 업로드 및 커뮤니티/숏츠 자동 관리" -Force | Out-Null
Write-Output "[OK] Registered Windows Scheduled Task: $TaskName (Daily 05:50 AM -> schedules 07:30 / 12:30 / 19:30 KST)"
