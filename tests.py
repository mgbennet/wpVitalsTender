#!/usr/bin/python
import unittest
import unittest.mock
import wpVitalsTender as wpvt
import json


def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content_file, status_code):
            self.content_file = content_file
            self.status_code = status_code

        def json(self):
            with open(self.content_file, 'r') as f:
                return json.loads(f.read())

    if "redirects" in args[1] and args[1]["titles"] == "Buildings|Bricks|Houses|WW2|WW1|Cup":
        return MockResponse('test_docs/test_Redirects.json', 200)
    if "prop" in args[1]:
        if args[1]["prop"] == "revisions" and args[1]["titles"] == "Wikipedia:Vital articles/Level/1":
            return MockResponse('test_docs/test_WikipediaLevel1_content.json', 200)
        if args[1]["prop"] == "pageassessments" and args[1]["titles"] == "Mummy Cave":
            return MockResponse('test_docs/test_MummyCave_assessment.json', 200)
        if args[1]["prop"] == "pageassessments" and args[1]["titles"].startswith('Building|Infrastructure|Brick|Cement|Concrete|Lumber'):
            file = "test_docs/MultiArticleAssessment/test_MultiArticleAssessment_"
            if args[1]["continue"] == "":
                file += "0.json"
            else:
                file += args[1]["mockcontinue"] + ".json"
            return MockResponse(file, 200)
        if args[1]["prop"] == "pageassessments" and args[1]["titles"].startswith('HVAC|Drainage|Dam|Aswan Dam|Hoover Dam'):
            file = "test_docs/MultiArticleAssessment/test_MultiArticleAssessment_"
            if args[1]["continue"] == "":
                file += "12.json"
            else:
                file += args[1]["mockcontinue"] + ".json"
            return MockResponse(file, 200)
    return MockResponse("", 404)


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
            "format": "json",
        }, headers={"User-Agent": wpvt.USER_AGENT})

    def test_parse_article(self):
        with open('test_docs/test_parse_article.txt', 'r') as article_file:
            test_content = article_file.read()
            result = wpvt.parse_article(test_content)

            self.assertEqual(len(result), 13)
            self.assertEqual("Land", result[0]["title"])
            self.assertEqual("C", result[0]["assessment"])
            self.assertEqual("Desert", result[1]["title"])
            self.assertEqual("GA", result[1]["assessment"])
            self.assertEqual("Glacier", result[4]["title"])
            self.assertEqual("B", result[4]["assessment"])
            self.assertEqual("DGA", result[4]["history"])
            self.assertEqual("start", result[10]["assessment"])
            self.assertEqual(None, result[10]["history"])
            self.assertEqual("E (mathematical constant)", result[11]["title"])
            self.assertEqual("FA", result[11]["assessment"])
            self.assertEqual(None, result[11]["history"])
            self.assertEqual("B", result[12]["assessment"])
            self.assertEqual("DGA", result[12]["history"])

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_find_redirects(self, mock_get):
        articles = ['Buildings', 'Bricks', 'Houses', 'WW2', 'WW1', 'Cup']
        redirects = ['Building', 'Brick', 'House', 'World War II', 'World War I', None]
        results = wpvt.find_redirects(articles)
        for i, a in enumerate(articles):
            if redirects[i]:
                self.assertEqual(redirects[i], results[a])
            else:
                self.assertNotIn(a, results)

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_current_assessment(self, mock_get):
        article_title = "Mummy Cave"
        result = wpvt.current_assessment(article_title)

        self.assertIn("GA", result)
        self.assertEqual(len(result), 5)

    @unittest.mock.patch('requests.get', side_effect=mock_requests_get)
    def test_current_assessments(self, mock_get):
        article_titles = ['Building', 'Infrastructure', 'Brick', 'Cement', 'Concrete', 'Lumber', 'Masonry', 'Quarry',
                          'Scaffolding', 'Arch', 'Ceiling', 'Column', 'Dome', 'Door', 'Elevator', 'Facade', 'Floor',
                          'Foundation (engineering)', 'Lighting', 'Roof', 'Room', 'Stairs', 'Wall', 'Window', 'Harbor',
                          'Lighthouse', 'Pier', 'Port', 'Office', 'Warehouse', 'Apartment', 'House', 'Hut', 'Igloo',
                          'Pagoda', 'Palace', 'Pyramid', 'Skyscraper', 'Tower', 'Tower block', 'Villa', 'Bathroom',
                          'Bedroom', 'Dining room', 'Garage (residential)', 'Kitchen', 'Living room', 'Tent', 'Yurt',
                          'Electrical wiring', 'HVAC', 'Drainage', 'Dam', 'Aswan Dam', 'Hoover Dam', 'Itaipu Dam',
                          'Three Gorges Dam', 'Flood control', 'Flood control in the Netherlands', 'Levee', 'Reservoir',
                          'Bridge', 'Akashi Kaikyō Bridge', 'Brooklyn Bridge', 'Golden Gate Bridge', 'London Bridge',
                          'Tunnel', 'Channel Tunnel']
        article_qualities = {"Brick": ["C", "C"], "Cement": ["B", "B"], "Column": ["Start", "Start"],
                             "Concrete": ["B", "B", ""], "Door": ["B", ""], "Harbor": ["Start", "Start"],
                             "House": ["C", "C", "C"], "Lighthouse": ["B", "B", "B", "B"], "Masonry": ["Start"],
                             "Palace": ["Start"], "Pyramid": ["C", "B", "B", "B", "B"], "Roof": ["Start", "Start"],
                             "Skyscraper": ["B", "B"], "Building": ["C", "C"], "Kitchen": ["B", "B", "B"],
                             "Wall": ["C"], "Window": ["C", "C", "C"], "Arch": ["C", "C"], "Floor": ["Start", "Start"],
                             "Lumber": ["Start", "C", "C"], "Port": ["", "Start", "Start"], "Dome": ["Start", "B", "B"],
                             "Igloo": ["Start", "Start", "Start"], "Infrastructure": ["C", "", "C", "C"],
                             "Tower block": ["C"], "Bathroom": ["Start", "Start", "Start"], "Lighting": ["C"],
                             "Quarry": ["Start", "Start"], "Scaffolding": ["C"], "Tower": ["Start", "Start"],
                             "Apartment": ["C", "C"], "Pagoda": ["C", "C", "C", "C", "C", "C", "C", "C", "C"],
                             "Pier": ["Start"], "Stairs": ["C", "C"], "Tent": ["C", ""], "Facade": ["Start"],
                             "Office": ["C", "C"], "Villa": ["C"], "Bedroom": ["Start", "Start"],
                             "Dining room": ["Start", "Start", "Start"], "Foundation (engineering)": ["Start"],
                             "Warehouse": ["C", "C"], "Yurt": ["Start", "Start"], "Ceiling": ["Start", "Start"],
                             "Electrical wiring": ["C", "C"], "Garage (residential)": ["Start", "Start"],
                             "Hut": ["Start", "Start"], "Living room": ["Start", "Start"], "Elevator": ["C", "C", "C"],
                             "Room": ["Start", "Start"], "Bridge": ["C", "B", "B", "B"],
                             "Channel Tunnel": ["B", "B", "B", "B", "B"], "Golden Gate Bridge": ["B", "B", "B"],
                             "Hoover Dam": ["FA", "FA", "", "FA", "FA", "FA", "FA"],
                             "Levee": ["Start", "Start", "Start", ""], "Brooklyn Bridge": ["B", "B", "B", "B", "B"],
                             "Dam": ["C", "B", "B", "B", "B"], "Drainage": ["C"], "HVAC": ["C", "C", "C"],
                             "Three Gorges Dam": ["GA", "GA", "GA", "GA", "GA"],
                             "Itaipu Dam": ["C", "C", "C", "C", "C"],
                             "London Bridge": ["B", "B", "", "Start", "B", "B", "Start"],
                             "Akashi Kaikyō Bridge": ["Start", "", "Start"], "Tunnel": ["C", "C", "C"],
                             "Aswan Dam": ["C", "C", "C"], "Flood control in the Netherlands": ["C", "C", "C", "C"],
                             "Reservoir": ["C", "C", "C"], "Flood control": ["C", "C", "C"]}
        result = wpvt.current_assessments(article_titles)
        for article, assessments in result.items():
            self.assertCountEqual(assessments, article_qualities[article])

    def test_find_mismatches(self):
        with open('test_docs/test_parse_article.txt', 'r') as article_file:
            test_content = article_file.read()
            listings = wpvt.parse_article(test_content)
            assessments = {
                "Land": ["C"],
                "Desert": ["GA", "B"],
                "Sahara": ["B"],  # Actually GA
                "Glacier": ["B"],
                "Grand Canyon": ["Start", "stub", "B"],  # B, but not accurate enough
                "Mountain": ["Start", "c", "C"],
                "Alps (mountains)": ["c", "c", "b", "Start"],
                "Andes": ["Start"],
                "Himalayas": ["B"],  # Actually C
                "Mount Everest": ["Start"],
                "E (mathematical constant)": ["FA"],
                "Rocky Mountains": ["B"],
            }
            results = wpvt.find_mismatches(listings, assessments, .5)

            self.assertEqual(len(results), 4)
            self.assertIn({"title": "Forest", "listed_as": "B", "current": None}, results)
            self.assertIn({"title": "Sahara", "listed_as": "ga", "current": ["B"]}, results)
            self.assertIn({"title": "Grand Canyon", "listed_as": "B", "current": ["Start", "stub", "B"]}, results)
            self.assertIn({"title": "Himalayas", "listed_as": "C", "current": ["B"]}, results)


if __name__ == '__main__':
    unittest.main()
