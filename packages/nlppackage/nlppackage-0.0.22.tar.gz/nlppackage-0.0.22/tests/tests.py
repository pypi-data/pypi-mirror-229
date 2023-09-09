import unittest
from nlppackage import NLP

class TestStringMethods(unittest.TestCase):

    def test_lowercase(self):
        nlp = NLP()
        test_text = "HEELLOé"
        assert(nlp.lowercaseText(test_text) == "heelloé")

    def test_accent(self):
        nlp = NLP()
        test_text = "azertyuiopmlkjéèdééèeaà"
        clean_text = nlp.cleanAccent(test_text)
        assert(clean_text == "azertyuiopmlkjeedeeeeaa")
        assert(x not in clean_text for x in ["é", "è", "à", "ù"])

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()