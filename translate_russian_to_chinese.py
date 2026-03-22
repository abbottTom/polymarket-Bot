#!/usr/bin/env python3
"""批量将Python文件中的俄语翻译为中文"""

import re
from pathlib import Path

# 俄语到中文的常见翻译映射
TRANSLATIONS = {
    # 常见词汇
    "Анализ": "分析",
    "анализ": "分析",
    "Проверка": "检查",
    "проверка": "检查",
    "Тест": "测试",
    "тест": "测试",
    "Демо": "演示",
    "демо": "演示",
    "Скрипт": "脚本",
    "скрипт": "脚本",
    "Функция": "函数",
    "функция": "函数",
    "Запуск": "运行",
    "запуск": "运行",
    "Успешно": "成功",
    "успешно": "成功",
    "Ошибка": "错误",
    "ошибка": "错误",
    "Результат": "结果",
    "результат": "结果",
    "Отчет": "报告",
    "отчет": "报告",
    "Данные": "数据",
    "данные": "数据",
    "Глубина": "深度",
    "глубина": "深度",
    "Цена": "价格",
    "цена": "价格",
    "Проскальзывание": "滑点",
    "проскальзывание": "滑点",
    "Арбитраж": "套利",
    "арбитраж": "套利",
    "Бот": "机器人",
    "бот": "机器人",
    "Рынок": "市场",
    "рынок": "市场",
    "Биржа": "交易所",
    "биржа": "交易所",
    "Стакан": "订单簿",
    "стакан": "订单簿",
    "Спред": "价差",
    "спред": "价差",

    # 动词
    "Генерируем": "生成",
    "генерируем": "生成",
    "Выводим": "输出",
    "выводим": "输出",
    "Вычисляем": "计算",
    "вычисляем": "计算",
    "Запускаем": "运行",
    "запускаем": "运行",
    "Проверяем": "检查",
    "проверяем": "检查",
    "Тестируем": "测试",
    "тестируем": "测试",

    # 短语
    "для": "用于",
    "с": "使用",
    "и": "和",
    "или": "或",
    "не": "不",
    "это": "这",
    "который": "的",
    "что": "什么",
    "все": "所有",
    "один": "一个",
    "два": "两个",
    "три": "三个",
}

def translate_line(line: str) -> str:
    """翻译一行中的俄语"""
    result = line
    # 按长度降序排序，避免部分匹配
    for rus, chi in sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        # 使用word boundary来避免部分匹配
        result = re.sub(rf'\b{re.escape(rus)}\b', chi, result)
    return result

def process_file(file_path: Path):
    """处理单个文件"""
    print(f"处理: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 检查是否包含俄语
        has_russian = any(re.search('[А-Яа-яЁё]', line) for line in lines)

        if not has_russian:
            print(f"  ✓ 无俄语，跳过")
            return

        # 翻译
        translated_lines = [translate_line(line) for line in lines]

        # 写回
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)

        # 检查是否还有俄语
        remaining_russian = sum(1 for line in translated_lines if re.search('[А-Яа-яЁё]', line))

        if remaining_russian > 0:
            print(f"  ⚠ 仍有 {remaining_russian} 行包含俄语（需要手动翻译）")
        else:
            print(f"  ✓ 已完全翻译")

    except Exception as e:
        print(f"  ✗ 错误: {e}")

def main():
    """主函数"""
    # 要处理的文件
    files = [
        "analyze_bot.py",
        "demo_arbitrage_logic.py",
        "demo_matching_detailed.py",
        "test_bot_logic.py",
        "test_deep_bugs.py",
        "experiments/main_improved_experimental.py",
        "tests/test_e2e_arbitrage.py",
        "tests/test_metrics.py",
        "tests/test_processor.py",
    ]

    base_dir = Path(__file__).parent

    print("🌐 批量翻译俄语到中文\n")

    for file_name in files:
        file_path = base_dir / file_name
        if file_path.exists():
            process_file(file_path)
        else:
            print(f"跳过（不存在）: {file_path}")

    print("\n✅ 批量翻译完成！")
    print("\n注意：自动翻译可能不完美，请手动检查剩余的俄语。")

if __name__ == "__main__":
    main()
