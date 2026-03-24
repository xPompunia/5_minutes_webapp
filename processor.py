import pandas as pd
import docx
import re
from nums import ORDINAL_NOMINATIVE, ORDINAL_GENITIVE
from dictionaries import BIBLICAL_BOOKS


def process_audio_text(text):
    text = text.replace(" (fragment)", ", fragment").replace("(fragment)", ", fragment")

    if text.startswith("Pieśń"):
        has_fragment = ", fragment" in text
        for abbr, full in BIBLICAL_BOOKS.items():
            if re.search(abbr, text):
                full_capitalized = full[0].upper() + full[1:]
                new_text = f"Pieśń z {full_capitalized}"
                if has_fragment:
                    new_text += ", fragment"
                return new_text

        text = text.replace("Pieśń ", "Pieśń z ", 1)
        text = re.sub(r'\s*\d+,\s*\d+.*', '', text)
        if has_fragment and ", fragment" not in text:
            text += ", fragment"
        return text

    text = re.sub(
        r'\b(\d+)\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\b',
        lambda m: f"{ORDINAL_GENITIVE.get(m.group(1), m.group(1))} {m.group(2)}", text)

    text = re.sub(r'\bPsalm (\d+)\b',
                  lambda m: f"Psalm {ORDINAL_NOMINATIVE.get(m.group(1), m.group(1))}", text)

    def siglum_replacer(match):
        rozdział = ORDINAL_NOMINATIVE.get(match.group(1), match.group(1))
        wers_od = ORDINAL_GENITIVE.get(match.group(2), match.group(2))
        wers_do = ORDINAL_GENITIVE.get(match.group(3), match.group(3))
        return f"rozdział {rozdział}, wersety od {wers_od} do {wers_do}"

    text = re.sub(r'\b(\d+),\s*(\d+)[–-](\d+)\b', siglum_replacer, text)

    def single_verse_replacer(match):
        rozdział = ORDINAL_NOMINATIVE.get(match.group(1), match.group(1))
        werset = ORDINAL_NOMINATIVE.get(match.group(2), match.group(2))
        return f"rozdział {rozdział}, werset {werset}"

    text = re.sub(r'\b(\d+),\s*(\d+)\b', single_verse_replacer, text)

    return text


def process_feast_audio(text):
    text = text.replace(" (", ", ").replace(")", "")
    text = text.replace("(", "").replace(")", "")

    roman_to_ordinal = {
        r"\bI\b": "Pierwsza", r"\bII\b": "Druga", r"\bIII\b": "Trzecia",
        r"\bIV\b": "Czwarta", r"\bV\b": "Piąta", r"\bVI\b": "Szósta",
        r"\bVII\b": "Siódma", r"\bVIII\b": "Ósma", r"\bIX\b": "Dziewiąta",
        r"\bX\b": "Dziesiąta", r"\bXI\b": "Jedenasta", r"\bXII\b": "Dwunasta",
        r"\bXIII\b": "Trzynasta", r"\bXIV\b": "Czternasta", r"\bXV\b": "Piętnasta",
        r"\bXVI\b": "Szesnasta", r"\bXVII\b": "Siedemnasta", r"\bXVIII\b": "Osiemnasta",
        r"\bXIX\b": "Dziewiętnasta", r"\bXX\b": "Dwudziesta", r"\bXXI\b": "Dwudziesta pierwsza",
        r"\bXXII\b": "Dwudziesta druga", r"\bXXIII\b": "Dwudziesta trzecia", r"\bXXIV\b": "Dwudziesta czwarta",
        r"\bXXV\b": "Dwudziesta piąta", r"\bXXVI\b": "Dwudziesta szósta", r"\bXXVII\b": "Dwudziesta siódma",
        r"\bXXVIII\b": "Dwudziesta ósma", r"\bXXIX\b": "Dwudziesta dziewiąta", r"\bXXX\b": "Trzydziesta",
        r"\bXXXI\b": "Trzydziesta pierwsza", r"\bXXXII\b": "Trzydziesta druga", r"\bXXXIII\b": "Trzydziesta trzecia",
        r"\bXXXIV\b": "Trzydziesta czwarta"
    }
    for roman, ordinal in roman_to_ordinal.items():
        text = re.sub(roman, ordinal, text)

    text = re.sub(r"\bNMP\b", "Najświętszej Maryi Panny", text)
    text = re.sub(r"\bNSPJ\b", "Najświętszego Serca Pana Jezusa", text)

    def expand_saint(match):
        prefix = match.group(1).lower()
        name = match.group(2)
        if prefix == "św":
            if name.endswith(('y', 'i')):
                title = "świętej"
            elif name.endswith(('ch', 'ów')):
                title = "świętych"
            else:
                title = "świętego"
        elif prefix == "bł":
            if name.endswith(('y', 'i')):
                title = "błogosławionej"
            elif name.endswith(('ch', 'ów')):
                title = "błogosławionych"
            else:
                title = "błogosławionego"
        return f"{title} {name}"

    text = re.sub(r"\b(św|bł)\.?\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)", expand_saint, text)
    return text


