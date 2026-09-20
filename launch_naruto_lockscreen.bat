@echo off
title Naruto 4K Live Lock Screen
echo ======================================================================
echo    NARUTO ENDLESS SKY // 4K LIVE WALLPAPER LOCK SCREEN
echo ======================================================================
echo.
echo [1/2] Checking 4K Video Source (E:\naruto-endless-sky.3840x2160.mp4)...
echo [2/2] Launching Hardware-Accelerated Live Lock Screen with Clock & Date...
echo.

:: Launch via Jarvis X Lockscreen Controller
python src\jarvisx\gui\naruto_live_lockscreen.py

echo.
echo [INFO] Lock Screen session closed. Welcome back!
pause
