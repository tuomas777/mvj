from django.utils.encoding import force_text
from rest_framework.fields import DecimalField
from rest_framework.metadata import SimpleMetadata


class FieldsMetadata(SimpleMetadata):
    """Returns metadata for all the fields and the possible choices in the
    serializer even when the fields are read only.

    Additionally adds decimal_places and max_digits info for DecimalFields."""

    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)

        serializer = view.get_serializer()
        metadata["fields"] = self.get_serializer_info(serializer)

        return metadata

    def get_field_info(self, field):
        field_info = super().get_field_info(field)

        if isinstance(field, DecimalField):
            field_info['decimal_places'] = field.decimal_places
            field_info['max_digits'] = field.max_digits

        if hasattr(field, 'choices'):
            field_info['choices'] = [{
                'value': choice_value,
                'display_name': force_text(choice_name, strings_only=True)
            } for choice_value, choice_name in field.choices.items()]

        return field_info
