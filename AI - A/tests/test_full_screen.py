#!/usr/bin/env python3
# Ana AI Assistant - Full Screen Character View Tests

import sys
import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ana.ui.full_screen_character import FullScreenCharacter, BackgroundType

class TestFullScreenCharacter(unittest.TestCase):
    """Test cases for the full screen character view"""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up test environment"""
        self.window = FullScreenCharacter()
    
    def tearDown(self):
        """Clean up after test"""
        self.window.close()
    
    def test_initialization(self):
        """Test basic initialization"""
        self.assertEqual(self.window.background_type, BackgroundType.GRADIENT)
        self.assertEqual(self.window.text_message, "")
    
    def test_set_message(self):
        """Test setting message text"""
        test_message = "Hello, this is a test message"
        self.window.set_message(test_message)
        self.assertEqual(self.window.text_message, test_message)
        self.assertTrue(self.window.message_label.isVisible())
        
        # Test empty message
        self.window.set_message("")
        self.assertEqual(self.window.text_message, "")
        self.assertFalse(self.window.message_label.isVisible())
    
    def test_set_background(self):
        """Test changing backgrounds"""
        # Test cyberpunk city background
        self.window.set_background(BackgroundType.CYBERPUNK_CITY)
        self.assertEqual(self.window.background_type, BackgroundType.CYBERPUNK_CITY)
        
        # Test matrix background
        self.window.set_background(BackgroundType.MATRIX)
        self.assertEqual(self.window.background_type, BackgroundType.MATRIX)
        
        # Test weather background
        self.window.set_background(BackgroundType.WEATHER, weather="rain", time_of_day="night")
        self.assertEqual(self.window.background_type, BackgroundType.WEATHER)
        self.assertEqual(self.window.weather_condition, "rain")
        self.assertEqual(self.window.time_of_day, "night")

if __name__ == '__main__':
    unittest.main() 