"""
fix_no_issn.py — дополнительный поиск квартилей для ненайденных журналов.
Стратегии поиска:
  1. Точное название
  2. Первые 5 слов названия
  3. Без скобок и подзаголовков
Проверяет схожесть найденного названия с оригиналом.

Использование:
    python fix_no_issn.py --api_key ВАШ_КЛЮЧ --result result.csv --output result_fixed.csv
"""

import requests, pandas as pd, time, argparse, json, re
from pathlib import Path
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument("--api_key", required=True)
parser.add_argument("--result",  default="result.csv",       help="Файл с результатами v5")
parser.add_argument("--output",  default="result_fixed.csv", help="Итоговый файл")
parser.add_argument("--year",    default="2024")
args = parser.parse_args()

HEADERS     = {"X-ELS-APIKey": args.api_key, "Accept": "application/json"}
TARGET_YEAR = args.year

def safe_get(url, params=None):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if r.status_code == 429:
                print("⏳ Rate limit 15 сек..."); time.sleep(15); continue
            return r
        except Exception as e:
            print(f"  ⚠ {e}"); time.sleep(3)
    return None

def similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def percentile_to_quartile(pct):
    try:
        p = float(pct)
        if p >= 75: return "Q1"
        if p >= 50: return "Q2"
        if p >= 25: return "Q3"
        return "Q4"
    except: return None

Q_ORDER = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}

SKIP_KEYWORDS = [
    'proceedings', 'conference', 'congress', 'symposium', 'workshop',
    'handbook', 'lecture notes', 'topics in', 'reshaping', 'lrec-coling',
    'icecco', 'icalt', 'balkancom', 'irc 20', 'icaiic', 'tiptekno',
    'aict 20', 'coconet', 'tale 20', 'sibcon', 'elnano', 'patat',
    'elmar', 'holm conference', 'routledge', 'how college students',
    'new media and political', 'practice fields', 'mapping the media',
    'river flowing', 'energy-growth nexus', 'digitalization and future',
    'examining the relationship', 'public policy analysis in turkey',
    'turkish foreign policy', 'new horizons in philosophy',
    'sustainable landscape planning',
]

def is_skip(name):
    low = name.lower()
    return any(kw in low for kw in SKIP_KEYWORDS)

def make_search_variants(name):
    variants = [name]
    no_brackets = re.sub(r'\(.*?\)', '', name).strip()
    if no_brackets != name: variants.append(no_brackets)
    words = name.split()
    if len(words) > 5: variants.append(" ".join(words[:5]))
    if ':' in name: variants.append(name.split(':')[0].strip())
    if ' - ' in name: variants.append(name.split(' - ')[0].strip())
    return list(dict.fromkeys(variants))

def find_journal(journal_name):
    variants = make_search_variants(journal_name)
    best = None
    best_score = 0

    for query in variants:
        r = safe_get("https://api.elsevier.com/content/serial/title",
                     {"title": query, "count": 5, "view": "STANDARD"})
        time.sleep(0.3)
        if not r or r.status_code != 200: continue
        entries = r.json().get("serial-metadata-response", {}).get("entry", [])
        for e in entries:
            if "error" in e: continue
            title_found = e.get("dc:title", "")
            score = similarity(journal_name, title_found)
            if score > best_score:
                best_score = score
                best = e

    if best is None or best_score < 0.65:
        return None, None, None, None, best_score

    sjr_list = best.get("SJRList", {}).get("SJR", [])
    sjr = None
    if isinstance(sjr_list, list) and sjr_list: sjr = sjr_list[-1].get("$")
    elif isinstance(sjr_list, dict):             sjr = sjr_list.get("$")

    return best.get("source-id"), best.get("prism:issn"), best.get("prism:eIssn"), sjr, best_score

def get_quartiles_by_issn(issn):
    url = f"https://api.elsevier.com/content/serial/title/issn/{issn}"
    r = safe_get(url, {"view": "CITESCORE"})
    if not r or r.status_code != 200:
        return [], f"http_{r.status_code if r else 'timeout'}"
    entries = r.json().get("serial-metadata-response", {}).get("entry", [])
    if not entries or "error" in entries[0]:
        return [], "no_entries"

    e = entries[0]
    subject_names = {
        sa.get("@code", ""): sa.get("$", "")
        for sa in e.get("subject-area", [])
        if isinstance(sa, dict)
    }

    cite_info  = e.get("citeScoreYearInfoList", {})
    year_infos = cite_info.get("citeScoreYearInfo", [])
    if isinstance(year_infos, dict): year_infos = [year_infos]

    target = None
    for yi in year_infos:
        if str(yi.get("@year", "")) == TARGET_YEAR and yi.get("@status") == "Complete":
            target = yi; break
    if target is None:
        for yi in year_infos:
            if yi.get("@status") == "Complete": target = yi
    if target is None and year_infos: target = year_infos[-1]
    if target is None: return [], "no_year_info"

    actual_year = target.get("@year", "?")
    results = []

    info_list = target.get("citeScoreInformationList", [])
    if isinstance(info_list, dict): info_list = [info_list]

    for info in info_list:
        cite_infos = info.get("citeScoreInfo", [])
        if isinstance(cite_infos, dict): cite_infos = [cite_infos]

        # Сначала ищем docType == "all", если нет — берём любой
        doc_types_all = [ci for ci in cite_infos if ci.get("docType") == "all"]
        cite_infos_filtered = doc_types_all if doc_types_all else cite_infos

        for ci in cite_infos_filtered:
            ranks = ci.get("citeScoreSubjectRank", [])
            if isinstance(ranks, dict): ranks = [ranks]
            for rank in ranks:
                code        = str(rank.get("subjectCode", ""))
                pct         = rank.get("percentile")
                rank_num    = rank.get("rank")
                rank_out_of = rank.get("rankOutOf")
                if rank_num and rank_out_of:
                    rank_str = f"{rank_num}/{rank_out_of}"
                else:
                    rank_str = str(rank_num) if rank_num else None
                q = percentile_to_quartile(pct)
                if q:
                    results.append({
                        "subject":    subject_names.get(code, code),
                        "quartile":   q,
                        "percentile": pct,
                        "rank":       rank_str,
                        "year":       actual_year,
                    })

    if not results: return [], "no_percentile"
    results.sort(key=lambda x: Q_ORDER.get(x["quartile"], 9))
    return results, f"ok_{actual_year}"

