from __future__ import absolute_import
import rules

@rules.predicate
def is_wordpress_admin(user):
    return user.groups.filter(name='wordpress_admin').exists()


@rules.predicate
def is_wordpress_editor(user):
    return user.groups.filter(name='wordpress_editor').exists()


rules.add_perm('daiquiri_auth.is_wordpress_admin', is_wordpress_admin)
rules.add_perm('daiquiri_auth.is_wordpress_editor', is_wordpress_editor)
rules.add_perm('daiquiri_auth.is_wordpress_staff', is_wordpress_admin | is_wordpress_editor)
