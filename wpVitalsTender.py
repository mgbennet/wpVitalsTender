#!/usr/bin/python
"""
wpVitalsTender

A tool for helping to maintain lists of Wikipedia articles.
https://en.wikipedia.org/wiki/Wikipedia:Vital_articles is a list of 1000 articles and
their corresponding assessed quality. However these listings can go out of date as
articles improve or deteriorate. This script uses the Wikipedia API to automatically
detect mismatches between an article's listed and actual assessed quality.
"""


import re
import argparse
import requests


USER_AGENT = "wpVitalsTender (https://github.com/mgbennet/wpVitalsTender)"

default_article = "Wikipedia:Vital articles/Level/2"
all_articles = [
    "Wikipedia:Vital articles/Level/1",
    "Wikipedia:Vital articles/Level/2",
    "Wikipedia:Vital articles",
    "Wikipedia:Vital articles/Level/4/People",
    "Wikipedia:Vital articles/Level/4/History",
    "Wikipedia:Vital articles/Level/4/Geography",
    "Wikipedia:Vital articles/Level/4/Arts",
    "Wikipedia:Vital articles/Level/4/Philosophy and religion",
    "Wikipedia:Vital articles/Level/4/Everyday life",
    "Wikipedia:Vital articles/Level/4/Society and social sciences",
    "Wikipedia:Vital articles/Level/4/Biology and health sciences",
    "Wikipedia:Vital articles/Level/4/Physical sciences",
    "Wikipedia:Vital articles/Level/4/Technology",
    "Wikipedia:Vital articles/Level/4/Mathematics"
]


def article_list_assessment_check(article_title, section=None, accuracy=.01):
    """Given a Wikipedia page listing articles, compares listed article
    quality assessments to actual current assessment.
    :param article_title: Wikipedia page containing a list of articles and their assessments
    :param section: optional sub section of above page.
    :param accuracy: minimum ratio of assessments to qualify as a mismatch
    :return: List containing all mismatched articles.
    """
    content = get_content(article_title, section)
    # probably should refactor so parse_articles returns a dictionary, not a list...
    listings = parse_article(content)
    print("Looking at {}. Checking {} articles.".format(article_title, len(listings)))
    redirects = find_redirects([l["title"] for l in listings])
    if len(redirects):
        print("Found {} redirects".format(len(redirects)))
    for listing in listings:
        if listing["title"] in redirects:
            print("{} redirects to {}".format(listing["title"], redirects[listing["title"]]))
            listing["title"] = redirects[listing["title"]]
    assessments = current_assessments([l["title"] for l in listings])
    mismatches = find_mismatches(listings, assessments, accuracy)

    for m in mismatches:
        if m["current"]:
            print("Mismatch found! {} listed as {}, currently {}".format(m["title"], m["listed_as"], m["current"]))
        else:
            print("{} has no assessments! Possible issue with WikiProject or talk page?".format(m["title"]))
    print("{} mismatches found.".format(len(mismatches)))
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
    resp = requests.get(baseurl, query_attrs, headers={"User-Agent": USER_AGENT})
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
        [*#]\s*                                         # line starts with a bullet or a number
        (?P<assessment>\{\{[Ii]con\|\w+\}\})            # assessment should always be first
        (?P<history>\s*\{\{[Ii]con\|\w+\}\})*           # option of multiple icons for FFA, or DGA
        \s*
        \'*\[\[(?P<title>[^#<>\[\]]+)\]\]               # actual title is a wikilink
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


def find_redirects(article_titles):
    """Finds all redirects in a list of article titles."""
    results = {}
    request = {
        "action": "query",
        "format": "json",
        "redirects": ""
    }
    # can only query for 50 titles at a time, and even then have to do some fanciness to actually get the info
    for i in range(0, len(article_titles), 50):
        request["titles"] = "|".join(article_titles[i:i + 50])
        r = requests.get("https://en.wikipedia.org/w/api.php", request, headers={"User-Agent": USER_AGENT}).json()
        if "redirects" in r["query"]:
            for redirect in r["query"]["redirects"]:
                results[redirect["from"]] = redirect["to"]
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
    resp = requests.get(baseurl, query_attrs, headers={"User-Agent": USER_AGENT})
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
            r = requests.get("https://en.wikipedia.org/w/api.php", req, headers={"User-Agent": USER_AGENT}).json()
            num_queries += 1
            if "error" in r:
                raise ConnectionError(r["error"])
            if "query" in r:
                for page_key, page_val in r["query"]["pages"].items():
                    # returns piecemeal, not all props in the same request
                    if request["prop"] in page_val:
                        if page_val["title"] in results:
                            results[page_val["title"]].update(page_val[request["prop"]])
                        else:
                            results[page_val["title"]] = page_val[request["prop"]]
            if "batchcomplete" in r:
                break
            last_continue = r["continue"]
    if print_num_queries:
        print("Number of calls to complete batch query: ", num_queries)
    return results


def find_mismatches(listings, assessments, accuracy=.01):
    """Finds any listings that are listed as having different assessments.

    :param listings: article listings as generated by parse_article
    :param assessments: dict of assessments of all listed articles
    :param accuracy: minimum ratio of assessments to qualify as a mismatch
    :return: array of mismatches
    """
    mismatches = []
    for l in listings:
        if l["title"] in assessments:
            article_assessments = assessments[l["title"]]
            processed_assessments = list(map(str.lower, filter(lambda c: c != '', article_assessments)))
            # We don't have a good solution if there are no project ratings
            if len(processed_assessments) != 0:
                assessment_ratio = processed_assessments.count(l["assessment"].lower()) / len(processed_assessments)
                if assessment_ratio < accuracy:
                    mismatches.append({
                        "title": l["title"],
                        "listed_as": l["assessment"],
                        "current": article_assessments
                    })
        else:
            mismatches.append({
                "title": l["title"],
                "listed_as": l["assessment"],
                "current": None
            })
    return mismatches


def main():
    parser = argparse.ArgumentParser(description="Find mismatches between listed and actual wikipedia article ratings.")
    parser.add_argument("articles", nargs="*", help="Title of the article to parse", default=[default_article])
    parser.add_argument("-s", "--section", help="Index of section to parse", default=None)
    parser.add_argument("-a", "--accuracy", help="Ratio of listings required of match", type=float, default=0.01)
    args = parser.parse_args()

    if args.articles[0].lower() == "all":
        for article in all_articles:
            article_list_assessment_check(article, accuracy=args.accuracy)
    else:
        for article in args.articles:
            article_list_assessment_check(article, section=args.section, accuracy=args.accuracy)


if __name__ == "__main__":
    main()
