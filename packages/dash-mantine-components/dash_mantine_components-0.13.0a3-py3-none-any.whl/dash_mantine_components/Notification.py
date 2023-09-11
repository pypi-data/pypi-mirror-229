# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Notification(Component):
    """A Notification component.
w dynamic notifications and alerts to user, part of notifications system

Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks.

- action (a value equal to: 'show', 'update', 'hide'; required):
    Action.

- aria-* (string; optional):
    Wild card aria attributes.

- autoClose (number; optional):
    Auto close timeout in milliseconds, False to disable auto close.

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

- className (string; optional):
    Often used with CSS to style elements with common properties.

- classNames (dict; optional):
    Adds class names to Mantine components.

- closeButtonProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to close button.

- color (string; optional):
    Notification line or icon color.

- data-* (string; optional):
    Wild card data attributes.

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

- icon (a list of or a singular dash component, string or number; optional):
    Notification icon, replaces color line.

- inset (string | number; optional):
    inset.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- loading (boolean; optional):
    Replaces colored line or icon with Loader component.

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

- message (a list of or a singular dash component, string or number; required):
    Notification body, place main text here.

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

- radius (string; optional):
    Radius from theme.radius, or number to set border-radius in px.

- right (string | number; optional):
    right.

- style (boolean | number | string | dict | list; optional):
    Inline style.

- styles (boolean | number | string | dict | list; optional):
    Mantine styles API.

- sx (boolean | number | string | dict | list; optional):
    With sx you can add styles to component root element. If you need
    to customize styles of other elements within component use styles
    prop.

- ta (a value equal to: 'initial', 'inherit', 'left', 'right', 'center', 'justify'; optional):
    textAlign.

- td (a value equal to: 'initial', 'inherit', 'none', 'underline', 'overline', 'line-through'; optional):
    textDecoration.

- title (a list of or a singular dash component, string or number; optional):
    Notification title, displayed before body.

- top (string | number; optional):
    top.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- w (string | number; optional):
    width.

- withBorder (boolean; optional):
    Adds border styles.

- withCloseButton (boolean; optional):
    Determines whether close button should be visible, True by
    default."""
    _children_props = ['icon', 'title', 'message']
    _base_nodes = ['icon', 'title', 'message', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'Notification'
    @_explicitize_args
    def __init__(self, color=Component.UNDEFINED, radius=Component.UNDEFINED, icon=Component.UNDEFINED, title=Component.UNDEFINED, message=Component.REQUIRED, loading=Component.UNDEFINED, withBorder=Component.UNDEFINED, withCloseButton=Component.UNDEFINED, closeButtonProps=Component.UNDEFINED, id=Component.REQUIRED, autoClose=Component.UNDEFINED, action=Component.REQUIRED, className=Component.UNDEFINED, style=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'action', 'aria-*', 'autoClose', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeButtonProps', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'icon', 'inset', 'left', 'lh', 'loading', 'lts', 'm', 'mah', 'maw', 'mb', 'message', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'title', 'top', 'tt', 'unstyled', 'w', 'withBorder', 'withCloseButton']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'action', 'aria-*', 'autoClose', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeButtonProps', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'icon', 'inset', 'left', 'lh', 'loading', 'lts', 'm', 'mah', 'maw', 'mb', 'message', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'title', 'top', 'tt', 'unstyled', 'w', 'withBorder', 'withCloseButton']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id', 'action', 'message']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Notification, self).__init__(**args)
