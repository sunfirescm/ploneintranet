# -*- coding: utf-8 -*-
from plone import api
from zExceptions import BadRequest
import logging

log = logging.getLogger(__name__)

# These add-ons will be uninstalled. They are either dependencies
# of ploneintranet.suite that are not from the ploneintranet-namespace
# or are dependencies of dependencies of ploneintranet.suite that make little
# or no sense out side its context
ADDITIONAL_DEPENDENCIES = [
    'collective.mustread',
    'collective.workspace',
    'collective.documentviewer',
    'slc.mailrouter'
]


def uninstall(context):
    """Run when installing the uninstall-profile.
    """
    portal = api.portal.get()
    uninstall_dependencies(portal)


def uninstall_dependencies(portal):
    # Uninstall dependencies of ploneintranet from the
    # ploneinstranet-namespace plus some additional add-ons.
    # We do not check if the product is installed since it may be
    # INonInstallable
    qi = api.portal.get_tool('portal_quickinstaller')
    install_profile = qi.getInstallProfile('ploneintranet.suite')
    dependencies = install_profile.get('dependencies', ())
    dependencies = list(dependencies)
    dependencies.extend(ADDITIONAL_DEPENDENCIES)
    for dependency in dependencies:
        dependency = str(dependency.split('profile-')[-1].split(':')[0])
        if dependency.startswith('ploneintranet.') or \
           dependency.startswith('quaive.') or \
           dependency in ADDITIONAL_DEPENDENCIES:
            try:
                qi.uninstallProducts([dependency])
                log.info('Uninstalled dependency "%s"' % dependency)
            except (AttributeError, BadRequest):
                pass
