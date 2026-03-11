import logging
import os
from datetime import datetime

import aqt
from aqt.qt import QAction, QFileDialog
from aqt.utils import tooltip


def export_debug_logs():
    """Export Migaku debug logs to a file for troubleshooting."""
    try:
        # Collect logs from all Migaku loggers
        log_content = []
        log_content.append("=" * 80)
        log_content.append(f"Migaku Anki Add-on Debug Logs")
        log_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append("=" * 80)
        log_content.append("")
        
        # Get connection status
        connection = aqt.mw.migaku_connection
        is_connected = connection.is_connected()
        log_content.append(f"Browser Extension Connected: {is_connected}")
        log_content.append("")
        
        # Try to read from log file if it exists
        log_file = os.path.join(aqt.mw.pm.profileFolder(), "migaku_addon.log")
        if os.path.exists(log_file):
            log_content.append("--- Recent Log Entries ---")
            log_content.append("")
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    # Get last 1000 lines or entire file
                    lines = f.readlines()
                    recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                    log_content.extend(line.rstrip() for line in recent_lines)
            except Exception as e:
                log_content.append(f"Error reading log file: {e}")
        else:
            log_content.append("No log file found. Logs may only be in console.")
            log_content.append("To enable file logging, add this to src/__init__.py:")
            log_content.append("")
            log_content.append("import logging")
            log_content.append("log_file = os.path.join(aqt.mw.pm.profileFolder(), 'migaku_addon.log')")
            log_content.append("handler = logging.FileHandler(log_file)")
            log_content.append("handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))")
            log_content.append("logging.getLogger('migaku').addHandler(handler)")
        
        log_content.append("")
        log_content.append("=" * 80)
        
        # Prompt user for save location
        default_filename = f"migaku_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            aqt.mw,
            "Export Migaku Debug Logs",
            os.path.join(os.path.expanduser("~"), "Desktop", default_filename),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_content))
            
            tooltip(f"Debug logs exported to:<br>{file_path}", period=5000)
            
            # Offer to open the file location
            if aqt.utils.askUser(
                "Logs exported successfully!\n\nWould you like to open the folder?",
                parent=aqt.mw,
                title="Export Complete"
            ):
                if os.name == 'nt':  # Windows
                    os.startfile(os.path.dirname(file_path))
                elif os.name == 'posix':  # macOS/Linux
                    import subprocess
                    subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', 
                                   os.path.dirname(file_path)])
    
    except Exception as e:
        aqt.utils.showWarning(
            f"Failed to export debug logs:\n\n{str(e)}",
            title="Export Failed",
            parent=aqt.mw
        )


# Create the menu action
action = QAction("Export Debug Logs…", aqt.mw)
action.triggered.connect(export_debug_logs)
