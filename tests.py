import unittest
import wpVitalsTender as wpvt


class TestWpVitalsTender(unittest.TestCase):

    def test_get_content(self):
        article_title = "Wikipedia:Vital articles/Level/1"
        result = wpvt.get_content(article_title)
        self.assertIn("Earth", result)
        self.assertIn("Technology", result)
        self.assertIn("[[Category:Wikipedia level-1 vital articles|*]]", result)

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

    def test_current_assessment(self):
        # As this queries a real Wikipedia article, this test may need to be updated if the page improves.
        article_title = "Mummy Cave"
        article_quality = "GA"
        result = wpvt.current_assessment(article_title)
        self.assertIn(article_quality, result)

    def test_current_assessments(self):
        article_titles = ["Mummy Cave", "Land", "Tunng", "Bread"]
        article_qualities = ["GA", "C", "Start", "C"]
        result = wpvt.current_assessments(article_titles)
        for ind, article in enumerate(article_titles):
            self.assertIn(article_qualities[ind], result[article])

if __name__ == '__main__':
    unittest.main()