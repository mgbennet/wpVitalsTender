"""
wpVitalsTender

A tool for helping to maintain lists of Wikipedia articles.
https://en.wikipedia.org/wiki/Wikipedia:Vital_articles is a list of 1000 articles and
their corresponding assessed quality. However these listings can go out of date as
articles improve or deteriorate. This script uses the Wikipedia API to automatically
detect mismatches between an article's listed and actual assessed quality.
"""


import sys
import re
import requests


def article_list_assessment_check(article_title, section=None):
    """Given a Wikipedia page listing articles, compares listed article
    quality assessments to actual current assessment.
    :param article_title: Wikipedia page containing a list of articles and their assessments
    :param section: optional sub section of above page.
    :return: List containing all mismatched articles.
    """
    content = get_content(article_title, section)
    listings = parse_article(content)
    print("Looking at " + article_title + ". Checking " + str(len(listings)) + " articles.")
    assessments = current_assessments([l["title"] for l in listings])
    mismatches = find_mismatches(listings, assessments)

    for m in mismatches:
        if m["current"]:
            print("Found a mismatch! " + m["title"] + " listed as " + m["listed_as"] + ", currently " + str(m["current"]))
        else:
            print(m["title"] + " has no assessments! Possible redirect or issue with WikiProject?")
    print(str(len(mismatches)) + " mismatches found.")
    return mismatches


def get_content(article_title, section=None):
    """Returns the content of a Wikipedia article, or optional section of an article."""
    baseurl = "https://en.wikipedia.org/w/api.php"
    query_attrs = {
        "action": "query",
        "titles": article_title,
        "prop": "revisions",
        "rvprop": "content",
        "format": "json"
    }
    if section:
        query_attrs["rvsection"] = section
    resp = requests.get(baseurl, query_attrs)
    pages = resp.json()["query"]["pages"]
    # only one page is queried, so return the first page's first revision text, or None if we didn't get anything.
    for p_key, p_val in pages.items():
        return p_val["revisions"][0]["*"]
    return None


def parse_article(content):
    """Finds all article links with an icon indicating assessed quality in a Wikipedia page.
    Matches listings structured like:
    1. {{icon|FA}} {{Icon|FGA}} [[Article title]]
     or
    * {{icon|Start}} [[Article title|Displayed article title]]

    :param content: The content to be parsed
    :return: List of dicts of style: {title: "article_title", assessment: "Stub|C|B|A|etc.", history: None|"FFA|FGA"}
    """
    article_listing_regex = re.compile(r'''
        [\*#]\s*                                        # line starts with a bullet or a number
        (?P<assessment>\{\{[Ii]con\|\w+\}\})            # assessment should always be first
        (?P<history>\s*\{\{[Ii]con\|\w+\}\})*           # option of multiple icons for FFA, or DGA
        \s*
        \'*\[\[(?P<title>[^#<>\[\]\{\}]+)\]\]           # actual title is a wikilink
    ''', re.VERBOSE)
    results = []
    for l in article_listing_regex.finditer(content):
        article = {
            "title": l.group("title").split("|")[0],
            "assessment": l.group("assessment").split("|")[-1][:-2],
            "history": None,
        }
        if l.group("history"):
            article["history"] = l.group("history").split("|")[-1][:-2]
        results.append(article)
    return results


def current_assessment(article_title):
    """Retrieves current assessment of one Wikipedia article."""
    baseurl = "https://en.wikipedia.org/w/api.php"
    query_attrs = {
        "action": "query",
        "titles": article_title,
        "prop": "pageassessments",
        "format": "json"
    }
    resp = requests.get(baseurl, query_attrs)
    pages = resp.json()["query"]["pages"]
    for p_key, p_val in pages.items():
        assessments = [proj_val["class"] for proj_key, proj_val in p_val["pageassessments"].items()]
        return assessments
    return None


def current_assessments(article_titles):
    """Retrieves current assessments for list of Wikipedia articles.
    returns {"article_title": [list, of, project, assessments], ....} """
    result = batch_query({"prop": "pageassessments"}, article_titles)
    return {page: [proj["class"] for proj_key, proj in result[page].items()] for page in result}


def batch_query(request, article_titles, print_num_queries=False):
    """Queries Wikipedia article for multiple articles

    :param request: Query attributes dict. Most import value is "prop"
    :param article_titles: List of article titles to be queried.
    :param print_num_queries: Option to print the number of api calls that were made
    :return: Dict of format {"article_title": {dict of "prop" results}}
    """
    request["action"] = "query"
    request["format"] = "json"
    results = {}
    num_queries = 0
    # can only query for 50 titles at a time, and even then have to do some fanciness to actually get the info
    for i in range(0, len(article_titles), 50):
        last_continue = {"continue": ""}
        request["titles"] = "|".join(article_titles[i:i + 50])
        while True:
            req = request.copy()
            req.update(last_continue)
            r = requests.get("https://en.wikipedia.org/w/api.php", params=req).json()
            num_queries += 1
            if "error" in r:
                raise ConnectionError(r["error"])
            if "query" in r:
                for page_key, page_val in r["query"]["pages"].items():
                    # page_val may not have
                    if request["prop"] in page_val:
                        if page_val["title"] in results:
                            results[page_val["title"]].update(page_val[request["prop"]])
                        else:
                            results[page_val["title"]] = page_val[request["prop"]]
            if "batchcomplete" in r:
                break
            last_continue = r["continue"]
    if print_num_queries:
        print(num_queries)
    return results


def find_mismatches(listings, assessments):
    mismatches = []
    for l in listings:
        if l["title"] in assessments:
            article_assessments = assessments[l["title"]]
            if not l["assessment"] in article_assessments:
                mismatches.append({"title": l["title"], "listed_as": l["assessment"], "current": article_assessments})
        else:
            mismatches.append({"title": l["title"], "listed_as": l["assessment"], "current": None})
    return mismatches


def main():
    args = sys.argv[1:]
    article_title = "Wikipedia:Vital articles/Level/2"
    section = None
    if len(args):
        article_title = args[0]
        if len(args) > 1:
            section = args[1]
    article_list_assessment_check(article_title, section)


if __name__ == "__main__":
    main()