"""
fetch_quartiles_v5.py
Исправление: запрос CITESCORE через ISSN вместо source_id.
API endpoint: /content/serial/title/issn/{issn}?view=CITESCORE
"""

import requests, pandas as pd, time, argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--api_key", required=True)
parser.add_argument("--input",   default="publications.csv")
parser.add_argument("--output",  default="publications_with_quartiles.csv")
parser.add_argument("--year",    default="2024")
parser.add_argument("--debug",   action="store_true")
args = parser.parse_args()

HEADERS     = {"X-ELS-APIKey": args.api_key, "Accept": "application/json"}
TARGET_YEAR = args.year
CACHE_FILE  = "quartile_cache_v5.json"

cache = {}
if Path(CACHE_FILE).exists():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    print(f"📦 Кэш: {len(cache)} журналов")

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def safe_get(url, params=None):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if r.status_code == 429:
                print("⏳ Rate limit, ожидание 15 сек...")
                time.sleep(15)
                continue
            return r
        except Exception as e:
            print(f"  ⚠ Попытка {attempt+1}: {e}")
            time.sleep(3)
    return None

def percentile_to_quartile(pct):
    try:
        p = float(pct)
        if p >= 75: return "Q1"
        if p >= 50: return "Q2"
        if p >= 25: return "Q3"
        return "Q4"
    except:
        return None

Q_ORDER = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}

# ── Шаг 1: получить ISSN и source_id по названию ─────────────────────────────
def get_journal_meta(journal_name):
    r = safe_get("https://api.elsevier.com/content/serial/title",
                 {"title": journal_name, "count": 1, "view": "STANDARD"})
    if not r or r.status_code != 200:
        return None, None, None, None
    entries = r.json().get("serial-metadata-response", {}).get("entry", [])
    if not entries or "error" in entries[0]:
        return None, None, None, None
    e         = entries[0]
    source_id = e.get("source-id")
    issn      = e.get("prism:issn")
    eissn     = e.get("prism:eIssn")
    sjr_list  = e.get("SJRList", {}).get("SJR", [])
    sjr = None
    if isinstance(sjr_list, list) and sjr_list:
        sjr = sjr_list[-1].get("$")
    elif isinstance(sjr_list, dict):
        sjr = sjr_list.get("$")
    return source_id, issn, eissn, sjr

# ── Шаг 2: квартили через /issn/{issn}?view=CITESCORE ────────────────────────
def get_all_quartiles_by_issn(issn):
    """Запрос по конкретному ISSN — гарантирует нужный журнал."""
    url = f"https://api.elsevier.com/content/serial/title/issn/{issn}"
    r = safe_get(url, {"view": "CITESCORE"})
    if not r or r.status_code != 200:
        return [], f"http_{r.status_code if r else 'timeout'}"

    entries = r.json().get("serial-metadata-response", {}).get("entry", [])
    if not entries or "error" in entries[0]:
        return [], "no_entries"

    e = entries[0]

    # Карта subjectCode → название
    subject_names = {}
    for sa in e.get("subject-area", []):
        if isinstance(sa, dict):
            subject_names[sa.get("@code", "")] = sa.get("$", "")

    cite_info  = e.get("citeScoreYearInfoList", {})
    year_infos = cite_info.get("citeScoreYearInfo", [])
    if isinstance(year_infos, dict):
        year_infos = [year_infos]

    # Выбираем год: сначала TARGET_YEAR Complete, потом любой Complete, потом In-Progress
    target = None
    for yi in year_infos:
        if str(yi.get("@year", "")) == TARGET_YEAR and yi.get("@status") == "Complete":
            target = yi
            break
    if target is None:
        for yi in year_infos:
            if yi.get("@status") == "Complete":
                target = yi
    if target is None and year_infos:
        target = year_infos[-1]
    if target is None:
        return [], "no_year_info"

    actual_year = target.get("@year", "?")

    # Собираем все предметные области
    results = []
    info_list = target.get("citeScoreInformationList", [])
    if isinstance(info_list, dict):
        info_list = [info_list]

    for info in info_list:
        cite_infos = info.get("citeScoreInfo", [])
        if isinstance(cite_infos, dict):
            cite_infos = [cite_infos]

        # Сначала ищем docType == "all", если нет — берём любой
        doc_types_all = [ci for ci in cite_infos if ci.get("docType") == "all"]
        cite_infos_filtered = doc_types_all if doc_types_all else cite_infos

        for ci in cite_infos_filtered:
            ranks = ci.get("citeScoreSubjectRank", [])
            if isinstance(ranks, dict):
                ranks = [ranks]
            for rank in ranks:
                code        = str(rank.get("subjectCode", ""))
                percentile  = rank.get("percentile")
                rank_num    = rank.get("rank")
                rank_out_of = rank.get("rankOutOf")
                if rank_num and rank_out_of:
                    rank_str = f"{rank_num}/{rank_out_of}"
                else:
                    rank_str = str(rank_num) if rank_num else None
                quartile    = percentile_to_quartile(percentile)
                if quartile:
                    results.append({
                        "subject":      subject_names.get(code, code),
                        "subject_code": code,
                        "quartile":     quartile,
                        "percentile":   percentile,
                        "rank":         rank_str,
                        "year":         actual_year,
                    })

    if not results:
        return [], "no_percentile"

    results.sort(key=lambda x: Q_ORDER.get(x["quartile"], 9))
    return results, f"ok_{actual_year}"

