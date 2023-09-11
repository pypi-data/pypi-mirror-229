# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tooltip(Component):
    """A Tooltip component.
ders tooltip at given element on mouse over or any other event

Keyword arguments:

- children (a list of or a singular dash component, string or number; required):
    Target element.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- arrowOffset (number; optional):
    Arrow offset.

- arrowPosition (a value equal to: 'center', 'side'; optional):
    Arrow position *.

- arrowRadius (number; optional):
    Arrow radius.

- arrowSize (number; optional):
    Arrow size.

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

- closeDelay (number; optional):
    Close delay in ms.

- color (string; optional):
    Key of theme.colors.

- data-* (string; optional):
    Wild card data attributes.

- disabled (boolean; optional):
    Disables tooltip.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- events (dict; optional):
    Determines which events will be used to show tooltip.

    `events` is a dict with keys:

    - focus (boolean; required)

    - hover (boolean; required)

    - touch (boolean; required)

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

- inline (boolean; optional):
    Set if tooltip is attached to an inline element.

- inset (string | number; optional):
    inset.

- keepMounted (boolean; optional):
    If set tooltip will not be unmounted from the DOM when it is
    hidden, display: none styles will be added instead.

- label (a list of or a singular dash component, string or number; required):
    Tooltip label.

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

- multiline (boolean; optional):
    Defines whether content should be wrapped on to the next line.

- mx (string | number; optional):
    marginRight, marginLeft.

- my (string | number; optional):
    marginTop, marginBottom.

- offset (number; optional):
    Space between target element and tooltip.

- opacity (number; optional):
    opacity.

- openDelay (number; optional):
    Open delay in ms.

- opened (boolean; optional):
    Controls opened state.

- p (string | number; optional):
    padding.

- pb (string | number; optional):
    paddingBottom.

- pl (string | number; optional):
    paddingLeft.

- pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
    position.

- position (a value equal to: 'top', 'right', 'bottom', 'left', 'top-end', 'top-start', 'right-end', 'right-start', 'bottom-end', 'bottom-start', 'left-end', 'left-start'; optional):
    Tooltip position relative to target element (default) or mouse
    (floating).

- positionDependencies (list of boolean | number | string | dict | lists; optional):
    useEffect dependencies to force update tooltip position.

- pr (string | number; optional):
    paddingRight.

- pt (string | number; optional):
    paddingTop.

- px (string | number; optional):
    paddingRight, paddingLeft.

- py (string | number; optional):
    paddingTop, paddingBottom.

- radius (string | number; optional):
    Key of theme.radius or any valid CSS value to set border-radius,
    theme.defaultRadius by default.

- refProp (string; optional):
    Key of the prop that should be used to get element ref.

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

- ta (a value equal to: 'right', 'left', 'initial', 'inherit', 'center', 'justify'; optional):
    textAlign.

- td (a value equal to: 'initial', 'inherit', 'none', 'underline', 'overline', 'line-through'; optional):
    textDecoration.

- top (string | number; optional):
    top.

- transitionProps (dict; optional):
    Props added to Transition component that used to animate tooltip
    presence, use to configure duration and animation type, {
    duration: 100, transition: 'fade' } by default.

    `transitionProps` is a dict with keys:

    - duration (number; optional):
        Transition duration in ms.

    - exitDuration (number; optional):
        Exit transition duration in ms.

    - keepMounted (boolean; optional):
        If set element will not be unmounted from the DOM when it is
        hidden, display: none styles will be added instead.

    - mounted (boolean; required):
        When True, component will be mounted.

    - timingFunction (string; optional):
        Transition timing function, defaults to
        theme.transitionTimingFunction.

    - transition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; required):
        Predefined transition name or transition styles.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- w (string | number; optional):
    width.

- width (number; optional):
    Tooltip width.

- withArrow (boolean; optional):
    Determines whether component should have an arrow.

- withinPortal (boolean; optional):
    Determines whether tooltip should be rendered within Portal.

- zIndex (number; optional):
    Tooltip z-index."""
    _children_props = ['label']
    _base_nodes = ['label', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'Tooltip'
    @_explicitize_args
    def __init__(self, children=None, openDelay=Component.UNDEFINED, closeDelay=Component.UNDEFINED, opened=Component.UNDEFINED, offset=Component.UNDEFINED, withArrow=Component.UNDEFINED, arrowSize=Component.UNDEFINED, arrowOffset=Component.UNDEFINED, arrowRadius=Component.UNDEFINED, arrowPosition=Component.UNDEFINED, transitionProps=Component.UNDEFINED, events=Component.UNDEFINED, positionDependencies=Component.UNDEFINED, inline=Component.UNDEFINED, keepMounted=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, position=Component.UNDEFINED, refProp=Component.UNDEFINED, label=Component.REQUIRED, withinPortal=Component.UNDEFINED, radius=Component.UNDEFINED, color=Component.UNDEFINED, multiline=Component.UNDEFINED, width=Component.UNDEFINED, zIndex=Component.UNDEFINED, disabled=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeDelay', 'color', 'data-*', 'disabled', 'display', 'events', 'ff', 'fs', 'fw', 'fz', 'h', 'inline', 'inset', 'keepMounted', 'label', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'multiline', 'mx', 'my', 'offset', 'opacity', 'openDelay', 'opened', 'p', 'pb', 'pl', 'pos', 'position', 'positionDependencies', 'pr', 'pt', 'px', 'py', 'radius', 'refProp', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'transitionProps', 'tt', 'unstyled', 'w', 'width', 'withArrow', 'withinPortal', 'zIndex']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeDelay', 'color', 'data-*', 'disabled', 'display', 'events', 'ff', 'fs', 'fw', 'fz', 'h', 'inline', 'inset', 'keepMounted', 'label', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'multiline', 'mx', 'my', 'offset', 'opacity', 'openDelay', 'opened', 'p', 'pb', 'pl', 'pos', 'position', 'positionDependencies', 'pr', 'pt', 'px', 'py', 'radius', 'refProp', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'transitionProps', 'tt', 'unstyled', 'w', 'width', 'withArrow', 'withinPortal', 'zIndex']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['label']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        if 'children' not in _explicit_args:
            raise TypeError('Required argument children was not specified.')

        super(Tooltip, self).__init__(children=children, **args)
