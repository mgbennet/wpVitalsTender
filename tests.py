import unittest
import unittest.mock
import wpVitalsTender as wpvt
import requests
import json


class TestWpVitalsTender(unittest.TestCase):

    @unittest.mock.patch.object(requests, 'get', autospec=True)
    def test_get_content(self, mock_get):
        def get_mock_json():
            with open('test_docs/test_get_content.json', 'r') as file:
                return json.loads(file.read())
        mock_get.return_value.json = get_mock_json

        article_title = "Wikipedia:Vital articles/Level/1"
        result = wpvt.get_content(article_title)

        self.assertIn("Earth", result)
        self.assertIn("Technology", result)
        self.assertIn("[[Category:Wikipedia level-1 vital articles|*]]", result)
        mock_get.assert_called_with('https://en.wikipedia.org/w/api.php',{
            "action": "query",
            "titles": article_title,
            "prop": "revisions",
            "rvprop": "content",
            "format": "json"
        })

    def test_parse_article(self):
        with open('test_docs/test_parse_article.txt', 'r') as file:
            test_content = file.read();
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

    @unittest.mock.patch.object(requests, 'get', autospec=True)
    def test_current_assessment(self, mock_get):
        def get_mock_json():
            with open('test_docs/test_current_assessment.json', 'r') as file:
                return json.loads(file.read())
        mock_get.return_value.json = get_mock_json
        article_title = "Mummy Cave"

        result = wpvt.current_assessment(article_title)

        self.assertIn("GA", result)
        self.assertEqual(len(result), 5)

    def test_current_assessments(self):
        article_titles = ["Mummy Cave", "Land", "Tunng", "Bread"]
        article_qualities = ["GA", "C", "Start", "C"]
        result = wpvt.current_assessments(article_titles)
        for ind, article in enumerate(article_titles):
            self.assertIn(article_qualities[ind], result[article])

    def test_find_mismatches(self):
        with open('test_docs/test_parse_article.txt', 'r') as file:
            test_content = file.read();
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