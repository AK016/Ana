#!/usr/bin/env python3
# Ana AI Assistant - Music Tab

import logging
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QFrame, QListWidget, QListWidgetItem, QProgressBar
)

logger = logging.getLogger('Ana.MusicTab')

class MusicTab(QWidget):
    """Music player interface for Ana AI Assistant"""
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._setup_ui()
        self._setup_connections()
        logger.info("Music tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the music tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("music_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("MUSIC PLAYER")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Add music button
        self.add_music_btn = QPushButton("ADD MUSIC")
        self.add_music_btn.setObjectName("primary_button")
        self.add_music_btn.setIcon(QIcon("../assets/icons/add.png"))
        self.add_music_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.add_music_btn)
        
        self.layout.addWidget(self.header)
        
        # Now Playing section
        self.now_playing = QFrame()
        self.now_playing.setObjectName("now_playing_frame")
        self.now_playing.setMinimumHeight(200)
        self.now_playing_layout = QHBoxLayout(self.now_playing)
        
        # Album art
        self.album_art = QLabel()
        self.album_art.setObjectName("album_art")
        self.album_art.setMinimumSize(180, 180)
        self.album_art.setMaximumSize(180, 180)
        self.album_art.setScaledContents(True)
        
        # Try to load a placeholder image
        placeholder_path = "../assets/album_placeholder.png"
        try:
            self.album_art.setPixmap(QPixmap(placeholder_path))
        except:
            self.album_art.setText("Album Art")
            self.album_art.setStyleSheet("background-color: #333; color: white; border-radius: 5px; text-align: center;")
        
        self.now_playing_layout.addWidget(self.album_art)
        
        # Track info and controls
        self.track_info = QWidget()
        self.track_info_layout = QVBoxLayout(self.track_info)
        self.track_info_layout.setContentsMargins(20, 10, 10, 10)
        
        # Track title
        self.track_title = QLabel("Not Playing")
        self.track_title.setObjectName("track_title")
        self.track_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.track_info_layout.addWidget(self.track_title)
        
        # Artist
        self.track_artist = QLabel("Select a track to begin")
        self.track_artist.setObjectName("track_artist")
        self.track_artist.setStyleSheet("font-size: 14px; color: #aaa;")
        self.track_info_layout.addWidget(self.track_artist)
        
        self.track_info_layout.addSpacing(10)
        
        # Progress bar
        self.progress_container = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_container)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_layout.setSpacing(5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("music_progress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(5)
        self.progress_bar.setMaximumHeight(5)
        self.progress_layout.addWidget(self.progress_bar)
        
        # Time labels
        self.time_container = QWidget()
        self.time_layout = QHBoxLayout(self.time_container)
        self.time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_time = QLabel("0:00")
        self.current_time.setObjectName("current_time")
        self.time_layout.addWidget(self.current_time)
        
        self.time_layout.addStretch()
        
        self.total_time = QLabel("0:00")
        self.total_time.setObjectName("total_time")
        self.time_layout.addWidget(self.total_time)
        
        self.progress_layout.addWidget(self.time_container)
        self.track_info_layout.addWidget(self.progress_container)
        
        # Playback controls
        self.controls = QWidget()
        self.controls_layout = QHBoxLayout(self.controls)
        self.controls_layout.setContentsMargins(0, 20, 0, 0)
        self.controls_layout.setSpacing(20)
        
        self.controls_layout.addStretch()
        
        # Previous button
        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("prev_button")
        self.prev_btn.setIcon(QIcon("../assets/icons/previous.png"))
        self.prev_btn.setIconSize(QSize(32, 32))
        self.prev_btn.setFixedSize(50, 50)
        self.controls_layout.addWidget(self.prev_btn)
        
        # Play/Pause button
        self.play_btn = QPushButton()
        self.play_btn.setObjectName("play_button")
        self.play_btn.setIcon(QIcon("../assets/icons/play.png"))
        self.play_btn.setIconSize(QSize(40, 40))
        self.play_btn.setFixedSize(60, 60)
        self.controls_layout.addWidget(self.play_btn)
        
        # Next button
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("next_button")
        self.next_btn.setIcon(QIcon("../assets/icons/next.png"))
        self.next_btn.setIconSize(QSize(32, 32))
        self.next_btn.setFixedSize(50, 50)
        self.controls_layout.addWidget(self.next_btn)
        
        self.controls_layout.addStretch()
        
        self.track_info_layout.addWidget(self.controls)
        self.now_playing_layout.addWidget(self.track_info)
        
        self.layout.addWidget(self.now_playing)
        
        # Playlist
        self.playlist_container = QFrame()
        self.playlist_container.setObjectName("playlist_container")
        self.playlist_layout = QVBoxLayout(self.playlist_container)
        self.playlist_layout.setContentsMargins(10, 10, 10, 10)
        
        # Playlist header
        self.playlist_header = QLabel("PLAYLIST")
        self.playlist_header.setObjectName("playlist_header")
        self.playlist_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00E5FF;")
        self.playlist_layout.addWidget(self.playlist_header)
        
        # Track list
        self.track_list = QListWidget()
        self.track_list.setObjectName("track_list")
        self.track_list.setFrameShape(QFrame.NoFrame)
        self.playlist_layout.addWidget(self.track_list)
        
        self.layout.addWidget(self.playlist_container)
        
        # Add playlist items
        self._add_playlist_items()
    
    def _add_playlist_items(self):
        """Add placeholder playlist items"""
        tracks = [
            {"title": "Cyberpunk Dreams", "artist": "Neon Syntax", "duration": "3:45"},
            {"title": "Digital Horizon", "artist": "Virtual Construct", "duration": "4:12"},
            {"title": "Neural Network", "artist": "AI Collective", "duration": "5:30"},
            {"title": "Quantum Resonance", "artist": "Particle Wave", "duration": "3:58"},
            {"title": "Silicon Valley", "artist": "Tech Pioneers", "duration": "4:22"}
        ]
        
        for track in tracks:
            self._add_track_item(track["title"], track["artist"], track["duration"])
    
    def _add_track_item(self, title, artist, duration):
        """Add a track item to the playlist"""
        item = QListWidgetItem()
        self.track_list.addItem(item)
        
        track_widget = QWidget()
        track_layout = QHBoxLayout(track_widget)
        track_layout.setContentsMargins(10, 5, 10, 5)
        
        # Track info (title and artist)
        track_info = QWidget()
        info_layout = QVBoxLayout(track_info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("track_item_title")
        info_layout.addWidget(title_label)
        
        # Artist
        artist_label = QLabel(artist)
        artist_label.setObjectName("track_item_artist")
        artist_label.setStyleSheet("color: #aaa; font-size: 12px;")
        info_layout.addWidget(artist_label)
        
        track_layout.addWidget(track_info)
        track_layout.addStretch()
        
        # Duration
        duration_label = QLabel(duration)
        duration_label.setObjectName("track_duration")
        duration_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        track_layout.addWidget(duration_label)
        
        # Set the widget for the item
        item.setSizeHint(track_widget.sizeHint())
        self.track_list.setItemWidget(item, track_widget)
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.play_btn.clicked.connect(self._on_play_clicked)
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.prev_btn.clicked.connect(self._on_prev_clicked)
        self.track_list.itemClicked.connect(self._on_track_selected)
    
    def _on_play_clicked(self):
        """Handle play/pause button click"""
        # This would control actual playback in a real implementation
        # For this demo, we'll just toggle the button icon
        if self.progress_bar.value() == 0:
            self.progress_bar.setValue(45)
            self.play_btn.setIcon(QIcon("../assets/icons/pause.png"))
            self.current_time = "1:48"
            self.total_time = "4:12"
        else:
            self.play_btn.setIcon(QIcon("../assets/icons/play.png"))
    
    def _on_next_clicked(self):
        """Handle next track button click"""
        # This would play the next track in a real implementation
        pass
    
    def _on_prev_clicked(self):
        """Handle previous track button click"""
        # This would play the previous track in a real implementation
        pass
    
    def _on_track_selected(self, item):
        """Handle track selection from playlist"""
        # Get the widget associated with the item
        track_widget = self.track_list.itemWidget(item)
        
        # Extract title and artist from the widget
        title_label = track_widget.findChild(QLabel, "track_item_title")
        artist_label = track_widget.findChild(QLabel, "track_item_artist")
        
        # Update now playing information
        if title_label and artist_label:
            self.track_title.setText(title_label.text())
            self.track_artist.setText(artist_label.text())
        
        # Reset progress and show as if ready to play
        self.progress_bar.setValue(0)
        self.current_time.setText("0:00")
        
        # Get duration from the track item
        duration_label = track_widget.findChild(QLabel, "track_duration")
        if duration_label:
            self.total_time.setText(duration_label.text())
        
        # Update play button to show play icon
        self.play_btn.setIcon(QIcon("../assets/icons/play.png")) 