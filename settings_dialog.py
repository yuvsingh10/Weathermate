"""Settings dialog window for preferences."""

import customtkinter as ctk
from settings import Settings
import logging

logger = logging.getLogger(__name__)


class SettingsDialog(ctk.CTkToplevel):
    """Settings preferences dialog window."""
    
    def __init__(self, parent, settings: Settings, on_change=None):
        """Initialize settings dialog.
        
        Args:
            parent: Parent window
            settings: Settings object
            on_change: Callback function when settings change
        """
        super().__init__(parent)
        self.settings = settings
        self.on_change = on_change
        
        self.title("⚙️ Settings")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create settings UI widgets."""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="⚙️ SETTINGS",
            font=("Segoe UI", 16, "bold"),
            text_color="#1f6aa5"
        )
        title.pack(pady=10)
        
        # --- THEME SECTION ---
        self._create_section(main_frame, "🎨 APPEARANCE")
        
        ctk.CTkLabel(
            main_frame,
            text="Theme:",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        theme_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        theme_frame.pack(anchor="w", padx=40, pady=5)
        
        self.theme_var = ctk.StringVar(value=self.settings.get_theme())
        ctk.CTkRadioButton(
            theme_frame,
            text="Dark",
            variable=self.theme_var,
            value="dark",
            command=self._on_theme_change,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            theme_frame,
            text="Light",
            variable=self.theme_var,
            value="light",
            command=self._on_theme_change,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)
        
        # Font Size
        ctk.CTkLabel(
            main_frame,
            text="Font Size:",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        self.font_var = ctk.StringVar(value=self.settings.get_font_size())
        font_options = ["Small", "Medium", "Large"]
        
        font_menu = ctk.CTkComboBox(
            main_frame,
            values=font_options,
            variable=self.font_var,
            command=self._on_font_change,
            font=("Segoe UI", 10),
            width=150
        )
        font_menu.pack(anchor="w", padx=40, pady=5)
        
        # --- UNITS SECTION ---
        self._create_section(main_frame, "🌡️ UNITS & LOCATION")
        
        ctk.CTkLabel(
            main_frame,
            text="Temperature Unit:",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        unit_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        unit_frame.pack(anchor="w", padx=40, pady=5)
        
        self.unit_var = ctk.StringVar(value=self.settings.get_temperature_unit())
        ctk.CTkRadioButton(
            unit_frame,
            text="Celsius (°C)",
            variable=self.unit_var,
            value="C",
            command=self._on_unit_change,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            unit_frame,
            text="Fahrenheit (°F)",
            variable=self.unit_var,
            value="F",
            command=self._on_unit_change,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)
        
        # Auto-refresh
        ctk.CTkLabel(
            main_frame,
            text="Auto-Refresh (minutes):",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        refresh_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        refresh_frame.pack(anchor="w", padx=40, pady=5)
        
        refresh_values = [str(i*5) for i in range(1, 13)]  # 5-60 mins
        self.refresh_var = ctk.StringVar(
            value=str(self.settings.get_auto_refresh())
        )
        
        refresh_menu = ctk.CTkComboBox(
            refresh_frame,
            values=refresh_values,
            variable=self.refresh_var,
            command=self._on_refresh_change,
            font=("Segoe UI", 10),
            width=100
        )
        refresh_menu.pack(side="left", padx=5)
        
        # Default city
        ctk.CTkLabel(
            main_frame,
            text="Default City:",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        self.city_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter default city",
            font=("Segoe UI", 10),
            width=250
        )
        self.city_entry.insert(0, self.settings.get_default_city())
        self.city_entry.pack(anchor="w", padx=40, pady=5)
        
        # --- FEATURES SECTION ---
        self._create_section(main_frame, "⚡ FEATURES")
        
        self.notif_var = ctk.BooleanVar(
            value=self.settings.are_notifications_enabled()
        )
        ctk.CTkCheckBox(
            main_frame,
            text="Enable Notifications",
            variable=self.notif_var,
            command=self._on_notif_change,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=20, pady=5)
        
        self.alerts_var = ctk.BooleanVar(
            value=self.settings.are_weather_alerts_enabled()
        )
        ctk.CTkCheckBox(
            main_frame,
            text="Enable Weather Alerts",
            variable=self.alerts_var,
            command=self._on_alerts_change,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=20, pady=5)
        
        # --- BUTTONS ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults,
            font=("Segoe UI", 10),
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="✓ Done",
            command=self._on_save,
            font=("Segoe UI", 10),
            fg_color="#1f6aa5",
            hover_color="#0d47a1",
            width=150
        ).pack(side="right", padx=5)
    
    def _create_section(self, parent, title: str) -> None:
        """Create a settings section header.
        
        Args:
            parent: Parent frame
            title: Section title
        """
        separator = ctk.CTkLabel(
            parent,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color="#1f6aa5"
        )
        separator.pack(anchor="w", padx=20, pady=(15, 5))
    
    def _on_theme_change(self) -> None:
        """Handle theme change."""
        self.settings.set_theme(self.theme_var.get())
        logger.info(f"Theme changed to {self.theme_var.get()}")
    
    def _on_font_change(self, value: str) -> None:
        """Handle font size change."""
        self.settings.set_font_size(value.lower())
        logger.info(f"Font size changed to {value}")
    
    def _on_unit_change(self) -> None:
        """Handle unit change."""
        self.settings.set_temperature_unit(self.unit_var.get())
        logger.info(f"Unit changed to {self.unit_var.get()}")
    
    def _on_refresh_change(self, value: str) -> None:
        """Handle refresh interval change."""
        try:
            minutes = int(value)
            self.settings.set_auto_refresh(minutes)
            logger.info(f"Auto-refresh changed to {minutes} minutes")
        except ValueError:
            pass
    
    def _on_notif_change(self) -> None:
        """Handle notification toggle."""
        self.settings.set("notifications", self.notif_var.get())
    
    def _on_alerts_change(self) -> None:
        """Handle weather alerts toggle."""
        self.settings.set("weather_alerts", self.alerts_var.get())
    
    def _reset_defaults(self) -> None:
        """Reset all settings to defaults."""
        from tkinter import messagebox
        
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?"
        ):
            self.settings.reset_to_defaults()
            self.destroy()
            
            if self.on_change:
                self.on_change()
    
    def _on_save(self) -> None:
        """Save default city and close dialog."""
        city = self.city_entry.get().strip()
        if city:
            self.settings.set_default_city(city)
        
        if self.on_change:
            self.on_change()
        
        self.destroy()
