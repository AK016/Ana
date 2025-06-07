#!/usr/bin/env python3
# Ana AI Assistant - Health Tab

import logging
import random
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QBrush, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTabWidget, QScrollArea, QLineEdit
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

logger = logging.getLogger('Ana.HealthTab')

class HealthTab(QWidget):
    """Health monitoring interface for Ana AI Assistant"""
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self._setup_ui()
        self._setup_connections()
        logger.info("Health tab initialized")
    
    def _setup_ui(self):
        """Set up the UI components for the health tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("health_header")
        self.header.setMaximumHeight(60)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.header_label = QLabel("HEALTH MONITORING")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E5FF;")
        self.header_layout.addWidget(self.header_label)
        
        self.header_layout.addStretch()
        
        # Add health entry button
        self.add_entry_btn = QPushButton("ADD ENTRY")
        self.add_entry_btn.setObjectName("primary_button")
        self.add_entry_btn.setIcon(QIcon("../assets/icons/add.png"))
        self.add_entry_btn.setIconSize(QSize(18, 18))
        self.header_layout.addWidget(self.add_entry_btn)
        
        self.layout.addWidget(self.header)
        
        # Health metrics summary
        self.metrics_container = QFrame()
        self.metrics_container.setObjectName("metrics_container")
        self.metrics_container.setMinimumHeight(100)
        self.metrics_container.setMaximumHeight(120)
        self.metrics_layout = QHBoxLayout(self.metrics_container)
        self.metrics_layout.setContentsMargins(15, 10, 15, 10)
        self.metrics_layout.setSpacing(20)
        
        # Add metric cards
        metrics = [
            {"label": "HEART RATE", "value": "72", "unit": "BPM", "icon": "heart.png"},
            {"label": "STEPS", "value": "8,432", "unit": "steps", "icon": "steps.png"},
            {"label": "SLEEP", "value": "7.5", "unit": "hours", "icon": "sleep.png"},
            {"label": "CALORIES", "value": "1,845", "unit": "kcal", "icon": "calories.png"}
        ]
        
        for metric in metrics:
            metric_card = self._create_metric_card(
                metric["label"], 
                metric["value"], 
                metric["unit"], 
                metric["icon"]
            )
            self.metrics_layout.addWidget(metric_card)
        
        self.layout.addWidget(self.metrics_container)
        
        # Charts and data tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("health_tabs")
        
        # Heart rate tab
        self.heart_rate_tab = QWidget()
        self.heart_rate_layout = QVBoxLayout(self.heart_rate_tab)
        self.heart_rate_layout.setContentsMargins(10, 15, 10, 10)
        
        # Heart rate chart
        self.heart_rate_chart = self._create_line_chart("Heart Rate", "#ff5252", 40, 180)
        self.heart_rate_layout.addWidget(self.heart_rate_chart)
        
        # Activity tab
        self.activity_tab = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_tab)
        self.activity_layout.setContentsMargins(10, 15, 10, 10)
        
        # Activity chart
        self.activity_chart = self._create_line_chart("Steps", "#4caf50", 0, 12000)
        self.activity_layout.addWidget(self.activity_chart)
        
        # Sleep tab
        self.sleep_tab = QWidget()
        self.sleep_layout = QVBoxLayout(self.sleep_tab)
        self.sleep_layout.setContentsMargins(10, 15, 10, 10)
        
        # Sleep chart
        self.sleep_chart = self._create_line_chart("Sleep Hours", "#2196f3", 0, 12)
        self.sleep_layout.addWidget(self.sleep_chart)
        
        # Nutrition tab
        self.nutrition_tab = QWidget()
        self.nutrition_layout = QVBoxLayout(self.nutrition_tab)
        self.nutrition_layout.setContentsMargins(10, 15, 10, 10)
        
        # Nutrition chart
        self.nutrition_chart = self._create_line_chart("Calories", "#ffc107", 0, 3000)
        self.nutrition_layout.addWidget(self.nutrition_chart)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.heart_rate_tab, "Heart Rate")
        self.tabs.addTab(self.activity_tab, "Activity")
        self.tabs.addTab(self.sleep_tab, "Sleep")
        self.tabs.addTab(self.nutrition_tab, "Nutrition")
        
        self.layout.addWidget(self.tabs)
        
        # Health recommendations
        self.recommendations_container = QFrame()
        self.recommendations_container.setObjectName("recommendations_container")
        self.recommendations_container.setMinimumHeight(120)
        self.recommendations_container.setMaximumHeight(150)
        self.recommendations_layout = QVBoxLayout(self.recommendations_container)
        self.recommendations_layout.setContentsMargins(15, 10, 15, 10)
        
        # Recommendations header
        self.recommendations_header = QLabel("RECOMMENDATIONS")
        self.recommendations_header.setObjectName("recommendations_header")
        self.recommendations_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00E5FF;")
        self.recommendations_layout.addWidget(self.recommendations_header)
        
        # Recommendations list
        self.recommendations_list = QLabel(
            "• Try to increase your daily steps to reach 10,000 steps/day\n"
            "• Your heart rate is within normal range, keep it up!\n"
            "• Consider going to bed 30 minutes earlier to improve sleep quality"
        )
        self.recommendations_list.setObjectName("recommendations_list")
        self.recommendations_list.setWordWrap(True)
        self.recommendations_layout.addWidget(self.recommendations_list)
        
        self.layout.addWidget(self.recommendations_container)
    
    def _create_metric_card(self, label, value, unit, icon_name):
        """Create a metric card widget"""
        card = QFrame()
        card.setObjectName("metric_card")
        card.setMinimumWidth(150)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setObjectName("metric_icon")
        icon_label.setFixedSize(QSize(32, 32))
        
        # Try to load icon
        icon_path = f"../assets/icons/{icon_name}"
        try:
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        except:
            # Default to colored circle if icon not found
            icon_label.setText("")
            icon_label.setStyleSheet(f"background-color: #00E5FF; border-radius: 16px;")
        
        card_layout.addWidget(icon_label)
        
        # Value and label
        value_container = QWidget()
        value_layout = QVBoxLayout(value_container)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setObjectName("metric_value")
        value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        value_layout.addWidget(value_label)
        
        unit_label = QLabel(f"{unit}")
        unit_label.setObjectName("metric_unit")
        unit_label.setStyleSheet("font-size: 12px; color: #aaa;")
        value_layout.addWidget(unit_label)
        
        label_label = QLabel(label)
        label_label.setObjectName("metric_label")
        label_label.setStyleSheet("font-size: 12px; color: #00E5FF;")
        value_layout.addWidget(label_label)
        
        card_layout.addWidget(value_container)
        
        return card
    
    def _create_line_chart(self, title, color, min_value, max_value):
        """Create a line chart for health data"""
        # Create chart
        chart = QChart()
        chart.setTitle(title)
        # Use direct reference to PyQt5.QtGui.QFont instead of QFont
        from PyQt5.QtGui import QFont as QtFont
        chart.setTitleFont(QtFont("Rajdhani", 12))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        
        # Create series
        series = QLineSeries()
        
        # Generate random data for the past 7 days
        now = datetime.now()
        for i in range(7):
            date = now - timedelta(days=6-i)
            timestamp = date.timestamp() * 1000  # Convert to milliseconds
            if title == "Heart Rate":
                value = random.uniform(60, 80)
            elif title == "Steps":
                value = random.uniform(6000, 10000)
            elif title == "Sleep Hours":
                value = random.uniform(6, 8)
            else:  # Calories
                value = random.uniform(1500, 2200)
            
            series.append(timestamp, value)
        
        chart.addSeries(series)
        
        # Setup axes
        axisX = QDateTimeAxis()
        axisX.setFormat("MMM dd")
        axisX.setTitleText("Date")
        axisX.setLabelsAngle(-45)
        
        axisY = QValueAxis()
        axisY.setRange(min_value, max_value)
        if title == "Steps":
            axisY.setLabelFormat("%.0f")
        elif title == "Calories":
            axisY.setLabelFormat("%.0f")
        else:
            axisY.setLabelFormat("%.1f")
        
        chart.addAxis(axisX, Qt.AlignBottom)
        chart.addAxis(axisY, Qt.AlignLeft)
        
        series.attachAxis(axisX)
        series.attachAxis(axisY)
        
        # Set series color
        pen = QPen(QColor(color))
        pen.setWidth(3)
        series.setPen(pen)
        
        # Create chart view
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        return chartView
    
    def _setup_connections(self):
        """Set up signal/slot connections"""
        self.add_entry_btn.clicked.connect(self._on_add_entry)
        self.tabs.currentChanged.connect(self._on_tab_changed)
    
    def _on_add_entry(self):
        """Handle add entry button click"""
        # In a real implementation, this would open a dialog to add health data
        # For this example, we'll do nothing
        pass
    
    def _on_tab_changed(self, index):
        """Handle tab change"""
        # In a real implementation, this might update the charts or reload data
        pass 