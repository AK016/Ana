#!/usr/bin/env python3
# Ana AI Assistant - Health Widget UI Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QTabWidget, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QFont
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSet, QBarSeries

import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CircularProgressBar(QWidget):
    """Custom circular progress bar widget with cyberpunk style"""
    
    def __init__(self, parent=None, value=0, maximum=100, text="", size=120):
        super().__init__(parent)
        self.value = value
        self.maximum = maximum
        self.text = text
        self.size = size
        self.setMinimumSize(QSize(size, size))
        self.setSizePolicy(
            QWidget.SizePolicy.Fixed,
            QWidget.SizePolicy.Fixed
        )
        
        # Cyberpunk color scheme
        self.bg_color = QColor(25, 25, 35)
        self.track_color = QColor(40, 40, 50)
        self.progress_color_start = QColor(0, 200, 200)
        self.progress_color_end = QColor(0, 255, 170)
        self.text_color = QColor(220, 220, 220)
        self.value_color = QColor(0, 255, 200)
        
    def setValue(self, value):
        self.value = value
        self.update()
        
    def sizeHint(self):
        return QSize(self.size, self.size)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Calculate sizes
        width = self.width()
        height = self.height()
        margin = 10
        size = min(width, height) - 2 * margin
        center_x = width / 2
        center_y = height / 2
        
        # Draw track
        track_width = size / 10
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.track_color)
        painter.drawEllipse(
            int(center_x - size/2), 
            int(center_y - size/2),
            int(size), 
            int(size)
        )
        
        # Draw progress
        angle = self.value / self.maximum * 360
        
        # Create gradient
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, self.progress_color_start)
        gradient.setColorAt(1, self.progress_color_end)
        
        painter.setBrush(self.bg_color)
        painter.drawEllipse(
            int(center_x - size/2 + track_width), 
            int(center_y - size/2 + track_width),
            int(size - 2 * track_width), 
            int(size - 2 * track_width)
        )
        
        # Draw progress arc
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        
        path = QPainterPath()
        path.moveTo(center_x, center_y)
        path.arcTo(
            int(center_x - size/2), 
            int(center_y - size/2),
            int(size), 
            int(size),
            90, 
            -angle
        )
        path.lineTo(center_x, center_y)
        
        painter.drawPath(path)
        
        # Draw inner circle
        painter.setBrush(self.bg_color)
        painter.drawEllipse(
            int(center_x - size/2 + track_width), 
            int(center_y - size/2 + track_width),
            int(size - 2 * track_width), 
            int(size - 2 * track_width)
        )
        
        # Draw text
        painter.setPen(self.text_color)
        font = QFont()
        font.setPointSize(int(size / 12))
        painter.setFont(font)
        
        text_rect = self.rect().adjusted(0, int(size/2), 0, 0)
        painter.drawText(text_rect, Qt.AlignHCenter, self.text)
        
        # Draw value
        value_text = f"{self.value}"
        painter.setPen(self.value_color)
        font.setPointSize(int(size / 8))
        painter.setFont(font)
        
        value_rect = self.rect().adjusted(0, -int(size/8), 0, 0)
        painter.drawText(value_rect, Qt.AlignHCenter | Qt.AlignVCenter, value_text)

