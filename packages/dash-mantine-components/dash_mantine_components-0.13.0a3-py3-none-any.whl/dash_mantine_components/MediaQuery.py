# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MediaQuery(Component):
    """A MediaQuery component.
ly styles to children if media query matches

Keyword arguments:

- children (a list of or a singular dash component, string or number; required):
    Child that should be shown at given breakpoint, it must accept
    className prop.

- boxWrapperProps (dict; optional):
    props to wrapper box component.

    `boxWrapperProps` is a dict with keys:

    - aria-* (string; optional):
        Wild card aria attributes.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - data-* (string; optional):
        Wild card data attributes.

    - id (string; optional):
        Unique ID to identify this component in Dash callbacks.

    - setProps (required):
        Update props to trigger callbacks.

    - style (boolean

      Or number | string | dict | list; optional):
        Inline style. | dict with keys:

    - bg (string; optional):
        background.

    - bga (a value equal to: 'initial', 'inherit', 'scroll', 'fixed', 'local'; optional):
        backgroundAttachment.

    - bgp (string | number; optional):
        backgroundPosition.

    - bgr (a value equal to: 'initial', 'inherit', 'repeat', 'repeat-x', 'repeat-y', 'no-repeat'; optional):
        backgroundRepeat.

    - bgsz (string | number; optional):
        backgroundSize.

    - bottom (string | number; optional):
        bottom.

    - c (string; optional):
        color.

    - display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
        display.

    - ff (string; optional):
        fontFamily.

    - fs (a value equal to: 'initial', 'inherit', 'normal', 'italic', 'oblique'; optional):
        fontStyle.

    - fw (number; optional):
        fontWeight.

    - fz (string | number; optional):
        fontSize.

    - h (string | number; optional):
        height.

    - inset (string | number; optional):
        inset.

    - left (string | number; optional):
        left.

    - lh (string | number; optional):
        lineHeight.

    - lts (string | number; optional):
        letterSpacing.

    - m (string | number; optional):
        margin.

    - mah (string | number; optional):
        minHeight.

    - maw (string | number; optional):
        maxWidth.

    - mb (string | number; optional):
        marginBottom.

    - mih (string | number; optional):
        minHeight.

    - miw (string | number; optional):
        minWidth.

    - ml (string | number; optional):
        marginLeft.

    - mr (string | number; optional):
        marginRight.

    - mt (string | number; optional):
        marginTop.

    - mx (string | number; optional):
        marginRight, marginLeft.

    - my (string | number; optional):
        marginTop, marginBottom.

    - opacity (number; optional):
        opacity.

    - p (string | number; optional):
        padding.

    - pb (string | number; optional):
        paddingBottom.

    - pl (string | number; optional):
        paddingLeft.

    - pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
        position.

    - pr (string | number; optional):
        paddingRight.

    - pt (string | number; optional):
        paddingTop.

    - px (string | number; optional):
        paddingRight, paddingLeft.

    - py (string | number; optional):
        paddingTop, paddingBottom.

    - right (string | number; optional):
        right.

    - ta (a value equal to: 'initial', 'inherit', 'left', 'right', 'center', 'justify'; optional):
        textAlign.

    - td (a value equal to: 'initial', 'inherit', 'none', 'underline', 'overline', 'line-through'; optional):
        textDecoration.

    - top (string | number; optional):
        top.

    - tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
        textTransform.

    - w (string | number; optional):
        width. | dict with keys:

    - classNames (dict; optional):
        Adds class names to Mantine components.

    - styles (boolean | number | string | dict | list; optional):
        Mantine styles API.

    - sx (boolean | number | string | dict | list; optional):
        With sx you can add styles to component root element. If you
        need to customize styles of other elements within component
        use styles prop.

    - unstyled (boolean; optional):
        Remove all Mantine styling from the component.

- largerThan (string | number; optional):
    Styles applied to child when viewport is larger than given
    breakpoint.

- query (string; optional):
    Any other media query.

- smallerThan (string | number; optional):
    Styles applied to child when viewport is smaller than given
    breakpoint.

- styles (dict; required):
    Styles applied to child when breakpoint matches.

    `styles` is a dict with keys:
"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'MediaQuery'
    @_explicitize_args
    def __init__(self, children=None, smallerThan=Component.UNDEFINED, largerThan=Component.UNDEFINED, query=Component.UNDEFINED, styles=Component.REQUIRED, boxWrapperProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'boxWrapperProps', 'largerThan', 'query', 'smallerThan', 'styles']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'boxWrapperProps', 'largerThan', 'query', 'smallerThan', 'styles']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['styles']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        if 'children' not in _explicit_args:
            raise TypeError('Required argument children was not specified.')

        super(MediaQuery, self).__init__(children=children, **args)
