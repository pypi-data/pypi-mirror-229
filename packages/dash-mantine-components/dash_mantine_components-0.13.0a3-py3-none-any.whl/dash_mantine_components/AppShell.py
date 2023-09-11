# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class AppShell(Component):
    """An AppShell component.
Responsive shell for your application with header and navbar. For more information, see: https://mantine.dev/core/app-shell/

Keyword arguments:

- children (a list of or a singular dash component, string or number; required):
    AppShell content.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- aside (dict; optional):
    <Aside /> component.

    `aside` is a dict with keys:

    - key (string | number; required)

    - props (boolean | number | string | dict | list; required)

    - type (string; required)

- asideOffsetBreakpoint (string | number; optional):
    Breakpoint at which Aside component should no longer be offset
    with padding-right, applicable only for fixed position.

- bg (string; optional):
    background.

- bga (a value equal to: 'fixed', 'initial', 'inherit', 'scroll', 'local'; optional):
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

- data-* (string; optional):
    Wild card data attributes.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- ff (string; optional):
    fontFamily.

- fixed (boolean; optional):
    True to switch from static layout to fixed.

- footer (dict; optional):
    <Footer /> component.

    `footer` is a dict with keys:

    - key (string | number; required)

    - props (boolean | number | string | dict | list; required)

    - type (string; required)

- fs (a value equal to: 'initial', 'inherit', 'normal', 'italic', 'oblique'; optional):
    fontStyle.

- fw (number; optional):
    fontWeight.

- fz (string | number; optional):
    fontSize.

- h (string | number; optional):
    height.

- header (dict; optional):
    <Header /> component.

    `header` is a dict with keys:

    - key (string | number; required)

    - props (boolean | number | string | dict | list; required)

    - type (string; required)

- hidden (boolean; optional):
    True to hide all AppShell parts and render only children.

- inset (string | number; optional):
    inset.

- layout (a value equal to: 'default', 'alt'; optional):
    Determines how Navbar and Aside components are positioned relative
    to Header and Footer components.

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

- navbar (dict; optional):
    <Navbar /> component.

    `navbar` is a dict with keys:

    - key (string | number; required)

    - props (boolean | number | string | dict | list; required)

    - type (string; required)

- navbarOffsetBreakpoint (string | number; optional):
    Breakpoint at which Navbar component should no longer be offset
    with padding-left, applicable only for fixed position.

- opacity (number; optional):
    opacity.

- p (string | number; optional):
    padding.

- padding (string | number; optional):
    Content padding.

- pb (string | number; optional):
    paddingBottom.

- pl (string | number; optional):
    paddingLeft.

- pos (a value equal to: 'fixed', 'initial', 'inherit', 'static', 'absolute', 'relative', 'sticky'; optional):
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

- w (string | number; optional):
    width.

- zIndex (number; optional):
    zIndex prop passed to Navbar and Header components."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'AppShell'
    @_explicitize_args
    def __init__(self, children=None, layout=Component.UNDEFINED, navbar=Component.UNDEFINED, aside=Component.UNDEFINED, header=Component.UNDEFINED, footer=Component.UNDEFINED, zIndex=Component.UNDEFINED, fixed=Component.UNDEFINED, hidden=Component.UNDEFINED, padding=Component.UNDEFINED, navbarOffsetBreakpoint=Component.UNDEFINED, asideOffsetBreakpoint=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'aside', 'asideOffsetBreakpoint', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data-*', 'display', 'ff', 'fixed', 'footer', 'fs', 'fw', 'fz', 'h', 'header', 'hidden', 'inset', 'layout', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'navbar', 'navbarOffsetBreakpoint', 'opacity', 'p', 'padding', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'w', 'zIndex']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'aside', 'asideOffsetBreakpoint', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data-*', 'display', 'ff', 'fixed', 'footer', 'fs', 'fw', 'fz', 'h', 'header', 'hidden', 'inset', 'layout', 'left', 'lh', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'navbar', 'navbarOffsetBreakpoint', 'opacity', 'p', 'padding', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'w', 'zIndex']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        if 'children' not in _explicit_args:
            raise TypeError('Required argument children was not specified.')

        super(AppShell, self).__init__(children=children, **args)
