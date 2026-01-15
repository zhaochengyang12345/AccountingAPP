"""
账单管理界面 - 查询、筛选和导出账单
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, ThreeLineListItem, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from datetime import datetime
import os

try:
    from openpyxl import Workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class BillingScreen(MDScreen):
    """账单管理界面"""
    
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.filter_customer = None
        self.filter_start_date = None
        self.filter_end_date = None
        self.dialog = None
        self.customer_menu = None
        self.customer_field_ref = None
        self.build_ui()
    
    def build_ui(self):
        """构建账单管理界面UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # 标题栏
        toolbar = MDTopAppBar(
            title="账单管理",
            elevation=2,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["filter", lambda x: self.show_filter_dialog()],
                ["export", lambda x: self.export_bills()]
            ],
            md_bg_color=(0.9, 0.5, 0.2, 1)
        )
        layout.add_widget(toolbar)
        
        # 统计信息
        self.stats_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), 0],
            font_style="H6"
        )
        layout.add_widget(self.stats_label)
        
        # 账单列表
        scroll = MDScrollView()
        self.bill_list = MDList()
        scroll.add_widget(self.bill_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """进入界面时刷新账单列表"""
        self.refresh_bill_list()
    
    def go_back(self):
        """返回主界面"""
        self.manager.current = 'main'
    
    def refresh_bill_list(self):
        """刷新账单列表"""
        self.bill_list.clear_widgets()
        
        # 根据筛选条件获取账单
        bills = self.database.filter_bills(
            customer_name=self.filter_customer,
            start_date=self.filter_start_date,
            end_date=self.filter_end_date
        )
        
        # 更新统计信息
        total_count = len(bills)
        total_amount = sum(bill['total_price'] for bill in bills)
        
        filter_text = ""
        if self.filter_customer or self.filter_start_date or self.filter_end_date:
            filter_text = " (已筛选)"
        
        self.stats_label.text = f"共 {total_count} 条账单{filter_text} | 总金额: ¥{total_amount:.2f}"
        
        # 显示账单列表
        for bill in bills:
            source_text = "📝手动" if bill['source'] == 'manual' else "📷拍照"
            
            item = ThreeLineListItem(
                text=f"{bill['customer_name']} - {bill['date']}",
                secondary_text=f"{bill['specification']} | 数量: {bill['quantity']} | 单价: ¥{bill['unit_price']:.2f}",
                tertiary_text=f"{source_text} | 总价: ¥{bill['total_price']:.2f}",
                on_release=lambda x, bid=bill['id']: self.show_bill_detail(bid)
            )
            self.bill_list.add_widget(item)
    
    def show_filter_dialog(self):
        """显示筛选对话框"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(260),
            padding=dp(10)
        )
        
        # 客户筛选 - 使用下拉菜单
        content.add_widget(MDLabel(text="客户名称:", size_hint_y=None, height=dp(20)))
        customer_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(40)
        )
        customer_field = MDTextField(
            hint_text="点击选择客户（留空显示全部）",
            text=self.filter_customer or "",
            readonly=True,
            size_hint_x=0.85,
            height=dp(40)
        )
        self.customer_field_ref = customer_field
        customer_btn = MDIconButton(
            icon="menu-down",
            size_hint_x=0.15,
            on_release=self.show_customer_dropdown_for_filter
        )
        customer_layout.add_widget(customer_field)
        customer_layout.add_widget(customer_btn)
        content.add_widget(customer_layout)
        
        # 开始日期
        content.add_widget(MDLabel(text="开始日期:", size_hint_y=None, height=dp(20)))
        date_layout_start = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(40)
        )
        start_date_field = MDTextField(
            hint_text="留空不限制",
            text=self.filter_start_date or "",
            readonly=True,
            size_hint_x=0.7,
            height=dp(40)
        )
        start_date_btn = MDRaisedButton(
            text="选择日期",
            size_hint_x=0.3,
            on_release=lambda x: self.show_date_picker_for_filter(start_date_field, "start")
        )
        date_layout_start.add_widget(start_date_field)
        date_layout_start.add_widget(start_date_btn)
        content.add_widget(date_layout_start)
        
        # 结束日期
        content.add_widget(MDLabel(text="结束日期:", size_hint_y=None, height=dp(20)))
        date_layout_end = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(40)
        )
        end_date_field = MDTextField(
            hint_text="留空不限制",
            text=self.filter_end_date or "",
            readonly=True,
            size_hint_x=0.7,
            height=dp(40)
        )
        end_date_btn = MDRaisedButton(
            text="选择日期",
            size_hint_x=0.3,
            on_release=lambda x: self.show_date_picker_for_filter(end_date_field, "end")
        )
        date_layout_end.add_widget(end_date_field)
        date_layout_end.add_widget(end_date_btn)
        content.add_widget(date_layout_end)
        
        self.dialog = MDDialog(
            title="筛选账单",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="清除筛选",
                    on_release=lambda x: self.clear_filter()
                ),
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="应用",
                    on_release=lambda x: self.apply_filter(
                        customer_field.text,
                        start_date_field.text,
                        end_date_field.text
                    )
                ),
            ],
        )
        self.dialog.open()
    
    def show_date_picker_for_filter(self, field, date_type):
        """显示日期选择器"""
        date_dialog = MDDatePicker()
        date_dialog.bind(
            on_save=lambda instance, value, date_range: 
                self.on_filter_date_select(field, value)
        )
        date_dialog.open()
    
    def on_filter_date_select(self, field, value):
        """日期选择回调"""
        field.text = value.strftime("%Y-%m-%d")
    
    def show_customer_dropdown_for_filter(self, instance):
        """显示客户下拉菜单（用于筛选）"""
        customers = self.database.get_all_customers()
        
        # 添加"全部客户"选项
        menu_items = [{
            "text": "全部客户",
            "viewclass": "OneLineListItem",
            "on_release": lambda: self.select_filter_customer("")
        }]
        
        # 添加所有客户
        for customer in customers:
            menu_items.append({
                "text": customer['name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda cname=customer['name']: self.select_filter_customer(cname)
            })
        
        # 创建下拉菜单
        self.customer_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.customer_menu.open()
    
    def select_filter_customer(self, customer_name):
        """选择筛选客户"""
        if self.customer_field_ref:
            self.customer_field_ref.text = customer_name
        
        # 关闭下拉菜单
        if self.customer_menu:
            self.customer_menu.dismiss()
    
    def apply_filter(self, customer_name, start_date, end_date):
        """应用筛选"""
        self.filter_customer = customer_name.strip() if customer_name.strip() else None
        self.filter_start_date = start_date.strip() if start_date.strip() else None
        self.filter_end_date = end_date.strip() if end_date.strip() else None
        
        self.dialog.dismiss()
        self.refresh_bill_list()
    
    def clear_filter(self):
        """清除筛选"""
        self.filter_customer = None
        self.filter_start_date = None
        self.filter_end_date = None
        
        if self.dialog:
            self.dialog.dismiss()
        
        self.refresh_bill_list()
    
    def show_bill_detail(self, bill_id):
        """显示账单详情"""
        bills = self.database.filter_bills()
        bill = next((b for b in bills if b['id'] == bill_id), None)
        
        if not bill:
            return
        
        detail_text = f"""
客户: {bill['customer_name']}
日期: {bill['date']}
规格: {bill['specification']}
数量: {bill['quantity']}
单价: ¥{bill['unit_price']:.2f}
总价: ¥{bill['total_price']:.2f}
来源: {'手动录入' if bill['source'] == 'manual' else '拍照识别'}
        """
        
        detail_dialog = MDDialog(
            title="账单详情",
            text=detail_text,
            buttons=[
                MDFlatButton(
                    text="删除",
                    on_release=lambda x: self.confirm_delete_bill(bill_id, detail_dialog)
                ),
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: detail_dialog.dismiss()
                ),
            ],
        )
        detail_dialog.open()
    
    def confirm_delete_bill(self, bill_id, detail_dialog):
        """确认删除账单"""
        detail_dialog.dismiss()
        
        confirm_dialog = MDDialog(
            title="确认删除",
            text="确定要删除这条账单吗？",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    on_release=lambda x: self.delete_bill(bill_id, confirm_dialog)
                ),
            ],
        )
        confirm_dialog.open()
    
    def delete_bill(self, bill_id, confirm_dialog):
        """删除账单"""
        success, message = self.database.delete_bill(bill_id)
        confirm_dialog.dismiss()
        
        if success:
            self.refresh_bill_list()
            self.show_message("成功", message)
        else:
            self.show_message("错误", message)
    
    def export_bills(self):
        """导出账单到Excel"""
        if not EXCEL_AVAILABLE:
            self.show_message("错误", "需要安装openpyxl库才能导出Excel")
            return
        
        # 获取当前筛选的账单
        bills = self.database.filter_bills(
            customer_name=self.filter_customer,
            start_date=self.filter_start_date,
            end_date=self.filter_end_date
        )
        
        if not bills:
            self.show_message("提示", "没有账单可导出")
            return
        
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "账单明细"
            
            # 写入表头
            headers = ["客户名称", "日期", "规格", "数量", "单价", "总价", "来源"]
            ws.append(headers)
            
            # 写入数据
            for bill in bills:
                source_text = "手动录入" if bill['source'] == 'manual' else "拍照识别"
                ws.append([
                    bill['customer_name'],
                    bill['date'],
                    bill['specification'],
                    bill['quantity'],
                    bill['unit_price'],
                    bill['total_price'],
                    source_text
                ])
            
            # 保存文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"账单明细_{timestamp}.xlsx"
            filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)
            
            wb.save(filepath)
            self.show_message("成功", f"账单已导出到:\n{filepath}")
            
        except Exception as e:
            self.show_message("错误", f"导出失败: {str(e)}")
    
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
