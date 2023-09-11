# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Highlight(Component):
    """A Highlight component.
hlight given part of a string with mark tag

Keyword arguments:

- children (string; optional):
    Content   Text content.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- align (a value equal to: 'initial', 'inherit', 'left', 'right', 'center', 'justify'; optional):
    Sets text-align css property.

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
    Key of theme.colors or any valid CSS color.

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

- gradient (dict; optional):
    Controls gradient settings in gradient variant only.

    `gradient` is a dict with keys:

    - deg (number; optional)

    - from (string; required)

    - to (string; required)

- h (string | number; optional):
    height.

- highlight (string | list of strings; required):
    Substring or an array of substrings to highlight in children.

- highlightColor (boolean | number | string | dict | list; optional):
    Color from theme that is used for highlighting.

- inherit (boolean; optional):
    Inherit font properties from parent element.

- inline (boolean; optional):
    Sets line-height to 1 for centering.

- inset (string | number; optional):
    inset.

- italic (boolean; optional):
    Adds font-style: italic style.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- lineClamp (number; optional):
    CSS -webkit-line-clamp property.

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

- size (string | number; optional):
    Key of theme.fontSizes or any valid CSS value to set font-size.

- span (boolean; optional):
    Shorthand for component=\"span\".

- strikethrough (boolean; optional):
    Add strikethrough styles.

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

- transform (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    Sets text-transform css property.

- truncate (boolean | number | string | dict | list; optional):
    CSS truncate overflowing text with an ellipsis.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- underline (boolean; optional):
    Underline the text.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- variant (a value equal to: 'gradient', 'text'; optional):
    Link or text variant.

- w (string | number; optional):
    width.

- weight (number; optional):
    Sets font-weight css property."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'Highlight'
    @_explicitize_args
    def __init__(self, children=None, highlight=Component.REQUIRED, highlightColor=Component.UNDEFINED, size=Component.UNDEFINED, color=Component.UNDEFINED, weight=Component.UNDEFINED, transform=Component.UNDEFINED, align=Component.UNDEFINED, variant=Component.UNDEFINED, lineClamp=Component.UNDEFINED, truncate=Component.UNDEFINED, inline=Component.UNDEFINED, underline=Component.UNDEFINED, strikethrough=Component.UNDEFINED, italic=Component.UNDEFINED, inherit=Component.UNDEFINED, gradient=Component.UNDEFINED, span=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'align', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'gradient', 'h', 'highlight', 'highlightColor', 'inherit', 'inline', 'inset', 'italic', 'left', 'lh', 'lineClamp', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'right', 'size', 'span', 'strikethrough', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'transform', 'truncate', 'tt', 'underline', 'unstyled', 'variant', 'w', 'weight']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'align', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'gradient', 'h', 'highlight', 'highlightColor', 'inherit', 'inline', 'inset', 'italic', 'left', 'lh', 'lineClamp', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'p', 'pb', 'pl', 'pos', 'pr', 'pt', 'px', 'py', 'right', 'size', 'span', 'strikethrough', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'transform', 'truncate', 'tt', 'underline', 'unstyled', 'variant', 'w', 'weight']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['highlight']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Highlight, self).__init__(children=children, **args)
