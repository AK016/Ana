#!/usr/bin/env python3
# Ana AI Assistant - Task Widget

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QHBoxLayout, QLineEdit, QLabel, QCheckBox
)
from PyQt5.QtCore import Qt

logger = logging.getLogger('Ana.UI.TaskWidget')

class TaskWidget(QWidget):
    """Widget for managing tasks with Ana"""
    
    def __init__(self, assistant, settings):
        """Initialize task widget with settings"""
        super().__init__()
        self.assistant = assistant
        self.settings = settings
        
        # Initialize UI
        self._init_ui()
        
        logger.info("Task widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.setObjectName("taskInput")
        self.task_input.returnPressed.connect(self._add_task)
        
        self.add_button = QPushButton("Add")
        self.add_button.setObjectName("addTaskButton")
        self.add_button.clicked.connect(self._add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_button)
        
        # Add widgets to layout
        self.layout.addWidget(QLabel("My Tasks"))
        self.layout.addWidget(self.task_list)
        self.layout.addLayout(input_layout)
        
        # Load tasks
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from memory"""
        # This would be implemented to load from the assistant's memory
        pass
    
    def _add_task(self):
        """Add a new task"""
        task_text = self.task_input.text().strip()
        if not task_text:
            return
            
        # Clear input field
        self.task_input.clear()
        
        # Add task to UI
        task_item = QListWidgetItem()
        task_widget = self._create_task_item(task_text)
        
        self.task_list.addItem(task_item)
        self.task_list.setItemWidget(task_item, task_widget)
        task_item.setSizeHint(task_widget.sizeHint())
    
    def _create_task_item(self, task_text):
        """Create a widget for a task item"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        checkbox = QCheckBox(task_text)
        checkbox.stateChanged.connect(lambda state, c=checkbox: self._task_state_changed(c))
        
        delete_button = QPushButton("✕")
        delete_button.setFixedSize(24, 24)
        delete_button.clicked.connect(lambda _, c=checkbox: self._delete_task(c))
        
        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(delete_button)
        
        widget.setLayout(layout)
        return widget
    
    def _task_state_changed(self, checkbox):
        """Handle task state change"""
        if checkbox.isChecked():
            # Mark as completed in memory
            pass
    
    def _delete_task(self, checkbox):
        """Delete a task"""
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget.layout().itemAt(0).widget() == checkbox:
                self.task_list.takeItem(i)
                break 