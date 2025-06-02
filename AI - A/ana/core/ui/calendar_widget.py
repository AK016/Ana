#!/usr/bin/env python3
# Ana AI Assistant - Calendar Widget

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget, QListWidget, 
    QPushButton, QHBoxLayout, QLabel, QSplitter
)
from PyQt5.QtCore import Qt, QDate

logger = logging.getLogger('Ana.UI.CalendarWidget')

class CalendarWidget(QWidget):
    """Widget for calendar integration with Ana"""
    
    def __init__(self, assistant, settings):
        """Initialize calendar widget with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Calendar widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Calendar splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Calendar area
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setObjectName("calendarWidget")
        self.calendar_widget.selectionChanged.connect(self._date_selected)
        
        # Event list area
        event_widget = QWidget()
        event_layout = QVBoxLayout(event_widget)
        
        self.date_label = QLabel("Events for Today")
        self.date_label.setObjectName("dateLabel")
        
        self.event_list = QListWidget()
        self.event_list.setObjectName("eventList")
        
        # Add event button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.setObjectName("addEventButton")
        self.add_event_button.clicked.connect(self._add_event)
        
        event_layout.addWidget(self.date_label)
        event_layout.addWidget(self.event_list)
        event_layout.addWidget(self.add_event_button)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.calendar_widget)
        self.splitter.addWidget(event_widget)
        self.splitter.setSizes([300, 300])  # Equal sizes
        
        # Add splitter to layout
        self.layout.addWidget(self.splitter)
        
        # Load events for today
        self._load_events(QDate.currentDate())
    
    def _date_selected(self):
        """Handle date selection change"""
        selected_date = self.calendar_widget.selectedDate()
        self.date_label.setText(f"Events for {selected_date.toString('MMMM d, yyyy')}")
        self._load_events(selected_date)
    
    def _load_events(self, date):
        """Load events for the selected date"""
        # This would be implemented to load from the assistant's calendar integration
        self.event_list.clear()
        
        # Placeholder events
        self.event_list.addItem("No events for this day")
    
    def _add_event(self):
        """Add a new event"""
        # This would open a dialog to add an event
        pass 