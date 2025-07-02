import argparse
import csv
from typing import List, Dict, Optional, Tuple, Any
from tabulate import tabulate


def read_csv(file_path: str) -> List[Dict[str, str]]:
    """Читает CSV-файл и возвращает список строк."""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def apply_filter(rows: List[Dict[str, str]], condition: Optional[str]) -> List[Dict[str, str]]:
    """Фильтрует строки по условию, например 'rating>4.5'."""
    if not condition:
        return rows
    column, op, value = parse_condition(condition)
    filtered: List[Dict[str, str]] = []

    for row in rows:
        cell: Any = row[column]
        if is_number(cell):
            cell = float(cell)
            value = float(value)
        if (
            (op == '>' and cell > value) or
            (op == '<' and cell < value) or
            (op == '=' and cell == value)
        ):
            filtered.append(row)

    return filtered


def parse_condition(condition: str) -> Tuple[str, str, str]:
    """Парсит строку условия фильтрации, например 'price>500'."""
    for op in ['>=', '<=', '>', '<', '=']:
        if op in condition:
            column, value = condition.split(op)
            return column.strip(), op, value.strip()
    raise ValueError("Invalid filter condition")


def is_number(s: str) -> bool:
    """Проверяет, является ли строка числом."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def aggregate(rows: List[Dict[str, str]], agg_str: Optional[str]) -> Optional[Dict[str, float]]:
    """Выполняет агрегацию: avg, min, max."""
    if not agg_str:
        return None

    column, op = agg_str.split('=')
    column, op = column.strip(), op.strip()
    values = [float(row[column]) for row in rows]

    if op == 'avg':
        result = sum(values) / len(values)
    elif op == 'min':
        result = min(values)
    elif op == 'max':
        result = max(values)
    else:
        raise ValueError("Invalid aggregation operation")

    return {op: round(result, 2)}


def apply_order(rows: List[Dict[str, str]], order_str: Optional[str]) -> List[Dict[str, str]]:
    """Сортирует строки по колонке: 'column=asc' или 'column=desc'."""
    if not order_str:
        return rows

    parts = order_str.strip().split('=')
    if len(parts) != 2:
        raise ValueError("Invalid order-by format. Use column=asc or column=desc")

    column, direction = parts
    reverse = direction.lower() == 'desc'

    return sorted(
        rows,
        key=lambda r: float(r[column]) if is_number(r[column]) else r[column],
        reverse=reverse
    )


def main() -> None:
    """Точка входа CLI: парсит аргументы, запускает фильтрацию, агрегацию и сортировку."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to CSV file')
    parser.add_argument('--where', help='Filter condition, e.g. rating>4.5')
    parser.add_argument('--aggregate', help='Aggregate, e.g. rating=avg')
    parser.add_argument('--order-by', help='Order by, e.g. rating=desc or name=asc')
    args = parser.parse_args()

    rows = read_csv(args.file)
    rows = apply_filter(rows, args.where)
    rows = apply_order(rows, args.order_by)

    if args.aggregate:
        result = aggregate(rows, args.aggregate)
        print(tabulate([result.values()], headers=result.keys(), tablefmt="grid"))
    else:
        print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == '__main__':
    main()
