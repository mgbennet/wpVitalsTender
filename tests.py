import unittest
import unittest.mock
import wpVitalsTender as wpvt
import requests
import json


def mock_requests_get(*args, **kwargs):
    class Mock_Response:
        def __init__(self, content_file, status_code):
            with open(content_file, 'r') as f:
                self.content = f.read()
                self.status_code = status_code

        def json(self):
            return json.loads(self.content)

    if args[1]["titles"] == "Wikipedia:Vital articles/Level/1":
        return Mock_Response('test_docs/test_WikipediaLevel1_content.json', 200)
    if args[1]["titles"] == "Mummy Cave":
        return Mock_Response('test_docs/test_MummyCave_assessment.json', 200)
    if args[1]["titles"] == "Mummy Cave|Land|Tunng|Bread":
        return Mock_Response('test_docs/test_MultipleArticles_assessment.json', 200)
    return Mock_Response("", 404)


class TestWpVitalsTender(unittest.TestCase):

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_get_content(self, mock_get):
        article_title = "Wikipedia:Vital articles/Level/1"
        result = wpvt.get_content(article_title)

        self.assertIn("Earth", result)
        self.assertIn("Technology", result)
        self.assertIn("[[Category:Wikipedia level-1 vital articles|*]]", result)
        mock_get.assert_called_with('https://en.wikipedia.org/w/api.php', {
            "action": "query",
            "titles": article_title,
            "prop": "revisions",
            "rvprop": "content",
            "format": "json"
        })

    def test_parse_article(self):
        with open('test_docs/test_parse_article.txt', 'r') as article_file:
            test_content = article_file.read()
            result = wpvt.parse_article(test_content)

            self.assertEqual(len(result), 12)
            self.assertEqual("Land", result[0]["title"])
            self.assertEqual("Glacier", result[4]["title"])
            self.assertEqual("Rocky Mountains", result[11]["title"])
            self.assertEqual("C", result[0]["assessment"])
            self.assertEqual("GA", result[1]["assessment"])
            self.assertEqual("B", result[4]["assessment"])
            self.assertEqual("B", result[11]["assessment"])
            self.assertEqual("DGA", result[4]["history"])
            self.assertEqual(None, result[10]["history"])
            self.assertEqual("DGA", result[11]["history"])

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_current_assessment(self, mock_get):
        article_title = "Mummy Cave"
        result = wpvt.current_assessment(article_title)

        self.assertIn("GA", result)
        self.assertEqual(len(result), 5)

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_current_assessments(self, mock_get):
        article_titles = ["Mummy Cave", "Land", "Tunng", "Bread"]
        article_qualities = ["GA", "C", "Start", "C"]
        result = wpvt.current_assessments(article_titles)

        for ind, article in enumerate(article_titles):
            self.assertIn(article_qualities[ind], result[article])

    def test_find_mismatches(self):
        with open('test_docs/test_parse_article.txt', 'r') as article_file:
            test_content = article_file.read()
            listings = wpvt.parse_article(test_content)
            assessments = {
                "Land": ["C"],
                "Desert": ["GA", "B"],
                "Sahara": ["B"],
                "Glacier": ["B"],
                "Grand Canyon": ["B"],
                "Mountain": ["Start", "B", "Stub"],  # Actually C
                "Alps (mountains)": ["C", "C", "C", "Start"],
                "Andes": ["C"],
                "Himalayas": ["B"],  # Actually C
                "Mount Everest": ["Start"],
                "Rocky Mountains": ["B"],
            }
            results = wpvt.find_mismatches(listings, assessments)

            self.assertIn({"title": "Forest", "listed_as": "B", "current": None}, results)
            self.assertIn({"title": "Mountain", "listed_as": "C", "current": ["Start", "B", "Stub"]}, results)
            self.assertIn({"title": "Himalayas", "listed_as": "C", "current": ["B"]}, results)


if __name__ == '__main__':
    unittest.main()