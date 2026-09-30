# Land Registry Analytics

Streamlit-застосунок для аналізу реєстру земельних ділянок (MS SQL Server, `UPI_AGRO_WORK`).

## Запуск
```powershell
.\scripts\setup.ps1              # створює .venv, ставить залежності, готує .env
uv run streamlit run app.py
```
Потрібен встановлений **ODBC Driver 17 for SQL Server**. Файл `UPI.png` (іконка) лежить у корені.

## Структура
| Шлях | Призначення |
|---|---|
| `app.py` | точка входу: збирає сторінку з блоків |
| `land_registry/config.py` | константи, кольори, періоди, env |
| `land_registry/db.py` | SQLAlchemy engine |
| `land_registry/repository.py` | усі SQL-запити (кешовані) |
| `land_registry/geo.py` | WKT → GeoJSON (shapely), bounds |
| `land_registry/domain.py` | бізнес-логіка: категорії, підготовка, зведення |
| `land_registry/exports.py` | Excel-експорти (xlsxwriter / openpyxl) |
| `land_registry/ui/` | блоки інтерфейсу: filters, summary, analytics, map_view |
| `sql/` | коригувальні скрипти (`@Apply = 0` → перегляд → `1` → застосування) |

## Перевірки
```powershell
uv run ruff check .
uv run python -m compileall -q app.py land_registry
```
