"""This module automatically inserts Open directives for accounts not opened (at
the date of the first entry) and automatically removes open directives for
unused accounts. This can be used as a convenience for doing demos, or when
setting up your initial transactions, as an intermediate step.
"""
__author__ = "Martin Blais <blais@furius.ca>"

from beancount.core import data
from beancount.core import getters

__plugins__ = ('auto_insert_open',)


def auto_insert_open(entries, unused_options_map):
    """Insert implicitly defined prices from Transactions.

    Explicit price entries are simply maintained in the output list. Prices from
    postings with costs or with prices from Transaction entries are synthesized
    as new Price entries in the list of entries output.

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      unused_options_map: A parser options dict.
    Returns:
      A list of entries, possibly with more Price entries than before, and a
      list of errors.
    """
    opened_accounts = {entry.account
                       for entry in entries
                       if isinstance(entry, data.Open)}

    new_entries = []
    accounts_first, _ = getters.get_accounts_use_map(entries)
    for account, date_first_used in accounts_first.items():
        if account not in opened_accounts:
            meta = data.new_metadata('<auto_accounts>', 0)
            new_entries.append(data.Open(meta, date_first_used, account,
                                         None, None))

    if new_entries:
        new_entries.extend(entries)
        new_entries.sort(key=data.entry_sortkey)
    else:
        new_entries = entries

    return new_entries, []
