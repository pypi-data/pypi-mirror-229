# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MenuItem(Component):
    """A MenuItem component.
bine a list of secondary actions into single interactive area

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Item label.

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

- c (string; optional):
    color.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- classNames (dict; optional):
    Adds class names to Mantine components.

- closeMenuOnClick (boolean; optional):
    Determines whether menu should be closed when item is clicked,
    overrides closeOnItemClick prop on Menu component.

- color (boolean | number | string | dict | list; optional):
    Key of theme.colors.

- data-* (string; optional):
    Wild card data attributes.

- disabled (boolean; optional):
    Is item disabled.

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

- href (string; optional):
    href if MenuItem is supposed to be used as a link.

- icon (a list of or a singular dash component, string or number; optional):
    Icon rendered on the left side of the label.

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

- refresh (boolean; optional):
    Whether to refresh the page.

- right (string | number; optional):
    right.

- rightSection (a list of or a singular dash component, string or number; optional):
    Section rendered on the right side of the label.

- style (boolean | number | string | dict | list; optional):
    Inline style.

- styles (boolean | number | string | dict | list; optional):
    Mantine styles API.

- sx (boolean | number | string | dict | list; optional):
    With sx you can add styles to component root element. If you need
    to customize styles of other elements within component use styles
    prop.

- ta (a value equal to: 'right', 'left', 'center', 'initial', 'inherit', 'justify'; optional):
    textAlign.

- target (a value equal to: '_blank', '_self'; optional):
    Target if MenuItem is supposed to be used as a link.

- td (a value equal to: 'initial', 'inherit', 'none', 'underline', 'overline', 'line-through'; optional):
    textDecoration.

- top (string | number; optional):
    top.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- w (string | number; optional):
    width."""
    _children_props = ['icon', 'rightSection']
    _base_nodes = ['icon', 'rightSection', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'MenuItem'
    @_explicitize_args
    def __init__(self, children=None, color=Component.UNDEFINED, closeMenuOnClick=Component.UNDEFINED, icon=Component.UNDEFINED, rightSection=Component.UNDEFINED, disabled=Component.UNDEFINED, href=Component.UNDEFINED, n_clicks=Component.UNDEFINED, target=Component.UNDEFINED, refresh=Component.UNDEFINED, boxWrapperProps=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'boxWrapperProps', 'c', 'className', 'classNames', 'closeMenuOnClick', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'href', 'icon', 'inset', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_clicks', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'refresh', 'right', 'rightSection', 'style', 'styles', 'sx', 'ta', 'target', 'td', 'top', 'tt', 'unstyled', 'w']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'boxWrapperProps', 'c', 'className', 'classNames', 'closeMenuOnClick', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'href', 'icon', 'inset', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_clicks', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'refresh', 'right', 'rightSection', 'style', 'styles', 'sx', 'ta', 'target', 'td', 'top', 'tt', 'unstyled', 'w']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(MenuItem, self).__init__(children=children, **args)
