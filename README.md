# wpVitalsTender
wpVitalsTender is designed to help maintain the list of [vital articles](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles) of the English Wikipedia. This page contains a list of articles and their current [assessed quality](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Wikipedia/Assessment). However, as article quality can change over time and there are thousands of articles listed, it would behoove us to make an automated solution.

Specifically, this script reads the listed assessment of the article and compares it to the current assessment (using the average assessment if there are multiple projects with different assessments).

It does so by making API calls concerning the [content](https://www.mediawiki.org/wiki/API:Main_page) of the Vital Articles page and the [page assessment](https://www.mediawiki.org/wiki/Extension:PageAssessments) of each listed page. In the event that the article is in multiple WikiProjects with different assessments, it merely confirms that one project has the listed assessment.

## Usage
Don't run this script all willy-nilly! It makes an API call to the Wikipedia servers for every 2-3 listed articles, and with long lists like the level 4 articles, it will quickly get into the thousands of calls. While you won't bring down the Wikipedia servers with this script, it would be [very rude](https://www.mediawiki.org/wiki/API:Etiquette) to use this non-stop.

1. Ensure you have Python 3 installed and usable from the command line.

2. In your command line terminal, navigate to the folder containing this project and enter the command `python wpVitalsTender.py "Wikipedia:Vital articles"` to run the script on the [Vital articles](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles) page.

3. The script will print out any mismatches found, as well as any pages without assessments, such as pages not belonging to WikiProjects that do assessments (Classical Music is one such project).

### Parameters
* The first parameter passed is the name of the Vital Articles page you want to run the script on, in quotation marks.
* If you want to run the script against every page in the Vital Articles project, you can pass "all" as the first parameter. This can take quite a while to run.
* -s: Index of the section you want to run the script against. You can run the script on a single section to increase the speed of the query. The section's index is the number of headers between it and the top of the page.
* -a: Accuracy, from 0 to 1. Sometimes an article has different assessments from different projects. If you run wpVitalsTender with an accuracy rating, the script will calculate the percentage of projects rating the article at the listed rating, and mark the article as a mismatch if that percentage is less than the accuracy. For example, if an article listed as "B" is ranked "B" by two projects and "C" by another, it will be printed out as a mismatch if the project is run with an accuracy rating of .66 or higher, but will not be counted as a mismatch with a lower accuracy rating. Projects which have no assessment are ignored.

## To-do
* More graceful handling of multiple WikiProjects with different assessments, maybe printing a warning?
* Check if delisted good articles and former featured articles are appropriately marked.
* Expand test coverage
* GUI...?
* Option to export results to file (csv? txt?) with date
* Add option to check section counts listed in headers
* Maybe make a bot that automatically updates the listing? There may be too many edge cases, like articles that belong to only one WikiProject that doesn't do assessment (for example the Classical Music project)...
