import os
import sys
import unittest


SDK_PATH = '/usr/local/google_appengine'
TEST_PATH = os.path.join(os.path.curdir, '')


def main():
    sys.path.insert(0, SDK_PATH)

    import dev_appserver
    dev_appserver.fix_sys_path()

    try:
        import appengine_config
        (appengine_config)
    except ImportError:
        print "Note: unable to import appengine_config."

    # Discover and run tests.
    suite = unittest.loader.TestLoader().discover(TEST_PATH)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
