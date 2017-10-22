#!/usr/bin/python
"""
Really quick script to build test data for multiple assessments
"""


import requests
import wpVitalsTender as wpvt
import json

# https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Expanded/Technology#Infrastructure_.2872_articles.29
articles = wpvt.parse_article(wpvt.get_content("Wikipedia:Vital articles/Expanded/Technology", 33))
article_titles = [l["title"] for l in articles]

results = []
request = {"prop": "pageassessments", "action": "query", "format": "json", "continue": ""}
num_queries = 0

for i in range(0, len(article_titles), 50):
    last_continue = {"continue": ""}
    request["titles"] = "|".join(article_titles[i:i + 50])
    while True:
        req = request.copy()
        req.update(last_continue)
        r = requests.get("https://en.wikipedia.org/w/api.php", req).json()
        num_queries += 1
        if "query" in r:
            results.append(r)
        if "batchcomplete" in r:
            break
        last_continue = r["continue"]

print(num_queries)

for i, j in enumerate(results):
    with open('test_docs/MultiArticleAssessment/test_MultiArticleAssessment_' + str(i) + '.json', 'w') as outfile:
        if "batchcomplete" not in j:
            j["continue"]["mockcontinue"] = str(i + 1)
        json.dump(j, outfile, indent=4, separators=(',', ': '))
