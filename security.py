#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全模块 - SQL注入防护和输入验证
提供全面的安全防护功能
"""

import re
import html
import pymysql
from typing import Any, Dict, List, Optional, Union
from functools import wraps
from flask import request, jsonify, flash, redirect, url_for

class SQLInjectionProtector:
    """SQL注入防护类"""
    
    # 危险的SQL关键词模式
    DANGEROUS_PATTERNS = [
        r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
        r'(\-\-|\#|\/\*|\*\/)',  # SQL注释
        r'(\;|\|\||&&)',  # SQL分隔符和逻辑操作符
        r'(\bor\b|\band\b)\s+\d+\s*=\s*\d+',  # 经典注入模式
        r'(\bor\b|\band\b)\s+[\'\"]\w+[\'\"]\s*=\s*[\'\"]\w+[\'\"]*',  # 字符串注入
        r'(\bor\b|\band\b)\s+\d+\s*<\s*\d+',  # 数字比较注入
        r'(\bor\b|\band\b)\s+[\'\"]\w*[\'\"]\s*like\s*[\'\"]\%',  # LIKE注入
        r'(script|javascript|vbscript|onload|onerror)',  # XSS防护
        r'(\<|\>|\&lt\;|\&gt\;)',  # HTML标签
    ]
    
    @classmethod
    def is_sql_injection_attempt(cls, input_string: str) -> bool:
        """
        检测是否为SQL注入尝试
        
        Args:
            input_string: 待检测的输入字符串
            
        Returns:
            bool: 如果检测到SQL注入尝试返回True，否则返回False
        """
        if not isinstance(input_string, str):
            return False
            
        # 转换为小写进行检测
        lower_input = input_string.lower()
        
        # 检查每个危险模式
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, lower_input, re.IGNORECASE):
                return True
                
        return False
    
    @classmethod
    def sanitize_input(cls, input_value: Any) -> str:
        """
        清理输入数据
        
        Args:
            input_value: 待清理的输入值
            
        Returns:
            str: 清理后的安全字符串
        """
        if input_value is None:
            return ""
            
        # 转换为字符串
        str_value = str(input_value).strip()
        
        # HTML转义
        str_value = html.escape(str_value)
        
        # 移除危险字符
        str_value = re.sub(r'[<>"\';\\]', '', str_value)
        
        return str_value
    
    @classmethod
    def validate_integer(cls, value: Any, min_val: int = None, max_val: int = None) -> Optional[int]:
        """
        验证并转换整数
        
        Args:
            value: 待验证的值
            min_val: 最小值限制
            max_val: 最大值限制
            
        Returns:
            Optional[int]: 验证通过返回整数，否则返回None
        """
        try:
            int_val = int(value)
            
            if min_val is not None and int_val < min_val:
                return None
            if max_val is not None and int_val > max_val:
                return None
                
            return int_val
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def validate_string(cls, value: Any, max_length: int = 255, allow_empty: bool = False) -> Optional[str]:
        """
        验证字符串
        
        Args:
            value: 待验证的值
            max_length: 最大长度限制
            allow_empty: 是否允许空字符串
            
        Returns:
            Optional[str]: 验证通过返回字符串，否则返回None
        """
        if value is None:
            return "" if allow_empty else None
            
        str_val = str(value).strip()
        
        # 检查长度
        if len(str_val) > max_length:
            return None
            
        # 检查是否为空
        if not allow_empty and not str_val:
            return None
            
        # 检查SQL注入
        if cls.is_sql_injection_attempt(str_val):
            return None
            
        return cls.sanitize_input(str_val)

class SecureDatabase:
    """安全数据库操作类"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = True):
        """
        安全执行查询
        
        Args:
            query: SQL查询语句（必须使用参数化查询）
            params: 查询参数
            fetch_one: 是否只获取一条记录
            fetch_all: 是否获取所有记录
            
        Returns:
            查询结果或None
        """
        # 验证查询语句是否使用了参数化查询
        if not self._is_parameterized_query(query, params):
            raise ValueError("查询必须使用参数化查询以防止SQL注入")
            
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
                    
        except Exception as e:
            print(f"查询执行失败: {e}")
            return None
        finally:
            connection.close()
    
    def execute_transaction(self, operations: List[Dict]):
        """
        安全执行事务
        
        Args:
            operations: 操作列表，每个操作包含query和params
            
        Returns:
            bool: 事务是否成功
        """
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            with connection.cursor() as cursor:
                # 开始事务
                connection.begin()
                
                for operation in operations:
                    query = operation.get('query', '')
                    params = operation.get('params', ())
                    
                    # 验证参数化查询
                    if not self._is_parameterized_query(query, params):
                        raise ValueError("所有查询必须使用参数化查询")
                        
                    cursor.execute(query, params)
                
                # 提交事务
                connection.commit()
                return True
                
        except Exception as e:
            print(f"事务执行失败: {e}")
            connection.rollback()
            return False
        finally:
            connection.close()
    
    def _is_parameterized_query(self, query: str, params: tuple) -> bool:
        """
        检查是否为参数化查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            bool: 是否为安全的参数化查询
        """
        # 计算查询中的占位符数量
        placeholder_count = query.count('%s')
        
        # 检查参数数量是否匹配
        if placeholder_count != len(params):
            return False
            
        # 检查是否包含直接拼接的危险内容
        if SQLInjectionProtector.is_sql_injection_attempt(query):
            return False
            
        return True

