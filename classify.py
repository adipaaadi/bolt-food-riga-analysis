import re
from collections import Counter
import pandas as pd

df = pd.read_csv("bfriga_2019_2023.csv", encoding="utf-8-sig")
df["text_clean"] = df["text_clean"].fillna("")

days = r"pirmdiena|otrdiena|trešdiena|ceturtdiena|piektdiena|sestdiena|svētdiena|monday|tuesday|wednesday|thursday|friday|saturday|sunday"

patterns = {
    "daily_pricing": r"(?:" + days + r")(?:\s*/\s*\w+)?\s*\(\d{1,2}\.\d{1,2}\.\d{2,4}\)",
    "weather": r"lietus|lietū|lietaina|sniegs|sniega|sniegā|aukstums|ir auksts|aukstā laikā|salst|slidens|apledojum|rain\b|rains\b|raining\b|rainy\b|rained\b|snow\b|snowing\b|snowy\b|cold weather|freezing|frost|storm|дожд\w*|снег\w*|холод|мороз\w*|гололед|ливень",
    "holiday": r"ziemassv\w*|jaungad\w*|līgo|jāņi|jāņu|valentīn\w*|sieviešu diena|neatkarības proklamēšan\w*|neatkarības atjaunošan\w*|hokej\w*|lieldien\w*|christmas|new year|midsummer|valentine\w*|women'?s day|independence day|proclamation day|hockey|easter|рождеств\w*|новый год|новогодн\w*|женский день|независимост\w*|хоккей|пасх\w*",
    "technical": r"tehnisk\w*\s+(?:problēm|iemesl|kļūm|traucēj)\w*|technical\s+(?:issue|problem|reason|difficult|error)\w*|issues?\s+(?:has|have|had|is|are|were|was)\s+(?:been\s+)?(?:resolved|solved|fixed)|problēm\w*\s+(?:ir\s+)?novērst\w*|glitch|outage|not working|nedarbojas|bilanc\w*|ошибк\w*|сбой|техническ\w*\s+проблем\w*|не работает|баланс|problēmas ar internetu|internet problems",
    "app_feature": r"new feature|jaunu funkciju|jauna funkcija|jaunā funkcija|funkcionalitāt\w*|feature\w*|in-app|app update|atjaunin\w*|update the app|tips|tested|testēt\w*|testē|rolling out|ieviešam|ieviest\w*|обновите",
    "policy": r"bezkontakt\w*|sejas maskas|maskas|maskām|pašnodarbin\w*|kvalitāt\w*|alkohol\w*|noteikum\w*|contactless|masks?\b|self-employed|quality|alcohol|rules|policy|бесконтакт\w*|маск\w*|самозанят\w*|качеств\w*|алкогол\w*|правил(?:а|ам|ах|ами|о)\b|aizliegt\w*|pārkāpum\w*|prohibited|violation\w*|termo soma\w*",
    "launch": r"bolt market\s+(?:veikals\s+)?(?:uzsāk|is\s+(?:already\s+)?open|opens|launch)\w*|uzsāk\w*\s+(?:darbu|darbību)|store is (?:already )?open|is now open|batched orders|apvienot\w* pasūtījum\w*|jauns restor\w*|jauni restor\w*|jauna vieta|paplašin\w*|new restaurant\w*|new location|expand\w*|now available|launch\w*|atgriežas|coming back|bolt food is coming|drīzumā|joined bolt food|pievienojušies|pievienojās|новый ресторан|новые рестораны|расшир\w*|запуск\w*|группировк\w*",
    "fare": r"base fare|base rate|payout model|pricing change|new pricing|maksājumu mode\w*|izmaksu mode\w*|bāzes likme|apmaksas izmaiņ\w*|samaksas izmaiņ\w*|tarif\w*|изменени\w* (?:тариф|оплат)\w*|тариф\w*|ставк\w*|выплат\w*|waiting time|of waiting|gaidīšan\w*|maksa par piegād\w*|delivery fee",
    "competition": r"konkurs\w*|loterij\w*|izloz\w*|balvas|aptauj\w*|draugiem|uzaicinājuma kod\w*|referral|invite (?:a )?friends?|giveaway|raffle|contest|prize|survey|winner|uzvarētāj\w*|gift card|dāvanu kart\w*|розыгрыш\w*|конкурс\w*|приз\w*|опрос\w*|пригласи\w*|реферал\w*|победител\w*|jacket|jaku|laimīgo",
    "promo": r"atlaid\w*|discount\w*|-\s?\d+\s?%|\d+\s?%\s?(?:off|atlaide)|free delivery|bezmaksas piegād\w*|akcij\w*|скидк\w*",
    "onboarding": r"application form|pieteikšanās|pieteikties|pieteikumu|apmācīb\w*|apmācību|presentation|prezentācij\w*|training|vacanc\w*|position is available|pieejama sekojoša pozīcija|meklējam jaunus",
    "restaurant_ops": r"lido|mcdonald\w*|stockmann|where to pick up|kur saņemt|pick-?up point|saņemšanas kast\w*|order receiving|pasūtījumu saņemšan\w* no|bolt market",
    "support": r"atbalst\w*|darba laiks|tālrun\w*|customer support|support team|support hours|working hours|hotline|contact us|поддержк\w*|горячая линия|свяжитесь",
    "bonus": r"bonus\w*|reizin\w*|reizes|reizē|boost\w*|multiplier\w*|coefficient|koeficient\w*|x\s?\d[.,]\d+|\d+(?:[.,]\d+)?\s?(?:eur|€)\s?(?:per|par|за)|(?:earn|saņem)\s+(?:at least |vismaz |a minimum of )?\d+(?:[.,]\d+)?\s?(?:eur|€)|\d+(?:[.,]\d+)?\s?(?:eur|€)\s?min\w*|min(?:imum)?\.?\s?\d+(?:[.,]\d+)?\s?(?:eur|€)|from now (?:on )?(?:and )?until|no šī brīža līdz|paaugstināt\w*|increased (?:earnings|multiplier|pay)|бонус\w*|множител\w*|коэффициент\w*",
    "traffic": r"traffic|satiksm\w*|road ?works|ceļ\w* darb\w*|road clos\w*|iela (?:ir )?slēgt\w*|пробк\w*",
    "peak": r"peak|pīķa|pīķis|orders incoming|incoming orders|go online|come online|join (?:us|online|now)|demand|full of orders|tons of orders|lot of orders|loads of|orders? (?:are )?coming in|non[- ]?stop|amount of orders|orders is growing|keeps? rais\w*|raising|pieslēdz\w*|pievienojies|pilsēta pilna|pilna ar pasūtījumiem|aizņemti|daudz pasūtījum\w*|pasūtījumu skaits|pieaug|nāk iekšā|ienāk|every \d+ seconds|city on fire|busy|busiest|hungry|izsalku\w*|noslogot\w*|needs? more (?:couriers|delivery)|more (?:couriers|delivery heroes)|vairāk kurjeru|woken|rīga ir aktīva|unstoppable|increases|after the other|plenty of orders|lots? of orders|crazy amounts|city is on fire|join the party|party is going on|city needs|lose your chance|loosing a great chance|zaudē lielisku iespēju|every minute|ik minūti|пик|выходите на линию|много заказов|высокий спрос",
}

