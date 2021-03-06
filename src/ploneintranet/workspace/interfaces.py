# coding=utf-8
from plone.app.contenttypes.interfaces import IFolder
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout import interfaces as ilayout
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface


class IPloneintranetWorkspaceLayer(Interface):
    """Zope 3 browser layer which is active regardless of themeswitching"""


class IThemedWorkspaceLayer(IPloneintranetWorkspaceLayer):
    """Zope 3 browser layer which is *not* present in Barceloneta fallback"""


class IWorkspaceAppContentLayer(ilayout.IPloneintranetContentLayer,
                                ilayout.IAppLayer):
    """Marker interface for content within a workspace app."""


class IWorkspaceAppFormLayer(ilayout.IPloneintranetFormLayer,
                             ilayout.IAppLayer):
    """Marker interface for forms within a workspace app."""


class IParticipationPolicyChangedEvent(Interface):
    """ Event, which is fired once the participation policy
    of the workspace has changed
    """
    old_policy = Attribute(u"Policy we are moving away from")
    new_policy = Attribute(u"Policy we are moving to")


class IWorkspaceRosterChangedEvent(Interface):
    """
    Event, which is fired once the roster of a workspace had changed
    """


class IWorkspaceState(Interface):
    """A view that gives access to the containing workspace
    """

    def workspace():
        """
        The workspace
        """

    def state():
        """
        The state of the workspace
        """


class IBaseWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    Interface for WorkspaceFolder
    """
    calendar_visible = schema.Bool(
        title=_(
            u"label_workspace_calendar_visibility",
            u"Calendar visible in central calendar"),
        required=False,
        default=False,
    )
    division = schema.TextLine(
        title=_(u'label_workspace_division', u'Belongs to this Division'),
        required=False,
        default=u'',
    )
    email = schema.TextLine(
        title=_(u'label_workspace_email', u'E-mail address'),
        required=False,
        default=u'',
    )
    archival_date = schema.Datetime(
        title=_('label_archived', u'Archived'),
        required=False,
        default=None,
    )
    related_workspaces = schema.List(
        value_type=schema.ASCIILine(
            title=_(u'label_workspace_uid', u'UID of a workspace'),
            required=False,
            default=''),
        title=_(u'label_related_workspaces', u'Related workspaces'),
        required=False,
        default=[]
    )
    hero_image = NamedBlobImage(
        title=_(u"Hero Image"),
        required=False
    )
    event_global_default = schema.Bool(
        title=_(u'label_event_global_default', u'Global Events by default?'),
        required=False,
        default=False,
    )


class IWorkspaceFolder(IBaseWorkspaceFolder):
    ''' A workspace folder can be a division,
    while other objects inheriting from IBaseWorkspaceFolder cannot,
    e.g. cases
    '''
    is_division = schema.Bool(
        title=_(
            u"label_workspace_is_division",
            u"Is this workspace representing a division?"),
        description=_(
            u"Divisions represent sections of the overall "
            u"organisation and appear "
            u"as groupings on the workspace overview."),
        required=False,
        default=False,
    )


class IMetroMap(Interface):
    """Methods required to display a metromap
    """

    def metromap_sequence():
        """An ordered dict with the structure required for displaying tasks in
        the metromap and in the sidebar of a Case item. This is used to
        determine which states have been finished, and
        which transitions are currently available.
        OrderedDict([(
            "new", {
                "is_current": False,
                "transition_id": "transfer_to_department",
                "finished": True,
            }), (
            "in_progress", {
                "is_current": False,
                "transition_id": "transfer_to_department",
                "finished": True,
            }),
        ])
        """


class IGroupingStoragable(Interface):
    """marker interface for things that can have a GroupingStorage
    """


class IGroupingStorage(Interface):

    def update_groupings(obj):
        """ Update the groupings dict with the values stored on obj.
        """

    def remove_from_groupings(obj):
        """ Remove obj's grouping relevant information to its workspace.
        """

    def reset_order():
        """ Reset the order for all groupings to default, i.e. same order
            as the keys of the OOBTree
        """

    def get_order_for(grouping,
                      include_archived=False,
                      alphabetical=False):
        """ Get order for a given grouping
        """

    def set_order_for(grouping, order):
        """ Set order for a given grouping
        """

    def get_groupings():
        """ Return groupings
        """


class IMail(IFolder):
    ''' Marker interface for the ploneintranet.workspace.mail content type
    '''
