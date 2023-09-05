from .filter_field_renderer import FIELD_RENDERER_MAP


class FilterRenderer:
    """
    A class for rendering and managing filters within a filterset.

    This class is designed to work in conjunction with a `filterset` object from the
    Django `django-filter` package and provides methods for setting up filter renderers,
    organizing filters into positions, and retrieving applied filters and filter fields.

    :param filterset: The filterset from `django-filter` to which this renderer is associated.

    :ivar filters: A dictionary to categorize filters into different positions
                   ('top_left', 'top_right', 'top_body', 'side').
    :ivar filterset: A reference to the associated `filterset` from `django-filter`.
    :ivar renderers: A dictionary that stores filter renderers associated with filter names.
                     The renderers are created during initialization.
    """

    def __init__(self, filterset):
        """
        Initialize a new FilterRenderer instance for the given `filterset`.

        :param filterset: The filterset from `django-filter` to which this renderer is associated.
        """
        self.filters = {
            "top_left": [],
            "top_right": [],
            "top_body": [],
            "side": []
        }
        self.filterset = filterset
        self.renderers = {}

    def get(self, *args, **kwargs):
        """
        Set up filter renderers for the associated `filterset`.

        This method iterates over the filters defined in the associated `filterset` and
        attempts to create a filter renderer for each filter field. It uses the
        `get_filter_renderer_field` method to retrieve the appropriate renderer for
        each filter field type.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The FilterRenderer instance.
        """
        for name, filter_field in self.filterset.filters.items():
            value = self.filterset.form.data.get('name', None)
            renderer = self.get_filter_renderer_field(filter_field)
            try:
                filter_renderer = renderer(
                    filter_field=filter_field,
                    form_field=self.filterset.form[name],
                    value=value,
                    filter_type=self.filterset.filterset_types.get(name) if self.filterset.filterset_types.get(name,
                                                                                                               None) else 'filter',
                )
                self.renderers[name] = filter_renderer
            except Exception as e:
                raise Exception("No Renderer Implemented for: \"{}\"".format(type(filter_field)))
        return self

    def as_applied_filters(self):
        """
        Get a list of applied filters.

        This method iterates through the filter renderers stored in `self.renderers`
        and checks if each filter has been applied. If a filter is applied, it retrieves
        the applied filter(s) and returns them as a list.

        :return: A list of applied filters.
        """
        applied_filters = []
        for name, renderer in self.renderers.items():
            if renderer.is_applied():
                for applied_filter in renderer.get_applied_filter():
                    applied_filters.append(applied_filter)
        return applied_filters

    def as_fields(self):
        """
        Organize filter fields into different positions.

        This method organizes the filter fields into different positions
        ('top_left', 'top_right', 'top_body', 'side') based on the filter's name and
        visibility. It iterates through the filter renderers and appends the filter's
        representation to the corresponding position in the `self.filters` dictionary.

        :return: A dictionary categorizing filter fields by position.
        """
        for name, renderer in self.renderers.items():
            if not renderer.is_hidden() or name in self.filterset.force_visibility:
                position = self.get_position(name)
                self.filters[position].append(renderer.get())
        return self.filters

    def get_filter_renderer_field(self, filter_field):
        """
        Get the filter renderer class for a given filter field type.

        This method is a utility method that returns the appropriate renderer class
        for a given filter field based on its type. It uses the `FIELD_RENDERER_MAP`
        dictionary to map filter field types to renderer classes.

        :param filter_field: The filter field for which to retrieve the renderer.
        :return: The filter renderer class.
        """
        return FIELD_RENDERER_MAP.get(type(filter_field))

    def get_position(self, name):
        """
        Determine the position of a filter based on its name.

        This method checks the `self.filterset.fields_map` dictionary to find the
        position associated with the filter's name. If the name is not found in the
        `fields_map`, it defaults to the "side" position.

        :param name: The name of the filter.
        :return: The position of the filter ('top_left', 'top_right', 'top_body', or 'side').
        """
        for position, fields in self.filterset.fields_map.items():
            if name in fields:
                return position
        return "side"
