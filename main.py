"""
主应用程序 - 记账小助手
"""
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
import os

from database import Database
from settings_screen import SettingsScreen
from manual_entry_screen import ManualEntryScreen
from photo_entry_screen import PhotoEntryScreen
from billing_screen import BillingScreen

# 注册中文字体 - 只注册文本字体，不影响图标
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
if os.path.exists(FONT_PATH):
    # 只注册Roboto字体用于文本显示
    LabelBase.register(name='Roboto',
                      fn_regular=FONT_PATH,
                      fn_bold=FONT_PATH,
                      fn_italic=FONT_PATH,
                      fn_bolditalic=FONT_PATH)


class MainScreen(MDScreen):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.build_ui()
    
    def build_ui(self):
        """构建主界面UI"""
        layout = MDBoxLayout(
            orientation='vertical'
        )
        
        # 标题栏
        toolbar = MDTopAppBar(
            title="记账小助手",
            elevation=2,
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(toolbar)
        
        # 顶部空白
        layout.add_widget(MDBoxLayout(size_hint_y=0.15))
        
        # 按钮容器
        button_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(25),
            padding=[dp(40), 0, dp(40), 0],
            size_hint_y=0.7
        )
        
        # 手动记账按钮
        btn_manual = MDRaisedButton(
            text="手动记账",
            size_hint=(1, None),
            height=dp(60),
            md_bg_color=(0.2, 0.6, 0.8, 1),
            on_release=self.go_to_manual_entry
        )
        button_layout.add_widget(btn_manual)
        
        # 拍照记账按钮
        btn_photo = MDRaisedButton(
            text="拍照记账",
            size_hint=(1, None),
            height=dp(60),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=self.go_to_photo_entry
        )
        button_layout.add_widget(btn_photo)
        
        # 账单管理按钮
        btn_billing = MDRaisedButton(
            text="账单管理",
            size_hint=(1, None),
            height=dp(60),
            md_bg_color=(0.9, 0.5, 0.2, 1),
            on_release=self.go_to_billing
        )
        button_layout.add_widget(btn_billing)
        
        # 客户信息按钮
        btn_settings = MDRaisedButton(
            text="客户信息",
            size_hint=(1, None),
            height=dp(60),
            md_bg_color=(0.5, 0.5, 0.5, 1),
            on_release=self.go_to_settings
        )
        button_layout.add_widget(btn_settings)
        
        layout.add_widget(button_layout)
        
        # 底部空白
        layout.add_widget(MDBoxLayout(size_hint_y=0.15))
        
        self.add_widget(layout)
    
    def go_to_manual_entry(self, instance):
        """跳转到手动记账界面"""
        self.manager.current = 'manual_entry'
    
    def go_to_photo_entry(self, instance):
        """跳转到拍照记账界面"""
        self.manager.current = 'photo_entry'
    
    def go_to_billing(self, instance):
        """跳转到账单管理界面"""
        self.manager.current = 'billing'
    
    def go_to_settings(self, instance):
        """跳转到设置界面"""
        self.manager.current = 'settings'


class AccountingApp(MDApp):
    """主应用程序类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = Database()
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        # 设置字体
        self.theme_cls.font_styles.update({
            "H1": ["Roboto", 96, False, -1.5],
            "H2": ["Roboto", 60, False, -0.5],
            "H3": ["Roboto", 48, False, 0],
            "H4": ["Roboto", 34, False, 0.25],
            "H5": ["Roboto", 24, False, 0],
            "H6": ["Roboto", 20, False, 0.15],
            "Subtitle1": ["Roboto", 16, False, 0.15],
            "Subtitle2": ["Roboto", 14, False, 0.1],
            "Body1": ["Roboto", 16, False, 0.5],
            "Body2": ["Roboto", 14, False, 0.25],
            "Button": ["Roboto", 14, True, 1.25],
            "Caption": ["Roboto", 12, False, 0.4],
            "Overline": ["Roboto", 10, True, 1.5],
        })
    
    def build(self):
        """构建应用程序"""
        # 设置窗口大小（开发时使用）
        Window.size = (360, 640)
        
        # 创建屏幕管理器
        sm = MDScreenManager()
        
        # 添加所有界面
        sm.add_widget(MainScreen())
        sm.add_widget(SettingsScreen(database=self.database, name='settings'))
        sm.add_widget(ManualEntryScreen(database=self.database, name='manual_entry'))
        sm.add_widget(PhotoEntryScreen(database=self.database, name='photo_entry'))
        sm.add_widget(BillingScreen(database=self.database, name='billing'))
        
        return sm


if __name__ == '__main__':
    AccountingApp().run()
