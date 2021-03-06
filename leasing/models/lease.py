from auditlog.registry import auditlog
from django.db import models, transaction
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField

from leasing.enums import Classification, LeaseRelationType, LeaseState, NoticePeriodType
from leasing.models import Contact
from leasing.models.mixins import NameModel, TimeStampedModel, TimeStampedSafeDeleteModel


class LeaseType(NameModel):
    """
    In Finnish: Laji
    """
    id = models.CharField(verbose_name=_("Identifier"), max_length=255, primary_key=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)


class Municipality(NameModel):
    """
    In Finnish: Kaupunki
    """

    class Meta:
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'
        ordering = ['id']


class District(NameModel):
    """
    In Finnish: Kaupunginosa
    """
    municipality = models.ForeignKey(Municipality, verbose_name=_("Municipality"), related_name='districts',
                                     on_delete=models.PROTECT)
    identifier = models.IntegerField(verbose_name=_('Identifier within the municipality'))

    class Meta:
        unique_together = ('municipality', 'identifier')
        ordering = ('municipality__name', 'name')


class IntendedUse(NameModel):
    """
    In Finnish: Käyttötarkoitus
    """


class StatisticalUse(NameModel):
    """
    In Finnish: Tilastollinen pääkäyttötarkoitus
    """


class SupportiveHousing(NameModel):
    """
    In Finnish: Erityisasunnot
    """


class Financing(NameModel):
    """
    In Finnish: Rahoitusmuoto
    """
    id = models.CharField(verbose_name=_("Identifier"), max_length=255, primary_key=True)

    class Meta:
        verbose_name = 'Form of financing'
        verbose_name_plural = 'Forms of financing'
        ordering = ['name']


class Management(NameModel):
    """
    In Finnish: Hallintamuoto
    """
    id = models.CharField(verbose_name=_("Identifier"), max_length=255, primary_key=True)

    class Meta:
        verbose_name = 'Form of management'
        verbose_name_plural = 'Forms of management'
        ordering = ['name']


class Regulation(NameModel):
    """
    In Finnish: Sääntelymuoto
    """

    class Meta:
        verbose_name = 'Form of regulation'
        verbose_name_plural = 'Forms of regulation'
        ordering = ['name']


class Hitas(NameModel):
    """
    In Finnish: Hitas
    """
    id = models.CharField(verbose_name=_("Identifier"), max_length=255, primary_key=True)

    class Meta:
        verbose_name = 'Hitas'
        verbose_name_plural = 'Hitas'
        ordering = ['name']


class NoticePeriod(NameModel):
    """
    In Finnish: Irtisanomisaika
    """
    type = EnumField(NoticePeriodType, verbose_name=_("Period type"), max_length=30)
    duration = models.CharField(verbose_name=_("Duration"), null=True, blank=True, max_length=255,
                                help_text=_("In ISO 8601 Duration format"))


class LeaseIdentifier(TimeStampedSafeDeleteModel):
    """
    In Finnish: Vuokraustunnus
    """
    # In Finnish: Laji
    type = models.ForeignKey(LeaseType, verbose_name=_("Lease type"), on_delete=models.PROTECT)

    # In Finnish: Kaupunki
    municipality = models.ForeignKey(Municipality, verbose_name=_("Municipality"), on_delete=models.PROTECT)

    # In Finnish: Kaupunginosa
    district = models.ForeignKey(District, verbose_name=_("District"), on_delete=models.PROTECT)

    # In Finnish: Juokseva numero
    sequence = models.PositiveIntegerField(verbose_name=_("Sequence number"))

    class Meta:
        unique_together = ('type', 'municipality', 'district', 'sequence')

    def __str__(self):
        """Returns the lease identifier as a string

        The lease identifier is constructed out of type, municipality,
        district, and sequence, in that order. For example, the identifier
        for a residence (A1) in Helsinki (1), Vallila (22), and sequence
        number 1 would be A1122-1.
        """
        return '{}{}{:02}-{}'.format(self.type.id, self.municipality.id, self.district.identifier, self.sequence)


