#!/usr/bin/env python3
# Ana AI Assistant - Theme Manager

import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt

logger = logging.getLogger('Ana.UI.ThemeManager')

class ThemeManager:
    """Theme manager for Ana AI Assistant"""
    
    def __init__(self, settings):
        """Initialize theme manager with settings"""
        self.settings = settings
        self.current_theme = settings["ui"]["theme"]
        self.accent_color = settings["ui"]["accent_color"]
        self.secondary_color = settings["ui"]["secondary_color"]
        
        # Generate theme palettes
        self.theme_palettes = {
            "dark": self._create_dark_palette(),
            "light": self._create_light_palette()
        }
        
        # Generate stylesheets
        self.theme_stylesheets = {
            "dark": self._create_dark_stylesheet(),
            "light": self._create_light_stylesheet()
        }
        
        logger.info(f"Theme manager initialized with theme: {self.current_theme}")
    
    def _create_dark_palette(self):
        """Create dark theme palette"""
        palette = QPalette()
        
        # Base colors
        bg_color = QColor("#121212")
        text_color = QColor("#ffffff")
        highlight_color = QColor(self.accent_color)
        secondary_highlight = QColor(self.secondary_color)
        
        # Dark theme panel colors
        panel_bg = QColor("#1e1e1e")
        panel_light = QColor("#2d2d2d")
        
        # Set palette colors
        palette.setColor(QPalette.Window, bg_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, panel_bg)
        palette.setColor(QPalette.AlternateBase, panel_light)
        palette.setColor(QPalette.ToolTipBase, panel_bg)
        palette.setColor(QPalette.ToolTipText, text_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, panel_bg)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, Qt.white)
        palette.setColor(QPalette.Link, highlight_color)
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        return palette
    
    def _create_light_palette(self):
        """Create light theme palette"""
        palette = QPalette()
        
        # Base colors
        bg_color = QColor("#f5f5f5")
        text_color = QColor("#212121")
        highlight_color = QColor(self.accent_color)
        secondary_highlight = QColor(self.secondary_color)
        
        # Light theme panel colors
        panel_bg = QColor("#ffffff")
        panel_light = QColor("#e8e8e8")
        
        # Set palette colors
        palette.setColor(QPalette.Window, bg_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, panel_bg)
        palette.setColor(QPalette.AlternateBase, panel_light)
        palette.setColor(QPalette.ToolTipBase, panel_bg)
        palette.setColor(QPalette.ToolTipText, text_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, panel_bg)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, Qt.black)
        palette.setColor(QPalette.Link, highlight_color)
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        return palette
    
    def _create_dark_stylesheet(self):
        """Create dark theme stylesheet"""
        accent_color = self.accent_color
        secondary_color = self.secondary_color
        
        return f"""
        /* Cyberpunk-inspired Dark Theme for Ana */
        
        QWidget {{
            background-color: #121212;
            color: #ffffff;
            font-size: 10pt;
        }}
        
        /* Frame styling */
        QFrame#headerFrame {{
            background-color: #1e1e1e;
            border-bottom: 2px solid {accent_color};
            border-radius: 5px;
        }}
        
        QFrame#footerFrame {{
            background-color: #1e1e1e;
            border-top: 2px solid {accent_color};
            border-radius: 5px;
        }}
        
        QFrame#contentFrame {{
            background-color: transparent;
            border: none;
        }}
        
        QFrame#voiceStatusFrame {{
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 5px;
        }}
        
        QFrame#audioVizFrame {{
            background-color: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 5px;
        }}
        
        /* Tab widget styling */
        QTabWidget::pane {{
            border: 1px solid #333333;
            border-top: none;
            border-radius: 0px 0px 5px 5px;
            background-color: #1e1e1e;
        }}
        
        QTabBar::tab {{
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #333333;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 15px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: #1e1e1e;
            color: {accent_color};
            border-bottom: 2px solid {accent_color};
        }}
        
        QTabBar::tab:hover {{
            background-color: #353535;
        }}
        
        /* Label styling */
        QLabel#titleLabel {{
            color: {accent_color};
            font-size: 20pt;
            font-weight: bold;
        }}
        
        QLabel#greetingLabel {{
            color: {secondary_color};
            font-size: 14pt;
        }}
        
        QLabel#voiceStatusLabel {{
            color: {accent_color};
            font-size: 10pt;
        }}
        
        /* Button styling */
        QPushButton {{
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #444444;
            border-radius: 5px;
            padding: 8px 16px;
        }}
        
        QPushButton:hover {{
            background-color: #353535;
            border: 1px solid {accent_color};
        }}
        
        QPushButton:pressed {{
            background-color: {accent_color};
            color: black;
        }}
        
        QPushButton#micButton {{
            background-color: #1e1e1e;
            border: 2px solid {accent_color};
            border-radius: 24px;
        }}
        
        QPushButton#micButton:hover {{
            background-color: #2d2d2d;
        }}
        
        QPushButton#micButton:pressed {{
            background-color: {accent_color};
        }}
        
        /* Slider styling */
        QSlider::groove:horizontal {{
            border: 1px solid #444444;
            height: 8px;
            background: #2d2d2d;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {accent_color};
            border: 1px solid {accent_color};
            width: 18px;
            border-radius: 9px;
            margin: -5px 0;
        }}
        
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {accent_color}, stop: 1 {secondary_color});
            border: 1px solid #444444;
            height: 8px;
            border-radius: 4px;
        }}
        
        /* Text editing widgets */
        QTextEdit, QLineEdit {{
            background-color: #1a1a1a;
            color: white;
            border: 1px solid #444444;
            border-radius: 5px;
            padding: 5px;
        }}
        
        QTextEdit:focus, QLineEdit:focus {{
            border: 1px solid {accent_color};
        }}
        
        /* Scrollbar styling */
        QScrollBar:vertical {{
            border: none;
            background: #1a1a1a;
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: #444444;
            min-height: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {accent_color};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Glowing accents */
        .GlowingAccent {{
            border: 2px solid {accent_color};
            border-radius: 5px;
            background-color: rgba(0, 0, 0, 0.2);
        }}
        """
    
    def _create_light_stylesheet(self):
        """Create light theme stylesheet"""
        accent_color = self.accent_color
        secondary_color = self.secondary_color
        
        return f"""
        /* Cyberpunk-inspired Light Theme for Ana */
        
        QWidget {{
            background-color: #f5f5f5;
            color: #212121;
            font-size: 10pt;
        }}
        
        /* Frame styling */
        QFrame#headerFrame {{
            background-color: #ffffff;
            border-bottom: 2px solid {accent_color};
            border-radius: 5px;
        }}
        
        QFrame#footerFrame {{
            background-color: #ffffff;
            border-top: 2px solid {accent_color};
            border-radius: 5px;
        }}
        
        QFrame#contentFrame {{
            background-color: transparent;
            border: none;
        }}
        
        QFrame#voiceStatusFrame {{
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 5px;
        }}
        
        QFrame#audioVizFrame {{
            background-color: #f0f0f0;
            border: 1px solid #dddddd;
            border-radius: 5px;
        }}
        
        /* Tab widget styling */
        QTabWidget::pane {{
            border: 1px solid #dddddd;
            border-top: none;
            border-radius: 0px 0px 5px 5px;
            background-color: #ffffff;
        }}
        
        QTabBar::tab {{
            background-color: #eeeeee;
            color: #666666;
            border: 1px solid #dddddd;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 15px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: #ffffff;
            color: {accent_color};
            border-bottom: 2px solid {accent_color};
        }}
        
        QTabBar::tab:hover {{
            background-color: #f5f5f5;
        }}
        
        /* Label styling */
        QLabel#titleLabel {{
            color: {accent_color};
            font-size: 20pt;
            font-weight: bold;
        }}
        
        QLabel#greetingLabel {{
            color: {secondary_color};
            font-size: 14pt;
        }}
        
        QLabel#voiceStatusLabel {{
            color: {accent_color};
            font-size: 10pt;
        }}
        
        /* Button styling */
        QPushButton {{
            background-color: #eeeeee;
            color: #212121;
            border: 1px solid #dddddd;
            border-radius: 5px;
            padding: 8px 16px;
        }}
        
        QPushButton:hover {{
            background-color: #e0e0e0;
            border: 1px solid {accent_color};
        }}
        
        QPushButton:pressed {{
            background-color: {accent_color};
            color: white;
        }}
        
        QPushButton#micButton {{
            background-color: #ffffff;
            border: 2px solid {accent_color};
            border-radius: 24px;
        }}
        
        QPushButton#micButton:hover {{
            background-color: #f0f0f0;
        }}
        
        QPushButton#micButton:pressed {{
            background-color: {accent_color};
        }}
        
        /* Slider styling */
        QSlider::groove:horizontal {{
            border: 1px solid #dddddd;
            height: 8px;
            background: #eeeeee;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {accent_color};
            border: 1px solid {accent_color};
            width: 18px;
            border-radius: 9px;
            margin: -5px 0;
        }}
        
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {accent_color}, stop: 1 {secondary_color});
            border: 1px solid #dddddd;
            height: 8px;
            border-radius: 4px;
        }}
        
        /* Text editing widgets */
        QTextEdit, QLineEdit {{
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #dddddd;
            border-radius: 5px;
            padding: 5px;
        }}
        
        QTextEdit:focus, QLineEdit:focus {{
            border: 1px solid {accent_color};
        }}
        
        /* Scrollbar styling */
        QScrollBar:vertical {{
            border: none;
            background: #f0f0f0;
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: #cccccc;
            min-height: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {accent_color};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Glowing accents */
        .GlowingAccent {{
            border: 2px solid {accent_color};
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.8);
        }}
        """
    
    def apply_theme(self, widget):
        """Apply the current theme to a widget"""
        # Apply palette
        if self.current_theme in self.theme_palettes:
            palette = self.theme_palettes[self.current_theme]
            widget.setPalette(palette)
            QApplication.setPalette(palette)
        
        # Apply stylesheet
        if self.current_theme in self.theme_stylesheets:
            stylesheet = self.theme_stylesheets[self.current_theme]
            widget.setStyleSheet(stylesheet)
            QApplication.setStyleSheet(stylesheet)
        
        logger.debug(f"Applied {self.current_theme} theme to widget")
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name not in ["dark", "light"]:
            logger.warning(f"Invalid theme name: {theme_name}")
            return False
            
        self.current_theme = theme_name
        self.settings["ui"]["theme"] = theme_name
        
        logger.info(f"Theme changed to: {theme_name}")
        return True
    
    def set_accent_color(self, color):
        """Set the accent color"""
        self.accent_color = color
        self.settings["ui"]["accent_color"] = color
        
        # Regenerate stylesheets
        self.theme_stylesheets["dark"] = self._create_dark_stylesheet()
        self.theme_stylesheets["light"] = self._create_light_stylesheet()
        
        logger.info(f"Accent color changed to: {color}")
        return True
    
    def set_secondary_color(self, color):
        """Set the secondary color"""
        self.secondary_color = color
        self.settings["ui"]["secondary_color"] = color
        
        # Regenerate stylesheets
        self.theme_stylesheets["dark"] = self._create_dark_stylesheet()
        self.theme_stylesheets["light"] = self._create_light_stylesheet()
        
        logger.info(f"Secondary color changed to: {color}")
        return True 