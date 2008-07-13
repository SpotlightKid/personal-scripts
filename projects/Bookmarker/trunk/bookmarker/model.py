__all__ = [
    'hub',
    'Bookmark',
    'Tag',
    'User',
    'Group',
    'Permission',
    'VisitIdentity'
]

from datetime import datetime

from sqlobject import *

from turbogears import identity
from turbogears.database import PackageHub

hub = PackageHub("bookmarker")
__connection__ = hub

class Bookmark(SQLObject):
    """A bookmark for a URL.

    Bookmarks have a title, a description and a URL plus some meta data.
    """

    class sqlmeta:
        defaultOrder = '-created'

    title = UnicodeCol(length=255, notNull=True, title='Bookmark title')
    url = UnicodeCol(length=255, notNull=True)
    description = UnicodeCol()

    tags = RelatedJoin('Tag', orderBy='name')

    # meta data
    created = DateTimeCol(default=datetime.now)
    owner = ForeignKey('User', notNull=True)

    def update_tags(self, taglist):
        """Update attached tags from taglist given as comma-separated string."""

        oldtags = set(self.tags)
        newtags = []

        for taglabel in taglist:
            if not taglabel:
                continue
            tagname = taglabel.lower()
            try:
                tag = Tag.select(
                  AND(Tag.q.name == tagname, Tag.q.ownerID == self.owner.id)
                )[0]
            except (SQLObjectNotFound, IndexError):
                tag = Tag(name=tagname, label=taglabel, owner=self.owner)
            if tag not in oldtags:
                self.addTag(tag)
            newtags.append(tag)
        for tag in oldtags.difference(newtags):
            self.removeTag(tag)

    def __str__(self):
        return self.title


class Tag(SQLObject):
    """A tag (category) for a bookmark.

    Bookmarks can have unlimited tags.
    """

    class sqlmeta:
        defaultOrder = 'name'

    # name will be normalized (lower case, replace certain characters, etc.)
    name = UnicodeCol(length=100, notNull=True)
    # label can contain any characters
    label = UnicodeCol(length=100, notNull=True)
    bookmarks = RelatedJoin('Bookmark', orderBy='-created')

    # meta data
    owner = ForeignKey('User', notNull=True)
    created = DateTimeCol(default=datetime.now)

    def __str__(self):
        return self.label

# Identity classes

class Visit(SQLObject):
    class sqlmeta:
        table = "visit"

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    created = DateTimeCol(default=datetime.now)
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(SQLObject):
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    user_id = IntCol()


class Group(SQLObject):
    """
    An ultra-simple group definition.
    """

    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_group"

    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin("User", intermediateTable="user_group",
                        joinColumn="group_id", otherColumn="user_id")

    # collection of all permissions for this group
    permissions = RelatedJoin("Permission", joinColumn="group_id",
                              intermediateTable="group_permission",
                              otherColumn="permission_id")

    def __str__(self):
        return "%s (%s)" % (self.group_name, self.display_name)


class User(SQLObject):
    """
    Reasonably basic User definition. Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_user"

    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)

    # groups this user belongs to
    groups = RelatedJoin("Group", intermediateTable="user_group",
                         joinColumn="user_id", otherColumn="group_id")

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)

    def set_password_raw(self, password):
        "Saves the password as-is to the database."
        self._SO_set_password(password)

    def __str__(self):
        return "%s (%s)" % (self.user_name, self.display_name)

class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)

    groups = RelatedJoin("Group",
                        intermediateTable="group_permission",
                         joinColumn="permission_id",
                         otherColumn="group_id")
