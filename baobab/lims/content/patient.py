from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IPatient
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode


PatientID = StringField(
        'PatientID',
        required=1,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Patient ID"),
            description=_("The unique ID code assigned to the patient."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

# SelectedProject = ReferenceField(
#         'SelectedProject',
#         allowed_types=('Project'),
#         relationship='PatientProjects',
#         widget=bika_ReferenceWidget(
#             label=_("Select Projects"),
#             description=_("Select projects for patient"),
#             size=40,
#             visible={'edit': 'visible', 'view': 'visible'},
#             catalog_name='bika_catalog',
#             showOn=True
#         )
#     )

SelectedProject = ReferenceField(
    'SelectedProject',
    # required=True,
    allowed_types=('Project',),
    relationship='PatientProjects',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Project"),
        # catalog_name='bika_catalog',
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        render_own_label=True,
        description=_("Select the project of the sample."),
    )
)

InfoLink = StringField(
        'InfoLink',
        required=0,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Information Link"),
            description=_("The link to information for this patient."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

Sex = StringField(
        'Sex',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getSexes',
        widget=SelectionWidget(
            format='select',
            label=_("Sex"),
            description=_("Select the sex of the patient"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )

Age = FixedPointField(
        'Age',
        required=0,
        default="0.00",
        widget=DecimalWidget(
            label=_("Age"),
            size=15,
            description=_("The age of the patient."),
            visible={'edit': 'visible', 'view': 'visible'}
        )
    )

AgeUnit = StringField(
        'AgeUnit',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getAgeUnits',
        widget=SelectionWidget(
            format='select',
            label=_("Age Unit"),
            description=_("Whether the age is in years, months, weeks, days etc"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )


schema = BikaSchema.copy() + Schema((
    PatientID,
    SelectedProject,
    InfoLink,
    Sex,
    Age,
    AgeUnit
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class Patient(BaseContent):
    security = ClassSecurityInfo()
    implements(IPatient, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('PatientID').get(self)).encode('utf-8')

    def Description(self):
        return "Gender %s : Age %s %s" % (self.getSex(), self.getAge(), self.getAgeUnit())

    def getSexes(self):
        return ['Male', 'Female', 'Unknown', 'Undifferentiated']

    def getAgeUnits(self):
        return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

registerType(Patient, config.PROJECTNAME)