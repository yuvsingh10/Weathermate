"""Main entry point for Weather Mate application."""

import logging
from ui import create_gui
from config import logger


def main() -> None:
    """Start the Weather Mate application."""
    try:
        logger.info("Starting Weather Mate application")
        
        # Create and display the GUI
        root = create_gui()
        
        logger.info("GUI created successfully")
        
        # Start the event loop
        root.mainloop()
        
        logger.info("Weather Mate application closed")
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
