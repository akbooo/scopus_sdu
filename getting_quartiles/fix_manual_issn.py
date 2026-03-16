"""
fix_manual_issn.py — запрашивает квартили напрямую по известным ISSN
для журналов которые API не нашёл по названию.

Использование:
    python fix_manual_issn.py --api_key ВАШ_КЛЮЧ --input result_final.csv --output result_final2.csv
"""

import requests, pandas as pd, time, argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--api_key", required=True)
parser.add_argument("--input",  default="result_final.csv")
parser.add_argument("--output", default="result_final2.csv")
parser.add_argument("--year",   default="2024")
args = parser.parse_args()

HEADERS     = {"X-ELS-APIKey": args.api_key, "Accept": "application/json"}
TARGET_YEAR = args.year

# ISSN собраны вручную
MANUAL_ISSN = {
    'Cancers':                                   '2072-6694',
    'Technology in Society':                     '0160-791X',
    'Soft Computing':                            '1432-7643',
    'Economic Analysis and Policy':              '0313-5926',
    'Economics Bulletin':                        '1545-2921',
    'Mediterranean Journal of Social Sciences':  '2039-2117',
    'Asian Social Science':                      '1911-2017',
    'Toxics':                                    '2305-6304',
    'Ceramics International':                    '0272-8842',
    'Prostate':                                  '0270-4137',
    'Procedia - Social and Behavioral Sciences': '1877-0428',
    'Minerva':                                   '0026-4695',
    'World Applied Sciences Journal':            '1818-4952',
    'Oriental Studies':                          '2306-1596',
}

Q_ORDER = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}

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

def percentile_to_quartile(pct):
    try:
        p = float(pct)
        if p >= 75: return "Q1"
        if p >= 50: return "Q2"
        if p >= 25: return "Q3"
        return "Q4"
    except: return None

def get_quartiles_by_issn(issn):
    url = f"https://api.elsevier.com/content/serial/title/issn/{issn}"
    r = safe_get(url, {"view": "CITESCORE"})
    if not r or r.status_code != 200:
        return [], f"http_{r.status_code if r else 'timeout'}"

    entries = r.json().get("serial-metadata-response", {}).get("entry", [])
    if not entries or "error" in entries[0]:
        return [], "no_entries"

    e = entries[0]
    found_title = e.get("dc:title", "")

    subject_names = {
        sa.get("@code", ""): sa.get("$", "")
        for sa in e.get("subject-area", []) if isinstance(sa, dict)
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
        for ci in cite_infos:
            if ci.get("docType") != "all": continue
            ranks = ci.get("citeScoreSubjectRank", [])
            if isinstance(ranks, dict): ranks = [ranks]
            for rank in ranks:
                code = str(rank.get("subjectCode", ""))
                pct  = rank.get("percentile")
                q    = percentile_to_quartile(pct)
                if q:
                    results.append({
                        "subject":    subject_names.get(code, code),
                        "quartile":   q,
                        "percentile": pct,
                        "rank":       rank.get("rank"),
                        "year":       actual_year,
                    })

    if not results: return [], "no_percentile"
    results.sort(key=lambda x: Q_ORDER.get(x["quartile"], 9))
    return results, f"ok_{actual_year}"

# ── Загрузка ──────────────────────────────────────────────────────────────────
print(f"📂 {args.input}")
df = pd.read_csv(args.input, encoding='utf-8-sig')
for col in ['Квартиль_лучший','Квартили_все','Квартили_детально','Предметные_области','SJR','ISSN','API_Status']:
    df[col] = df[col].astype(object)

journal_col = "Название источника"
results = {}

print(f"\n🔍 Запрос по {len(MANUAL_ISSN)} журналам...\n")
for i, (journal, issn) in enumerate(MANUAL_ISSN.items(), 1):
    print(f"[{i}/{len(MANUAL_ISSN)}] {journal[:60]}")
    ql, status = get_quartiles_by_issn(issn)
    time.sleep(0.4)

    if ql:
        results[journal] = {
            'Квартиль_лучший':    ql[0]["quartile"],
            'Квартили_все':       ", ".join([q["quartile"] for q in ql]),
            'Квартили_детально':  "; ".join([f'{q["subject"]}: {q["quartile"]} ({q["percentile"]}%)' for q in ql]),
            'Предметные_области': "; ".join([q["subject"] for q in ql]),
            'ISSN':               issn,
            'API_Status':         status,
        }
        print(f"  ✅ {results[journal]['Квартили_все']}  [{status}]")
    else:
        results[journal] = {
            'Квартиль_лучший': None, 'Квартили_все': None,
            'Квартили_детально': None, 'Предметные_области': None,
            'ISSN': issn, 'API_Status': status,
        }
        print(f"  ❌ {status}")

# ── Обновляем датафрейм ───────────────────────────────────────────────────────
for journal, updates in results.items():
    mask = df[journal_col] == journal
    if mask.sum() == 0: continue
    for col, val in updates.items():
        df.loc[mask, col] = val

found = df['Квартиль_лучший'].notna().sum()
print(f"\n{'='*55}")
print(f"📊 С квартилем: {found}/{len(df)} ({found/len(df)*100:.1f}%)")
print(f"\nРаспределение:")
print(df['Квартиль_лучший'].value_counts().to_string())
print(f"\nСтатусы:")
print(df['API_Status'].value_counts().to_string())

df.to_csv(args.output, index=False, encoding='utf-8-sig')
print(f"\n✅ Сохранено: {args.output}")
