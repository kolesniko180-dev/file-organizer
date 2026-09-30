#!/usr/bin/env python3
"""
File Organizer - Програма для автоматичного перейменування та сортування файлів
"""

import argparse
import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class FileOrganizer:
    """Клас для организації файлів за шаблонами та правилами"""

    # Стандартні правила категоризації за розширеннями
    DEFAULT_CATEGORIES = {
        # Зображення
        'jpg': 'Зображення', 'jpeg': 'Зображення', 'png': 'Зображення',
        'gif': 'Зображення', 'bmp': 'Зображення', 'svg': 'Зображення',
        'webp': 'Зображення', 'ico': 'Зображення', 'tiff': 'Зображення',
        
        # Документи
        'pdf': 'Документи', 'doc': 'Документи', 'docx': 'Документи',
        'txt': 'Документи', 'rtf': 'Документи', 'odt': 'Документи',
        'xlsx': 'Таблиці', 'xls': 'Таблиці', 'csv': 'Таблиці',
        'ppt': 'Презентації', 'pptx': 'Презентації', 'odp': 'Презентації',
        
        # Аудіо
        'mp3': 'Аудіо', 'wav': 'Аудіо', 'flac': 'Аудіо',
        'aac': 'Аудіо', 'ogg': 'Аудіо', 'm4a': 'Аудіо', 'wma': 'Аудіо',
        
        # Відео
        'mp4': 'Відео', 'avi': 'Відео', 'mov': 'Відео',
        'mkv': 'Відео', 'wmv': 'Відео', 'flv': 'Відео', 'webm': 'Відео',
        
        # Архіви
        'zip': 'Архіви', 'rar': 'Архіви', '7z': 'Архіви',
        'tar': 'Архіви', 'gz': 'Архіви', 'bz2': 'Архіви',
        
        # Код
        'py': 'Код', 'js': 'Код', 'ts': 'Код', 'tsx': 'Код',
        'java': 'Код', 'cpp': 'Код', 'c': 'Код', 'cs': 'Код',
        'php': 'Код', 'html': 'Код', 'css': 'Код', 'json': 'Код',
        'xml': 'Код', 'yaml': 'Код', 'yml': 'Код', 'go': 'Код',
        'rb': 'Код', 'rs': 'Код', 'swift': 'Код',
    }

    def __init__(self, source_dir: str, target_dir: Optional[str] = None):
        """
        Ініціалізація організатора файлів
        
        Args:
            source_dir: Папка з файлами для обробки
            target_dir: Папка призначення (за замовчуванням = source_dir)
        """
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve() if target_dir else self.source_dir
        self.categories = self.DEFAULT_CATEGORIES.copy()
        self.operations = []
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Папка не існує: {self.source_dir}")
        
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def load_custom_rules(self, config_file: str) -> None:
        """Завантажити користувацькі правила з JSON файлу"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.categories.update(config.get('categories', {}))
        except FileNotFoundError:
            print(f"⚠️  Файл конфігурації не знайдено: {config_file}")

    def add_custom_rule(self, extension: str, category: str) -> None:
        """Додати користувацьке правило"""
        ext = extension.lower().lstrip('.')
        self.categories[ext] = category

    def get_category(self, file_path: Path) -> str:
        """Визначити категорію файлу за розширенням"""
        ext = file_path.suffix.lower().lstrip('.')
        return self.categories.get(ext, 'Інше')

    def normalize_filename(self, name: str) -> str:
        """Нормалізувати ім'я файлу"""
        # Видалити спеціальні символи
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Замінити кілька пробілів на один
        name = re.sub(r'\s+', ' ', name)
        # Видалити пробіли на початку/кінці
        name = name.strip()
        return name or 'файл'

    def generate_new_name(self, file_path: Path, template: str, counter: int = 1) -> str:
        """
        Згенерувати нове ім'я файлу за шаблоном
        
        Доступні змінні:
        {name} - ім'я файлу без розширення
        {ext} - розширення файлу
        {category} - категорія файлу
        {date} - дата модифікації (YYYY-MM-DD)
        {datetime} - дата й час (YYYY-MM-DD_HH-MM-SS)
        {counter} - лічильник для унікальності
        {year}, {month}, {day}, {hour}, {minute}, {second}
        """
        file_stat = file_path.stat()
        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        
        # Заготовка шаблонних змінних
        variables = {
            'name': self.normalize_filename(file_path.stem),
            'ext': file_path.suffix.lstrip('.').lower(),
            'category': self.get_category(file_path),
            'date': mod_time.strftime('%Y-%m-%d'),
            'datetime': mod_time.strftime('%Y-%m-%d_%H-%M-%S'),
            'year': str(mod_time.year),
            'month': str(mod_time.month).zfill(2),
            'day': str(mod_time.day).zfill(2),
            'hour': str(mod_time.hour).zfill(2),
            'minute': str(mod_time.minute).zfill(2),
            'second': str(mod_time.second).zfill(2),
            'counter': str(counter),
        }
        
        # Замінити змінні в шаблоні
        new_name = template
        for key, value in variables.items():
            new_name = new_name.replace('{' + key + '}', value)
        
        # Додати розширення якщо його немає
        if not new_name.endswith('.' + variables['ext']):
            new_name += '.' + variables['ext']
        
        return new_name

    def get_unique_path(self, target_dir: Path, filename: str) -> Path:
        """Повернути унікальний шлях, уникаючи конфліктів імен"""
        target_path = target_dir / filename
        
        if not target_path.exists():
            return target_path
        
        # Якщо файл існує, додати лічильник до імені
        stem = Path(filename).stem
        ext = Path(filename).suffix
        counter = 1
        
        while True:
            new_name = f"{stem}_{counter}{ext}"
            new_path = target_dir / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def organize(self, template: str = '{name}_{date}.{ext}', 
                sort_by: str = 'category', dry_run: bool = False) -> List[Dict]:
        """
        Організувати файли
        
        Args:
            template: Шаблон нового імені файлу
            sort_by: Спосіб сортування ('category', 'extension', 'date')
            dry_run: Якщо True, тільки показати що буде зроблено
        
        Returns:
            Список операцій
        """
        self.operations = []
        files = [f for f in self.source_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            print("❌ Файли не знайдено в папці")
            return []
        
        print(f"\n📁 Обробка {len(files)} файлів...\n")
        
        for file_path in sorted(files):
            # Визначити папку призначення
            if sort_by == 'extension':
                ext = file_path.suffix.lstrip('.').upper() or 'БЕЗ_РОЗШИРЕННЯ'
                folder_name = ext
            elif sort_by == 'date':
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                folder_name = mod_time.strftime('%Y-%m')
            else:  # category
                folder_name = self.get_category(file_path)
            
            # Створити папку призначення
            target_subdir = self.target_dir / folder_name
            if not dry_run:
                target_subdir.mkdir(parents=True, exist_ok=True)
            
            # Згенерувати нове ім'я
            new_filename = self.generate_new_name(file_path, template)
            new_path = self.get_unique_path(target_subdir, new_filename)
            
            # Пропустити якщо файл уже на місці
            if new_path == file_path:
                continue
            
            operation = {
                'source': str(file_path),
                'target': str(new_path),
                'category': folder_name,
                'old_name': file_path.name,
                'new_name': new_filename,
            }
            self.operations.append(operation)
            
            # Виконати перейменування/переміщення
            if not dry_run:
                try:
                    shutil.move(str(file_path), str(new_path))
                    print(f"✅ {file_path.name:40} → {new_filename:40}")
                except Exception as e:
                    print(f"❌ Помилка з файлом {file_path.name}: {e}")
                    self.operations[-1]['error'] = str(e)
            else:
                print(f"👁️  [PREVIEW] {file_path.name:40} → {new_filename:40}")
        
        return self.operations

    def print_summary(self) -> None:
        """Вивести підсумок операцій"""
        if not self.operations:
            print("\n📭 Не було виконано операцій")
            return
        
        print(f"\n{'='*80}")
        print(f"✨ Успішно оброблено {len(self.operations)} файлів")
        print(f"{'='*80}\n")
        
        # Групувати за категоріями
        by_category = {}
        for op in self.operations:
            cat = op['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(op)
        
        for category, ops in sorted(by_category.items()):
            print(f"📂 {category}: {len(ops)} файлів")
            for op in ops[:3]:  # Показати перші 3 файли
                print(f"   • {op['old_name']} → {op['new_name']}")
            if len(ops) > 3:
                print(f"   • ... та ще {len(ops) - 3}")

    def save_report(self, report_file: str = 'organize_report.json') -> None:
        """Зберегти звіт про операції"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'source_dir': str(self.source_dir),
            'target_dir': str(self.target_dir),
            'operations_count': len(self.operations),
            'operations': self.operations,
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Звіт збережено: {report_file}")


def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(
        description='File Organizer - Автоматичне перейменування та сортування файлів',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Приклади використання:

  # Сортування за категоріями з датою в назві
  python file_organizer.py --source ./downloads --sort-by category --template "{category}_{name}_{date}"

  # Сортування за розширеннями
  python file_organizer.py --source ./downloads --sort-by extension --template "{name}_{date}"

  # Попередній перегляд без змін
  python file_organizer.py --source ./downloads --dry-run

  # Сортування за датою зі спеціальним шаблоном
  python file_organizer.py --source ./downloads --sort-by date --template "{year}/{month}/{day}_{name}"

  # З користувацькими правилами
  python file_organizer.py --source ./downloads --config rules.json
        '''
    )
    
    parser.add_argument('--source', required=True, help='Папка з файлами для обробки')
    parser.add_argument('--target', help='Папка призначення (за замовчуванням = source)')
    parser.add_argument('--template', default='{name}_{date}.{ext}',
                       help='Шаблон нового імені файлу (за замовчуванням: {name}_{date}.{ext})')
    parser.add_argument('--sort-by', choices=['category', 'extension', 'date'], 
                       default='category', help='Спосіб сортування (за замовчуванням: category)')
    parser.add_argument('--config', help='JSON файл з користувацькими правилами')
    parser.add_argument('--dry-run', action='store_true', help='Попередній перегляд без змін')
    parser.add_argument('--report', help='Зберегти звіт про операції в JSON файл')
    
    args = parser.parse_args()
    
    try:
        # Створити організатор
        organizer = FileOrganizer(args.source, args.target)
        
        # Завантажити користувацькі правила
        if args.config:
            organizer.load_custom_rules(args.config)
        
        # Виконати сортування
        organizer.organize(
            template=args.template,
            sort_by=args.sort_by,
            dry_run=args.dry_run
        )
        
        # Вивести підсумок
        organizer.print_summary()
        
        # Зберегти звіт
        if args.report:
            organizer.save_report(args.report)
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
