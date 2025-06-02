#!/usr/bin/env python3
# Ana AI Assistant - Music Widget

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QComboBox, QListWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

logger = logging.getLogger('Ana.UI.MusicWidget')

class MusicWidget(QWidget):
    """Widget for music control with Ana"""
    
    def __init__(self, assistant, settings):
        """Initialize music widget with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Music widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Music source selection
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Music Source:"))
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["YouTube Music", "Spotify"])
        self.source_combo.currentIndexChanged.connect(self._source_changed)
        
        source_layout.addWidget(self.source_combo)
        source_layout.addStretch()
        
        # Currently playing
        self.now_playing_label = QLabel("Not Playing")
        self.now_playing_label.setObjectName("nowPlayingLabel")
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.prev_button = QPushButton()
        self.prev_button.setIcon(QIcon("assets/ui/icons/prev.png"))
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.clicked.connect(self._prev_track)
        
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon("assets/ui/icons/play.png"))
        self.play_button.setFixedSize(50, 50)
        self.play_button.clicked.connect(self._play_pause)
        
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon("assets/ui/icons/next.png"))
        self.next_button.setFixedSize(40, 40)
        self.next_button.clicked.connect(self._next_track)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addStretch()
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        
        # Search area
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for music...")
        self.search_input.returnPressed.connect(self._search_music)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._search_music)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setObjectName("musicResultsList")
        self.results_list.itemDoubleClicked.connect(self._result_selected)
        
        # Add all elements to layout
        self.layout.addLayout(source_layout)
        self.layout.addWidget(self.now_playing_label)
        self.layout.addLayout(controls_layout)
        self.layout.addWidget(self.progress_slider)
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.results_list)
    
    def _source_changed(self, index):
        """Handle music source change"""
        source = self.source_combo.currentText()
        logger.info(f"Music source changed to: {source}")
    
    def _play_pause(self):
        """Toggle play/pause"""
        # This would be implemented to control music playback
        pass
    
    def _prev_track(self):
        """Go to previous track"""
        # This would be implemented to control music playback
        pass
    
    def _next_track(self):
        """Go to next track"""
        # This would be implemented to control music playback
        pass
    
    def _search_music(self):
        """Search for music"""
        query = self.search_input.text().strip()
        if not query:
            return
            
        # Clear results
        self.results_list.clear()
        
        # Add placeholder results
        self.results_list.addItem("Search results would appear here")
    
    def _result_selected(self, item):
        """Handle music selection from results"""
        # This would be implemented to play the selected music
        pass 