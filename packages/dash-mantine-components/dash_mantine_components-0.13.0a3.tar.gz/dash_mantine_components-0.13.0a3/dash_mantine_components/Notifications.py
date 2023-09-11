# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Notifications(Component):
    """A Notifications component.
tine notifications system

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- autoClose (number; optional):
    Auto close timeout for all notifications, False to disable auto
    close, can be overwritten for individual notifications by
    notifications.show function.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- containerWidth (string | number; optional):
    Notification width, cannot exceed 100%.

- data-* (string; optional):
    Wild card data attributes.

- limit (number; optional):
    Maximum amount of notifications displayed at a time, other new
    notifications will be added to queue.

- notificationMaxHeight (string | number; optional):
    Notification max-height, used for transitions.

- position (a value equal to: 'top-left', 'top-right', 'top-center', 'bottom-left', 'bottom-right', 'bottom-center'; optional):
    Notifications position.

- transitionDuration (number; optional):
    Notification transitions duration, 0 to turn transitions off.

- zIndex (number; optional):
    Notifications container z-index."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'Notifications'
    @_explicitize_args
    def __init__(self, position=Component.UNDEFINED, autoClose=Component.UNDEFINED, transitionDuration=Component.UNDEFINED, containerWidth=Component.UNDEFINED, notificationMaxHeight=Component.UNDEFINED, limit=Component.UNDEFINED, zIndex=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'aria-*', 'autoClose', 'className', 'containerWidth', 'data-*', 'limit', 'notificationMaxHeight', 'position', 'transitionDuration', 'zIndex']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'aria-*', 'autoClose', 'className', 'containerWidth', 'data-*', 'limit', 'notificationMaxHeight', 'position', 'transitionDuration', 'zIndex']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Notifications, self).__init__(**args)
