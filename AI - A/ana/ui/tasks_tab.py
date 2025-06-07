#!/usr/bin/env python3
# Ana AI Assistant - Tasks Tab

import logging
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFrame, QLineEdit, QCheckBox
)

logger = logging.getLogger('Ana.TasksTab')

class TasksTab(QWidget):
    """Tasks interface for Ana AI Assistant"""
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._setup_ui()
        self._setup_connections()
        logger.info("Tasks tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the tasks tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("tasks_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("TASK MANAGEMENT")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Add task button
        self.add_task_btn = QPushButton("NEW TASK")
        self.add_task_btn.setObjectName("primary_button")
        self.add_task_btn.setIcon(QIcon("../assets/icons/add.png"))
        self.add_task_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.add_task_btn)
        
        self.layout.addWidget(self.header)
        
        # Task input area
        self.task_input_container = QFrame()
        self.task_input_container.setObjectName("task_input_frame")
        self.task_input_container.setMaximumHeight(80)
        self.task_input_layout = QHBoxLayout(self.task_input_container)
        self.task_input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        self.task_input.setObjectName("task_input")
        self.task_input_layout.addWidget(self.task_input)
        
        self.add_btn = QPushButton("ADD")
        self.add_btn.setObjectName("task_add_button")
        self.add_btn.setFixedWidth(100)
        self.task_input_layout.addWidget(self.add_btn)
        
        self.layout.addWidget(self.task_input_container)
        
        # Tasks list
        self.tasks_list = QListWidget()
        self.tasks_list.setObjectName("tasks_list")
        self.tasks_list.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.tasks_list)
        
        # Placeholder tasks for UI demo
        self._add_placeholder_tasks()
    
    def _add_placeholder_tasks(self):
        """Add placeholder tasks for UI demonstration"""
        sample_tasks = [
            "Schedule meeting with team",
            "Review project proposal",
            "Send weekly report",
            "Update system documentation",
            "Investigate performance issues"
        ]
        
        for task in sample_tasks:
            self._add_task(task)
    
    def _add_task(self, task_text):
        """Add a task to the list"""
        # Create list item
        item = QListWidgetItem()
        self.tasks_list.addItem(item)
        
        # Create task widget
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(10, 5, 10, 5)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setObjectName("task_checkbox")
        task_layout.addWidget(checkbox)
        
        # Task text
        task_label = QLabel(task_text)
        task_label.setObjectName("task_label")
        task_label.setWordWrap(True)
        task_layout.addWidget(task_label)
        
        task_layout.addStretch()
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("../assets/icons/delete.png"))
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setFixedSize(24, 24)
        delete_btn.setObjectName("task_delete_button")
        delete_btn.setToolTip("Delete task")
        task_layout.addWidget(delete_btn)
        
        # Set item widget
        item.setSizeHint(task_widget.sizeHint())
        self.tasks_list.setItemWidget(item, task_widget)
        
        # Connect checkbox to completion handler
        checkbox.stateChanged.connect(lambda state, i=item, l=task_label: 
                                     self._on_task_completed(state, i, l))
        
        # Connect delete button
        delete_btn.clicked.connect(lambda _, i=item: self._on_delete_task(i))
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.add_task_btn.clicked.connect(self._on_add_task_btn_clicked)
        self.add_btn.clicked.connect(self._on_add_task_btn_clicked)
        self.task_input.returnPressed.connect(self._on_add_task_btn_clicked)
    
    def _on_add_task_btn_clicked(self):
        """Handle add task button click"""
        task_text = self.task_input.text().strip()
        if task_text:
            self._add_task(task_text)
            self.task_input.clear()
    
    def _on_task_completed(self, state, item, label):
        """Handle task completion state change"""
        if state == Qt.Checked:
            label.setStyleSheet("text-decoration: line-through; color: #888;")
        else:
            label.setStyleSheet("")
    
    def _on_delete_task(self, item):
        """Handle task deletion"""
        row = self.tasks_list.row(item)
        self.tasks_list.takeItem(row) 