class Lease(TimeStampedSafeDeleteModel):
    """
    In Finnish: Vuokraus
    """
    # Identifier fields
    # In Finnish: Laji
    type = models.ForeignKey(LeaseType, verbose_name=_("Lease type"), on_delete=models.PROTECT)

    # In Finnish: Kaupunki
    municipality = models.ForeignKey(Municipality, verbose_name=_("Municipality"), on_delete=models.PROTECT)

    # In Finnish: Kaupunginosa
    district = models.ForeignKey(District, verbose_name=_("District"), on_delete=models.PROTECT)

    # In Finnish: Vuokratunnus
    identifier = models.OneToOneField(LeaseIdentifier, verbose_name=_("Lease identifier"), null=True, blank=True,
                                      on_delete=models.PROTECT)

    # Other fields
    # In Finnish: Alkupäivämäärä
    start_date = models.DateField(verbose_name=_("Start date"), null=True, blank=True)

    # In Finnish: Loppupäivämäärä
    end_date = models.DateField(verbose_name=_("End date"), null=True, blank=True)

    # In Finnish: Tila
    state = EnumField(LeaseState, verbose_name=_("State"), null=True, blank=True, max_length=30)

    # In Finnish: Julkisuusluokka
    classification = EnumField(Classification, verbose_name=_("Classification"), null=True, blank=True, max_length=30)

    # In Finnish: Käyttötarkoituksen selite
    intended_use_note = models.TextField(verbose_name=_("Intended use note"), null=True, blank=True)

    # In Finnish: Siirto-oikeus
    transferable = models.BooleanField(verbose_name=_("Transferable"), default=True)

    # In Finnish: Säännelty
    regulated = models.BooleanField(verbose_name=_("Regulated"), default=False)

    # In Finnish: Irtisanomisilmoituksen selite
    notice_note = models.TextField(verbose_name=_("Notice note"), null=True, blank=True)

    # Relations
    # In Finnish: Vuokranantaja
    lessor = models.ForeignKey(Contact, verbose_name=_("Lessor"), null=True, blank=True, on_delete=models.PROTECT)

    # In Finnish: Käyttötarkoitus
    intended_use = models.ForeignKey(IntendedUse, verbose_name=_("Intended use"), null=True, blank=True,
                                     on_delete=models.PROTECT)

    # In Finnish: Erityisasunnot
    supportive_housing = models.ForeignKey(SupportiveHousing, verbose_name=_("Supportive housing"), null=True,
                                           blank=True, on_delete=models.PROTECT)

    # In Finnish: Tilastollinen pääkäyttötarkoitus
    statistical_use = models.ForeignKey(StatisticalUse, verbose_name=_("Statistical use"), null=True, blank=True,
                                        on_delete=models.PROTECT)

    # In Finnish: Rahoitusmuoto
    financing = models.ForeignKey(Financing, verbose_name=_("Form of financing"), null=True, blank=True,
                                  on_delete=models.PROTECT)

    # In Finnish: Hallintamuoto
    management = models.ForeignKey(Management, verbose_name=_("Form of management"), null=True, blank=True,
                                   on_delete=models.PROTECT)

    # In Finnish: Sääntelymuoto
    regulation = models.ForeignKey(Regulation, verbose_name=_("Form of regulation"), null=True, blank=True,
                                   on_delete=models.PROTECT)
    # In Finnish: Hitas
    hitas = models.ForeignKey(Hitas, verbose_name=_("Hitas"), null=True, blank=True, on_delete=models.PROTECT)

    # In Finnish: Irtisanomisaika
    notice_period = models.ForeignKey(NoticePeriod, verbose_name=_("Notice period"), null=True, blank=True,
                                      on_delete=models.PROTECT)

    related_leases = models.ManyToManyField('self', through='leasing.RelatedLease', symmetrical=False,
                                            related_name='related_to')

    def __str__(self):
        return self.get_identifier_string()

    def get_identifier_string(self):
        if self.identifier:
            return str(self.identifier)
        else:
            return '{}{}{:02}-'.format(self.type.id, self.municipality.id, self.district.identifier)

    @transaction.atomic
    def create_identifier(self):
        if self.identifier_id:
            return

        if not self.type or not self.municipality or not self.district:
            return

        max_sequence = LeaseIdentifier.objects.filter(
            type=self.type,
            municipality=self.municipality,
            district=self.district).aggregate(Max('sequence'))['sequence__max']

        if not max_sequence:
            max_sequence = 0

        lease_identifier = LeaseIdentifier.objects.create(
            type=self.type,
            municipality=self.municipality,
            district=self.district,
            sequence=max_sequence + 1)

        self.identifier = lease_identifier

    def save(self, *args, **kwargs):
        self.create_identifier()

        super().save(*args, **kwargs)


class LeaseStateLog(TimeStampedModel):
    lease = models.ForeignKey(Lease, verbose_name=_("Lease"), on_delete=models.PROTECT)
    state = EnumField(LeaseState, verbose_name=_("State"), max_length=30)


class RelatedLease(TimeStampedSafeDeleteModel):
    from_lease = models.ForeignKey(Lease, verbose_name=_("From lease"), related_name='from_leases',
                                   on_delete=models.PROTECT)
    to_lease = models.ForeignKey(Lease, verbose_name=_("To lease"), related_name='to_leases', on_delete=models.PROTECT)
    type = EnumField(LeaseRelationType, verbose_name=_("Lease relation type"), max_length=30)
    start_date = models.DateField(verbose_name=_("Start date"), null=True, blank=True)
    end_date = models.DateField(verbose_name=_("End date"), null=True, blank=True)


auditlog.register(Lease)
auditlog.register(RelatedLease)
