import sys
import re
import requests


def article_list_assessment_check(article_title):
    #TO DO!
    return article_title + "pezoo!"


def parse_article(content):
    article_listing_regex = re.compile(r'\* (?P<assessment>\{\{[Ii]con\|\w+\}\})\s*(?P<history>\{\{[Ii]con\|\w+\}\})*\s*\'*\[\[(?P<title>[\w\d\s|]+)\]\]')
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


def current_assessment(article_title):
    resp = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles=" + article_title + "&prop=pageassessments&format=json")
    pages = resp.json()["query"]["pages"]
    for p_key, p_val in pages.items():
        assessments = [proj_val["class"] for proj_key, proj_val in p_val["pageassessments"].items()]
        common_assessment = max(set(assessments), key=assessments.count)
        return common_assessment
    return None


def main():
    args = sys.argv[1:]
    if len(args):
        article_title = args[0]
    else:
        article_title = "Wikipedia:Vital articles"
    article_list_assessment_check(article_title)


if __name__ == "__main__":
    main()