def sql_injection_protection(f):
    """
    SQL注入防护装饰器
    自动检查请求参数中的SQL注入尝试
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查GET参数
        for key, value in request.args.items():
            if SQLInjectionProtector.is_sql_injection_attempt(value):
                flash('检测到非法输入，请检查您的输入内容', 'error')
                return redirect(url_for('index'))
        
        # 检查POST参数
        if request.method == 'POST':
            for key, value in request.form.items():
                if isinstance(value, str) and SQLInjectionProtector.is_sql_injection_attempt(value):
                    flash('检测到非法输入，请检查您的输入内容', 'error')
                    return redirect(url_for('index'))
        
        # 检查JSON数据
        if request.is_json:
            json_data = request.get_json()
            if json_data:
                for key, value in json_data.items():
                    if isinstance(value, str) and SQLInjectionProtector.is_sql_injection_attempt(value):
                        return jsonify({'success': False, 'message': '检测到非法输入'})
        
        return f(*args, **kwargs)
    return decorated_function

def validate_user_input(username: str, password: str) -> Dict[str, Any]:
    """
    验证用户输入
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        Dict: 验证结果
    """
    result = {
        'valid': True,
        'errors': [],
        'username': None,
        'password': None
    }
    
    # 验证用户名
    clean_username = SQLInjectionProtector.validate_string(username, max_length=20, allow_empty=False)
    if clean_username is None:
        result['valid'] = False
        result['errors'].append('用户名格式不正确或包含非法字符')
    else:
        result['username'] = clean_username
    
    # 验证密码
    if not password or len(password) > 50:
        result['valid'] = False
        result['errors'].append('密码长度必须在1-50个字符之间')
    elif SQLInjectionProtector.is_sql_injection_attempt(password):
        result['valid'] = False
        result['errors'].append('密码包含非法字符')
    else:
        result['password'] = password
    
    return result

def validate_wish_params(wish_type: str, pool_type: str) -> Dict[str, Any]:
    """
    验证抽卡参数
    
    Args:
        wish_type: 抽卡类型
        pool_type: 卡池类型
        
    Returns:
        Dict: 验证结果
    """
    result = {
        'valid': True,
        'errors': [],
        'wish_type': None,
        'pool_type': None
    }
    
    # 验证抽卡类型
    if wish_type not in ['single', 'ten']:
        result['valid'] = False
        result['errors'].append('抽卡类型参数错误')
    else:
        result['wish_type'] = wish_type
    
    # 验证卡池类型
    if pool_type not in ['character', 'weapon']:
        result['valid'] = False
        result['errors'].append('卡池类型参数错误')
    else:
        result['pool_type'] = pool_type
    
    return result

def validate_pagination_params(page: Any, per_page: Any = 20) -> Dict[str, Any]:
    """
    验证分页参数
    
    Args:
        page: 页码
        per_page: 每页数量
        
    Returns:
        Dict: 验证结果
    """
    result = {
        'valid': True,
        'errors': [],
        'page': 1,
        'per_page': 20
    }
    
    # 验证页码
    validated_page = SQLInjectionProtector.validate_integer(page, min_val=1, max_val=10000)
    if validated_page is None:
        result['page'] = 1  # 默认第一页
    else:
        result['page'] = validated_page
    
    # 验证每页数量
    validated_per_page = SQLInjectionProtector.validate_integer(per_page, min_val=1, max_val=100)
    if validated_per_page is None:
        result['per_page'] = 20  # 默认20条
    else:
        result['per_page'] = validated_per_page
    
    return result

# 安全日志记录
def log_security_event(event_type: str, details: str, user_id: int = None):
    """
    记录安全事件
    
    Args:
        event_type: 事件类型
        details: 事件详情
        user_id: 用户ID（可选）
    """
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] SECURITY {event_type}: {details}"
    if user_id:
        log_message += f" (User: {user_id})"
    
    print(log_message)
    
    # 可以扩展为写入日志文件
    try:
        with open('security.log', 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception:
        pass  # 忽略日志写入错误

if __name__ == "__main__":
    # 测试SQL注入检测
    test_inputs = [
        "normal_username",
        "admin' OR '1'='1",
        "user; DROP TABLE users;--",
        "admin' UNION SELECT * FROM users--",
        "<script>alert('xss')</script>",
        "user' AND 1=1--"
    ]
    
    print("🔒 SQL注入检测测试:")
    print("=" * 50)
    
    for test_input in test_inputs:
        is_dangerous = SQLInjectionProtector.is_sql_injection_attempt(test_input)
        status = "🚨 危险" if is_dangerous else "✅ 安全"
        print(f"{status}: {test_input}")
    
    print("\n🧹 输入清理测试:")
    print("=" * 50)
    
    for test_input in test_inputs:
        cleaned = SQLInjectionProtector.sanitize_input(test_input)
        print(f"原始: {test_input}")
        print(f"清理: {cleaned}")
        print("-" * 30) 