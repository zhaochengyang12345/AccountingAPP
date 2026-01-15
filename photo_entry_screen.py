"""
拍照记账界面 - OCR识别发票信息
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.uix.image import Image
from datetime import datetime
import os

try:
    from plyer import camera
    from PIL import Image as PILImage
    import pytesseract
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False


class PhotoEntryScreen(MDScreen):
    """拍照记账界面"""
    
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.photo_path = None
        self.build_ui()
    
    def build_ui(self):
        """构建拍照记账界面UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # 标题栏
        toolbar = MDTopAppBar(
            title="拍照记账",
            elevation=2,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            md_bg_color=(0.3, 0.7, 0.4, 1)
        )
        layout.add_widget(toolbar)
        
        # 内容区域
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # 相机功能提示
        if not CAMERA_AVAILABLE:
            warning_label = MDLabel(
                text="注意：相机和OCR功能仅在Android设备上可用\n当前为测试环境，可手动填写数据",
                theme_text_color="Error",
                halign="center",
                size_hint_y=None,
                height=dp(60),
                padding=[dp(10), 0]
            )
            content.add_widget(warning_label)
        
        # 拍照按钮
        camera_btn = MDRaisedButton(
            text="拍摄发票",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=self.take_photo
        )
        content.add_widget(camera_btn)
        
        # 图片预览区域
        self.image_widget = Image(
            size_hint=(1, None),
            height=dp(200),
            allow_stretch=True,
            keep_ratio=True
        )
        content.add_widget(self.image_widget)
        
        # OCR识别按钮
        ocr_btn = MDRaisedButton(
            text="识别文字",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.2, 0.6, 0.8, 1),
            on_release=self.recognize_text
        )
        content.add_widget(ocr_btn)
        
        # 客户名称
        self.customer_field = MDTextField(
            hint_text="客户名称",
            size_hint=(1, None),
            height=dp(56)
        )
        content.add_widget(self.customer_field)
        
        # 日期
        self.date_field = MDTextField(
            hint_text="日期 (YYYY-MM-DD)",
            text=datetime.now().strftime("%Y-%m-%d"),
            size_hint=(1, None),
            height=dp(56)
        )
        content.add_widget(self.date_field)
        
        # 规格
        self.specification_field = MDTextField(
            hint_text="规格",
            size_hint=(1, None),
            height=dp(56)
        )
        content.add_widget(self.specification_field)
        
        # 数量
        self.quantity_field = MDTextField(
            hint_text="数量",
            input_filter="float",
            size_hint=(1, None),
            height=dp(56)
        )
        self.quantity_field.bind(text=self.calculate_total)
        content.add_widget(self.quantity_field)
        
        # 单价
        self.unit_price_field = MDTextField(
            hint_text="单价",
            input_filter="float",
            size_hint=(1, None),
            height=dp(56)
        )
        self.unit_price_field.bind(text=self.calculate_total)
        content.add_widget(self.unit_price_field)
        
        # 总价
        self.total_price_field = MDTextField(
            hint_text="总价",
            readonly=True,
            size_hint=(1, None),
            height=dp(56)
        )
        content.add_widget(self.total_price_field)
        
        # 保存按钮
        save_btn = MDRaisedButton(
            text="保存账单",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=self.save_bill
        )
        content.add_widget(save_btn)
        
        # 滚动视图
        scroll = MDScrollView()
        scroll.add_widget(content)
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
        self.photo_path = None
        self.image_widget.source = ""
        self.customer_field.text = ""
        self.date_field.text = datetime.now().strftime("%Y-%m-%d")
        self.specification_field.text = ""
        self.quantity_field.text = ""
        self.unit_price_field.text = ""
        self.total_price_field.text = ""
    
    def take_photo(self, instance):
        """拍摄照片"""
        if not CAMERA_AVAILABLE:
            self.show_message("提示", "相机功能仅在Android设备上可用")
            return
        
        try:
            # 生成照片保存路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.photo_path = f"/storage/emulated/0/DCIM/accounting_{timestamp}.jpg"
            
            # 调用相机
            camera.take_picture(
                filename=self.photo_path,
                on_complete=self.on_photo_complete
            )
        except Exception as e:
            self.show_message("错误", f"拍照失败: {str(e)}")
    
    def on_photo_complete(self, filename):
        """照片拍摄完成回调"""
        if filename:
            self.photo_path = filename
            self.image_widget.source = filename
            self.image_widget.reload()
            self.show_message("成功", "照片拍摄成功，请点击识别文字")
        else:
            self.show_message("错误", "照片拍摄失败")
    
    def recognize_text(self, instance):
        """识别文字"""
        if not self.photo_path:
            self.show_message("提示", "请先拍摄照片")
            return
        
        if not CAMERA_AVAILABLE:
            self.show_message("提示", "OCR功能仅在Android设备上可用\n您可以手动填写以下信息")
            return
        
        try:
            # 使用 pytesseract 进行OCR识别
            image = PILImage.open(self.photo_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            # 解析识别的文字（这里是简单示例，实际需要根据发票格式优化）
            self.parse_ocr_text(text)
            
            self.show_message("成功", "文字识别完成，请检查并补全信息")
        except Exception as e:
            self.show_message("错误", f"识别失败: {str(e)}\n请手动填写信息")
    
    def parse_ocr_text(self, text):
        """解析OCR识别的文字"""
        # 这是一个简单的解析示例
        # 实际应用中需要根据具体的发票格式进行优化
        
        lines = text.split('\n')
        
        # 尝试提取日期（格式：YYYY-MM-DD 或 YYYY/MM/DD）
        import re
        date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        for line in lines:
            date_match = re.search(date_pattern, line)
            if date_match:
                date_str = date_match.group(1).replace('/', '-')
                self.date_field.text = date_str
                break
        
        # 尝试提取数字（可能是数量或金额）
        number_pattern = r'(\d+\.?\d*)'
        numbers = []
        for line in lines:
            matches = re.findall(number_pattern, line)
            numbers.extend(matches)
        
        # 如果找到数字，尝试填充字段
        if len(numbers) >= 2:
            self.quantity_field.text = numbers[0]
            self.unit_price_field.text = numbers[1]
    
    def calculate_total(self, *args):
        """计算总价"""
        try:
            quantity = float(self.quantity_field.text) if self.quantity_field.text else 0
            unit_price = float(self.unit_price_field.text) if self.unit_price_field.text else 0
            
            total = quantity * unit_price
            self.total_price_field.text = f"{total:.2f}"
        except ValueError:
            self.total_price_field.text = "0.00"
    
    def save_bill(self, instance):
        """保存账单"""
        # 验证数据
        customer_name = self.customer_field.text.strip()
        if not customer_name:
            self.show_message("错误", "请输入客户名称")
            return
        
        specification = self.specification_field.text.strip()
        if not specification:
            self.show_message("错误", "请输入规格")
            return
        
        try:
            quantity = float(self.quantity_field.text)
            if quantity <= 0:
                self.show_message("错误", "数量必须大于0")
                return
        except ValueError:
            self.show_message("错误", "请输入有效的数量")
            return
        
        try:
            unit_price = float(self.unit_price_field.text)
            if unit_price <= 0:
                self.show_message("错误", "单价必须大于0")
                return
        except ValueError:
            self.show_message("错误", "请输入有效的单价")
            return
        
        # 查找或创建客户
        customers = self.database.get_all_customers()
        customer_id = None
        for customer in customers:
            if customer['name'] == customer_name:
                customer_id = customer['id']
                break
        
        # 如果客户不存在，创建新客户
        if customer_id is None:
            success, message = self.database.add_customer(customer_name)
            if success:
                customers = self.database.get_all_customers()
                for customer in customers:
                    if customer['name'] == customer_name:
                        customer_id = customer['id']
                        break
            else:
                self.show_message("错误", f"创建客户失败: {message}")
                return
        
        # 保存到数据库
        success, message = self.database.add_bill(
            customer_id=customer_id,
            customer_name=customer_name,
            date=self.date_field.text,
            specification=specification,
            quantity=quantity,
            unit_price=unit_price,
            source='photo',
            photo_path=self.photo_path
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
