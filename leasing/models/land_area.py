from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField
from safedelete.models import SafeDeleteModel

from leasing.enums import (
    ConstructabilityReportInvestigationState, ConstructabilityState, ConstructabilityType, LeaseAreaType, LocationType,
    PlotType, PollutedLandRentConditionState)
from leasing.models.lease import Lease
from users.models import User

from .mixins import NameModel, TimeStampedModel, TimeStampedSafeDeleteModel


class Land(TimeStampedModel):
    """Land is an abstract class with common fields for leased land,
    real properties, unseparated parcels, and plan units.

    In Finnish: Maa-alue
    """
    # In Finnish: Tunnus
    identifier = models.CharField(verbose_name=_("Identifier"), max_length=255)

    # In Finnish: Kokonaisala / Pinta-ala
    area = models.PositiveIntegerField(verbose_name=_("Area in square meters"))

    # In Finnish: Leikkausala
    section_area = models.PositiveIntegerField(verbose_name=_("Section area"))

    # In Finnish: Osoite
    address = models.CharField(verbose_name=_("Address"), max_length=255)

    # In Finnish: Postinumero
    postal_code = models.CharField(verbose_name=_("Postal code"), max_length=255)

    # In Finnish: Kaupunki
    city = models.CharField(verbose_name=_("City"), max_length=255)

    class Meta:
        abstract = True


class LeaseArea(Land, SafeDeleteModel):
    """
    In Finnish: Vuokra-alue
    """
    lease = models.ForeignKey(Lease, on_delete=models.PROTECT, related_name='lease_areas')
    type = EnumField(LeaseAreaType, verbose_name=_("Type"), max_length=30)
    # In Finnish: Sijainti (maanpäällinen, maanalainen)
    location = EnumField(LocationType, verbose_name=_("Location"), max_length=30)

    # Constructability fields
    # In Finnish: Rakentamiskelpoisuus

    # In Finnish: Selvitysaste (Esirakentaminen, johtosiirrot ja kunnallistekniikka)
    preconstruction_state = EnumField(ConstructabilityState, verbose_name=_("Preconstruction state"), null=True,
                                      blank=True, max_length=30)

    # In Finnish: Selvitysaste (Purku)
    demolition_state = EnumField(ConstructabilityState, verbose_name=_("Demolition state"), null=True, blank=True,
                                 max_length=30)

    # In Finnish: Selvitysaste (Pilaantunut maa-alue (PIMA))
    polluted_land_state = EnumField(ConstructabilityState, verbose_name=_("Polluted land state"), null=True, blank=True,
                                    max_length=30)

    # In Finnish: Vuokraehdot (kysyminen)
    polluted_land_rent_condition_state = EnumField(PollutedLandRentConditionState,
                                                   verbose_name=_("Polluted land rent condition state"), null=True,
                                                   blank=True, max_length=30)

    # In Finnish: Vuokraehtojen kysymisen päivämäärä
    polluted_land_rent_condition_date = models.DateField(verbose_name=_("Polluted land rent condition date"), null=True,
                                                         blank=True)

    # In Finnish: PIMA valmistelija
    polluted_land_planner = models.ForeignKey(User, verbose_name=_("User"), null=True, blank=True,
                                              on_delete=models.PROTECT)

    # In Finnish: ProjectWise kohdenumero
    polluted_land_projectwise_number = models.CharField(verbose_name=_("ProjectWise number"), null=True, blank=True,
                                                        max_length=255)

    # In Finnish: Matti raportti
    polluted_land_matti_report_number = models.CharField(verbose_name=_("Matti report number"), null=True, blank=True,
                                                         max_length=255)

    # In Finnish: Selvitysaste (Rakennettavuusselvitys)
    constructability_report_state = EnumField(ConstructabilityState, verbose_name=_("Constructability report state"),
                                              null=True, blank=True, max_length=30)

    # In Finnish: Rakennettavuusselvityksen tila
    constructability_report_investigation_state = EnumField(
        ConstructabilityReportInvestigationState, verbose_name=_("Constructability report investigation state"),
        null=True, blank=True, max_length=30)

    # In Finnish: Allekirjoituspäivämäärä
    constructability_report_signing_date = models.DateField(verbose_name=_("Constructability report signing date"),
                                                            null=True, blank=True)

    # In Finnish: Allekirjoittaja
    constructability_report_signer = models.CharField(verbose_name=_("Constructability report signer"), null=True,
                                                      blank=True, max_length=255)

    # In Finnish: Geoteknisen palvelun tiedosto
    constructability_report_geotechnical_number = models.CharField(
        verbose_name=_("Constructability report geotechnical number"), null=True, blank=True, max_length=255)

    # In Finnish: Selvitysaste (Muut)
    other_state = EnumField(ConstructabilityState, verbose_name=_("Other state"), null=True, blank=True, max_length=30)


