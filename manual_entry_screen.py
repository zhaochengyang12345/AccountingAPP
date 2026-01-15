"""
手动记账界面 - 快捷录入账单信息
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from datetime import datetime


class ManualEntryScreen(MDScreen):
    """手动记账界面"""
    
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.dialog = None
        self.customer_menu = None
        self.spec_menu = None
        self.build_ui()
    
    def build_ui(self):
        """构建手动记账界面UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # 标题栏
        toolbar = MDTopAppBar(
            title="手动记账",
            elevation=2,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(toolbar)
        
        # 表单内容
        form_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 客户选择 - 使用水平布局放置输入框和下拉按钮
        customer_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(56), spacing=dp(5))
        self.customer_field = MDTextField(
            hint_text="客户名称",
            text="点击选择客户",
            readonly=True,
            size_hint=(0.85, None),
            height=dp(56)
        )
        customer_dropdown_btn = MDIconButton(
            icon="menu-down",
            size_hint=(0.15, None),
            height=dp(56),
            on_release=self.show_customer_dropdown
        )
        customer_box.add_widget(self.customer_field)
        customer_box.add_widget(customer_dropdown_btn)
        form_layout.add_widget(customer_box)
        
        # 日期选择
        self.date_field = MDTextField(
            hint_text="日期",
            text=datetime.now().strftime("%Y-%m-%d"),
            readonly=True,
            size_hint=(1, None),
            height=dp(56),
            on_focus=self.show_date_picker
        )
        form_layout.add_widget(self.date_field)
        
        # 规格选择 - 使用水平布局放置输入框和下拉按钮
        spec_box = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(56), spacing=dp(5))
        self.specification_field = MDTextField(
            hint_text="规格",
            text="点击选择规格",
            readonly=True,
            size_hint=(0.85, None),
            height=dp(56)
        )
        spec_dropdown_btn = MDIconButton(
            icon="menu-down",
            size_hint=(0.15, None),
            height=dp(56),
            on_release=self.show_specification_dropdown
        )
        spec_box.add_widget(self.specification_field)
        spec_box.add_widget(spec_dropdown_btn)
        form_layout.add_widget(spec_box)
        
        # 数量输入
        self.quantity_field = MDTextField(
            hint_text="数量",
            input_filter="float",
            size_hint=(1, None),
            height=dp(56)
        )
        self.quantity_field.bind(text=self.calculate_total)
        form_layout.add_widget(self.quantity_field)
        
        # 单价显示
        self.unit_price_field = MDTextField(
            hint_text="单价",
            readonly=True,
            size_hint=(1, None),
            height=dp(56)
        )
        form_layout.add_widget(self.unit_price_field)
        
        # 总价显示
        self.total_price_field = MDTextField(
            hint_text="总价",
            readonly=True,
            size_hint=(1, None),
            height=dp(56)
        )
        form_layout.add_widget(self.total_price_field)
        
        # 保存按钮
        save_btn = MDRaisedButton(
            text="保存账单",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=self.save_bill
        )
        form_layout.add_widget(save_btn)
        
        # 滚动视图
        scroll = MDScrollView()
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """进入界面时重置表单"""
        self.reset_form()
    
    def go_back(self):
        """返回主界面"""
        self.manager.current = 'main'
    
    def reset_form(self):
        """重置表单"""
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.customer_field.text = "点击选择客户"
        self.date_field.text = datetime.now().strftime("%Y-%m-%d")
        self.specification_field.text = "点击选择规格"
        self.quantity_field.text = ""
        self.unit_price_field.text = ""
        self.total_price_field.text = ""
    
    def show_customer_dropdown(self, instance):
        """显示客户下拉菜单"""
        customers = self.database.get_all_customers()
        
        if not customers:
            self.show_message("提示", "暂无客户，请先在'客户信息'中添加客户")
            self.show_message("提示", "请先在设置中添加客户")
            return
        
        # 创建菜单项
        menu_items = []
        for customer in customers:
            menu_items.append({
                "text": customer['name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda cid=customer['id'], cname=customer['name']: 
                    self.select_customer(cid, cname)
            })
        
        # 创建下拉菜单
        self.customer_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.customer_menu.open()
    
    def select_customer(self, customer_id, customer_name):
        """选择客户"""
        self.selected_customer_id = customer_id
        self.selected_customer_name = customer_name
        self.customer_field.text = customer_name
        
        # 重置规格和价格
        self.specification_field.text = "点击选择规格"
        self.unit_price_field.text = ""
        self.total_price_field.text = ""
        
        # 关闭下拉菜单
        if self.customer_menu:
            self.customer_menu.dismiss()
    
    def show_date_picker(self, instance, value):
        """显示日期选择器"""
        if not value:
            return
        
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_select)
        date_dialog.open()
    
    def on_date_select(self, instance, value, date_range):
        """日期选择回调"""
        self.date_field.text = value.strftime("%Y-%m-%d")
    
    def show_specification_dropdown(self, instance):
        """显示规格下拉菜单"""
        if not self.selected_customer_id:
            self.show_message("提示", "请先选择客户")
            return
        
        products = self.database.get_products_by_customer(self.selected_customer_id)
        
        if not products:
            self.show_message("提示", f"请先在'客户信息'中为【{self.selected_customer_name}】添加产品规格")
            return
        
        # 创建菜单项
        menu_items = []
        for product in products:
            menu_items.append({
                "text": f"{product['specification']} - ¥{product['unit_price']:.2f}",
                "viewclass": "OneLineListItem",
                "on_release": lambda spec=product['specification'], price=product['unit_price']: 
                    self.select_specification(spec, price)
            })
        
        # 创建下拉菜单
        self.spec_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.spec_menu.open()
    
    def select_specification(self, specification, unit_price):
        """选择规格"""
        self.specification_field.text = specification
        self.unit_price_field.text = f"¥{unit_price:.2f}"
        
        # 自动计算总价
        self.calculate_total()
        
        # 关闭下拉菜单
        if self.spec_menu:
            self.spec_menu.dismiss()
    
    def calculate_total(self, *args):
        """计算总价"""
        try:
            quantity = float(self.quantity_field.text) if self.quantity_field.text else 0
            unit_price_text = self.unit_price_field.text.replace("¥", "").strip()
            unit_price = float(unit_price_text) if unit_price_text else 0
            
            total = quantity * unit_price
            self.total_price_field.text = f"¥{total:.2f}"
        except ValueError:
            self.total_price_field.text = "¥0.00"
    
    def save_bill(self, instance):
        """保存账单"""
        # 验证数据
        if not self.selected_customer_id:
            self.show_message("错误", "请选择客户")
            return
        
        if self.specification_field.text == "点击选择规格":
            self.show_message("错误", "请选择规格")
            return
        
        try:
            quantity = float(self.quantity_field.text)
            if quantity <= 0:
                self.show_message("错误", "数量必须大于0")
                return
        except ValueError:
            self.show_message("错误", "请输入有效的数量")
            return
        
        unit_price_text = self.unit_price_field.text.replace("¥", "").strip()
        try:
            unit_price = float(unit_price_text)
        except ValueError:
            self.show_message("错误", "单价无效")
            return
        
        # 保存到数据库
        success, message = self.database.add_bill(
            customer_id=self.selected_customer_id,
            customer_name=self.selected_customer_name,
            date=self.date_field.text,
            specification=self.specification_field.text,
            quantity=quantity,
            unit_price=unit_price,
            source='manual'
        )
        
        if success:
            self.show_message("成功", "账单保存成功", callback=self.reset_form)
        else:
            self.show_message("错误", message)
    
    def show_message(self, title, text, callback=None):
        """显示消息对话框"""
        msg_dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="确定",
                    on_release=lambda x: self.close_message_dialog(msg_dialog, callback)
                ),
            ],
        )
        msg_dialog.open()
    
    def close_message_dialog(self, dialog, callback=None):
        """关闭消息对话框"""
        dialog.dismiss()
        if callback:
            callback()
