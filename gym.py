import sys
import sqlite3
from datetime import datetime, timedelta
 


from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, 
                         QDate, QTimer, QRect, QSize, QPoint)
from PyQt5.QtGui import (QColor, QLinearGradient, QPainter, QFont, QIcon, 
                         QPixmap, QBrush, QPalette)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QLineEdit, QComboBox, 
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QScrollArea, QFrame, QMessageBox, QSizePolicy, QSpacerItem,
    QGraphicsDropShadowEffect, QToolButton, QTabWidget, QDialog,QTabWidget,  QFormLayout, QDialog
)


class GymManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitPro Gym Management")
        self.setWindowIcon(QIcon.fromTheme("applications-fitness"))
        self.setMinimumSize(1200, 800)
        
        # Database setup
        self.init_db()
        
        # UI Setup
        self.init_ui()
        
        # Load initial data
        self.load_members()
        self.load_attendance()
        self.load_payments()
        self.update_dashboard()
        
        # Start clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        
        # Apply stylesheet
        self.setStyleSheet(self.get_stylesheet())
        
    def init_db(self):
        self.conn = sqlite3.connect("gym_management.db")
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            dob TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            membership_type TEXT,
            join_date TEXT,
            expiry_date TEXT,
            status TEXT DEFAULT 'Active'
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            date TEXT,
            time_in TEXT,
            time_out TEXT,
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL,
            payment_date TEXT,
            due_date TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'Paid',
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
        """)
        
        self.conn.commit()
    
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(20)
        
        # Logo and title
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 0, 20, 20)
        
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(":/icons/gym_icon.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_name = QLabel("FitPro")
        self.logo_name.setObjectName("logoName")
        self.logo = QLabel("🏋️")  # Using emoji as fallback
        self.logo.setStyleSheet("font-size: 24px;")
        
        logo_layout.addWidget(self.logo)
        logo_layout.addWidget(self.logo_name)
        logo_layout.addStretch()
        
        sidebar_layout.addLayout(logo_layout)
        
        # Menu buttons
        self.btn_dashboard = self.create_menu_button("Dashboard", ":/icons/dashboard.png")
        self.btn_members = self.create_menu_button("Members", ":/icons/members.png")
        self.btn_attendance = self.create_menu_button("Attendance", ":/icons/attendance.png")
        self.btn_payments = self.create_menu_button("Payments", ":/icons/payments.png")
        self.btn_reports = self.create_menu_button("Reports", ":/icons/reports.png")
        self.btn_settings = self.create_menu_button("Settings", ":/icons/settings.png")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_members)
        sidebar_layout.addWidget(self.btn_attendance)
        sidebar_layout.addWidget(self.btn_payments)
        sidebar_layout.addWidget(self.btn_reports)
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()
        
        # User profile at bottom
        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(20, 20, 20, 0)
        
        self.user_avatar = QLabel()
        self.user_avatar.setPixmap(QPixmap(":/icons/user.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.user_info = QVBoxLayout()
        self.user_info.setSpacing(2)
        
        self.user_name = QLabel("Admin")
        self.user_name.setObjectName("userName")
        
        self.user_role = QLabel("Administrator")
        self.user_role.setObjectName("userRole")
        
        self.user_info.addWidget(self.user_name)
        self.user_info.addWidget(self.user_role)
        
        user_layout.addWidget(self.user_avatar)
        user_layout.addLayout(self.user_info)
        user_layout.addStretch()
        
        sidebar_layout.addLayout(user_layout)
        
        # Main content area
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        self.top_bar = QFrame()
        self.top_bar.setObjectName("topBar")
        self.top_bar.setFixedHeight(60)
        
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("titleLabel")
        
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.clock_label)
        
        content_layout.addWidget(self.top_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_dashboard_page()
        self.create_members_page()
        self.create_attendance_page()
        self.create_payments_page()
        self.create_reports_page()
        self.create_settings_page()
        
        # Add sidebar and content area to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        # Connect menu buttons
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_members.clicked.connect(lambda: self.switch_page(1))
        self.btn_attendance.clicked.connect(lambda: self.switch_page(2))
        self.btn_payments.clicked.connect(lambda: self.switch_page(3))
        self.btn_reports.clicked.connect(lambda: self.switch_page(4))
        self.btn_settings.clicked.connect(lambda: self.switch_page(5))
        
        # Apply shadow effects
        self.apply_shadow_effect(self.sidebar, 20)
        self.apply_shadow_effect(self.top_bar, 10)
    
    def create_menu_button(self, text, icon_path):
        btn = QToolButton()
        btn.setText(text)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(24, 24))
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn.setObjectName("menuButton")
        btn.setCursor(Qt.PointingHandCursor)
        return btn
    
    def apply_shadow_effect(self, widget, blur_radius):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_members_card = self.create_stat_card("Total Members", "0", QColor(70, 130, 180), ":/icons/members.png")
        self.active_members_card = self.create_stat_card("Active Members", "0", QColor(60, 179, 113), ":/icons/active.png")
        self.expired_members_card = self.create_stat_card("Expired Members", "0", QColor(220, 20, 60), ":/icons/expired.png")
        self.today_attendance_card = self.create_stat_card("Today's Attendance", "0", QColor(255, 140, 0), ":/icons/attendance_today.png")
        
        stats_layout.addWidget(self.total_members_card)
        stats_layout.addWidget(self.active_members_card)
        stats_layout.addWidget(self.expired_members_card)
        stats_layout.addWidget(self.today_attendance_card)
        
        layout.addLayout(stats_layout)
        
        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Attendance chart
        attendance_chart = QFrame()
        attendance_chart.setObjectName("chartFrame")
        attendance_chart.setMinimumHeight(300)
        
        charts_layout.addWidget(attendance_chart, 2)
        
        # Membership types chart
        membership_chart = QFrame()
        membership_chart.setObjectName("chartFrame")
        membership_chart.setMinimumHeight(300)
        
        charts_layout.addWidget(membership_chart, 1)
        
        layout.addLayout(charts_layout)
        
        # Recent activity
        recent_activity_label = QLabel("Recent Activity")
        recent_activity_label.setObjectName("sectionLabel")
        
        self.activity_table = QTableWidget()
        self.activity_table.setObjectName("activityTable")
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Member", "Activity", "Date", "Time"])
        self.activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.setShowGrid(False)
        
        layout.addWidget(recent_activity_label)
        layout.addWidget(self.activity_table)
        
        self.stacked_widget.addWidget(page)
    
    def create_stat_card(self, title, value, color, icon_path):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Animate on hover
        card.enterEvent = lambda event: self.animate_card_hover(card, True)
        card.leaveEvent = lambda event: self.animate_card_hover(card, False)
        
        return card
    
    def animate_card_hover(self, card, hover):
        animation = QPropertyAnimation(card, b"pos")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        
        if hover:
             animation.setEndValue(card.pos() + QPoint(0, -5))  # Fixed QPoint usage
        else:
             animation.setEndValue(card.pos() + QPoint(0, 5))
        
        animation.start()
    
    def create_members_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        
        members_label = QLabel("Members Management")
        members_label.setObjectName("sectionLabel")
        
        self.add_member_btn = QPushButton("Add New Member")
        self.add_member_btn.setObjectName("addButton")
        self.add_member_btn.setIcon(QIcon(":/icons/add.png"))
        self.add_member_btn.setCursor(Qt.PointingHandCursor)
        self.add_member_btn.clicked.connect(self.show_add_member_dialog)
        
        header_layout.addWidget(members_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_member_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search members...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.load_members)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Expired"])
        self.status_filter.setObjectName("filterCombo")
        self.status_filter.currentIndexChanged.connect(self.load_members)
        
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setObjectName("membersTable")
        self.members_table.setColumnCount(8)
        self.members_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Membership", "Join Date", "Expiry Date", "Status", "Actions"])
        self.members_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.members_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.members_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.members_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.members_table)
        
        self.stacked_widget.addWidget(page)
    
    def create_attendance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        attendance_label = QLabel("Attendance Tracking")
        attendance_label.setObjectName("sectionLabel")
        
        self.mark_attendance_btn = QPushButton("Mark Attendance")
        self.mark_attendance_btn.setObjectName("addButton")
        self.mark_attendance_btn.setIcon(QIcon(":/icons/checkin.png"))
        self.mark_attendance_btn.setCursor(Qt.PointingHandCursor)
        self.mark_attendance_btn.clicked.connect(self.show_mark_attendance_dialog)
        
        header_layout.addWidget(attendance_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mark_attendance_btn)
        
        layout.addLayout(header_layout)
        
        # Date filter
        date_filter_layout = QHBoxLayout()
        date_filter_layout.setSpacing(15)
        
        date_filter_layout.addWidget(QLabel("Date:"))
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setObjectName("dateFilter")
        self.date_filter.dateChanged.connect(self.load_attendance)
        
        date_filter_layout.addWidget(self.date_filter)
        date_filter_layout.addStretch()
        
        layout.addLayout(date_filter_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setObjectName("attendanceTable")
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels(["ID", "Member", "Date", "Time In", "Time Out", "Duration"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.attendance_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.attendance_table.verticalHeader().setVisible(False)
        self.attendance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.attendance_table)
        
        self.stacked_widget.addWidget(page)
    
    def create_payments_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        payments_label = QLabel("Payments Management")
        payments_label.setObjectName("sectionLabel")
        
        self.record_payment_btn = QPushButton("Record Payment")
        self.record_payment_btn.setObjectName("addButton")
        self.record_payment_btn.setIcon(QIcon(":/icons/payment.png"))
        self.record_payment_btn.setCursor(Qt.PointingHandCursor)
        self.record_payment_btn.clicked.connect(self.show_record_payment_dialog)
        
        header_layout.addWidget(payments_label)
        header_layout.addStretch()
        header_layout.addWidget(self.record_payment_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        self.payment_search_input = QLineEdit()
        self.payment_search_input.setPlaceholderText("Search payments...")
        self.payment_search_input.setObjectName("searchInput")
        self.payment_search_input.textChanged.connect(self.load_payments)
        
        self.payment_status_filter = QComboBox()
        self.payment_status_filter.addItems(["All", "Paid", "Pending"])
        self.payment_status_filter.setObjectName("filterCombo")
        self.payment_status_filter.currentIndexChanged.connect(self.load_payments)
        
        filter_layout.addWidget(self.payment_search_input)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.payment_status_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setObjectName("paymentsTable")
        self.payments_table.setColumnCount(7)
        self.payments_table.setHorizontalHeaderLabels(["ID", "Member", "Amount", "Payment Date", "Due Date", "Status", "Method"])
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.payments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.payments_table.verticalHeader().setVisible(False)
        self.payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.payments_table)
        
        self.stacked_widget.addWidget(page)
    
    def create_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        reports_label = QLabel("Reports & Analytics")
        reports_label.setObjectName("sectionLabel")
        
        layout.addWidget(reports_label)
        
        # Report type selection
        report_type_layout = QHBoxLayout()
        report_type_layout.setSpacing(15)
        
        report_type_layout.addWidget(QLabel("Report Type:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Attendance Summary", 
            "Membership Types", 
            "Revenue Analysis", 
            "Member Growth"
        ])
        self.report_type_combo.setObjectName("reportCombo")
        
        report_type_layout.addWidget(self.report_type_combo)
        report_type_layout.addStretch()
        
        # Date range
        report_type_layout.addWidget(QLabel("Date Range:"))
        
        self.report_start_date = QDateEdit()
        self.report_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.report_start_date.setCalendarPopup(True)
        self.report_start_date.setObjectName("dateFilter")
        
        self.report_end_date = QDateEdit()
        self.report_end_date.setDate(QDate.currentDate())
        self.report_end_date.setCalendarPopup(True)
        self.report_end_date.setObjectName("dateFilter")
        
        report_type_layout.addWidget(self.report_start_date)
        report_type_layout.addWidget(QLabel("to"))
        report_type_layout.addWidget(self.report_end_date)
        
        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.setObjectName("actionButton")
        self.generate_report_btn.clicked.connect(self.generate_report)
        
        report_type_layout.addWidget(self.generate_report_btn)
        
        layout.addLayout(report_type_layout)
        
        # Report display area
        self.report_display = QFrame()
        self.report_display.setObjectName("reportDisplay")
        self.report_display.setMinimumHeight(500)
        
        layout.addWidget(self.report_display)
        
        self.stacked_widget.addWidget(page)
    
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        settings_label = QLabel("System Settings")
        settings_label.setObjectName("sectionLabel")
        
        layout.addWidget(settings_label)
        
        # Settings tabs
        settings_tabs = QTabWidget()
        settings_tabs.setObjectName("settingsTabs")
        
        # General settings
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(20, 20, 20, 20)
        general_layout.setSpacing(15)
        
        # Gym name
        gym_name_layout = QHBoxLayout()
        gym_name_layout.addWidget(QLabel("Gym Name:"))
        
        self.gym_name_input = QLineEdit("FitPro Gym")
        gym_name_layout.addWidget(self.gym_name_input)
        gym_name_layout.addStretch()
        
        general_layout.addLayout(gym_name_layout)
        
        # Membership types
        membership_types_label = QLabel("Membership Types:")
        general_layout.addWidget(membership_types_label)
        
        self.membership_types_table = QTableWidget()
        self.membership_types_table.setColumnCount(2)
        self.membership_types_table.setHorizontalHeaderLabels(["Type", "Duration (months)"])
        self.membership_types_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.membership_types_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.membership_types_table.verticalHeader().setVisible(False)
        
        # Add default membership types
        self.membership_types_table.setRowCount(3)
        self.membership_types_table.setItem(0, 0, QTableWidgetItem("Basic"))
        self.membership_types_table.setItem(0, 1, QTableWidgetItem("1"))
        self.membership_types_table.setItem(1, 0, QTableWidgetItem("Standard"))
        self.membership_types_table.setItem(1, 1, QTableWidgetItem("3"))
        self.membership_types_table.setItem(2, 0, QTableWidgetItem("Premium"))
        self.membership_types_table.setItem(2, 1, QTableWidgetItem("12"))
        
        general_layout.addWidget(self.membership_types_table)
        
        # Add/remove buttons
        membership_buttons_layout = QHBoxLayout()
        
        self.add_membership_type_btn = QPushButton("Add Type")
        self.add_membership_type_btn.setObjectName("actionButton")
        self.add_membership_type_btn.clicked.connect(self.add_membership_type)
        
        self.remove_membership_type_btn = QPushButton("Remove Selected")
        self.remove_membership_type_btn.setObjectName("actionButton")
        self.remove_membership_type_btn.clicked.connect(self.remove_membership_type)
        
        membership_buttons_layout.addWidget(self.add_membership_type_btn)
        membership_buttons_layout.addWidget(self.remove_membership_type_btn)
        membership_buttons_layout.addStretch()
        
        general_layout.addLayout(membership_buttons_layout)
        
        # Save settings button
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.setObjectName("saveButton")
        self.save_settings_btn.clicked.connect(self.save_settings)
        
        general_layout.addStretch()
        general_layout.addWidget(self.save_settings_btn)
        
        settings_tabs.addTab(general_tab, "General")
        
        # Add more tabs as needed...
        
        layout.addWidget(settings_tabs)
        
        self.stacked_widget.addWidget(page)
    
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Update title
        titles = [
            "Dashboard",
            "Members Management",
            "Attendance Tracking",
            "Payments Management",
            "Reports & Analytics",
            "System Settings"
        ]
        self.title_label.setText(titles[index])
        
        # Highlight active button
        buttons = [
            self.btn_dashboard,
            self.btn_members,
            self.btn_attendance,
            self.btn_payments,
            self.btn_reports,
            self.btn_settings
        ]
        
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("background-color: rgba(255, 255, 255, 30);")
            else:
                btn.setStyleSheet("")
    
    def load_members(self):
        search_text = self.search_input.text().strip()
        status_filter = self.status_filter.currentText()
        
        query = "SELECT id, name, phone, membership_type, join_date, expiry_date, status FROM members WHERE 1=1"
        params = []
        
        if search_text:
            query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY name"
        
        self.cursor.execute(query, params)
        members = self.cursor.fetchall()
        
        self.members_table.setRowCount(len(members))
        
        for row, member in enumerate(members):
            for col, value in enumerate(member[:7]):  # First 7 columns
                item = QTableWidgetItem(str(value))
                self.members_table.setItem(row, col, item)
            
            # Add action buttons
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)
            
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon(":/icons/view.png"))
            view_btn.setToolTip("View Details")
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setObjectName("actionButton")
            view_btn.clicked.connect(lambda _, m=member: self.view_member_details(m[0]))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon(":/icons/edit.png"))
            edit_btn.setToolTip("Edit")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setObjectName("actionButton")
            edit_btn.clicked.connect(lambda _, m=member: self.edit_member(m[0]))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon(":/icons/delete.png"))
            delete_btn.setToolTip("Delete")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setObjectName("actionButton")
            delete_btn.clicked.connect(lambda _, m=member: self.delete_member(m[0]))
            
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            
            self.members_table.setCellWidget(row, 7, btn_widget)
    
    def load_attendance(self):
        date = self.date_filter.date().toString("yyyy-MM-dd")
        
        query = """
        SELECT a.id, m.name, a.date, a.time_in, a.time_out 
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        WHERE a.date = ?
        ORDER BY a.time_in DESC
        """
        
        self.cursor.execute(query, (date,))
        attendance_records = self.cursor.fetchall()
        
        self.attendance_table.setRowCount(len(attendance_records))
        
        for row, record in enumerate(attendance_records):
            for col, value in enumerate(record[:5]):  # First 5 columns
                item = QTableWidgetItem(str(value))
                self.attendance_table.setItem(row, col, item)
            
            # Calculate duration if time_out exists
            if record[4]:  # time_out
                time_in = datetime.strptime(record[3], "%H:%M:%S")
                time_out = datetime.strptime(record[4], "%H:%M:%S")
                duration = time_out - time_in
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m"
            else:
                duration_str = "In Progress"
            
            duration_item = QTableWidgetItem(duration_str)
            self.attendance_table.setItem(row, 5, duration_item)
            
            # Add action button for check-out if needed
            if not record[4]:  # No time_out
                btn_checkout = QPushButton("Check Out")
                btn_checkout.setObjectName("actionButton")
                btn_checkout.setCursor(Qt.PointingHandCursor)
                btn_checkout.clicked.connect(lambda _, r=record: self.check_out_member(r[0]))
                self.attendance_table.setCellWidget(row, 5, btn_checkout)
    
    def load_payments(self):
        search_text = self.payment_search_input.text().strip()
        status_filter = self.payment_status_filter.currentText()
        
        query = """
        SELECT p.id, m.name, p.amount, p.payment_date, p.due_date, p.status, p.payment_method 
        FROM payments p
        JOIN members m ON p.member_id = m.id
        WHERE 1=1
        """
        params = []
        
        if search_text:
            query += " AND (m.name LIKE ? OR p.id LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        if status_filter != "All":
            query += " AND p.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY p.payment_date DESC"
        
        self.cursor.execute(query, params)
        payments = self.cursor.fetchall()
        
        self.payments_table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            for col, value in enumerate(payment[:7]):  # All 7 columns
                item = QTableWidgetItem(str(value))
                
                # Format amount as currency
                if col == 2:
                    item.setText(f"${float(value):.2f}")
                
                self.payments_table.setItem(row, col, item)
    
    def update_dashboard(self):
        # Update stats cards
        self.cursor.execute("SELECT COUNT(*) FROM members")
        total_members = self.cursor.fetchone()[0]
        self.total_members_card.findChild(QLabel, "statValue").setText(str(total_members))
        
        self.cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        active_members = self.cursor.fetchone()[0]
        self.active_members_card.findChild(QLabel, "statValue").setText(str(active_members))
        
        self.cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Expired'")
        expired_members = self.cursor.fetchone()[0]
        self.expired_members_card.findChild(QLabel, "statValue").setText(str(expired_members))
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
        today_attendance = self.cursor.fetchone()[0]
        self.today_attendance_card.findChild(QLabel, "statValue").setText(str(today_attendance))
        
        # Load recent activity (last 10 attendance records)
        self.cursor.execute("""
        SELECT m.name, a.date, a.time_in, a.time_out 
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        ORDER BY a.date DESC, a.time_in DESC
        LIMIT 10
        """)
        activities = self.cursor.fetchall()
        
        self.activity_table.setRowCount(len(activities))
        
        for row, activity in enumerate(activities):
            member_item = QTableWidgetItem(activity[0])
            date_item = QTableWidgetItem(activity[1])
            
            # Determine activity type
            if activity[3]:  # Has time_out
                activity_type = "Workout Completed"
            else:
                activity_type = "Checked In"
            
            activity_item = QTableWidgetItem(activity_type)
            time_item = QTableWidgetItem(activity[2])
            
            self.activity_table.setItem(row, 0, member_item)
            self.activity_table.setItem(row, 1, activity_item)
            self.activity_table.setItem(row, 2, date_item)
            self.activity_table.setItem(row, 3, time_item)
    
    def show_add_member_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Member")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)
        
        self.member_name_input = QLineEdit()
        self.member_gender_combo = QComboBox()
        self.member_gender_combo.addItems(["Male", "Female", "Other"])
        
        self.member_dob_input = QDateEdit()
        self.member_dob_input.setCalendarPopup(True)
        self.member_dob_input.setMaximumDate(QDate.currentDate())
        
        self.member_phone_input = QLineEdit()
        self.member_email_input = QLineEdit()
        self.member_address_input = QLineEdit()
        
        self.member_type_combo = QComboBox()
        self.member_type_combo.addItems(["Basic", "Standard", "Premium"])
        
        join_date = QDate.currentDate()
        self.member_join_date_input = QDateEdit(join_date)
        self.member_join_date_input.setCalendarPopup(True)
        self.member_join_date_input.setMaximumDate(QDate.currentDate())
        
        # Calculate expiry date based on membership type
        self.member_type_combo.currentTextChanged.connect(lambda: self.update_expiry_date())
        
        self.member_expiry_date_input = QDateEdit()
        self.member_expiry_date_input.setCalendarPopup(True)
        self.member_expiry_date_input.setEnabled(False)
        self.update_expiry_date()  # Set initial value
        
        form_layout.addRow("Full Name:", self.member_name_input)
        form_layout.addRow("Gender:", self.member_gender_combo)
        form_layout.addRow("Date of Birth:", self.member_dob_input)
        form_layout.addRow("Phone:", self.member_phone_input)
        form_layout.addRow("Email:", self.member_email_input)
        form_layout.addRow("Address:", self.member_address_input)
        form_layout.addRow("Membership Type:", self.member_type_combo)
        form_layout.addRow("Join Date:", self.member_join_date_input)
        form_layout.addRow("Expiry Date:", self.member_expiry_date_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(lambda: self.save_member(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def update_expiry_date(self):
        membership_type = self.member_type_combo.currentText()
        join_date = self.member_join_date_input.date()
        
        months = 1  # Default to Basic (1 month)
        if membership_type == "Standard":
            months = 3
        elif membership_type == "Premium":
            months = 12
        
        expiry_date = join_date.addMonths(months)
        self.member_expiry_date_input.setDate(expiry_date)
    
    def save_member(self, dialog):
        name = self.member_name_input.text().strip()
        phone = self.member_phone_input.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Validation Error", "Name and phone are required fields.")
            return
        
        try:
            self.cursor.execute("""
            INSERT INTO members (
                name, gender, dob, phone, email, address, 
                membership_type, join_date, expiry_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                self.member_gender_combo.currentText(),
                self.member_dob_input.date().toString("yyyy-MM-dd"),
                phone,
                self.member_email_input.text().strip(),
                self.member_address_input.text().strip(),
                self.member_type_combo.currentText(),
                self.member_join_date_input.date().toString("yyyy-MM-dd"),
                self.member_expiry_date_input.date().toString("yyyy-MM-dd")
            ))
            
            self.conn.commit()
            QMessageBox.information(self, "Success", "Member added successfully!")
            self.load_members()
            self.update_dashboard()
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add member: {str(e)}")
    
    def view_member_details(self, member_id):
        self.cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = self.cursor.fetchone()
        
        if not member:
            QMessageBox.warning(self, "Not Found", "Member not found.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Member Details")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Member info
        info_layout = QFormLayout()
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(10)
        
        labels = [
            "ID:", "Name:", "Gender:", "Date of Birth:", "Phone:", 
            "Email:", "Address:", "Membership Type:", "Join Date:", 
            "Expiry Date:", "Status:"
        ]
        
        for i, label in enumerate(labels):
            value = str(member[i]) if member[i] is not None else "N/A"
            info_layout.addRow(QLabel(label), QLabel(value))
        
        layout.addLayout(info_layout)
        
        # Tabs for additional info
        tabs = QTabWidget()
        
        # Attendance history
        attendance_tab = QWidget()
        attendance_layout = QVBoxLayout(attendance_tab)
        
        self.member_attendance_table = QTableWidget()
        self.member_attendance_table.setColumnCount(4)
        self.member_attendance_table.setHorizontalHeaderLabels(["Date", "Time In", "Time Out", "Duration"])
        self.member_attendance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.member_attendance_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.member_attendance_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.member_attendance_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.member_attendance_table.verticalHeader().setVisible(False)
        self.member_attendance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Load attendance data
        self.cursor.execute("""
        SELECT date, time_in, time_out 
        FROM attendance 
        WHERE member_id = ? 
        ORDER BY date DESC, time_in DESC
        """, (member_id,))
        
        attendance_records = self.cursor.fetchall()
        self.member_attendance_table.setRowCount(len(attendance_records))
        
        for row, record in enumerate(attendance_records):
            for col, value in enumerate(record[:3]):  # First 3 columns
                item = QTableWidgetItem(str(value))
                self.member_attendance_table.setItem(row, col, item)
            
            # Calculate duration if time_out exists
            if record[2]:  # time_out
                time_in = datetime.strptime(record[1], "%H:%M:%S")
                time_out = datetime.strptime(record[2], "%H:%M:%S")
                duration = time_out - time_in
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m"
            else:
                duration_str = "In Progress"
            
            duration_item = QTableWidgetItem(duration_str)
            self.member_attendance_table.setItem(row, 3, duration_item)
        
        attendance_layout.addWidget(self.member_attendance_table)
        tabs.addTab(attendance_tab, "Attendance")
        
        # Payment history
        payment_tab = QWidget()
        payment_layout = QVBoxLayout(payment_tab)
        
        self.member_payments_table = QTableWidget()
        self.member_payments_table.setColumnCount(5)
        self.member_payments_table.setHorizontalHeaderLabels(["Date", "Amount", "Due Date", "Status", "Method"])
        self.member_payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.member_payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.member_payments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.member_payments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.member_payments_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.member_payments_table.verticalHeader().setVisible(False)
        self.member_payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Load payment data
        self.cursor.execute("""
        SELECT payment_date, amount, due_date, status, payment_method 
        FROM payments 
        WHERE member_id = ? 
        ORDER BY payment_date DESC
        """, (member_id,))
        
        payment_records = self.cursor.fetchall()
        self.member_payments_table.setRowCount(len(payment_records))
        
        for row, record in enumerate(payment_records):
            for col, value in enumerate(record[:5]):  # All 5 columns
                item = QTableWidgetItem(str(value))
                
                # Format amount as currency
                if col == 1:
                    item.setText(f"${float(value):.2f}")
                
                self.member_payments_table.setItem(row, col, item)
        
        payment_layout.addWidget(self.member_payments_table)
        tabs.addTab(payment_tab, "Payments")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def edit_member(self, member_id):
        self.cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = self.cursor.fetchone()
        
        if not member:
            QMessageBox.warning(self, "Not Found", "Member not found.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Member")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)
        
        self.edit_member_id = member_id
        self.edit_name_input = QLineEdit(member[1])
        self.edit_gender_combo = QComboBox()
        self.edit_gender_combo.addItems(["Male", "Female", "Other"])
        self.edit_gender_combo.setCurrentText(member[2] if member[2] else "Male")
        
        dob = QDate.fromString(member[3], "yyyy-MM-dd") if member[3] else QDate.currentDate()
        self.edit_dob_input = QDateEdit(dob)
        self.edit_dob_input.setCalendarPopup(True)
        self.edit_dob_input.setMaximumDate(QDate.currentDate())
        
        self.edit_phone_input = QLineEdit(member[4])
        self.edit_email_input = QLineEdit(member[5])
        self.edit_address_input = QLineEdit(member[6])
        
        self.edit_type_combo = QComboBox()
        self.edit_type_combo.addItems(["Basic", "Standard", "Premium"])
        self.edit_type_combo.setCurrentText(member[7] if member[7] else "Basic")
        
        join_date = QDate.fromString(member[8], "yyyy-MM-dd") if member[8] else QDate.currentDate()
        self.edit_join_date_input = QDateEdit(join_date)
        self.edit_join_date_input.setCalendarPopup(True)
        self.edit_join_date_input.setMaximumDate(QDate.currentDate())
        
        expiry_date = QDate.fromString(member[9], "yyyy-MM-dd") if member[9] else QDate.currentDate().addMonths(1)
        self.edit_expiry_date_input = QDateEdit(expiry_date)
        self.edit_expiry_date_input.setCalendarPopup(True)
        
        self.edit_status_combo = QComboBox()
        self.edit_status_combo.addItems(["Active", "Expired"])
        self.edit_status_combo.setCurrentText(member[10] if member[10] else "Active")
        
        # Connect signals for auto-updating expiry date
        self.edit_type_combo.currentTextChanged.connect(lambda: self.update_edit_expiry_date())
        self.edit_join_date_input.dateChanged.connect(lambda: self.update_edit_expiry_date())
        
        form_layout.addRow("Full Name:", self.edit_name_input)
        form_layout.addRow("Gender:", self.edit_gender_combo)
        form_layout.addRow("Date of Birth:", self.edit_dob_input)
        form_layout.addRow("Phone:", self.edit_phone_input)
        form_layout.addRow("Email:", self.edit_email_input)
        form_layout.addRow("Address:", self.edit_address_input)
        form_layout.addRow("Membership Type:", self.edit_type_combo)
        form_layout.addRow("Join Date:", self.edit_join_date_input)
        form_layout.addRow("Expiry Date:", self.edit_expiry_date_input)
        form_layout.addRow("Status:", self.edit_status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(lambda: self.save_member_edits(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def update_edit_expiry_date(self):
        membership_type = self.edit_type_combo.currentText()
        join_date = self.edit_join_date_input.date()
        
        months = 1  # Default to Basic (1 month)
        if membership_type == "Standard":
            months = 3
        elif membership_type == "Premium":
            months = 12
        
        expiry_date = join_date.addMonths(months)
        self.edit_expiry_date_input.setDate(expiry_date)
    
    def save_member_edits(self, dialog):
        name = self.edit_name_input.text().strip()
        phone = self.edit_phone_input.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Validation Error", "Name and phone are required fields.")
            return
        
        try:
            self.cursor.execute("""
            UPDATE members SET
                name = ?, gender = ?, dob = ?, phone = ?, email = ?, address = ?,
                membership_type = ?, join_date = ?, expiry_date = ?, status = ?
            WHERE id = ?
            """, (
                name,
                self.edit_gender_combo.currentText(),
                self.edit_dob_input.date().toString("yyyy-MM-dd"),
                phone,
                self.edit_email_input.text().strip(),
                self.edit_address_input.text().strip(),
                self.edit_type_combo.currentText(),
                self.edit_join_date_input.date().toString("yyyy-MM-dd"),
                self.edit_expiry_date_input.date().toString("yyyy-MM-dd"),
                self.edit_status_combo.currentText(),
                self.edit_member_id
            ))
            
            self.conn.commit()
            QMessageBox.information(self, "Success", "Member updated successfully!")
            self.load_members()
            self.update_dashboard()
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update member: {str(e)}")
    
    def delete_member(self, member_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this member?\nThis will also delete their attendance and payment records.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete attendance records first (foreign key constraint)
                self.cursor.execute("DELETE FROM attendance WHERE member_id = ?", (member_id,))
                
                # Delete payment records
                self.cursor.execute("DELETE FROM payments WHERE member_id = ?", (member_id,))
                
                # Delete member
                self.cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
                
                self.conn.commit()
                QMessageBox.information(self, "Success", "Member deleted successfully!")
                self.load_members()
                self.update_dashboard()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete member: {str(e)}")
    
    def show_mark_attendance_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Mark Attendance")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Member selection
        member_layout = QHBoxLayout()
        member_layout.addWidget(QLabel("Member:"))
        
        self.attendance_member_combo = QComboBox()
        self.attendance_member_combo.setObjectName("memberCombo")
        
        # Load active members
        self.cursor.execute("SELECT id, name FROM members WHERE status = 'Active' ORDER BY name")
        members = self.cursor.fetchall()
        
        for member in members:
            self.attendance_member_combo.addItem(member[1], member[0])
        
        member_layout.addWidget(self.attendance_member_combo)
        layout.addLayout(member_layout)
        
        # Check-in/out selection
        self.attendance_action_combo = QComboBox()
        self.attendance_action_combo.addItems(["Check In", "Check Out"])
        layout.addWidget(QLabel("Action:"))
        layout.addWidget(self.attendance_action_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(lambda: self.save_attendance(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_attendance(self, dialog):
        member_id = self.attendance_member_combo.currentData()
        action = self.attendance_action_combo.currentText()
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        
        try:
            if action == "Check In":
                # Check if already checked in today
                self.cursor.execute("""
                SELECT id FROM attendance 
                WHERE member_id = ? AND date = ? AND time_out IS NULL
                """, (member_id, today))
                
                if self.cursor.fetchone():
                    QMessageBox.warning(self, "Already Checked In", "This member is already checked in today.")
                    return
                
                # Record check-in
                self.cursor.execute("""
                INSERT INTO attendance (member_id, date, time_in)
                VALUES (?, ?, ?)
                """, (member_id, today, now))
                
                self.conn.commit()
                QMessageBox.information(self, "Success", "Check-in recorded successfully!")
            else:  # Check Out
                # Find open check-in record
                self.cursor.execute("""
                SELECT id FROM attendance 
                WHERE member_id = ? AND date = ? AND time_out IS NULL
                ORDER BY time_in DESC
                LIMIT 1
                """, (member_id, today))
                
                record = self.cursor.fetchone()
                
                if not record:
                    QMessageBox.warning(self, "No Check-In", "No check-in found for this member today.")
                    return
                
                # Record check-out
                self.cursor.execute("""
                UPDATE attendance SET time_out = ?
                WHERE id = ?
                """, (now, record[0]))
                
                self.conn.commit()
                QMessageBox.information(self, "Success", "Check-out recorded successfully!")
            
            self.load_attendance()
            self.update_dashboard()
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to record attendance: {str(e)}")
    
    def check_out_member(self, attendance_id):
        now = datetime.now().strftime("%H:%M:%S")
        
        try:
            self.cursor.execute("""
            UPDATE attendance SET time_out = ?
            WHERE id = ?
            """, (now, attendance_id))
            
            self.conn.commit()
            QMessageBox.information(self, "Success", "Check-out recorded successfully!")
            self.load_attendance()
            self.update_dashboard()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to record check-out: {str(e)}")
    
    def show_record_payment_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Payment")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)
        
        # Member selection
        self.payment_member_combo = QComboBox()
        self.payment_member_combo.setObjectName("memberCombo")
        
        # Load active members
        self.cursor.execute("SELECT id, name FROM members WHERE status = 'Active' ORDER BY name")
        members = self.cursor.fetchall()
        
        for member in members:
            self.payment_member_combo.addItem(member[1], member[0])
        
        form_layout.addRow("Member:", self.payment_member_combo)
        
        # Amount
        self.payment_amount_input = QLineEdit()
        self.payment_amount_input.setValidator(QDoubleValidator(0, 9999, 2))
        form_layout.addRow("Amount ($):", self.payment_amount_input)
        
        # Payment date
        self.payment_date_input = QDateEdit(QDate.currentDate())
        self.payment_date_input.setCalendarPopup(True)
        form_layout.addRow("Payment Date:", self.payment_date_input)
        
        # Due date (default to 1 month from now)
        self.payment_due_date_input = QDateEdit(QDate.currentDate().addMonths(1))
        self.payment_due_date_input.setCalendarPopup(True)
        form_layout.addRow("Due Date:", self.payment_due_date_input)
        
        # Payment method
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other"])
        form_layout.addRow("Payment Method:", self.payment_method_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Record Payment")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(lambda: self.save_payment(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_payment(self, dialog):
        member_id = self.payment_member_combo.currentData()
        amount = self.payment_amount_input.text().strip()
        
        if not amount or float(amount) <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid payment amount.")
            return
        
        try:
            self.cursor.execute("""
            INSERT INTO payments (
                member_id, amount, payment_date, due_date, payment_method
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                member_id,
                float(amount),
                self.payment_date_input.date().toString("yyyy-MM-dd"),
                self.payment_due_date_input.date().toString("yyyy-MM-dd"),
                self.payment_method_combo.currentText()
            ))
            
            # Update member's expiry date if this is a membership payment
            # (This is a simplified approach - you might want to make it more sophisticated)
            self.cursor.execute("""
            UPDATE members SET expiry_date = ?
            WHERE id = ? AND expiry_date < ?
            """, (
                self.payment_due_date_input.date().toString("yyyy-MM-dd"),
                member_id,
                self.payment_due_date_input.date().toString("yyyy-MM-dd")
            ))
            
            self.conn.commit()
            QMessageBox.information(self, "Success", "Payment recorded successfully!")
            self.load_payments()
            self.update_dashboard()
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to record payment: {str(e)}")
    
    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        start_date = self.report_start_date.date().toString("yyyy-MM-dd")
        end_date = self.report_end_date.date().toString("yyyy-MM-dd")
        
        # Clear previous report
        for i in reversed(range(self.report_display.layout().count())): 
            self.report_display.layout().itemAt(i).widget().setParent(None)
        
        layout = QVBoxLayout(self.report_display)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Generate report based on type
        if report_type == "Attendance Summary":
            self.generate_attendance_report(layout, start_date, end_date)
        elif report_type == "Membership Types":
            self.generate_membership_report(layout)
        elif report_type == "Revenue Analysis":
            self.generate_revenue_report(layout, start_date, end_date)
        elif report_type == "Member Growth":
            self.generate_growth_report(layout, start_date, end_date)
        
        # Add stretch to push content up
        layout.addStretch()
    
    def generate_attendance_report(self, layout, start_date, end_date):
        # Title
        title = QLabel(f"Attendance Summary Report\n{start_date} to {end_date}")
        title.setObjectName("reportTitle")
        layout.addWidget(title)
        
        # Total attendance
        self.cursor.execute("""
        SELECT COUNT(*) FROM attendance 
        WHERE date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        total_attendance = self.cursor.fetchone()[0]
        
        stats_layout = QHBoxLayout()
        
        total_card = QFrame()
        total_card.setObjectName("statCard")
        total_card.setFixedHeight(80)
        
        total_layout = QVBoxLayout(total_card)
        total_layout.addWidget(QLabel("Total Visits"))
        total_layout.addWidget(QLabel(str(total_attendance)))
        
        stats_layout.addWidget(total_card)
        
        # Unique members
        self.cursor.execute("""
        SELECT COUNT(DISTINCT member_id) FROM attendance 
        WHERE date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        unique_members = self.cursor.fetchone()[0]
        
        unique_card = QFrame()
        unique_card.setObjectName("statCard")
        unique_card.setFixedHeight(80)
        
        unique_layout = QVBoxLayout(unique_card)
        unique_layout.addWidget(QLabel("Unique Members"))
        unique_layout.addWidget(QLabel(str(unique_members)))
        
        stats_layout.addWidget(unique_card)
        
        # Average visits per member
        avg_visits = total_attendance / unique_members if unique_members > 0 else 0
        
        avg_card = QFrame()
        avg_card.setObjectName("statCard")
        avg_card.setFixedHeight(80)
        
        avg_layout = QVBoxLayout(avg_card)
        avg_layout.addWidget(QLabel("Avg Visits/Member"))
        avg_layout.addWidget(QLabel(f"{avg_visits:.1f}"))
        
        stats_layout.addWidget(avg_card)
        
        layout.addLayout(stats_layout)
        
        # Daily attendance chart (simplified - in a real app you'd use a proper charting library)
        chart_label = QLabel("Daily Attendance")
        chart_label.setObjectName("chartLabel")
        layout.addWidget(chart_label)
        
        # Get daily counts
        self.cursor.execute("""
        SELECT date, COUNT(*) 
        FROM attendance 
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """, (start_date, end_date))
        
        daily_data = self.cursor.fetchall()
        
        # Create a simple bar chart using labels
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        for date, count in daily_data:
            row = QHBoxLayout()
            
            date_label = QLabel(date)
            date_label.setFixedWidth(100)
            
            bar = QLabel()
            bar.setFixedHeight(20)
            bar.setStyleSheet(f"background-color: #4CAF50; min-width: {count * 5}px;")
            
            count_label = QLabel(str(count))
            
            row.addWidget(date_label)
            row.addWidget(bar)
            row.addWidget(count_label)
            
            chart_layout.addLayout(row)
        
        layout.addWidget(chart_frame)
    
    def generate_membership_report(self, layout):
        # Title
        title = QLabel("Membership Types Report")
        title.setObjectName("reportTitle")
        layout.addWidget(title)
        
        # Get counts by membership type
        self.cursor.execute("""
        SELECT membership_type, COUNT(*) 
        FROM members 
        GROUP BY membership_type
        """)
        
        membership_data = self.cursor.fetchall()
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        for mtype, count in membership_data:
            card = QFrame()
            card.setObjectName("statCard")
            card.setFixedHeight(80)
            
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(mtype))
            card_layout.addWidget(QLabel(str(count)))
            
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Pie chart representation (simplified)
        chart_label = QLabel("Membership Distribution")
        chart_label.setObjectName("chartLabel")
        layout.addWidget(chart_label)
        
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QHBoxLayout(chart_frame)
        
        total_members = sum(count for _, count in membership_data)
        
        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
        
        for i, (mtype, count) in enumerate(membership_data):
            if i >= len(colors):
                break  # Only support up to 5 types with this simple approach
            
            percentage = (count / total_members) * 100 if total_members > 0 else 0
            
            segment = QFrame()
            segment.setObjectName("chartSegment")
            segment.setStyleSheet(f"background-color: {colors[i]};")
            segment.setFixedHeight(20)
            segment.setFixedWidth(int(percentage * 3))  # Scale for visibility
            
            tooltip = f"{mtype}: {count} ({percentage:.1f}%)"
            segment.setToolTip(tooltip)
            
            chart_layout.addWidget(segment)
        
        layout.addWidget(chart_frame)
    
    def generate_revenue_report(self, layout, start_date, end_date):
        # Title
        title = QLabel(f"Revenue Analysis Report\n{start_date} to {end_date}")
        title.setObjectName("reportTitle")
        layout.addWidget(title)
        
        # Total revenue
        self.cursor.execute("""
        SELECT SUM(amount) 
        FROM payments 
        WHERE payment_date BETWEEN ? AND ? AND status = 'Paid'
        """, (start_date, end_date))
        
        total_revenue = self.cursor.fetchone()[0] or 0
        
        stats_layout = QHBoxLayout()
        
        total_card = QFrame()
        total_card.setObjectName("statCard")
        total_card.setFixedHeight(80)
        
        total_layout = QVBoxLayout(total_card)
        total_layout.addWidget(QLabel("Total Revenue"))
        total_layout.addWidget(QLabel(f"${total_revenue:,.2f}"))
        
        stats_layout.addWidget(total_card)
        
        # Revenue by payment method
        self.cursor.execute("""
        SELECT payment_method, SUM(amount) 
        FROM payments 
        WHERE payment_date BETWEEN ? AND ? AND status = 'Paid'
        GROUP BY payment_method
        """, (start_date, end_date))
        
        method_data = self.cursor.fetchall()
        
        for method, amount in method_data:
            card = QFrame()
            card.setObjectName("statCard")
            card.setFixedHeight(80)
            
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(method))
            card_layout.addWidget(QLabel(f"${amount:,.2f}"))
            
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Monthly revenue trend (simplified)
        chart_label = QLabel("Monthly Revenue Trend")
        chart_label.setObjectName("chartLabel")
        layout.addWidget(chart_label)
        
        # Get monthly totals
        self.cursor.execute("""
        SELECT strftime('%Y-%m', payment_date) AS month, SUM(amount)
        FROM payments
        WHERE payment_date BETWEEN ? AND ? AND status = 'Paid'
        GROUP BY month
        ORDER BY month
        """, (start_date, end_date))
        
        monthly_data = self.cursor.fetchall()
        
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        max_amount = max(amount for _, amount in monthly_data) if monthly_data else 1
        
        for month, amount in monthly_data:
            row = QHBoxLayout()
            
            month_label = QLabel(month)
            month_label.setFixedWidth(100)
            
            # Scale bar width based on maximum amount
            bar_width = int((amount / max_amount) * 300) if max_amount > 0 else 0
            
            bar = QLabel()
            bar.setFixedHeight(20)
            bar.setStyleSheet("background-color: #36A2EB;")
            bar.setFixedWidth(bar_width)
            
            amount_label = QLabel(f"${amount:,.2f}")
            
            row.addWidget(month_label)
            row.addWidget(bar)
            row.addWidget(amount_label)
            
            chart_layout.addLayout(row)
        
        layout.addWidget(chart_frame)
    
    def generate_growth_report(self, layout, start_date, end_date):
        # Title
        title = QLabel(f"Member Growth Report\n{start_date} to {end_date}")
        title.setObjectName("reportTitle")
        layout.addWidget(title)
        
        # New members
        self.cursor.execute("""
        SELECT COUNT(*) 
        FROM members 
        WHERE join_date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        new_members = self.cursor.fetchone()[0]
        
        stats_layout = QHBoxLayout()
        
        new_card = QFrame()
        new_card.setObjectName("statCard")
        new_card.setFixedHeight(80)
        
        new_layout = QVBoxLayout(new_card)
        new_layout.addWidget(QLabel("New Members"))
        new_layout.addWidget(QLabel(str(new_members)))
        
        stats_layout.addWidget(new_card)
        
        # Lost members (expired)
        self.cursor.execute("""
        SELECT COUNT(*) 
        FROM members 
        WHERE status = 'Expired' AND expiry_date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        lost_members = self.cursor.fetchone()[0]
        
        lost_card = QFrame()
        lost_card.setObjectName("statCard")
        lost_card.setFixedHeight(80)
        
        lost_layout = QVBoxLayout(lost_card)
        lost_layout.addWidget(QLabel("Expired Members"))
        lost_layout.addWidget(QLabel(str(lost_members)))
        
        stats_layout.addWidget(lost_card)
        
        # Net growth
        net_growth = new_members - lost_members
        
        net_card = QFrame()
        net_card.setObjectName("statCard")
        net_card.setFixedHeight(80)
        
        net_layout = QVBoxLayout(net_card)
        net_layout.addWidget(QLabel("Net Growth"))
        net_layout.addWidget(QLabel(str(net_growth)))
        
        stats_layout.addWidget(net_card)
        
        layout.addLayout(stats_layout)
        
        # Monthly growth chart
        chart_label = QLabel("Monthly Member Growth")
        chart_label.setObjectName("chartLabel")
        layout.addWidget(chart_label)
        
        # Get monthly joins and expires
        self.cursor.execute("""
        SELECT strftime('%Y-%m', join_date) AS month, COUNT(*)
        FROM members
        WHERE join_date BETWEEN ? AND ?
        GROUP BY month
        ORDER BY month
        """, (start_date, end_date))
        
        join_data = self.cursor.fetchall()
        
        self.cursor.execute("""
        SELECT strftime('%Y-%m', expiry_date) AS month, COUNT(*)
        FROM members
        WHERE status = 'Expired' AND expiry_date BETWEEN ? AND ?
        GROUP BY month
        ORDER BY month
        """, (start_date, end_date))
        
        expire_data = self.cursor.fetchall()
        
        # Combine data
        months = sorted(set([m for m, _ in join_data] + [m for m, _ in expire_data]))
        
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        max_count = max(
            max(count for _, count in join_data) if join_data else 0,
            max(count for _, count in expire_data) if expire_data else 0
        )
        
        for month in months:
            joins = next((count for m, count in join_data if m == month), 0)
            expires = next((count for m, count in expire_data if m == month), 0)
            net = joins - expires
            
            row = QHBoxLayout()
            
            month_label = QLabel(month)
            month_label.setFixedWidth(100)
            
            # Join bar (green)
            join_bar = QLabel()
            join_bar.setFixedHeight(15)
            join_bar.setStyleSheet("background-color: #4CAF50;")
            join_bar.setFixedWidth(int((joins / max_count) * 300) if max_count > 0 else 0)
            join_bar.setToolTip(f"Joins: {joins}")
            
            # Expire bar (red)
            expire_bar = QLabel()
            expire_bar.setFixedHeight(15)
            expire_bar.setStyleSheet("background-color: #F44336;")
            expire_bar.setFixedWidth(int((expires / max_count) * 300) if max_count > 0 else 0)
            expire_bar.setToolTip(f"Expires: {expires}")
            
            # Net label
            net_label = QLabel(f"Net: {net:+d}")
            
            row.addWidget(month_label)
            row.addWidget(join_bar)
            row.addWidget(expire_bar)
            row.addWidget(net_label)
            
            chart_layout.addLayout(row)
        
        layout.addWidget(chart_frame)
    
    def add_membership_type(self):
        # Get current row count
        row = self.membership_types_table.rowCount()
        self.membership_types_table.insertRow(row)
        
        # Add empty items
        self.membership_types_table.setItem(row, 0, QTableWidgetItem(""))
        self.membership_types_table.setItem(row, 1, QTableWidgetItem("1"))
        
        # Edit the new row
        self.membership_types_table.editItem(self.membership_types_table.item(row, 0))
    
    def remove_membership_type(self):
        selected = self.membership_types_table.selectedItems()
        
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a membership type to remove.")
            return
        
        # Get unique rows from selected items
        rows = set(item.row() for item in selected)
        
        # Remove rows (starting from the bottom to avoid index issues)
        for row in sorted(rows, reverse=True):
            self.membership_types_table.removeRow(row)
    
    def save_settings(self):
        # In a real application, you would save these settings to a config file or database
        QMessageBox.information(self, "Settings Saved", "System settings have been saved successfully.")
    
    def update_clock(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.clock_label.setText(f"{current_date} | {current_time}")
    
    def get_stylesheet(self):
        return """
        /* Main window */
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        /* Sidebar */
        #sidebar {
            background-color: #2c3e50;
            border: none;
        }
        
        /* Logo */
        #logoName {
            color: #ecf0f1;
            font-size: 20px;
            font-weight: bold;
        }
        
        /* Menu buttons */
        #menuButton {
            background-color: transparent;
            color: #bdc3c7;
            text-align: left;
            padding: 10px 20px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
        }
        
        #menuButton:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: #ecf0f1;
        }
        
        #menuButton:pressed {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        /* User info */
        #userName {
            color: #ecf0f1;
            font-size: 14px;
            font-weight: bold;
        }
        
        #userRole {
            color: #bdc3c7;
            font-size: 12px;
        }
        
        /* Content area */
        #contentArea {
            background-color: #f5f5f5;
            border: none;
        }
        
        /* Top bar */
        #topBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
        }
        
        #titleLabel {
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
        }
        
        #clockLabel {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        /* Stat cards */
        #statCard {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        #statTitle {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        #statValue {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        
        /* Tables */
        #membersTable, #attendanceTable, #paymentsTable, #activityTable {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            gridline-color: #e0e0e0;
            font-size: 14px;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 10px;
            border: none;
            font-weight: bold;
        }
        
        /* Section labels */
        #sectionLabel {
            color: #2c3e50;
            font-size: 20px;
            font-weight: bold;
        }
        
        /* Chart frames */
        #chartFrame, #reportDisplay {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* Buttons */
        #addButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        #addButton:hover {
            background-color: #2980b9;
        }
        
        #actionButton {
            background-color: #e0e0e0;
            color: #333333;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        #actionButton:hover {
            background-color: #d0d0d0;
        }
        
        #saveButton {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        #saveButton:hover {
            background-color: #27ae60;
        }
        
        #cancelButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        #cancelButton:hover {
            background-color: #c0392b;
        }
        
        #closeButton {
            background-color: #95a5a6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        #closeButton:hover {
            background-color: #7f8c8d;
        }
        
        /* Input fields */
        #searchInput, #memberCombo, #dateFilter, #filterCombo, #reportCombo {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        /* Report elements */
        #reportTitle {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        #chartLabel {
            color: #2c3e50;
            font-size: 16px;
            font-weight: bold;
            margin: 15px 0 10px 0;
        }
        
        #chartSegment {
            border-radius: 10px;
            margin-right: 5px;
        }
        """
    
    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    # Create and show main window
    window = GymManagementSystem()
    window.show()
    
    sys.exit(app.exec_())