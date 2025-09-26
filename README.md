# ZakupAI
Репозиторий для проекта ИИ-агента по закупкам 
# ZakupAI — ИИ-ассистент для закупок по 44-ФЗ

Автоматизирует обработку планов-графиков, извещений и протоколов на основе блок-cхемы.

## Структура
- `ingestion/` — приём PDF и данных из ЕИС  
- `ai_core/` — извлечение сущностей и валидация по 44-ФЗ  
- `rules/` — правила из статей 16, 59–83  
- `storage/` — работа с БД  
- `dashboard/` — экспорт для Power BI

## Первый запуск
```bash
pip install -r requirements.txt

#### 📄 `requirements.txt`
```txt
python==3.11
fastapi
uvicorn
pdfplumber
PyPDF2
tqdm
spacy
psycopg2-binary
minio
