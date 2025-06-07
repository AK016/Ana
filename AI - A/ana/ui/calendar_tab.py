#!/usr/bin/env python3
# Ana AI Assistant - Calendar Tab

import logging
import calendar
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QCalendarWidget, QListWidget, QListWidgetItem,
    QSplitter, QTimeEdit, QLineEdit, QDialog, QFormLayout
)

logger = logging.getLogger('Ana.CalendarTab')

class CalendarTab(QWidget):
    """Calendar interface for Ana AI Assistant"""
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._setup_ui()
        self._setup_connections()
        logger.info("Calendar tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the calendar tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("calendar_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("CALENDAR SYNC")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Add event button
        self.add_event_btn = QPushButton("NEW EVENT")
        self.add_event_btn.setObjectName("primary_button")
        self.add_event_btn.setIcon(QIcon("../assets/icons/add.png"))
        self.add_event_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.add_event_btn)
        
        self.layout.addWidget(self.header)
        
        # Split view for calendar and events
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Calendar widget on the left
        self.calendar_container = QFrame()
        self.calendar_container.setObjectName("calendar_container")
        self.calendar_layout = QVBoxLayout(self.calendar_container)
        self.calendar_layout.setContentsMargins(10, 10, 10, 10)
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setObjectName("calendar_widget")
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar_widget.setMinimumWidth(400)
        
        # Set current date format
        self.calendar_widget.setDateEditEnabled(True)
        self.calendar_widget.setSelectedDate(QDate.currentDate())
        
        self.calendar_layout.addWidget(self.calendar_widget)
        
        # Events list on the right
        self.events_container = QFrame()
        self.events_container.setObjectName("events_container")
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setContentsMargins(10, 10, 10, 10)
        
        self.events_date_label = QLabel("Events for Today")
        self.events_date_label.setObjectName("events_date_label")
        self.events_date_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00E5FF;")
        self.events_layout.addWidget(self.events_date_label)
        
        self.events_list = QListWidget()
        self.events_list.setObjectName("events_list")
        self.events_list.setFrameShape(QFrame.NoFrame)
        self.events_layout.addWidget(self.events_list)
        
        # Add to splitter
        self.splitter.addWidget(self.calendar_container)
        self.splitter.addWidget(self.events_container)
        self.splitter.setStretchFactor(1, 1)  # Events list gets more stretch
        
        self.layout.addWidget(self.splitter)
        
        # Add placeholder events
        self._add_placeholder_events()
    
    def _add_placeholder_events(self):
        """Add placeholder events for UI demonstration"""
        today = datetime.now()
        
        events = [
            {"title": "Team Meeting", "time": "09:30 - 10:30", "location": "Conference Room A"},
            {"title": "Project Review", "time": "13:00 - 14:00", "location": "Virtual"},
            {"title": "Client Call", "time": "15:30 - 16:00", "location": "Phone"}
        ]
        
        for event in events:
            self._add_event_item(event["title"], event["time"], event["location"])
    
    def _add_event_item(self, title, time_str, location):
        """Add an event item to the list"""
        item = QListWidgetItem()
        self.events_list.addItem(item)
        
        event_widget = QWidget()
        event_layout = QVBoxLayout(event_widget)
        event_layout.setContentsMargins(10, 10, 10, 10)
        event_layout.setSpacing(5)
        
        # Event title
        title_label = QLabel(title)
        title_label.setObjectName("event_title")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        event_layout.addWidget(title_label)
        
        # Event time
        time_label = QLabel(f"⏰ {time_str}")
        time_label.setObjectName("event_time")
        event_layout.addWidget(time_label)
        
        # Event location
        location_label = QLabel(f"📍 {location}")
        location_label.setObjectName("event_location")
        event_layout.addWidget(location_label)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)
        button_layout.setSpacing(10)
        
        # Add spacer to push buttons to the right
        button_layout.addStretch()
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("event_edit_button")
        edit_btn.setFixedWidth(60)
        button_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("event_delete_button")
        delete_btn.setFixedWidth(60)
        button_layout.addWidget(delete_btn)
        
        event_layout.addWidget(button_container)
        
        # Style the event item
        event_widget.setObjectName("event_item")
        
        # Set the widget for the item
        item.setSizeHint(event_widget.sizeHint())
        self.events_list.setItemWidget(item, event_widget)
        
        # Connect buttons
        delete_btn.clicked.connect(lambda _, i=item: self._on_delete_event(i))
        edit_btn.clicked.connect(lambda _: self._on_edit_event(title, time_str, location))
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.add_event_btn.clicked.connect(self._on_add_event)
        self.calendar_widget.selectionChanged.connect(self._on_date_selected)
    
    def _on_date_selected(self):
        """Handle date selection in calendar"""
        selected_date = self.calendar_widget.selectedDate()
        date_str = selected_date.toString("dddd, MMMM d, yyyy")
        self.events_date_label.setText(f"Events for {date_str}")
        
        # In a real app, we would load events for the selected date
        # For now, we'll just clear and add some placeholders
        self.events_list.clear()
        self._add_placeholder_events()
    
    def _on_add_event(self):
        """Handle add event button click"""
        # In a real implementation, this would open a dialog to add an event
        # For this example, we'll just add a placeholder event
        self._add_event_item(
            "New Event", 
            "12:00 - 13:00", 
            "Office"
        )
    
    def _on_delete_event(self, item):
        """Handle event deletion"""
        row = self.events_list.row(item)
        self.events_list.takeItem(row)
    
    def _on_edit_event(self, title, time_str, location):
        """Handle event editing"""
        # In a real implementation, this would open a dialog to edit the event
        # For this example, we'll do nothing
        pass 