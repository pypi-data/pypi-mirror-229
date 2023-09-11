# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Menu(Component):
    """A Menu component.
bine a list of secondary actions into single interactive area

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Menu content.

- id (string; optional):
    id base to create accessibility connections.

- arrowOffset (number; optional):
    Arrow offset.

- arrowPosition (a value equal to: 'center', 'side'; optional):
    Arrow position *.

- arrowRadius (number; optional):
    Arrow border-radius.

- arrowSize (number; optional):
    Arrow size.

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

    - ta (a value equal to: 'right', 'left', 'center', 'initial', 'inherit', 'justify'; optional):
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

- classNames (dict; optional):
    Adds class names to Mantine components.

- clickOutsideEvents (list of strings; optional):
    Events that trigger outside clicks.

- closeDelay (number; optional):
    Close delay in ms, applicable only to trigger=\"hover\" variant.

- closeOnClickOutside (boolean; optional):
    Determines whether dropdown should be closed on outside clicks,
    default to True.

- closeOnEscape (boolean; optional):
    Determines whether dropdown should be closed when Escape key is
    pressed, defaults to True.

- closeOnItemClick (boolean; optional):
    Determines whether Menu should be closed when item is clicked.

- disabled (boolean; optional):
    If set, popover dropdown will not render.

- keepMounted (boolean; optional):
    If set dropdown will not be unmounted from the DOM when it is
    hidden, display: none styles will be added instead.

- loop (boolean; optional):
    Determines whether arrow key presses should loop though items
    (first to last and last to first).

- middlewares (dict; optional):
    Floating ui middlewares to configure position handling.

    `middlewares` is a dict with keys:

    - flip (boolean; required)

    - inline (boolean; optional)

    - shift (boolean; required)

- offset (number; optional):
    Default Y axis or either (main, cross, alignment) X and Y axis
    space between target element and dropdown.

- openDelay (number; optional):
    Open delay in ms, applicable only to trigger=\"hover\" variant.

- opened (boolean; optional):
    Controlled menu opened state.

- position (a value equal to: 'top', 'right', 'bottom', 'left', 'top-end', 'top-start', 'right-end', 'right-start', 'bottom-end', 'bottom-start', 'left-end', 'left-start'; optional):
    Dropdown position relative to target.

- positionDependencies (list of boolean | number | string | dict | lists; optional):
    useEffect dependencies to force update dropdown position.

- radius (string | number; optional):
    Key of theme.radius or any valid CSS value to set border-radius,
    theme.defaultRadius by default.

- returnFocus (boolean; optional):
    Determines whether focus should be automatically returned to
    control when dropdown closes, False by default.

- shadow (string; optional):
    Key of theme.shadow or any other valid css box-shadow value.

- styles (boolean | number | string | dict | list; optional):
    Mantine styles API.

- sx (boolean | number | string | dict | list; optional):
    With sx you can add styles to component root element. If you need
    to customize styles of other elements within component use styles
    prop.

- transitionProps (dict; optional):
    Props added to Transition component that used to animate dropdown
    presence, use to configure duration and animation type, {
    duration: 150, transition: 'fade' } by default.

    `transitionProps` is a dict with keys:

    - duration (number; optional):
        Transition duration in ms.

    - exitDuration (number; optional):
        Exit transition duration in ms.

    - keepMounted (boolean; optional):
        If set element will not be unmounted from the DOM when it is
        hidden, display: none styles will be added instead.

    - timingFunction (string; optional):
        Transition timing function, defaults to
        theme.transitionTimingFunction.

    - transition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; required):
        Predefined transition name or transition styles.

- trigger (a value equal to: 'click', 'hover'; optional):
    Event which should open menu.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- width (number; optional):
    Dropdown width, or 'target' to make dropdown width the same as
    target element.

- withArrow (boolean; optional):
    Determines whether component should have an arrow.

- withinPortal (boolean; optional):
    Determines whether dropdown should be rendered within Portal,
    defaults to False.

- zIndex (number; optional):
    Dropdown z-index."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'Menu'
    @_explicitize_args
    def __init__(self, children=None, opened=Component.UNDEFINED, closeOnItemClick=Component.UNDEFINED, loop=Component.UNDEFINED, closeOnEscape=Component.UNDEFINED, trigger=Component.UNDEFINED, openDelay=Component.UNDEFINED, closeDelay=Component.UNDEFINED, closeOnClickOutside=Component.UNDEFINED, clickOutsideEvents=Component.UNDEFINED, id=Component.UNDEFINED, boxWrapperProps=Component.UNDEFINED, position=Component.UNDEFINED, offset=Component.UNDEFINED, positionDependencies=Component.UNDEFINED, keepMounted=Component.UNDEFINED, transitionProps=Component.UNDEFINED, width=Component.UNDEFINED, middlewares=Component.UNDEFINED, withArrow=Component.UNDEFINED, arrowSize=Component.UNDEFINED, arrowOffset=Component.UNDEFINED, arrowRadius=Component.UNDEFINED, arrowPosition=Component.UNDEFINED, withinPortal=Component.UNDEFINED, zIndex=Component.UNDEFINED, radius=Component.UNDEFINED, shadow=Component.UNDEFINED, disabled=Component.UNDEFINED, returnFocus=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'boxWrapperProps', 'classNames', 'clickOutsideEvents', 'closeDelay', 'closeOnClickOutside', 'closeOnEscape', 'closeOnItemClick', 'disabled', 'keepMounted', 'loop', 'middlewares', 'offset', 'openDelay', 'opened', 'position', 'positionDependencies', 'radius', 'returnFocus', 'shadow', 'styles', 'sx', 'transitionProps', 'trigger', 'unstyled', 'width', 'withArrow', 'withinPortal', 'zIndex']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'boxWrapperProps', 'classNames', 'clickOutsideEvents', 'closeDelay', 'closeOnClickOutside', 'closeOnEscape', 'closeOnItemClick', 'disabled', 'keepMounted', 'loop', 'middlewares', 'offset', 'openDelay', 'opened', 'position', 'positionDependencies', 'radius', 'returnFocus', 'shadow', 'styles', 'sx', 'transitionProps', 'trigger', 'unstyled', 'width', 'withArrow', 'withinPortal', 'zIndex']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Menu, self).__init__(children=children, **args)
