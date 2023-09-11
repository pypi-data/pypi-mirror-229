# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PinInput(Component):
    """A PinInput component.
ture password from user with option to toggle visibility

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- autoFocus (boolean; optional):
    If set, first input is focused when component is mounted.

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

- data-* (string; optional):
    Wild card data attributes.

- disabled (boolean; optional):
    Disabled input state.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- error (boolean; optional):
    Adds error styles to all inputs.

- ff (string; optional):
    fontFamily.

- form (string; optional):
    Hidden input form attribute.

- fs (a value equal to: 'initial', 'inherit', 'normal', 'italic', 'oblique'; optional):
    fontStyle.

- fw (number; optional):
    fontWeight.

- fz (string | number; optional):
    fontSize.

- h (string | number; optional):
    height.

- icon (a list of or a singular dash component, string or number; optional):
    Adds icon on the left side of input.

- iconWidth (string | number; optional):
    Width of icon section.

- inputType (string; optional):
    Inputs type attribute, inferred from type prop if not specified.

- inset (string | number; optional):
    inset.

- left (string | number; optional):
    left.

- length (number; optional):
    Number of input boxes.

- lh (string | number; optional):
    lineHeight.

- lts (string | number; optional):
    letterSpacing.

- m (string | number; optional):
    margin.

- mah (string | number; optional):
    minHeight.

- manageFocus (boolean; optional):
    Determines whether focus should be moved automatically to the next
    input once filled.

- mask (boolean; optional):
    Changes input type to \"password\".

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

- name (string; optional):
    Name prop.

- oneTimeCode (boolean; optional):
    Determines whether autocomplete=\"one-time-code\" attribute should
    be set on all inputs.

- opacity (number; optional):
    opacity.

- p (string | number; optional):
    padding.

- pb (string | number; optional):
    paddingBottom.

- pl (string | number; optional):
    paddingLeft.

- placeholder (string; optional):
    Placeholder.

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

- readOnly (boolean; optional):
    Determines whether the user can edit input content.

- right (string | number; optional):
    right.

- rightSection (a list of or a singular dash component, string or number; optional):
    Right section of input, similar to icon but on the right.

- rightSectionProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to rightSection div element.

- rightSectionWidth (string | number; optional):
    Width of right section, is used to calculate input padding-right.

- size (string; optional):
    Input size.

- spacing (string | number; optional):
    Key of theme.spacing or any valid CSS value to set spacing between
    inputs.

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

- type (boolean | number | string | dict | list; optional):
    The type of allowed values.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- value (string; optional):
    Value for controlled component.

- valueOnComplete (string; optional):
    Has the user entered the complete pin.

- variant (a value equal to: 'default', 'filled', 'unstyled'; optional):
    Defines input appearance, defaults to default in light color
    scheme and filled in dark.

- w (string | number; optional):
    width.

- wrapperProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Properties spread to root element."""
    _children_props = ['icon', 'rightSection']
    _base_nodes = ['icon', 'rightSection', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'PinInput'
    @_explicitize_args
    def __init__(self, form=Component.UNDEFINED, spacing=Component.UNDEFINED, radius=Component.UNDEFINED, autoFocus=Component.UNDEFINED, value=Component.UNDEFINED, manageFocus=Component.UNDEFINED, oneTimeCode=Component.UNDEFINED, error=Component.UNDEFINED, type=Component.UNDEFINED, mask=Component.UNDEFINED, length=Component.UNDEFINED, readOnly=Component.UNDEFINED, inputType=Component.UNDEFINED, valueOnComplete=Component.UNDEFINED, icon=Component.UNDEFINED, iconWidth=Component.UNDEFINED, rightSection=Component.UNDEFINED, rightSectionWidth=Component.UNDEFINED, rightSectionProps=Component.UNDEFINED, wrapperProps=Component.UNDEFINED, variant=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, placeholder=Component.UNDEFINED, name=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'aria-*', 'autoFocus', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data-*', 'disabled', 'display', 'error', 'ff', 'form', 'fs', 'fw', 'fz', 'h', 'icon', 'iconWidth', 'inputType', 'inset', 'left', 'length', 'lh', 'lts', 'm', 'mah', 'manageFocus', 'mask', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'name', 'oneTimeCode', 'opacity', 'p', 'pb', 'pl', 'placeholder', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'readOnly', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'size', 'spacing', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'type', 'unstyled', 'value', 'valueOnComplete', 'variant', 'w', 'wrapperProps']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'aria-*', 'autoFocus', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data-*', 'disabled', 'display', 'error', 'ff', 'form', 'fs', 'fw', 'fz', 'h', 'icon', 'iconWidth', 'inputType', 'inset', 'left', 'length', 'lh', 'lts', 'm', 'mah', 'manageFocus', 'mask', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'name', 'oneTimeCode', 'opacity', 'p', 'pb', 'pl', 'placeholder', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'readOnly', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'size', 'spacing', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'type', 'unstyled', 'value', 'valueOnComplete', 'variant', 'w', 'wrapperProps']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(PinInput, self).__init__(**args)
