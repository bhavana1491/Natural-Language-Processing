import unittest
import re
from french_count import french_count, prepare_input
from num2words import num2words

class test_fr_numbers(unittest.TestCase):
    def setUp(self):
        self.french = french_count()

    def test_frnumbers(self):
        s = []
        for ii in xrange(1,1000):
            try:
                fr = num2words(ii, lang='fr')
                fr = re.sub('-', ' ', fr)
                fr = re.sub('vingts', 'vingt', fr)
                fr = re.sub('cents', 'cent', fr)
                self.assertEqual(" ".join(self.french.transduce(prepare_input(ii))), fr)
            except:
                s.append(ii)

        print '\nNumber of failed numbers tests:', str(len(s))
        if len(s) != 0: print 'Failed numbers tests:', ','.join([str(x) for x in s])


if __name__ == '__main__':
    unittest.main()