@echo off
chcp 65001 >nul
title STEP Dosyasi Cikarici ve Ag Guvenlik Kurulumu

set "EXE_PATH=%~dp0StepExtractor.exe"
set "ICON_PATH=%~dp0app_icon.ico"

if not exist "%EXE_PATH%" (
    echo [HATA] StepExtractor.exe bulunamadi!
    pause
    exit /b 1
)

echo ========================================================
echo   STEP Cikarici ve Ag Guvenlik Yapilandirmasi
echo ========================================================
echo.

:: 1. Coklu secim limitini (15 dosya sinirini) kaldir
echo [1/4] Windows coklu dosya secim limiti (15 dosya) artiriliyor...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer" /v "MultipleInvokePromptMinimum" /t REG_DWORD /d 1000 /f >nul

:: 2. Sag tik menusu: STEP Dosyasini Cikar (Tum dosyalar ve PDF ozel)
echo [2/4] STEP Dosyasi Cikarici sag tik menusune ekleniyor...
reg add "HKCU\Software\Classes\*\shell\StepExtractor" /ve /t REG_SZ /d "STEP Dosyasını Çıkar" /f >nul
reg add "HKCU\Software\Classes\*\shell\StepExtractor" /v "Icon" /t REG_SZ /d "\"%EXE_PATH%\"" /f >nul
reg add "HKCU\Software\Classes\*\shell\StepExtractor" /v "MultiSelectModel" /t REG_SZ /d "Document" /f >nul
reg add "HKCU\Software\Classes\*\shell\StepExtractor\command" /ve /t REG_SZ /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

reg add "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor" /ve /t REG_SZ /d "STEP Dosyasını Çıkar" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor" /v "Icon" /t REG_SZ /d "\"%EXE_PATH%\"" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor" /v "MultiSelectModel" /t REG_SZ /d "Document" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor\command" /ve /t REG_SZ /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

:: 3. Yerel Ag Guvenlik Ayarlari
echo [3/4] Yerel ag guvenli bolgeye ekleniyor...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap" /v "UNCAsIntranet" /t REG_DWORD /d 1 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap" /v "AutoDetect" /t REG_DWORD /d 0 /f >nul

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range1" /v ":Range" /t REG_SZ /d "192.168.*.*" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range1" /v "*" /t REG_DWORD /d 1 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range1" /v "file" /t REG_DWORD /d 1 /f >nul

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range2" /v ":Range" /t REG_SZ /d "10.*.*.*" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range2" /v "*" /t REG_DWORD /d 1 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range2" /v "file" /t REG_DWORD /d 1 /f >nul

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range3" /v ":Range" /t REG_SZ /d "192.168.12.10" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range3" /v "*" /t REG_DWORD /d 1 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range3" /v "file" /t REG_DWORD /d 1 /f >nul

:: 4. Klasor sag tik menusune Dosya Kilitlerini Kaldir ekleme
echo [4/4] Klasor sag tik menusune Dosya Kilitlerini Kaldir ekleniyor...
reg add "HKCU\Software\Classes\Directory\shell\UnblockFolderFiles" /ve /t REG_SZ /d "Klasördeki Dosya Kilitlerini Kaldır" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\UnblockFolderFiles\command" /ve /t REG_SZ /d "powershell.exe -WindowStyle Hidden -NoProfile -Command \"Get-ChildItem -LiteralPath '%%1' -Recurse -Force ^| Unblock-File\"" /f >nul

reg add "HKCU\Software\Classes\Directory\Background\shell\UnblockFolderFiles" /ve /t REG_SZ /d "Bu Klasördeki Dosya Kilitlerini Kaldır" /f >nul
reg add "HKCU\Software\Classes\Directory\Background\shell\UnblockFolderFiles\command" /ve /t REG_SZ /d "powershell.exe -WindowStyle Hidden -NoProfile -Command \"Get-ChildItem -LiteralPath '%%V' -Recurse -Force ^| Unblock-File\"" /f >nul

:: Bilgi
echo.
echo Ayarlar basariyla kaydedildi.

echo.
echo ========================================================
echo   KURULUM BASARIYLA TAMAMLANDI!
echo ========================================================
echo.
echo 1. Coklu secim limiti (15 dosya) kaldirildi (1000 dosyaya cikarildi).
echo 2. STEP Dosyasini Cikar sag tik menusune eklendi.
echo 3. Sirket ici yerel ag (192.168.x.x) guvenli ag yapildi.
echo 4. Herhangi bir klasore sag tiklayip "Klasordeki Dosya
echo    Kilitlerini Kaldir" diyerek kilitleri acabilirsiniz.
echo.
echo ========================================================
echo.
pause
