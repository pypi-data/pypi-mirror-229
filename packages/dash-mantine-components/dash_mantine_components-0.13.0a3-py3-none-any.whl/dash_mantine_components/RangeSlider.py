# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RangeSlider(Component):
    """A RangeSlider component.
ture user feedback from a range of values

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- bg (string; optional):
    background.

- bga (a value equal to: 'local', 'initial', 'inherit', 'scroll', 'fixed'; optional):
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
    Color from theme.colors.

- data-* (string; optional):
    Wild card data attributes.

- disabled (boolean; optional):
    Disables slider.

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

- inverted (boolean; optional):
    Allows the track to be inverted.

- label (a list of or a singular dash component, string or number; optional):
    Function to generate label or any react node to render instead,
    set to None to disable label.

- labelAlwaysOn (boolean; optional):
    If True label will be not be hidden when user stops dragging.

- labelTransition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; optional):
    Label appear/disappear transition.

- labelTransitionDuration (number; optional):
    Label appear/disappear transition duration in ms.

- labelTransitionTimingFunction (string; optional):
    Label appear/disappear transition timing function, defaults to
    theme.transitionRimingFunction.

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

- marks (list of dicts; optional):
    Marks which will be placed on the track.

    `marks` is a list of dicts with keys:

    - label (a list of or a singular dash component, string or number; optional)

    - value (number; required)

- maw (string | number; optional):
    maxWidth.

- max (number; optional):
    Maximum possible value.

- maxRange (number; optional):
    Maximum range interval.

- mb (string | number; optional):
    marginBottom.

- mih (string | number; optional):
    minHeight.

- min (number; optional):
    Minimal possible value.

- minRange (number; optional):
    Minimal range interval.

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
    Hidden input name, use with uncontrolled variant.

- opacity (number; optional):
    opacity.

- p (string | number; optional):
    padding.

- pb (string | number; optional):
    paddingBottom.

- persisted_props (list of strings; default ["value"]):
    Properties whose user interactions will persist after refreshing
    the component or the page. Since only `value` is allowed this prop
    can normally be ignored.

- persistence (string | number; optional):
    Used to allow user interactions in this component to be persisted
    when the component - or the page - is refreshed. If `persisted` is
    truthy and hasn't changed from its previous value, a `value` that
    the user has changed while using the app will keep that change, as
    long as the new `value` also matches what was given originally.
    Used in conjunction with `persistence_type`.

- persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

- pl (string | number; optional):
    paddingLeft.

- pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
    position.

- pr (string | number; optional):
    paddingRight.

- precision (number; optional):
    Amount of digits after the decimal point.

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

- showLabelOnHover (boolean; optional):
    If True slider label will appear on hover.

- size (string | number; optional):
    Controls size of track and thumb.

- step (number; optional):
    Number by which value will be incremented/decremented with thumb
    drag and arrows.

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

- thumbChildren (a list of or a singular dash component, string or number; optional):
    Thumb children, can be used to add icon.

- thumbFromLabel (string; optional):
    First thumb aria-label.

- thumbLabel (string; optional):
    Thumb aria-label.

- thumbSize (number; optional):
    Thumb width and height.

- thumbToLabel (string; optional):
    Second thumb aria-label.

- top (string | number; optional):
    top.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- updatemode (a value equal to: 'mouseup', 'drag'; default 'mouseup'):
    Determines when the component should update its value property. If
    mouseup (the default) then the slider will only trigger its value
    when the user has finished dragging the slider. If drag, then the
    slider will update its value continuously as it is being dragged.

- value (list of 2 elements: [number, number]; optional):
    Current value for controlled slider.

- w (string | number; optional):
    width."""
    _children_props = ['marks[].label', 'label', 'thumbChildren']
    _base_nodes = ['label', 'thumbChildren', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'RangeSlider'
    @_explicitize_args
    def __init__(self, minRange=Component.UNDEFINED, maxRange=Component.UNDEFINED, thumbFromLabel=Component.UNDEFINED, thumbToLabel=Component.UNDEFINED, color=Component.UNDEFINED, radius=Component.UNDEFINED, size=Component.UNDEFINED, min=Component.UNDEFINED, max=Component.UNDEFINED, step=Component.UNDEFINED, precision=Component.UNDEFINED, value=Component.UNDEFINED, name=Component.UNDEFINED, marks=Component.UNDEFINED, label=Component.UNDEFINED, labelTransition=Component.UNDEFINED, labelTransitionDuration=Component.UNDEFINED, labelTransitionTimingFunction=Component.UNDEFINED, labelAlwaysOn=Component.UNDEFINED, thumbLabel=Component.UNDEFINED, showLabelOnHover=Component.UNDEFINED, thumbChildren=Component.UNDEFINED, disabled=Component.UNDEFINED, thumbSize=Component.UNDEFINED, inverted=Component.UNDEFINED, updatemode=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'inverted', 'label', 'labelAlwaysOn', 'labelTransition', 'labelTransitionDuration', 'labelTransitionTimingFunction', 'left', 'lh', 'lts', 'm', 'mah', 'marks', 'maw', 'max', 'maxRange', 'mb', 'mih', 'min', 'minRange', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'name', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'pos', 'pr', 'precision', 'pt', 'px', 'py', 'radius', 'right', 'showLabelOnHover', 'size', 'step', 'style', 'styles', 'sx', 'ta', 'td', 'thumbChildren', 'thumbFromLabel', 'thumbLabel', 'thumbSize', 'thumbToLabel', 'top', 'tt', 'unstyled', 'updatemode', 'value', 'w']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'color', 'data-*', 'disabled', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'inverted', 'label', 'labelAlwaysOn', 'labelTransition', 'labelTransitionDuration', 'labelTransitionTimingFunction', 'left', 'lh', 'lts', 'm', 'mah', 'marks', 'maw', 'max', 'maxRange', 'mb', 'mih', 'min', 'minRange', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'name', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'pos', 'pr', 'precision', 'pt', 'px', 'py', 'radius', 'right', 'showLabelOnHover', 'size', 'step', 'style', 'styles', 'sx', 'ta', 'td', 'thumbChildren', 'thumbFromLabel', 'thumbLabel', 'thumbSize', 'thumbToLabel', 'top', 'tt', 'unstyled', 'updatemode', 'value', 'w']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(RangeSlider, self).__init__(**args)
