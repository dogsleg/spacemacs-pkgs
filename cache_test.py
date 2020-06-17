import unittest

from cache import Cache


class TestCache(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.cache = Cache('test.sqlite')

        self.cache.update_last_update('debian', '2020-01-01')
        self.cache.update_last_update('spacemacs', '2020-01-02')
        self.cache.update_last_update('doomemacs', '2020-01-03')


        self.packages = [{'pkg_name': 'package1',
                          'homepage': 'homepage1',
                          'in_debian': 0,
                          'is_builtin': 0,
                          'spacemacs': 'se_layer1',
                          'doomemacs': ''},
                         {'pkg_name': 'package2',
                          'homepage': 'homepage2',
                          'in_debian': 1,
                          'is_builtin': 0,
                          'spacemacs': '',
                          'doomemacs': 'de_layer2'},
                         {'pkg_name': 'package3',
                          'homepage': 'homepage3',
                          'in_debian': 0,
                          'is_builtin': 0,
                          'spacemacs': 'se_layer3',
                          'doomemacs': 'de_layer3'},
                         {'pkg_name': 'package4',
                          'homepage': '',
                          'in_debian': 0,
                          'is_builtin': 1,
                          'spacemacs': 'se_layer4',
                          'doomemacs': ''},
                         {'pkg_name': 'package5',
                          'homepage': '',
                          'in_debian': 0,
                          'is_builtin': 1,
                          'spacemacs': 'se_layer5',
                          'doomemacs': ''}]

        self.new_packages = [{'pkg_name': 'package1',
                              'homepage': 'homepage12',
                              'in_debian': 0,
                              'is_builtin': 0,
                              'spacemacs': '',
                              'doomemacs': 'dm_layer12'},
                             {'pkg_name': 'package2',
                              'homepage': 'homepage22',
                              'in_debian': 0,
                              'is_builtin': 1,
                              'spacemacs': 'se_layer_22',
                              'doomemacs': ''},
                             {'pkg_name': 'package3',
                              'homepage': 'homepage3',
                              'in_debian': 1,
                              'is_builtin': 1,
                              'spacemacs': 'se_layer3',
                              'doomemacs': ''},
                             {'pkg_name': 'package4',
                              'homepage': '',
                              'in_debian': 0,
                              'is_builtin': 1,
                              'spacemacs': '',
                              'doomemacs': ''},
                             {'pkg_name': 'package5',
                              'homepage': 'homepage52',
                              'in_debian': 1,
                              'is_builtin': 0,
                              'spacemacs': 'se_layer5',
                              'doomemacs': 'dm_layer52'}]

        self.cache.update_packages(self.packages)

    def test_01_last_update(self):
        self.assertEqual(self.cache.last_update('debian'), '2020-01-01')
        self.assertEqual(self.cache.last_update('debian'), '2020-01-01')
        self.assertEqual(self.cache.last_update('debian'), '2020-01-01')

    def test_02_get_packages(self):
        self.assertEqual(self.cache.get_packages(), self.packages)

    def test_03_is_builtin(self):
        self.assertEqual(self.cache.is_builtin('package1'), False)
        self.assertEqual(self.cache.is_builtin('package2'), False)
        self.assertEqual(self.cache.is_builtin('package3'), False)
        self.assertEqual(self.cache.is_builtin('package4'), True)
        self.assertEqual(self.cache.is_builtin('package5'), True)

    def test_04_get_builtins(self):
        self.assertEqual(self.cache.get_builtins(), ['package4', 'package5'])

    def test_05_drop_package(self):
        self.cache.drop_package('package4')
        self.assertEqual(self.cache.get_packages(),
                         self.packages[:3] + self.packages[4:])
        self.assertEqual(self.cache.get_builtins(), ['package5'])

    def test_06_update_packages(self):
        self.cache.update_packages(self.new_packages)
        self.assertEqual(self.cache.get_packages(), self.new_packages)
        self.assertEqual(self.cache.get_builtins(), ['package2',
                                                     'package3',
                                                     'package4'])

    def test_07_clean_db(self):
        self.cache.update_packages(self.new_packages)
        self.cache.clean_db()
        self.assertEqual(self.cache.get_packages(),
                         self.new_packages[:3] + self.new_packages[4:])
        self.assertEqual(self.cache.get_builtins(), ['package2',
                                                     'package3'])

    def test_08_drop_suites(self):
        self.cache.drop_suites()
        self.cache.clean_db()
        self.assertEqual(self.cache.get_packages(), [])
        self.assertEqual(self.cache.get_builtins(), [])

    def tearDown(self):
        self.cache.close()

if __name__ == '__main__':
    unittest.main()