# ── Загрузка ──────────────────────────────────────────────────────────────────
print(f"📂 Загрузка {args.result}...")
df = pd.read_csv(args.result, encoding="utf-8-sig")
journal_col = "Название источника"

no_issn_journals = df[df["API_Status"] == "no_issn"][journal_col].unique().tolist()
real_journals    = [j for j in no_issn_journals if not is_skip(j)]
skip_journals    = [j for j in no_issn_journals if is_skip(j)]

print(f"   Всего no_issn: {len(no_issn_journals)}")
print(f"   Конференции/книги (пропускаем): {len(skip_journals)}")
print(f"   Реальных журналов для поиска:   {len(real_journals)}\n")

# ── Обработка реальных журналов ───────────────────────────────────────────────
new_results = {}

for i, journal in enumerate(real_journals, 1):
    print(f"[{i}/{len(real_journals)}] {journal[:70]}")
    source_id, issn, eissn, sjr, score = find_journal(journal)

    if not issn and not eissn:
        print(f"  ❌ Не найден (схожесть: {score:.2f})")
        new_results[journal] = {
            "quartile_best": None, "quartiles_all": None,
            "subjects_detail": None, "subjects": None,
            "issn": None, "sjr": sjr,
            "status": f"not_found_score_{score:.2f}"
        }
        continue

    print(f"  ✓ ISSN={issn or eissn}, схожесть={score:.2f}")
    ql, status = get_quartiles_by_issn(issn or eissn)
    time.sleep(0.35)

    if ql:
        new_results[journal] = {
            "quartile_best":   ql[0]["quartile"],
            "quartiles_all":   ", ".join([q["quartile"] for q in ql]),
            "subjects_detail": "; ".join([
                f'{q["subject"]}: {q["quartile"]} (rank {q["rank"]}, {q["percentile"]}%)'
                for q in ql
            ]),
            "subjects": "; ".join([q["subject"] for q in ql]),
            "issn":     issn,
            "sjr":      sjr,
            "status":   status,
        }
        print(f"  🏆 {new_results[journal]['quartiles_all']}")
    else:
        new_results[journal] = {
            "quartile_best": None, "quartiles_all": None,
            "subjects_detail": None, "subjects": None,
            "issn": issn, "sjr": sjr, "status": status
        }
        print(f"  ⚠ Нет квартиля: {status}")

# Конференции помечаем явно
for j in skip_journals:
    new_results[j] = {
        "quartile_best": None, "quartiles_all": None,
        "subjects_detail": None, "subjects": None,
        "issn": None, "sjr": None, "status": "conference_or_book"
    }

# ── Обновить датафрейм ────────────────────────────────────────────────────────
for col, key in [
    ("Квартиль_лучший",    "quartile_best"),
    ("Квартили_все",       "quartiles_all"),
    ("Квартили_детально",  "subjects_detail"),
    ("Предметные_области", "subjects"),
    ("ISSN",               "issn"),
    ("SJR",                "sjr"),
    ("API_Status",         "status"),
]:
    if col in df.columns:
        df[col] = df.apply(
            lambda row: new_results[row[journal_col]].get(key, row[col])
            if row[journal_col] in new_results else row[col],
            axis=1
        )

# ── Статистика ────────────────────────────────────────────────────────────────
found = df["Квартиль_лучший"].notna().sum()
print(f"\n{'='*55}")
print(f"📊 Итого с квартилем: {found}/{len(df)} ({found/len(df)*100:.1f}%)")
print(f"\nРаспределение квартилей:")
print(df["Квартиль_лучший"].value_counts().to_string())
print(f"\nAPI статусы:")
print(df["API_Status"].value_counts().to_string())

df.to_csv(args.output, index=False, encoding="utf-8-sig")
print(f"\n✅ Сохранено: {args.output}")