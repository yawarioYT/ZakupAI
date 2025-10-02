import pdfplumber
import re
from typing import Dict, List, Any
import json

def extract_text_and_tables(pdf_path: str) -> Dict[str, Any]:
    """
    Извлекает текст и таблицы из PDF-документа по закупкам.
    Возвращает структурированные данные.
    """
    full_text = ""
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Извлекаем текст
            text = page.extract_text()
            if text:
                full_text += text + "\n"
            
            # Извлекаем таблицы
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    return {
        "text": full_text,
        "tables": all_tables
    }

def parse_nmc(text: str) -> List[float]:
    """Извлекает все суммы НМЦК из текста (в рублях)."""
    # Шаблон: "НМЦК — 250 000 руб.", "250000", "300 млн руб."
    patterns = [
        r"НМЦК\D*([\d\s,]+(?:млн|тыс)?)",
        r"([\d\s,]+)\s*(?:руб|₽|рублей)",
        r"([\d\s,]+)\s*(?:млн|млн\.|млн руб)",
        r"([\d\s,]+)\s*(?:тыс|тыс\.|тыс руб)"
    ]
    nmc_values = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean = re.sub(r"[^\d]", "", match)
            if clean:
                num = int(clean)
                # Если сумма < 1_000_000 — возможно, это тысячи
                if num < 1_000_000 and "тыс" in match:
                    num *= 1_000
                elif num < 1_000_000 and "млн" in match:
                    num *= 1_000_000
                nmc_values.append(num)
    return nmc_values

def parse_procurement_method(text: str) -> str:
    """Определяет способ закупки по ключевым фразам."""
    text_lower = text.lower()
    if "ст. 93" in text_lower or "единственный поставщик" in text_lower:
        return "ст. 93"
    elif "аукцион" in text_lower:
        return "электронный аукцион"
    elif "запрос котировок" in text_lower or "зк" in text_lower:
        return "запрос котировок"
    else:
        return "не определён"

def parse_dates(text: str) -> Dict[str, List[str]]:
    """Извлекает даты по контексту."""
    # Пример: "не позднее чем за 10 дней", "размещено 05.04.2025"
    dates = {
        "plan_change": [],
        "notice_placement": [],
        "deadline": []
    }
    # Простой паттерн для дат ДД.ММ.ГГГГ
    date_pattern = r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b"
    generic_dates = re.findall(date_pattern, text)
    # В реальном проекте — привязка к контексту (через NLP)
    dates["notice_placement"] = generic_dates[:1]  # временно
    return dates

def parse_pdf_document(pdf_path: str) -> Dict[str, Any]:
    """Основная функция парсинга PDF-документа по закупкам."""
    raw = extract_text_and_tables(pdf_path)
    text = raw["text"]

    return {
        "source_file": pdf_path,
        "nmc_list": parse_nmc(text),
        "procurement_method": parse_procurement_method(text),
        "dates": parse_dates(text),
        "raw_text_snippet": text[:500] + "..." if len(text) > 500 else text
    }

# Пример использования
if __name__ == "__main__":
    # Замените на путь к вашему PDF (например, блок-схема_№162.pdf)
    result = parse_pdf_document("samples/blok-shema_№162.pdf")
    print(json.dumps(result, ensure_ascii=False, indent=2))
