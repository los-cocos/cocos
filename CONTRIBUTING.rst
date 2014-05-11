Patch submission guidelines [1]_
--------------------------------

We strongly prefer to receive contributions as Github Pull Requests (PR), and that
is what's described below.

If for some reason that is inconvenient, you can generate a patch [2]_ and
send it attached to the mailing list.

Just in case, a `good guide to git <http://documentup.com/skwp/git-workflows-book>`.

Steps
-----

**Make sure there is an open issue for your change.**

Perhaps, if it's a new feature, you probably want to
`discuss it first <http://groups.google.com/group/cocos-discuss>`_

**Have a local clone with upload rights to work with.**

  - if you have commit rights in los-cocos/cocos, have a clone of that project
  - if you don't, fork the project ( the button 'fork' in https://github.com/los-cocos/cocos ) and then clone ``your-username/cocos`` project

**Create a new Git branch specific to your change(s).**

For example, if you're adding a new feature to foo the bars, do something 
like the following::

    $ git checkout master
    $ git pull
    $ git checkout -b foo-the-bars
    <hack hack hack>
    $ git push origin HEAD

This makes life much easier for maintainers if you have (or ever plan to
have) additional changes in your own ``master`` branch.

**Submit pull request based on your new 'foo-the-bars' branch.**

  - Go to the Github page associated with your clone; if you forked it is the page for
    ``your-username/cocos`` project
  - In the button-dropdown list ``branch: zzz`` select branch ``foo-the-bar``
  - Press the green button to the left (the tooltip shows ``preview, create a pull request``)
  - Fill the subject and body. Make the subject descriptive and add a reference to the issue
    you are working, by example if the issue number was 123 the subject can be 'foo the bars , #123'
  
.. admonition:: A corollary:

      Please **don't put multiple fixes/features in the same
      branch/pull request**! In other words, if you're hacking on new feature X
      and find a bugfix that doesn't *require* new feature X, **make a new
      distinct branch and PR** for the bugfix.

Details
-------

- You may want to use the `Tim Pope’s Git commit messages standard
  <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.
  It’s not necessary, but if you are doing something big, we recommend
  describing it in the commit message.

- While working, **rebase instead of merging** (if possible).  We encourage
  using ``git rebase`` instead of ``git merge``.  If you are using
  ``git pull``, please run ``git config pull.rebase true`` to prevent merges
  from happening and replace them with rebase goodness.  There is also an
  “emergency switch” in case rebases fail and you do not know what to do:
  ``git pull --no-rebase``.

- **Make sure documentation is updated** — at the very least, keep docstrings
  current, and if necessary, update the reStructuredText documentation in ``docgen/``.

- **Add a changelog entry** at the top of ``CHANGELOG`` mentioning issue number
  and in the correct 'New Features'/'Bugfixes' section.

- **Be PEP8 compliant in new code**

- **Try writing some tests** if possible — again, following existing tests is
  often easiest, and a good way to tell whether the feature you are modifying is
  easily testable.
  
- Make sure to mention the issue it affects in the description of your pull request,
  so it's clear what to test and how to do it.

.. [1] Very inspired by `Nikola's https://github.com/getnikola/nikola/blob/master/CONTRIBUTING.rst`_ thanks!

.. [2] A good article on generating patches: https://ariejan.net/2009/10/26/how-to-create-and-apply-a-patch-with-git/
