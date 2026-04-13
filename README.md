# 👟 Sneaker Shop — Рефакторинг коду

## Опис проєкту

Цей проєкт демонструє практичне застосування технік рефакторингу до реального Python-застосунку — системи управління магазином кросівок. Початковий код функціональний, але містить численні «запахи коду». Рефакторизована версія усуває ці проблеми без зміни зовнішньої поведінки.

---

## Структура проєкту

```
/project-root
├── original_code.py          # Оригінальна версія (процедурний стиль)
├── refactored_code.py        # Рефакторизована версія (OOP + чисті техніки)
├── tests/
│   └── test_cases.py         # 40 юніт-тестів
├── docs/
│   └── refactoring_report.md # Детальний звіт по рефакторингу
└── README.md
```

---

## Застосовані техніки рефакторингу (10+)

| # | Техніка | Де застосовано |
|---|---------|----------------|
| 1 | Replace Magic Number with Symbolic Constant | Константи `BONUS_RATE`, `DELIVERY_COSTS`, статуси |
| 2 | Replace Array with Object | `ShoeVariant`, `OrderItem`, `CartItem` замість списків |
| 3 | Move Method | Логіка tier/bonus перенесена в клас `Customer` |
| 4 | Extract Method | `_find_shoe()`, `_validate_cart_items()`, `_reserve_items()` |
| 5 | Replace Temp with Query | `CartItem.subtotal`, `Cart.total()`, `OrderItem.subtotal` |
| 6 | Separate Query from Modifier | `get_sales_stats()` / `show_sales_report()` |
| 7 | Replace Nested Conditional with Guard Clauses | `place_order()`, `update_order_status()`, `create_return()` |
| 8 | Rename Method | camelCase → snake_case, `newShoe`→`add_shoe`, `stockUp`→`restock` |
| 9 | Consolidate Conditional Expression | `recalculate_tier()` — 4 окремих `if` → `if/elif/else` |
| 10 | Remove Control Flag | Булевий прапорець `bought` → `any()` у `rate_shoe()` |

---

## Запуск тестів

### Вимоги
- Python 3.10+
- Стандартна бібліотека (без зовнішніх залежностей)

### Команда

```bash
python -m pytest tests/test_cases.py -v
```

або без pytest:

```bash
python tests/test_cases.py
```

---

## Ключові покращення

- **Рядків коду:** 621 → 797 (більше, але структурованіше — класи, типи)
- **Класів/функцій:** 0 класів / 30 функцій → 11 класів / 40 методів
- **Читабельність:** індексний доступ `v[0]`, `v[2]` → іменовані атрибути `v.size`, `v.in_stock`
- **Цикломатична складність:** `placeOrder` — D(30) → `place_order` — C(11)
- **Повторний код:** усунено 18+ дублюючих блоків пошуку через _find_* методи (5 окремих методів: _find_shoe, _find_customer, _find_order, _find_promo, _find_supplier)
