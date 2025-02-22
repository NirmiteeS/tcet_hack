import sys
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import main  # Import the main GUI module

def create_icon():
    """Create and configure the system tray icon"""
    
    def on_open(icon, item):
        """Handle opening the main window"""
        try:
            threading.Thread(target=main.create_window, daemon=True).start()
        except Exception as e:
            print(f"Error opening window: {e}")

    def on_exit(icon, item):
        """Handle application exit"""
        try:
            # Stop the icon first
            icon.stop()
            # Exit the application
            sys.exit()
        except Exception as e:
            print(f"Error during exit: {e}")
            sys.exit(1)

    try:
        # Load the icon image from icon.jpg
        image = Image.open("icon.png")

        # Create system tray menu
        menu = Menu(
            MenuItem("Open", on_open),
            MenuItem("Exit", on_exit)
        )

        # Create and run system tray icon
        icon = Icon(
            name="DesktopExtension",
            icon=image,
            title="Desktop Extension",
            menu=menu
        )
        
        # Add a callback for left-click to open the window
        icon.icon = image
        icon.run()
        
    except Exception as e:
        print(f"Error creating system tray icon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Run system tray in separate thread
        tray_thread = threading.Thread(target=create_icon, daemon=True)
        tray_thread.start()
        
        # Keep main thread alive
        while tray_thread.is_alive():
            tray_thread.join(1)
    except KeyboardInterrupt:
        print("\nExiting application...")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
