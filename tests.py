import unittest
import wpVitalsTender as wpvt


class TestWpVitalsTender(unittest.TestCase):

    def test_get_content(self):
        article_title = "Wikipedia:Vital articles/Level/1"
        result = wpvt.get_content(article_title)
        self.assertIn("Technology", result)

    def test_parse_article(self):
        test_content = "This list is tailored to the English-language Wikipedia. There is also a [[m:List of articles every Wikipedia should have|list of one thousand articles]] considered vital to Wikipedias of all languages.\n\nFor more information on this list and the process for adding articles, please see the [[Wikipedia talk:Vital articles/Frequently Asked Questions|Frequently Asked Questions (FAQ) page]].\n\n==Current total: 1000==\nLast updated by [[User:Cobblet|Cobblet]] ([[User talk:Cobblet|talk]]) 02:25, 24 October 2016 (UTC)\n* Added [[Early human migrations]] per [[Wikipedia_talk:Vital_articles#Add_Early human migrations|discussion]]\n\n===Terrestrial features (12 articles)===* {{Icon|C}} '''[[Land]]''' ([[Wikipedia:Vital articles/Level/2|Level 2]])* {{Icon|GA}} [[Desert]]** {{Icon|B}} [[Sahara]]* {{Icon|B}} [[Forest]]* {{Icon|B}} {{Icon|DGA}} [[Glacier]]* {{Icon|B}} {{Icon|DGA}} [[Grand Canyon]]* {{Icon|C}} [[Mountain]]** {{Icon|C}} [[Alps]]** {{Icon|C}} [[Andes]]** {{Icon|C}} [[Himalayas]]\n*** {{Icon|B}} [[Mount Everest]]** {{Icon|B}} [[Rocky Mountains]]{{col-end}}"
        result = wpvt.parse_article(test_content)
        self.assertEqual(len(result), 12)
        self.assertEqual("Land", result[0]["title"])
        self.assertEqual("Glacier", result[4]["title"])
        self.assertEqual("Rocky Mountains", result[11]["title"])
        self.assertEqual("C", result[0]["assessment"])
        self.assertEqual("GA", result[1]["assessment"])
        self.assertEqual("B", result[4]["assessment"])
        self.assertEqual("B", result[11]["assessment"])
        self.assertEqual("DGA", result[5]["history"])
        self.assertEqual(None, result[11]["history"])

    def test_current_assessment(self):
        # As this queries a real Wikipedia article, this test may need to be updated if the page improves.
        article_title = "Mummy Cave"
        article_quality = "GA"
        result = wpvt.current_assessment(article_title)
        self.assertEqual(article_quality, result)

if __name__ == '__main__':
    unittest.main()