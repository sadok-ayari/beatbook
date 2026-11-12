import unittest

from beatbook.text import clean_byline, framing, name_key, tendency, themes_in

THEMES = [{"id": "cf", "name": "climate finance", "keywords": ["climate finance", "green bond"]},
          {"id": "en", "name": "energy transition", "keywords": ["solar", "renewable"]}]


class BylineTests(unittest.TestCase):
    def test_strips_by(self):
        self.assertEqual(clean_byline("By Aisha Karim"), "Aisha Karim")

    def test_keeps_caps_but_titlecases_shouting(self):
        self.assertEqual(clean_byline("AISHA KARIM"), "Aisha Karim")

    def test_strips_role_after_comma(self):
        self.assertEqual(clean_byline("Aisha Karim, Senior Correspondent"), "Aisha Karim")

    def test_strips_email_angle_brackets(self):
        self.assertEqual(clean_byline("By Omar Haddad <omar@example.org>"), "Omar Haddad")

    def test_two_authors_keep_the_first(self):
        self.assertEqual(clean_byline("By Leila Mansour and Omar Haddad"), "Leila Mansour")

    def test_empty_stays_empty(self):
        self.assertEqual(clean_byline(""), "")

    def test_email_only_is_not_a_name(self):
        self.assertEqual(clean_byline("desk@example.org"), "")

    def test_name_key_ignores_punctuation(self):
        self.assertEqual(name_key("Aisha Karim-Lopez"), "aisha karimlopez")


class ThemeTests(unittest.TestCase):
    def test_detects_theme_once(self):
        self.assertEqual(themes_in("green bond and climate finance", THEMES), ["climate finance"])

    def test_word_bounded(self):
        self.assertEqual(themes_in("solarisation of everything", THEMES), [])

    def test_multiple_themes(self):
        self.assertEqual(themes_in("solar and green bond", THEMES), ["climate finance", "energy transition"])


class FramingTests(unittest.TestCase):
    def test_counts_both_sides(self):
        counts = framing("The deal was welcomed as a boost, but critics warn of delay")
        self.assertEqual(counts["positive"], 3)
        self.assertEqual(counts["negative"], 2)

    def test_tendency_thresholds(self):
        self.assertEqual(tendency(0, 0), "neutral sample")
        self.assertEqual(tendency(9, 1), "consistently critical")
        self.assertEqual(tendency(6, 4), "leans critical")
        self.assertEqual(tendency(2, 8), "leans favourable")
        self.assertEqual(tendency(5, 5), "mixed")


if __name__ == "__main__":
    unittest.main()
