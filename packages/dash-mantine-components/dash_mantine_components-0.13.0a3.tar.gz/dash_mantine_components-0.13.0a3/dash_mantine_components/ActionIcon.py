# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ActionIcon(Component):
    """An ActionIcon component.
n button.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Icon.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

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

- color (string; optional):
    Key of theme.colors.

- data-* (string; optional):
    Wild card data attributes.

- disabled (boolean; optional):
    Indicates disabled state.

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

- gradient (dict; optional):
    Gradient input, only used when variant=\"gradient\",
    theme.defaultGradient by default.

    `gradient` is a dict with keys:

    - deg (number; optional)

    - from (string; required)

    - to (string; required)

- h (string | number; optional):
    height.

- inset (string | number; optional):
    inset.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- loaderProps (dict; optional):
    Props added to Loader component (only visible when `loading` prop
    is set).

    `loaderProps` is a dict with keys:

    - color (string; optional):
        Loader color from theme.

    - size (string

      Or number; optional):
        Defines width of loader.

    - variant (a value equal to: 'bars', 'oval', 'dots'; optional):
        Loader appearance. | dict with keys:

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

    - style (boolean | number | string | dict | list; optional):
        Inline style. | dict with keys:

    - classNames (dict; optional):
        Adds class names to Mantine components.

    - styles (boolean | number | string | dict | list; optional):
        Mantine styles API.

    - sx (boolean | number | string | dict | list; optional):
        With sx you can add styles to component root element. If you
        need to customize styles of other elements within component
        use styles prop.

    - unstyled (boolean; optional):
        Remove all Mantine styling from the component. | dict with keys:

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
        width.

- loading (boolean; optional):
    Indicates loading state.

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

- n_clicks (number; default 0):
    An integer that represents the number of times that this element
    has been clicked on.

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

- radius (string | number; optional):
    Key of theme.radius or any valid CSS value to set border-radius,
    theme.defaultRadius by default.

- right (string | number; optional):
    right.

- size (string | number; optional):
    Predefined button size or any valid CSS value to set width and
    height.

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

- top (string | number; optional):
    top.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- variant (a value equal to: 'subtle', 'filled', 'outline', 'light', 'default', 'transparent', 'gradient'; optional):
    Controls appearance, subtle by default.

- w (string | number; optional):
    width."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'ActionIcon'
    @_explicitize_args
    def __init__(self, children=None, variant=Component.UNDEFINED, color=Component.UNDEFINED, gradient=Component.UNDEFINED, radius=Component.UNDEFINED, size=Component.UNDEFINED, loaderProps=Component.UNDEFINED, loading=Component.UNDEFINED, n_clicks=Component.UNDEFINED, disabled=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'gradient', 'h', 'inset', 'left', 'lh', 'loaderProps', 'loading', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_clicks', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'size', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'variant', 'w']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'gradient', 'h', 'inset', 'left', 'lh', 'loaderProps', 'loading', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_clicks', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'size', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'variant', 'w']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ActionIcon, self).__init__(children=children, **args)
