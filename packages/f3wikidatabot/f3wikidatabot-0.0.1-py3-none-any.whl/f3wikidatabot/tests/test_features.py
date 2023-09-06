# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from unittest import mock
import pywikibot

from f3wikidatabot.bot import Bot
from f3wikidatabot.features import Features
from f3wikidatabot.tests.wikidata import WikidataHelper

log = logging.getLogger("f3wikidatabot")


class TestFeatures(object):
    def setup_class(self):
        self.site = WikidataHelper().login()

    def teardown_class(self):
        self.site.logout()

    def setup(self):
        pass

    def test_query(self):
        bot = Bot.factory(["--verbose"])
        features = Features(bot, bot.args)
        query = features.get_query([])
        assert "P31" in query

    def test_show(self):
        bot = Bot.factory(["--verbose", "--show", "--plugin", "Features"])
        forgejo = "Forgejo"
        heptapod = "Heptapod"
        found = []
        for forge in bot.run_query():
            if forge.label == forgejo:
                found.append(forge.label)
                assert "software repository" in forge.features
            elif forge.label == heptapod:
                found.append(forge.label)
                assert "repository" in forge.features
        assert sorted(found) == sorted([forgejo, heptapod])


# Local Variables:
# compile-command: "cd .. ; tox -e py3 tests/test_features.py"
# End:
