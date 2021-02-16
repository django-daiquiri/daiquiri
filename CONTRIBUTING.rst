Contributing to Daiquiri
========================

You are welcome to contribute to Daiquiri by improving and changing it! However, we want to provide a stable software for the community and therefore ask you to follow the following work flow:

* If you found a bug or want a feature to be added, look at the existing issues first. If you find a corresponding issue, please comment on it. If no issue matches, create one.
* If you decide to work on the issue yourself, please wait until you received some feedback by us. Maybe we are already working on it (and forgot to comment on the issue), or we have other plans for the affected code. After all, we are still in an early stage of development, and we don't want you to work for nothing.
* Please work in a fork (do not forget `git remote add upstream https://github.com/django-daiquiri/daiquiri`) of our repository and in new branch named according to what you want to do (e.g. ``fix_login_form`` or ``fancy_feature``). Please create this branch from ``dev``, not from ``master``.
* Please use the `coding standards from the Django project <https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/>`_ and try to follow our conventions as close as possible.
* Afterwards, check if your branch is still up to date. If yes, merge your branch into the ``dev`` branch of your fork. If not perform a rebase first.
* Create a new pull request and the project team will review your pull request.

Maintaining Daiquiri
====================

If you are a maintainer and you want to review a Pull-Request please follow the following instructions:
* Identify the PR you want to review with the following command: `git ls-remote --refs origin`
* Fetch the PR in your local-repository with: `git fetch origin pull/<PR-ID>/head:pr/<PR-ID> && git checkout pr/<PR-ID>`
* Perform the unit-tests of daiquiri
* Perform the instance-tests on the test-instance (dq-dev + test-app)
* Perform the instance-tests on the conserned services (dq-dev + service-app)
* Report any failure to the author of the pull-request