# ── Обработка одного журнала ──────────────────────────────────────────────────
def process_journal(journal_name):
    print(f"  🔍 {journal_name[:75]}")

    source_id, issn, eissn, sjr = get_journal_meta(journal_name)
    time.sleep(0.35)

    if not issn and not eissn:
        return {
            "quartiles_list":  [],
            "quartiles_all":   None,
            "quartile_best":   None,
            "subjects_detail": None,
            "subjects":        None,
            "source_id":       source_id,
            "issn":            issn,
            "sjr":             sjr,
            "status":          "no_issn",
        }

    # Пробуем сначала ISSN, потом eISSN
    quartiles_list, status = get_all_quartiles_by_issn(issn or eissn)
    if not quartiles_list and eissn and eissn != issn:
        quartiles_list, status = get_all_quartiles_by_issn(eissn)
    time.sleep(0.35)

    if quartiles_list:
        quartile_best   = quartiles_list[0]["quartile"]
        quartiles_all   = ", ".join([q["quartile"] for q in quartiles_list])
        subjects_detail = "; ".join([
            f'{q["subject"]}: {q["quartile"]} (rank {q["rank"]}, {q["percentile"]}%)'
            for q in quartiles_list
        ])
        subjects = "; ".join([q["subject"] for q in quartiles_list])
    else:
        quartile_best = quartiles_all = subjects_detail = subjects = None

    return {
        "quartiles_list":  quartiles_list,
        "quartiles_all":   quartiles_all,
        "quartile_best":   quartile_best,
        "subjects_detail": subjects_detail,
        "subjects":        subjects,
        "source_id":       source_id,
        "issn":            issn,
        "sjr":             sjr,
        "status":          status,
    }

# ── DEBUG ─────────────────────────────────────────────────────────────────────
if args.debug:
    test = "Plant Foods for Human Nutrition"
    print(f"\n🔬 DEBUG: {test}\n")
    result = process_journal(test)
    print(f"\nsource_id:       {result['source_id']}")
    print(f"issn:            {result['issn']}")
    print(f"SJR:             {result['sjr']}")
    print(f"Квартиль лучший: {result['quartile_best']}")
    print(f"Все квартили:    {result['quartiles_all']}")
    print(f"\nДетально по предметным областям:")
    for q in result["quartiles_list"]:
        print(f"  {q['quartile']}  percentile={q['percentile']:>3}%  rank={q['rank']:>10}  {q['subject']}")
    print(f"\nСтатус: {result['status']}")
    exit(0)

# ── Загрузка файла ────────────────────────────────────────────────────────────
print(f"\n📂 {args.input}")
df = pd.read_csv(args.input, encoding="utf-8-sig")
journal_col = "Название источника"
unique_journals = df[journal_col].dropna().unique().tolist()
print(f"   Строк: {len(df)} | Журналов: {len(unique_journals)}\n")

results = {}
for i, j in enumerate(unique_journals, 1):
    print(f"[{i}/{len(unique_journals)}]", end=" ")
    results[j] = process_journal(j)
    cache[j]   = results[j]
save_cache()

# ── Добавить колонки ──────────────────────────────────────────────────────────
df["Квартиль_лучший"]    = df[journal_col].map(lambda j: results.get(j, {}).get("quartile_best"))
df["Квартили_все"]       = df[journal_col].map(lambda j: results.get(j, {}).get("quartiles_all"))
df["Квартили_детально"]  = df[journal_col].map(lambda j: results.get(j, {}).get("subjects_detail"))
df["Предметные_области"] = df[journal_col].map(lambda j: results.get(j, {}).get("subjects"))
df["SJR"]                = df[journal_col].map(lambda j: results.get(j, {}).get("sjr"))
df["ISSN"]               = df[journal_col].map(lambda j: results.get(j, {}).get("issn"))
df["Source_ID"]          = df[journal_col].map(lambda j: results.get(j, {}).get("source_id"))
df["API_Status"]         = df[journal_col].map(lambda j: results.get(j, {}).get("status"))

found = df["Квартиль_лучший"].notna().sum()
print(f"\n{'='*55}")
print(f"📊 С квартилем: {found}/{len(df)} ({found/len(df)*100:.1f}%)")
if found:
    print(f"\nЛучший квартиль:")
    print(df["Квартиль_лучший"].value_counts().to_string())
    print(df["Квартили_детально"].value_counts().to_string())
    
print(f"\nAPI статусы:\n{df['API_Status'].value_counts().to_string()}")

df.to_csv(args.output, index=False, encoding="utf-8-sig")
print(f"\n✅ Сохранено: {args.output}")