def parse_docx_to_excel(docx_file, empty_xlsx_path, target_year):
    doc = docx.Document(docx_file)

    months_map = {
        "stycznia": "01", "lutego": "02", "marca": "03", "kwietnia": "04",
        "maja": "05", "czerwca": "06", "lipca": "07", "sierpnia": "08",
        "września": "09", "października": "10", "listopada": "11", "grudnia": "12"
    }

    rows = []
    current_day = {}
    current_section = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if " • " in text or "•" in text:
            if current_day:
                if 'contemplation' in current_day and current_day['contemplation']:
                    lines = current_day['contemplation'].strip().split('\n')
                    if lines and lines[-1].strip().endswith('?'):
                        current_day['contemplation_question'] = lines[-1].strip()
                        current_day['contemplation'] = '\n'.join(lines[:-1]).strip()

                for key in ['gospel', 'contemplation', 'prayer']:
                    if key in current_day and current_day[key]:
                        current_day[key] = current_day[key].replace('\n', ' ')
                        # usuwamy ewentualne podwójne spacje po usunięciu enterów
                        current_day[key] = re.sub(r'\s+', ' ', current_day[key]).strip()

                rows.append(current_day)

            date_part = text.split("•")[-1].strip()
            match = re.search(r'(\d+)\s+([a-ząćęłńóśźż]+)', date_part.lower())

            if match:
                day = match.group(1).zfill(2)
                month = months_map.get(match.group(2), "01")
                formatted_date = f"{day}/{month}/{target_year}"  # Używamy roku z aplikacji
            else:
                formatted_date = date_part

            current_day = {'date': formatted_date}
            current_section = "Feast_Check"
            continue

        if current_section == "Feast_Check":
            if not (text.startswith("Psalm") or text.startswith("Pieśń") or text.startswith("Psalmy")):
                current_day['feast'] = text
                current_day['feast_audio'] = process_feast_audio(text)
                current_section = None
                continue
            else:
                current_section = None

        if text.startswith("Psalm") or text.startswith("Pieśń") or text.startswith("Psalmy"):
            current_section = "psalm"
            current_day['psalm_title'] = text
            current_day['psalm_title_audio'] = process_audio_text(text)
            current_day[current_section] = ""

        elif text.startswith("Ewangelia"):
            current_section = "gospel"
            current_day['gospel_title'] = text

            audio_title = "Ewangelia"
            for abbr, full in BIBLICAL_BOOKS.items():
                if re.search(abbr, text):
                    audio_title = f"Ewangelia {full}"
                    break
            current_day['gospel_title_audio'] = audio_title
            current_day[current_section] = ""

        elif text == "Rozważanie":
            current_section = "contemplation"
            current_day['contemplation_title'] = text
            current_day[current_section] = ""
            current_day['contemplation_question'] = ""

        elif text == "Chwila refleksji":
            current_section = None
            current_day['reflection_title'] = text

        elif text == "Prośby":
            current_section = "requests"
            current_day['requests_title'] = text
            current_day[current_section] = ""

        elif text == "Ojcze nasz":
            current_section = None
            current_day['our_father_title'] = text

        elif text == "Modlitwa":
            current_section = "prayer"
            current_day['prayer_title'] = text
            current_day[current_section] = ""

        else:
            if current_section:
                if current_section == "psalm" and text.endswith('.'):
                    text += "*"

                if current_day.get(current_section):
                    current_day[current_section] += "\n" + text
                else:
                    current_day[current_section] = text

    # Zapisz ostatni dzień z pętli (te same operacje oczyszczania co wyżej)
    if current_day:
        if 'contemplation' in current_day and current_day['contemplation']:
            lines = current_day['contemplation'].strip().split('\n')
            if lines and lines[-1].strip().endswith('?'):
                current_day['contemplation_question'] = lines[-1].strip()
                current_day['contemplation'] = '\n'.join(lines[:-1]).strip()

        for key in ['gospel', 'contemplation', 'prayer']:
            if key in current_day and current_day[key]:
                current_day[key] = current_day[key].replace('\n', ' ')
                current_day[key] = re.sub(r'\s+', ' ', current_day[key]).strip()

        rows.append(current_day)

    empty_df = pd.read_excel(empty_xlsx_path)
    df = pd.DataFrame(rows)

    expected_columns = [
        "date", "feast", "feast_audio", "psalm_title", "psalm_title_audio", "psalm",
        "gospel_title", "gospel_title_audio", "gospel", "contemplation_title",
        "contemplation", "contemplation_question", "reflection_title", "requests_title",
        "requests", "our_father_title", "prayer_title", "prayer"
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[expected_columns]
    final_df = pd.concat([empty_df, df], ignore_index=True)

    return final_df