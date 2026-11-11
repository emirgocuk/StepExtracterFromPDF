@echo off
chcp 65001 >nul
title STEP Dosyası Çıkarıcı - Kaldır

echo Windows Sağ Tık Menülerinden Kaldırılıyor...

reg delete "HKCU\Software\Classes\*\shell\StepExtractor" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\UnblockFolderFiles" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\UnblockFolderFiles" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer" /v "MultipleInvokePromptMinimum" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range1" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range2" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges\Range3" /f >nul 2>&1

echo.
echo ========================================================
echo  BAŞARILI! Yapılan tüm kayıtlar temizlendi.
echo ========================================================
echo.
pause