class HealthWidget(QWidget):
    """Health data widget with cyberpunk aesthetics"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the health widget UI"""
        main_layout = QVBoxLayout(self)
        
        # Title with cyberpunk style
        title_label = QLabel("HEALTH MONITORING")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #00ffcc;
            background-color: #1a1a2e;
            padding: 8px;
            border-left: 3px solid #00ffcc;
            font-size: 16px;
            font-weight: bold;
        """)
        main_layout.addWidget(title_label)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                background-color: #1a1a2e;
                border: 1px solid #333366;
            }
            QTabBar::tab {
                background-color: #222244;
                color: #aaaacc;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a2e;
                color: #00ffcc;
                border-top: 2px solid #00ffcc;
            }
        """)
        
        # Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Health score section
        score_layout = QHBoxLayout()
        self.health_score = CircularProgressBar(value=85, text="HEALTH SCORE")
        score_layout.addWidget(self.health_score)
        
        self.score_details = QLabel(
            "Your health score reflects your overall well-being based on activity, "
            "sleep, stress levels, and heart performance."
        )
        self.score_details.setWordWrap(True)
        self.score_details.setStyleSheet("color: #aaaacc; padding: 10px;")
        score_layout.addWidget(self.score_details)
        overview_layout.addLayout(score_layout)
        
        # Key metrics layout
        metrics_layout = QHBoxLayout()
        
        # Steps metric
        self.steps_progress = CircularProgressBar(value=7500, maximum=10000, text="STEPS", size=100)
        metrics_layout.addWidget(self.steps_progress)
        
        # Sleep metric
        self.sleep_progress = CircularProgressBar(value=7, maximum=9, text="SLEEP (HRS)", size=100)
        metrics_layout.addWidget(self.sleep_progress)
        
        # Stress metric
        self.stress_progress = CircularProgressBar(value=35, maximum=100, text="STRESS", size=100)
        metrics_layout.addWidget(self.stress_progress)
        
        # Heart rate metric
        self.heart_progress = CircularProgressBar(value=72, maximum=100, text="AVG HR", size=100)
        metrics_layout.addWidget(self.heart_progress)
        
        overview_layout.addLayout(metrics_layout)
        
        # Daily summary
        self.summary_label = QLabel("Daily Health Summary")
        self.summary_label.setStyleSheet("color: #00ffcc; font-weight: bold; margin-top: 10px;")
        overview_layout.addWidget(self.summary_label)
        
        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet("""
            background-color: #222244;
            color: #aaaacc;
            padding: 10px;
            border-left: 2px solid #00ffcc;
        """)
        self.summary_text.setText(
            "You're having a good health day! Your step count is on track, "
            "and your sleep quality was excellent last night. Your stress levels "
            "are moderate, which is normal for a weekday. Try to take short breaks "
            "throughout the day to maintain your well-being."
        )
        overview_layout.addWidget(self.summary_text)
        
        # Refresh button
        refresh_btn = QPushButton("REFRESH DATA")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aaaa;
                color: #000000;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ffcc;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        overview_layout.addWidget(refresh_btn)
        
        # Add tab
        self.tabs.addTab(overview_tab, "Overview")
        
        # Activity Tab
        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        
        # Activity chart
        self.activity_chart = self.create_activity_chart()
        activity_layout.addWidget(self.activity_chart)
        
        # Activity stats
        activity_stats = QWidget()
        stats_layout = QHBoxLayout(activity_stats)
        
        stats_layout.addWidget(self.create_stat_label("Daily Average", "8,243 steps"))
        stats_layout.addWidget(self.create_stat_label("Weekly Total", "57,702 steps"))
        stats_layout.addWidget(self.create_stat_label("Calories Burned", "2,347 kcal"))
        stats_layout.addWidget(self.create_stat_label("Distance", "5.8 km"))
        
        activity_layout.addWidget(activity_stats)
        
        # Add tab
        self.tabs.addTab(activity_tab, "Activity")
        
        # Sleep Tab
        sleep_tab = QWidget()
        sleep_layout = QVBoxLayout(sleep_tab)
        
        # Sleep chart
        self.sleep_chart = self.create_sleep_chart()
        sleep_layout.addWidget(self.sleep_chart)
        
        # Sleep stats
        sleep_stats = QWidget()
        sleep_stats_layout = QHBoxLayout(sleep_stats)
        
        sleep_stats_layout.addWidget(self.create_stat_label("Total Sleep", "7h 15m"))
        sleep_stats_layout.addWidget(self.create_stat_label("Deep Sleep", "1h 45m"))
        sleep_stats_layout.addWidget(self.create_stat_label("REM Sleep", "1h 30m"))
        sleep_stats_layout.addWidget(self.create_stat_label("Sleep Score", "82/100"))
        
        sleep_layout.addWidget(sleep_stats)
        
        # Add tab
        self.tabs.addTab(sleep_tab, "Sleep")
        
        # Heart Rate Tab
        heart_tab = QWidget()
        heart_layout = QVBoxLayout(heart_tab)
        
        # Heart rate chart
        self.heart_chart = self.create_heart_rate_chart()
        heart_layout.addWidget(self.heart_chart)
        
        # Heart rate stats
        heart_stats = QWidget()
        heart_stats_layout = QHBoxLayout(heart_stats)
        
        heart_stats_layout.addWidget(self.create_stat_label("Average", "72 bpm"))
        heart_stats_layout.addWidget(self.create_stat_label("Maximum", "115 bpm"))
        heart_stats_layout.addWidget(self.create_stat_label("Minimum", "58 bpm"))
        heart_stats_layout.addWidget(self.create_stat_label("Resting", "65 bpm"))
        
        heart_layout.addWidget(heart_stats)
        
        # Add tab
        self.tabs.addTab(heart_tab, "Heart Rate")
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Apply global styles
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
    
    def create_stat_label(self, title, value):
        """Create a styled stat label"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #aaaacc; font-size: 12px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #00ffcc; font-size: 16px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.setStyleSheet("""
            background-color: #222244;
            border-radius: 4px;
            padding: 8px;
            margin: 5px;
        """)
        
        return widget
        
    def create_activity_chart(self):
        """Create activity chart using matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#222244')
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        steps = [7500, 9200, 8100, 10500, 7800, 12300, 6500]
        goal = [10000] * 7
        
        ax.bar(days, steps, color='#00cccc', alpha=0.7, width=0.6)
        ax.plot(days, goal, 'o-', color='#ff5566', linewidth=2, label='Goal')
        
        ax.set_title('Weekly Step Count', color='#e0e0e0', fontsize=14)
        ax.tick_params(colors='#aaaacc')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333366')
        ax.spines['left'].set_color('#333366')
        ax.grid(True, color='#333366', linestyle='--', alpha=0.3)
        
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_sleep_chart(self):
        """Create sleep chart using matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#222244')
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        deep_sleep = [1.7, 1.5, 2.0, 1.8, 1.5, 2.2, 2.1]
        light_sleep = [4.0, 3.8, 3.5, 4.2, 3.7, 4.5, 4.2]
        rem_sleep = [1.5, 1.3, 1.8, 1.5, 1.2, 1.8, 1.7]
        
        width = 0.5
        ax.bar(days, deep_sleep, width, label='Deep Sleep', color='#3333aa')
        ax.bar(days, light_sleep, width, bottom=deep_sleep, label='Light Sleep', color='#5555dd')
        ax.bar(days, rem_sleep, width, bottom=[d+l for d,l in zip(deep_sleep, light_sleep)], 
               label='REM Sleep', color='#00cccc')
        
        ax.set_title('Weekly Sleep Patterns', color='#e0e0e0', fontsize=14)
        ax.set_ylabel('Hours', color='#aaaacc')
        ax.tick_params(colors='#aaaacc')
        ax.legend(facecolor='#222244', edgecolor='#333366', labelcolor='#e0e0e0')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333366')
        ax.spines['left'].set_color('#333366')
        ax.grid(True, color='#333366', linestyle='--', alpha=0.3)
        
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_heart_rate_chart(self):
        """Create heart rate chart using matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#222244')
        
        # Generate sample heart rate data
        hours = list(range(24))
        heart_rates = [65, 63, 60, 58, 58, 60, 72, 85, 80, 75, 78, 82, 
                       80, 77, 75, 76, 80, 88, 85, 78, 72, 68, 66, 64]
        
        ax.plot(hours, heart_rates, '-', color='#ff3366', linewidth=2)
        ax.fill_between(hours, heart_rates, 50, alpha=0.2, color='#ff3366')
        
        ax.set_title('24-Hour Heart Rate', color='#e0e0e0', fontsize=14)
        ax.set_xlabel('Hour', color='#aaaacc')
        ax.set_ylabel('BPM', color='#aaaacc')
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlim(0, 23)
        ax.set_ylim(50, 100)
        
        ax.tick_params(colors='#aaaacc')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333366')
        ax.spines['left'].set_color('#333366')
        ax.grid(True, color='#333366', linestyle='--', alpha=0.3)
        
        canvas = FigureCanvas(fig)
        return canvas
    
    def update_data(self, health_data):
        """Update the UI with new health data"""
        if not health_data:
            return
            
        # Update health score
        if "health_score" in health_data:
            self.health_score.setValue(health_data["health_score"])
            
        # Update steps
        if "steps" in health_data:
            steps = health_data["steps"]["count"]
            self.steps_progress.setValue(min(steps, 10000))
            
        # Update sleep
        if "sleep" in health_data:
            sleep_duration = health_data["sleep"].get("duration_minutes", 0) / 60
            self.sleep_progress.setValue(sleep_duration)
            
        # Update stress
        if "stress" in health_data:
            stress_level = health_data["stress"]["level"]
            self.stress_progress.setValue(stress_level)
            
        # Update heart rate
        if "heart_rate" in health_data:
            heart_rate = health_data["heart_rate"]["average"]
            self.heart_progress.setValue(heart_rate)
            
        # Update summary text
        if "date" in health_data:
            from datetime import datetime
            date_obj = datetime.strptime(health_data["date"], "%Y-%m-%d")
            date_str = date_obj.strftime("%B %d, %Y")
            self.summary_label.setText(f"Health Summary for {date_str}")
            
        # Get interpretation if available
        if "interpretation" in health_data:
            self.summary_text.setText(health_data["interpretation"])
            
    def refresh(self):
        """Emit signal to request data refresh"""
        self.refresh_requested.emit() 