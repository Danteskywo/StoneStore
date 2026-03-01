import os
import re
from pathlib import Path

def add_i18n_attributes_to_file(filepath):
    """Добавляет data-i18n атрибуты ко всем текстам в HTML файле"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим все текстовые узлы в HTML
    # Это упрощенная версия, но для большинства случаев сработает
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Пропускаем строки с Django тегами
        if '{%' in line and '%}' in line:
            new_lines.append(line)
            continue
        
        # Ищем текст между тегами
        modified_line = line
        # Паттерн для нахождения текста между > и <
        pattern = r'>([^<]+)<'
        
        def replace_text(match):
            text = match.group(1).strip()
            if text and not text.startswith('{%') and not text.endswith('%}') and len(text) > 1:
                # Проверяем, нет ли уже data-i18n
                if 'data-i18n=' not in line:
                    return f' data-i18n="{text}">{text}<'
            return f'>{text}<'
        
        # Применяем замену
        matches = re.findall(pattern, line)
        if matches:
            for text in matches:
                if text and len(text.strip()) > 1 and 'data-i18n' not in line:
                    modified_line = line.replace(f'>{text}<', f' data-i18n="{text}">{text}<')
                    break
        
        new_lines.append(modified_line)
    
    # Записываем обратно
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Обработан: {filepath}")

def main():
    templates_dir = Path('templates')
    
    # Рекурсивно обходим все HTML файлы
    for html_file in templates_dir.rglob('*.html'):
        if html_file.is_file():
            try:
                add_i18n_attributes_to_file(html_file)
            except Exception as e:
                print(f"❌ Ошибка в {html_file}: {e}")

if __name__ == '__main__':
    main()
    print("\n✅ Все файлы обработаны! Теперь добавьте переводы в static/js/i18n.js")