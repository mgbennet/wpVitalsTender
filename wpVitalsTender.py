import sys
import re
import requests


def article_list_assessment_check(article_title):
    content = get_content(article_title)
    listings = parse_article(content)
    mismatches = []
    print("Looking at " + article_title + ". Checking " + str(len(listings)) + " articles.")
    for l in listings:
        assessments = current_assessment(l["title"])
        if not l["assessment"] in assessments:
            mismatches.append({"title": l["title"], "listed_as": l["assessment"], "current": assessments})
            print("Found a mismatch! " + l["title"] + " listed as " + l["assessment"] + ", currently " + str(assessments))
    print(str(len(mismatches)) + " mismatches found.")
    return mismatches


def get_content(article_title):
    resp = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=" + article_title + "&prop=revisions&rvprop=content&format=json")
    pages = resp.json()["query"]["pages"]
    for p_key, p_val in pages.items():
        return p_val["revisions"][0]["*"]
    return None


def parse_article(content):
    article_listing_regex = re.compile(r'''
        [\*#]\s*                                        # line starts with a bullet or a number
        (?P<assessment>\{\{[Ii]con\|\w+\}\})            # assessment should always be first
        (?P<history>\s*\{\{[Ii]con\|\w+\}\})*           # option of multiple icons for FFA, or DGA
        \s*
        \'*\[\[(?P<title>[^#<>\[\]\{\}]+)\]\]                # actual title is a wikilink
    ''', re.VERBOSE)
    results = []
    for l in article_listing_regex.finditer(content):
        article = {}
        article["title"] = l.group("title").split("|")[0]
        article["assessment"] = l.group("assessment").split("|")[-1][:-2]
        article["history"] = None
        if l.group("history"):
            article["history"] = l.group("history").split("|")[-1][:-2]
        results.append(article)
    return results


def current_assessment(article_title, most_common=False):
    resp = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=" + article_title + "&prop=pageassessments&format=json")
    pages = resp.json()["query"]["pages"]
    for p_key, p_val in pages.items():
        assessments = [proj_val["class"] for proj_key, proj_val in p_val["pageassessments"].items()]
        if most_common:
            common_assessment = max(set(assessments), key=assessments.count)
            return common_assessment
        else:
            return assessments
    return None


def main():
    args = sys.argv[1:]
    if len(args):
        article_title = args[0]
    else:
        article_title = "Wikipedia:Vital articles/Level/2"
    article_list_assessment_check(article_title)


if __name__ == "__main__":
    main()