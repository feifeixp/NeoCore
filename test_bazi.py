#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from WorldBuilder.bazi_analyzer import BaziAnalyzer

def main():
    """测试八字计算"""
    analyzer = BaziAnalyzer()
    
    # 运行内置测试
    analyzer.test_bazi_calculation()
    
    # 测试特定日期
    test_date = datetime(1982, 12, 3, 12, 0)
    print(f"\n\n测试特定日期: {test_date}")
    bazi = analyzer.get_bazi(test_date)
    print(f"八字结果: {bazi['sizhu']}")
    print(f"年柱: {bazi['year']}")
    print(f"月柱: {bazi['month']}")
    print(f"日柱: {bazi['day']}")
    print(f"时柱: {bazi['hour']}")
    
    # 允许用户输入日期进行测试
    try:
        user_input = input("\n\n请输入要测试的日期 (格式: YYYY-MM-DD HH:MM): ")
        user_date = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
        print(f"测试用户输入日期: {user_date}")
        user_bazi = analyzer.get_bazi(user_date)
        print(f"八字结果: {user_bazi['sizhu']}")
        print(f"年柱: {user_bazi['year']}")
        print(f"月柱: {user_bazi['month']}")
        print(f"日柱: {user_bazi['day']}")
        print(f"时柱: {user_bazi['hour']}")
    except Exception as e:
        print(f"处理用户输入时出错: {str(e)}")

if __name__ == "__main__":
    main() 