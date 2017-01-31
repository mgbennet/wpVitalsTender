# wpVitalsTender
wpVitalsTender is designed to help maintain the list of [vital articles](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles) of the English Wikipedia. This page contains a list of articles and their current [assessed quality](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Wikipedia/Assessment). However, as article quality can change over time and there are thousands of articles listed, it would behoove us to make an automated solution.

Specifically, it compares the listed assessment of the page and compares it to the current assessment (using the average assessment if there are multiple projects with different assessments).
It does so by making [API calls](https://www.mediawiki.org/wiki/API:Main_page) concerning the content of the Vital Articles page and each listed page.

For each listed article:
 1) Get its listed assessment and whether it is a former good or featured article.
 2) Get its current assessment with [another API call](https://www.mediawiki.org/wiki/Extension:PageAssessments).
 3) If there is a mismatch, print it out.

Future work may include making a bot to automatically update the listing, but I'd need to look into what it takes to run a Wikipedia bot.