__author__ = "Martin Blais <blais@furius.ca>"

import textwrap

from beancount.utils import test_utils
from beancount.reports import context
from beancount import loader


class TestContext(test_utils.TestCase):

    @loader.load_doc()
    def test_context(self, entries, errors, options_map):
        """
        plugin "beancount.plugins.implicit_prices"

        2012-01-01 open Assets:US:ETrade:Cash                       USD
        2012-01-01 open Assets:US:ETrade:ITOT                       ITOT
        2012-01-01 open Assets:US:ETrade:GLD                        GLD
        2012-01-01 open Income:US:ETrade:Gains                      USD
        2012-01-01 open Expenses:Financial:Commissions              USD

        2012-08-31 * "Buy shares of GLD"
          Assets:US:ETrade:Cash              -784.06 USD
          Assets:US:ETrade:GLD                  7.00 GLD       {110.73 USD}
          Expenses:Financial:Commissions        8.95 USD

        2012-08-31 * "Buy shares of ITOT"
          Assets:US:ETrade:Cash              -701.39 USD
          Assets:US:ETrade:ITOT                 4.00 ITOT       {173.11 USD}
          Expenses:Financial:Commissions        8.95 USD

        2012-10-13 * "Buy shares of ITOT"
          Assets:US:ETrade:Cash                                 -2,337.77 USD
          Assets:US:ETrade:ITOT                13.00 ITOT       {179.14 USD}
          Expenses:Financial:Commissions        8.95 USD

        2013-02-01 * "Sell shares of ITOT"
          Assets:US:ETrade:ITOT               -13.00 ITOT       {179.14 USD} @ 186.21 USD
          Assets:US:ETrade:Cash                                  2,411.78 USD
          Expenses:Financial:Commissions        8.95 USD
          Income:US:ETrade:Gains              -91.91 USD

        2013-02-07 * "Buy shares of ITOT"
          Assets:US:ETrade:Cash                                 -1,126.21 USD
          Assets:US:ETrade:ITOT                 6.00 ITOT       {186.21 USD}  ;; *
          Expenses:Financial:Commissions        8.95 USD

        2013-02-07 * "Buy shares of GLD"
          Assets:US:ETrade:Cash                                 -1,287.70 USD
          Assets:US:ETrade:GLD                 11.00 GLD       {116.25 USD}
          Expenses:Financial:Commissions        8.95 USD

        """
        self.assertFalse(errors)

        search_filename = entries[0].meta["filename"]
        search_lineno = entries[-3].meta["lineno"] + 2
        dcontext = options_map['dcontext']
        str_context = context.render_entry_context(entries, options_map, dcontext,
                                                   search_filename, search_lineno)

        self.assertLines(textwrap.dedent("""
        Hash:298dca350249afe0378cf8bac2fb12cf
        Location: <string>:31

        ;   Assets:US:ETrade:Cash                       -1411.44 USD

        ;   Assets:US:ETrade:ITOT             4.00 ITOT {173.11 USD}

        ;   Expenses:Financial:Commissions                 35.80 USD


        2013-02-07 * "Buy shares of ITOT"
          Assets:US:ETrade:Cash           -1126.21 USD                ;  -1126.21 USD
          Assets:US:ETrade:ITOT               6.00 ITOT {186.21 USD}  ; 1117.2600 USD
          Expenses:Financial:Commissions      8.95 USD                ;      8.95 USD


        ;;; Tolerances: ITOT=0.005, USD=0.005

        ; ! Assets:US:ETrade:Cash                      -2537.65 USD

        ;   Assets:US:ETrade:ITOT             4.00 ITOT {173.11 USD}
        ; ! Assets:US:ETrade:ITOT             6.00 ITOT {186.21 USD}

        ; ! Expenses:Financial:Commissions                 44.75 USD
        """), str_context)

    maxDiff = 8192
