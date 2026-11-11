"""
Windows Registry Manager for STEP Extractor Context Menu Integration.
Registers and unregisters the right-click context menu for .pdf files in Windows Explorer.
Uses HKEY_CURRENT_USER, so NO administrator privileges are needed!
"""

import os
import sys
import winreg
from typing import Tuple

REG_KEY_PATH = r"Software\Classes\*\shell\StepExtractor"
LEGACY_REG_KEY_PATH = r"Software\Classes\SystemFileAssociations\.pdf\shell\StepExtractor"
MENU_LABEL = "STEP Dosyasını Çıkar"


def get_target_command_and_icon() -> Tuple[str, str]:
    """Determine the optimal command string and icon path based on how the app is run."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exe_candidate = os.path.join(base_dir, "StepExtractor.exe")
    icon_candidate = os.path.join(base_dir, "app_icon.ico")

    # If running as a frozen PyInstaller bundle
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        return f'"{exe_path}" "%1"', exe_path

    # If StepExtractor.exe exists in the folder
    if os.path.exists(exe_candidate):
        return f'"{exe_candidate}" "%1"', exe_candidate

    # Otherwise run via pythonw (silent python interpreter)
    python_dir = os.path.dirname(sys.executable)
    pythonw_path = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw_path):
        pythonw_path = sys.executable

    main_script = os.path.join(base_dir, "main.py")
    cmd = f'"{pythonw_path}" "{main_script}" "%1"'
    icon = icon_candidate if os.path.exists(icon_candidate) else pythonw_path
    return cmd, icon


def is_installed() -> bool:
    """Check if the context menu is currently installed."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "")
            return val == MENU_LABEL
    except FileNotFoundError:
        return False
    except Exception:
        return False


def install() -> Tuple[bool, str]:
    """Register context menu in Windows registry for all files and mixed selections."""
    cmd_str, icon_path = get_target_command_and_icon()
    try:
        # Clean up legacy key if it exists
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{LEGACY_REG_KEY_PATH}\\command")
        except FileNotFoundError:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, LEGACY_REG_KEY_PATH)
        except FileNotFoundError:
            pass

        # Create or open base key on Software\Classes\*\shell\StepExtractor
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, MENU_LABEL)
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

        # Create command subkey
        cmd_key_path = f"{REG_KEY_PATH}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key_path) as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, cmd_str)

        return True, "Sağ tık menüsüne başarıyla eklendi!"
    except Exception as e:
        return False, f"Kayıt defteri yazma hatası: {e}"


def uninstall() -> Tuple[bool, str]:
    """Remove context menu from Windows registry."""
    try:
        for root_path in (REG_KEY_PATH, LEGACY_REG_KEY_PATH):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{root_path}\\command")
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, root_path)
            except FileNotFoundError:
                pass

        return True, "Sağ tık menüsünden başarıyla kaldırıldı!"
    except Exception as e:
        return False, f"Kayıt defteri silme hatası: {e}"
