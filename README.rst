Introduction
============

collective.betterbrowser improves the plone.testing browser with the
following, run inside your functional testcase: ::

    from collective.betterbrowser import new_browser

    def test_all_the_things(self):
        browser = new_browser(self.layer)
        browser.login_admin()
        browser.show()

At which point your default browser opens, showing the state of browser with
the ability to actually interact with the testing plone site in the background.
