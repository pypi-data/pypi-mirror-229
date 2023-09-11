# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class TimelineItem(Component):
    """A TimelineItem component.
play list of events in chronological order

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    React node that will be rendered after title.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- active (boolean; optional):
    Should this item be highlighted, controlled by Timeline component.

- align (a value equal to: 'right', 'left'; optional):
    Line and bullet position relative to item content, controlled by
    Timeline component.

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

- bullet (a list of or a singular dash component, string or number; optional):
    React node that should be rendered inside bullet – icon, image,
    avatar, etc.

- bulletSize (number; optional):
    Bullet width, height and border-radius, controlled by Timeline
    component.

- c (string; optional):
    color.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- classNames (dict; optional):
    Adds class names to Mantine components.

- color (string; optional):
    Highlight color for active item.

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

- inset (string | number; optional):
    inset.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- lineActive (boolean; optional):
    Should line of this item be highlighted, controlled by Timeline
    component.

- lineVariant (a value equal to: 'solid', 'dashed', 'dotted'; optional):
    Line border style.

- lineWidth (number; optional):
    Line border width, controlled by Timeline component.

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

- radius (string | number; optional):
    Key of theme.radius or any valid CSS value to set border-radius,
    \"xl\" by default.

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

- title (a list of or a singular dash component, string or number; optional):
    Item title, rendered next to bullet.

- top (string | number; optional):
    top.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- w (string | number; optional):
    width."""
    _children_props = ['title', 'bullet']
    _base_nodes = ['title', 'bullet', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'TimelineItem'
    @_explicitize_args
    def __init__(self, children=None, title=Component.UNDEFINED, bullet=Component.UNDEFINED, bulletSize=Component.UNDEFINED, radius=Component.UNDEFINED, active=Component.UNDEFINED, lineActive=Component.UNDEFINED, color=Component.UNDEFINED, align=Component.UNDEFINED, lineVariant=Component.UNDEFINED, lineWidth=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'active', 'align', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'bullet', 'bulletSize', 'c', 'className', 'classNames', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'left', 'lh', 'lineActive', 'lineVariant', 'lineWidth', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'title', 'top', 'tt', 'unstyled', 'w']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'active', 'align', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'bullet', 'bulletSize', 'c', 'className', 'classNames', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'left', 'lh', 'lineActive', 'lineVariant', 'lineWidth', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'right', 'style', 'styles', 'sx', 'ta', 'td', 'title', 'top', 'tt', 'unstyled', 'w']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(TimelineItem, self).__init__(children=children, **args)
