"""
数据库模块 - 管理客户、产品和账单数据
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class Database:
    def __init__(self, db_path: str = "accounting.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建客户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建产品规格表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                specification TEXT NOT NULL,
                unit_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建账单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                date TEXT NOT NULL,
                specification TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                source TEXT DEFAULT 'manual',
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== 客户管理 ====================
    
    def add_customer(self, name: str) -> Tuple[bool, str]:
        """添加客户"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            return True, "客户添加成功"
        except sqlite3.IntegrityError:
            return False, "客户已存在"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def get_all_customers(self) -> List[Dict]:
        """获取所有客户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM customers ORDER BY name")
        customers = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        return customers
    
    def delete_customer(self, customer_id: int) -> Tuple[bool, str]:
        """删除客户"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            conn.close()
            return True, "客户删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    # ==================== 产品管理 ====================
    
    def add_product(self, customer_id: int, specification: str, unit_price: float) -> Tuple[bool, str]:
        """添加产品规格"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (customer_id, specification, unit_price) VALUES (?, ?, ?)",
                (customer_id, specification, unit_price)
            )
            conn.commit()
            conn.close()
            return True, "产品添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def get_products_by_customer(self, customer_id: int) -> List[Dict]:
        """获取指定客户的所有产品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, specification, unit_price FROM products WHERE customer_id = ? ORDER BY specification",
            (customer_id,)
        )
        products = [
            {"id": row[0], "specification": row[1], "unit_price": row[2]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return products
    
    def update_product(self, product_id: int, specification: str, unit_price: float) -> Tuple[bool, str]:
        """更新产品信息"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET specification = ?, unit_price = ? WHERE id = ?",
                (specification, unit_price, product_id)
            )
            conn.commit()
            conn.close()
            return True, "产品更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """删除产品"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            return True, "产品删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    # ==================== 账单管理 ====================
    
    def add_bill(self, customer_id: int, customer_name: str, date: str, 
                 specification: str, quantity: float, unit_price: float, 
                 source: str = 'manual', photo_path: str = None) -> Tuple[bool, str]:
        """添加账单"""
        try:
            total_price = quantity * unit_price
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO bills (customer_id, customer_name, date, specification, 
                   quantity, unit_price, total_price, source, photo_path) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (customer_id, customer_name, date, specification, quantity, 
                 unit_price, total_price, source, photo_path)
            )
            conn.commit()
            conn.close()
            return True, "账单添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def get_all_bills(self) -> List[Dict]:
        """获取所有账单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, customer_id, customer_name, date, specification, 
               quantity, unit_price, total_price, source, photo_path, created_at 
               FROM bills ORDER BY date DESC, created_at DESC"""
        )
        bills = [
            {
                "id": row[0],
                "customer_id": row[1],
                "customer_name": row[2],
                "date": row[3],
                "specification": row[4],
                "quantity": row[5],
                "unit_price": row[6],
                "total_price": row[7],
                "source": row[8],
                "photo_path": row[9],
                "created_at": row[10]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        return bills
    
    def filter_bills(self, customer_name: Optional[str] = None, 
                    start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> List[Dict]:
        """筛选账单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """SELECT id, customer_id, customer_name, date, specification, 
                   quantity, unit_price, total_price, source, photo_path, created_at 
                   FROM bills WHERE 1=1"""
        params = []
        
        if customer_name:
            query += " AND customer_name = ?"
            params.append(customer_name)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        cursor.execute(query, params)
        bills = [
            {
                "id": row[0],
                "customer_id": row[1],
                "customer_name": row[2],
                "date": row[3],
                "specification": row[4],
                "quantity": row[5],
                "unit_price": row[6],
                "total_price": row[7],
                "source": row[8],
                "photo_path": row[9],
                "created_at": row[10]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        return bills
    
    def delete_bill(self, bill_id: int) -> Tuple[bool, str]:
        """删除账单"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
            conn.commit()
            conn.close()
            return True, "账单删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_bill_statistics(self, customer_name: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict:
        """获取账单统计信息"""
        bills = self.filter_bills(customer_name, start_date, end_date)
        
        total_amount = sum(bill['total_price'] for bill in bills)
        total_count = len(bills)
        
        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "bills": bills
        }