class ConstructabilityDescription(TimeStampedSafeDeleteModel):
    """
    In Finnish: Selitys (Rakentamiskelpoisuus)
    """
    lease_area = models.ForeignKey(LeaseArea, related_name='constructability_descriptions', on_delete=models.CASCADE)
    type = EnumField(ConstructabilityType, verbose_name=_("Type"), max_length=30)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.PROTECT)
    text = models.TextField(verbose_name=_("Text"))
    # In Finnish: AHJO diaarinumero
    ahjo_reference_number = models.CharField(verbose_name=_("AHJO reference number"), null=True, blank=True,
                                             max_length=255)


class Plot(Land):
    """Information about a piece of land regarding a lease area.

    In Finnish: Tontti, but also possibly Määräala or Kiinteistö depending on the context.
    """
    type = EnumField(PlotType, verbose_name=_("Type"), max_length=30)
    # In Finnish: Rekisteröintipäivä
    registration_date = models.DateField(verbose_name=_("Registration date"), null=True, blank=True)
    lease_area = models.ForeignKey(LeaseArea, related_name='plots', on_delete=models.CASCADE)
    # In Finnish: Sopimushetkellä
    in_contract = models.BooleanField(verbose_name=_("At time of contract"), default=False)


class PlanUnitType(NameModel):
    """
    In Finnish: Kaavayksikön laji
    """


class PlanUnitState(NameModel):
    """
    In Finnish: Kaavayksikön olotila
    """


class PlanUnit(Land):
    """Plan plots are like the atoms of city plans.

    Plan plots are the plan specialization of land areas. While one
    could say that they come before the parcel specializations of land
    areas, they may be planned according to preexisting land areas.
    Plan plots differ from parcels in that they cannot be physically
    owned. Plan plots can be divided (tonttijako).

    In Finnish: Kaavayksikkö
    """
    type = EnumField(PlotType, verbose_name=_("Type"), max_length=30)
    lease_area = models.ForeignKey(LeaseArea, related_name='plan_units', on_delete=models.CASCADE)
    # In Finnish: Sopimushetkellä
    in_contract = models.BooleanField(verbose_name=_("At time of contract"), default=False)

    # In Finnish: Tonttijaon tunnus
    plot_division_identifier = models.CharField(verbose_name=_("Plot division identifier"), max_length=255)

    # In Finnish: Tonttijaon hyväksymispvm
    plot_division_date_of_approval = models.DateField(verbose_name=_("Plot division date of approval"))

    # In Finnish: Asemakaava
    detailed_plan_identifier = models.CharField(verbose_name=_("Detailed plan identifier"), max_length=255)

    # In Finnish: Asemakaavan vahvistumispvm
    detailed_plan_date_of_approval = models.DateField(verbose_name=_("Detailed plan date of approval"))

    # In Finnish: Kaavayksikön laji
    plan_unit_type = models.ForeignKey(PlanUnitType, verbose_name=_("Plan unit type"), on_delete=models.PROTECT)

    # In Finnish: Kaavayksikön olotila
    plan_unit_state = models.ForeignKey(PlanUnitState, verbose_name=_("Plan unit state"), on_delete=models.PROTECT)


auditlog.register(LeaseArea)
auditlog.register(ConstructabilityDescription)
auditlog.register(Plot)
auditlog.register(PlanUnit)
