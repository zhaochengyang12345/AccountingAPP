"""
设置界面 - 管理客户和产品信息
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


class SettingsScreen(MDScreen):
    """设置界面 - 管理客户和产品"""
    
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.current_customer_id = None
        self.dialog = None
        self.edit_dialog = None
        self.build_ui()
    
    def build_ui(self):
        """构建设置界面UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # 标题栏
        toolbar = MDTopAppBar(
            title="客户信息管理",
            elevation=2,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            md_bg_color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(toolbar)
        
        # 主内容区域
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # 客户列表标题
        title_box = MDBoxLayout(size_hint_y=None, height=dp(50))
        title_label = MDLabel(
            text="客户列表",
            font_style="H6",
            size_hint_x=0.7
        )
        add_customer_btn = MDRaisedButton(
            text="添加客户",
            size_hint=(0.3, 1),
            md_bg_color=(0.2, 0.6, 0.8, 1),
            on_release=self.show_add_customer_dialog
        )
        title_box.add_widget(title_label)
        title_box.add_widget(add_customer_btn)
        content.add_widget(title_box)
        
        # 客户列表
        scroll = MDScrollView()
        self.customer_list = MDList()
        scroll.add_widget(self.customer_list)
        content.add_widget(scroll)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def on_enter(self):
        """进入界面时刷新客户列表"""
        self.refresh_customer_list()
    
    def go_back(self):
        """返回主界面"""
        self.manager.current = 'main'
    
    def refresh_customer_list(self):
        """刷新客户列表"""
        self.customer_list.clear_widgets()
        customers = self.database.get_all_customers()
        
        for customer in customers:
            item = TwoLineListItem(
                text=customer['name'],
                secondary_text="点击查看产品",
                on_release=lambda x, cid=customer['id'], cname=customer['name']: 
                    self.show_products(cid, cname)
            )
            self.customer_list.add_widget(item)
    
    def show_add_customer_dialog(self, instance):
        """显示添加客户对话框"""
        if not self.dialog:
            self.customer_name_field = MDTextField(
                hint_text="客户名称",
                helper_text="请输入客户公司名称",
                helper_text_mode="on_focus",
                size_hint_x=1
            )
            
            self.dialog = MDDialog(
                title="添加新客户",
                type="custom",
                content_cls=self.customer_name_field,
                buttons=[
                    MDFlatButton(
                        text="取消",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="添加",
                        on_release=self.add_customer
                    ),
                ],
            )
        
        self.customer_name_field.text = ""
        self.dialog.open()
    
    def add_customer(self, instance):
        """添加客户"""
        customer_name = self.customer_name_field.text.strip()
        
        if not customer_name:
            self.show_message("错误", "客户名称不能为空")
            return
        
        success, message = self.database.add_customer(customer_name)
        
        if success:
            self.dialog.dismiss()
            self.refresh_customer_list()
            self.show_message("成功", message)
        else:
            self.show_message("错误", message)
    
    def show_products(self, customer_id, customer_name):
        """显示客户的产品列表"""
        # 先关闭可能存在的对话框
        if hasattr(self, 'product_dialog') and self.product_dialog:
            self.product_dialog.dismiss()
        
        products = self.database.get_products_by_customer(customer_id)
        
        # 创建内容容器 - 使用Kivy原生BoxLayout
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.scrollview import ScrollView
        
        content_box = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))
        
        # 添加产品按钮
        add_btn = MDRaisedButton(
            text="+ 添加产品规格",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=lambda x: self.show_add_product_dialog(customer_id, customer_name)
        )
        content_box.add_widget(add_btn)
        
        # 如果没有产品
        if not products:
            hint = Label(
                text="暂无产品\n点击上方按钮添加",
                size_hint=(1, None),
                height=dp(100),
                color=(0.5, 0.5, 0.5, 1)
            )
            content_box.add_widget(hint)
        else:
            # 显示产品列表
            for product in products:
                item_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60), spacing=5)
                
                # 产品信息
                info = Label(
                    text=f"{product['specification']}\n单价: ¥{product['unit_price']:.2f}",
                    size_hint=(0.6, 1),
                    color=(0, 0, 0, 1)
                )
                
                # 编辑按钮
                edit_btn = MDRaisedButton(
                    text="编辑",
                    size_hint=(0.2, None),
                    height=dp(50),
                    md_bg_color=(0.2, 0.6, 0.8, 1),
                    on_release=lambda x, pid=product['id'], spec=product['specification'], 
                        price=product['unit_price']: 
                        self.show_edit_product_dialog(pid, spec, price, customer_id, customer_name)
                )
                
                # 删除按钮
                del_btn = MDRaisedButton(
                    text="删除",
                    size_hint=(0.2, None),
                    height=dp(50),
                    md_bg_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x, pid=product['id']: 
                        self.confirm_delete_product(pid, customer_id, customer_name)
                )
                
                item_box.add_widget(info)
                item_box.add_widget(edit_btn)
                item_box.add_widget(del_btn)
                content_box.add_widget(item_box)
        
        # 滚动视图
        scroll = ScrollView(size_hint=(1, None), height=dp(400))
        scroll.add_widget(content_box)
        
        # 对话框
        self.product_dialog = MDDialog(
            title=f"{customer_name} 的产品列表",
            type="custom",
            content_cls=scroll,
            size_hint=(0.9, None),
            height=dp(500),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.product_dialog.dismiss()
                ),
            ],
        )
        self.product_dialog.open()
    
    def show_add_product_dialog(self, customer_id, customer_name):
        """显示添加产品对话框"""
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        spec_field = MDTextField(
            hint_text="规格",
            helper_text="例如: 30x20x15cm",
            helper_text_mode="on_focus"
        )
        
        price_field = MDTextField(
            hint_text="单价",
            helper_text="请输入数字",
            helper_text_mode="on_focus",
            input_filter="float"
        )
        
        content.add_widget(spec_field)
        content.add_widget(price_field)
        
        add_dialog = MDDialog(
            title=f"为 {customer_name} 添加产品",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: add_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="添加",
                    on_release=lambda x: self.add_product(
                        customer_id, customer_name, spec_field.text, 
                        price_field.text, add_dialog
                    )
                ),
            ],
        )
        add_dialog.open()
    
    def add_product(self, customer_id, customer_name, specification, price_text, dialog):
        """添加产品"""
        specification = specification.strip()
        
        if not specification:
            self.show_message("错误", "规格不能为空")
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                self.show_message("错误", "单价必须大于0")
                return
        except ValueError:
            self.show_message("错误", "单价必须是有效数字")
            return
        
        success, message = self.database.add_product(customer_id, specification, price)
        
        if success:
            dialog.dismiss()
            self.show_message("成功", message)
            # 重新打开产品列表以显示新添加的产品
            self.show_products(customer_id, customer_name)
        else:
            self.show_message("错误", message)
    
    def show_edit_product_dialog(self, product_id, specification, unit_price, customer_id, customer_name):
        """显示编辑产品对话框"""
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        spec_field = MDTextField(
            hint_text="规格",
            text=specification
        )
        
        price_field = MDTextField(
            hint_text="单价",
            text=str(unit_price),
            input_filter="float"
        )
        
        content.add_widget(spec_field)
        content.add_widget(price_field)
        
        edit_dialog = MDDialog(
            title="编辑产品",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: edit_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x: self.update_product(
                        product_id, spec_field.text, price_field.text, 
                        edit_dialog, customer_id, customer_name
                    )
                ),
            ],
        )
        edit_dialog.open()
    
    def update_product(self, product_id, specification, price_text, dialog, customer_id, customer_name):
        """更新产品"""
        specification = specification.strip()
        
        if not specification:
            self.show_message("错误", "规格不能为空")
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                self.show_message("错误", "单价必须大于0")
                return
        except ValueError:
            self.show_message("错误", "单价必须是有效数字")
            return
        
        success, message = self.database.update_product(product_id, specification, price)
        
        if success:
            dialog.dismiss()
            self.show_message("成功", message)
            # 重新打开产品列表以显示更新
            self.show_products(customer_id, customer_name)
        else:
            self.show_message("错误", message)
    
    def confirm_delete_product(self, product_id, customer_id, customer_name):
        """确认删除产品"""
        confirm_dialog = MDDialog(
            title="确认删除",
            text="确定要删除这个产品吗？",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    md_bg_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x: self.delete_product(
                        product_id, confirm_dialog, customer_id, customer_name
                    )
                ),
            ],
        )
        confirm_dialog.open()
    
    def delete_product(self, product_id, confirm_dialog, customer_id, customer_name):
        """删除产品"""
        success, message = self.database.delete_product(product_id)
        
        confirm_dialog.dismiss()
        
        if success:
            self.show_message("成功", message)
            # 重新打开产品列表以显示删除结果
            self.show_products(customer_id, customer_name)
        else:
            self.show_message("错误", message)
    
    def show_message(self, title, text):
        """显示消息对话框"""
        msg_dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="确定",
                    on_release=lambda x: msg_dialog.dismiss()
                ),
            ],
        )
        msg_dialog.open()
