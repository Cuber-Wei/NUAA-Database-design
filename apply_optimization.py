#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL优化应用脚本
一键应用数据库优化
"""

import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "wishes_db",
    "charset": "utf8mb4",
}


def get_db_connection():
    """获取数据库连接"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def apply_sql_optimization():
    """应用SQL优化"""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        with connection.cursor() as cursor:
            print("🚀 开始应用SQL优化...")

            # 优化步骤
            optimizations = [
                {
                    "name": "删除低效索引",
                    "sql": "ALTER TABLE wishes DROP INDEX IF EXISTS idx_wtype",
                },
                {
                    "name": "添加用户+时间复合索引",
                    "sql": "ALTER TABLE wishes ADD INDEX IF NOT EXISTS idx_user_time_desc (Wuser, Wtime DESC)",
                },
                {
                    "name": "添加用户+类型+时间复合索引",
                    "sql": "ALTER TABLE wishes ADD INDEX IF NOT EXISTS idx_user_type_time (Wuser, Wtype, Wtime DESC)",
                },
                {
                    "name": "添加覆盖索引",
                    "sql": "ALTER TABLE wishes ADD INDEX IF NOT EXISTS idx_user_cover (Wuser, Wtime DESC, Wtype, Wcharacter, Wweapon)",
                },
                {
                    "name": "添加时间索引",
                    "sql": "ALTER TABLE wishes ADD INDEX IF NOT EXISTS idx_time_desc (Wtime DESC)",
                },
            ]

            # 执行优化
            for opt in optimizations:
                try:
                    print(f"  📝 {opt['name']}...")
                    cursor.execute(opt["sql"])
                    print(f"  ✅ {opt['name']} 完成")
                except Exception as e:
                    print(f"  ⚠️  {opt['name']} 跳过: {e}")

            connection.commit()
            print("\n🎉 SQL优化应用完成！")

            # 验证索引
            print("\n📋 验证索引状态:")
            cursor.execute("SHOW INDEX FROM wishes")
            indexes = cursor.fetchall()

            for idx in indexes:
                print(f"  📈 {idx[2]}: {idx[4]}")  # Key_name: Column_name

            return True

    except Exception as e:
        print(f"❌ 优化失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


if __name__ == "__main__":
    print("🎯 原神抽卡系统 - SQL优化工具")
    print("=" * 50)

    # 确认操作
    confirm = input("是否要应用SQL优化？(y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("❌ 操作已取消")
        sys.exit(0)

    # 应用优化
    if apply_sql_optimization():
        print("\n✅ 优化成功！建议运行 python test_performance.py 验证性能")
    else:
        print("\n❌ 优化失败！请检查数据库连接和权限")
        sys.exit(1)