order = list(patterns.keys())
compiled = {k: re.compile(r"\b(?:" + v + ")", re.IGNORECASE) for k, v in patterns.items()}


def classify(text):
    hits = []
    kw = ""
    for k in order:
        m = compiled[k].search(text)
        if m:
            if not hits:
                kw = m.group(0).lower()
            hits.append(k)
    return pd.Series({
        "category": hits[0] if hits else "other",
        "all_categories": "|".join(hits) if hits else "other",
        "n_matches": len(hits),
        "kw": kw,
    })


df = pd.concat([df, df["text_clean"].apply(classify)], axis=1)
df.to_csv("bfriga_classified.csv", index=False, encoding="utf-8-sig")

print("\nFirst-match category counts")
counts = df["category"].value_counts()
print(pd.DataFrame({"n": counts, "pct": (counts / len(df) * 100).round(1)}))

print("\nCategory by year")
print(pd.crosstab(df["category"], df["year"]))

print("\nMessages matching 2+ categories:", (df["n_matches"] > 1).sum())

print("\nTop matched keywords per category")
for cat in order:
    top = df[df["category"] == cat]["kw"].value_counts().head(8)
    print(cat, top.to_dict())

other = df[df["category"] == "other"]
words = Counter(w for t in other["text_clean"] for w in re.findall(r"\w{4,}", t.lower()))
print("\nTop words in other")
print(words.most_common(60))


def snippet(text):
    return text.replace("\n", " ")[:220]


with open("samples.txt", "w", encoding="utf-8") as f:
    for cat in order + ["other"]:
        sub = df[df["category"] == cat]
        n = 25 if cat == "other" else 10
        f.write(f"\n===== {cat} ({len(sub)}) =====\n")
        for _, row in sub.sample(min(n, len(sub)), random_state=1).iterrows():
            f.write(f"[{row['id']}] ({row['kw']}) {snippet(row['text_clean'])}\n")

print("\nSamples written to samples.txt")