from zope.interface import Interface

###############################################################################
# Application Node markers
###############################################################################

class IUgm(Interface):
    """Marker for UGM root application model node.
    """

class ISettings(Interface):
    """Marker for settings model node.
    """

class IUsers(Interface):
    """Marker for users model node.
    """

class IUser(Interface):
    """Marker for user model node.
    """

class IGroups(Interface):
    """Marker for groups model node.
    """

class IGroup(Interface):
    """Marker for group model node.
    """