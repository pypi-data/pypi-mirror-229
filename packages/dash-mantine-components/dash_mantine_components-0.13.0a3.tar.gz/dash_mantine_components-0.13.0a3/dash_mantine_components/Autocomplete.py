# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Autocomplete(Component):
    """An Autocomplete component.
ocomplete user input with any list of options

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

- data (list of strings; required):
    suggestion data.

- data-* (string; optional):
    Wild card data attributes.

- debounce (number; default 0):
    Debounce time in ms.

- description (a list of or a singular dash component, string or number; optional):
    Input description, displayed after label.

- descriptionProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to description element.

- disabled (boolean; optional):
    Disabled input state.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- dropdownPosition (a value equal to: 'bottom', 'top', 'flip'; optional):
    Dropdown positioning behavior.

- error (a list of or a singular dash component, string or number; optional):
    Displays error message after input.

- errorProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to error element.

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

- hoverOnSearchChange (boolean; optional):
    Hovers the first result when input changes.

- icon (a list of or a singular dash component, string or number; optional):
    Adds icon on the left side of input.

- iconWidth (string | number; optional):
    Width of icon section.

- initiallyOpened (boolean; optional):
    Initial dropdown opened state.

- inputWrapperOrder (list of a value equal to: 'label', 'description', 'error', 'input's; optional):
    Controls order of the Input.Wrapper elements.

- inset (string | number; optional):
    inset.

- label (a list of or a singular dash component, string or number; optional):
    Input label, displayed before input.

- labelProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to label element.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- limit (number; optional):
    Limit amount of items displayed at a time for searchable select.

- lts (string | number; optional):
    letterSpacing.

- m (string | number; optional):
    margin.

- mah (string | number; optional):
    minHeight.

- maw (string | number; optional):
    maxWidth.

- maxDropdownHeight (string | number; optional):
    Maximum dropdown height.

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

- n_submit (number; default 0):
    An integer that represents the number of times that this element
    has been submitted.

- name (string; optional):
    Name prop.

- nothingFound (a list of or a singular dash component, string or number; optional):
    Nothing found label.

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

- required (boolean; optional):
    Adds required attribute to the input and red asterisk on the right
    side of label.

- right (string | number; optional):
    right.

- rightSection (a list of or a singular dash component, string or number; optional):
    Right section of input, similar to icon but on the right.

- rightSectionProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to rightSection div element.

- rightSectionWidth (string | number; optional):
    Width of right section, is used to calculate input padding-right.

- shadow (string; optional):
    Dropdown shadow from theme or any value to set box-shadow.

- size (string; optional):
    Input size.

- spellCheck (boolean; optional):
    Spell check property.

- style (boolean | number | string | dict | list; optional):
    Inline style.

- styles (boolean | number | string | dict | list; optional):
    Mantine styles API.

- switchDirectionOnFlip (boolean; optional):
    Whether to switch item order and keyboard navigation on dropdown
    position flip.

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

- transitionProps (dict; optional):
    Props added to Transition component that used to animate dropdown
    presence, use to configure duration and animation type, {
    duration: 0, transition: 'fade' } by default.

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

- value (string; default ''):
    Controlled input value.

- variant (a value equal to: 'default', 'filled', 'unstyled'; optional):
    Defines input appearance, defaults to default in light color
    scheme and filled in dark.

- w (string | number; optional):
    width.

- withAsterisk (boolean; optional):
    Determines whether required asterisk should be rendered, overrides
    required prop, does not add required attribute to the input.

- withinPortal (boolean; optional):
    Whether to render the dropdown in a Portal.

- wrapperProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Properties spread to root element.

- zIndex (number; optional):
    Dropdown z-index."""
    _children_props = ['icon', 'rightSection', 'label', 'description', 'error', 'nothingFound']
    _base_nodes = ['icon', 'rightSection', 'label', 'description', 'error', 'nothingFound', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'Autocomplete'
    @_explicitize_args
    def __init__(self, value=Component.UNDEFINED, data=Component.REQUIRED, maxDropdownHeight=Component.UNDEFINED, hoverOnSearchChange=Component.UNDEFINED, spellCheck=Component.UNDEFINED, n_submit=Component.UNDEFINED, debounce=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, icon=Component.UNDEFINED, iconWidth=Component.UNDEFINED, rightSection=Component.UNDEFINED, rightSectionWidth=Component.UNDEFINED, rightSectionProps=Component.UNDEFINED, wrapperProps=Component.UNDEFINED, radius=Component.UNDEFINED, variant=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, placeholder=Component.UNDEFINED, name=Component.UNDEFINED, label=Component.UNDEFINED, description=Component.UNDEFINED, error=Component.UNDEFINED, required=Component.UNDEFINED, withAsterisk=Component.UNDEFINED, labelProps=Component.UNDEFINED, descriptionProps=Component.UNDEFINED, errorProps=Component.UNDEFINED, inputWrapperOrder=Component.UNDEFINED, transitionProps=Component.UNDEFINED, shadow=Component.UNDEFINED, initiallyOpened=Component.UNDEFINED, withinPortal=Component.UNDEFINED, limit=Component.UNDEFINED, nothingFound=Component.UNDEFINED, zIndex=Component.UNDEFINED, dropdownPosition=Component.UNDEFINED, switchDirectionOnFlip=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data', 'data-*', 'debounce', 'description', 'descriptionProps', 'disabled', 'display', 'dropdownPosition', 'error', 'errorProps', 'ff', 'fs', 'fw', 'fz', 'h', 'hoverOnSearchChange', 'icon', 'iconWidth', 'initiallyOpened', 'inputWrapperOrder', 'inset', 'label', 'labelProps', 'left', 'lh', 'limit', 'lts', 'm', 'mah', 'maw', 'maxDropdownHeight', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_submit', 'name', 'nothingFound', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'placeholder', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'required', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'shadow', 'size', 'spellCheck', 'style', 'styles', 'switchDirectionOnFlip', 'sx', 'ta', 'td', 'top', 'transitionProps', 'tt', 'unstyled', 'value', 'variant', 'w', 'withAsterisk', 'withinPortal', 'wrapperProps', 'zIndex']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'data', 'data-*', 'debounce', 'description', 'descriptionProps', 'disabled', 'display', 'dropdownPosition', 'error', 'errorProps', 'ff', 'fs', 'fw', 'fz', 'h', 'hoverOnSearchChange', 'icon', 'iconWidth', 'initiallyOpened', 'inputWrapperOrder', 'inset', 'label', 'labelProps', 'left', 'lh', 'limit', 'lts', 'm', 'mah', 'maw', 'maxDropdownHeight', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'n_submit', 'name', 'nothingFound', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'placeholder', 'pos', 'pr', 'pt', 'px', 'py', 'radius', 'required', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'shadow', 'size', 'spellCheck', 'style', 'styles', 'switchDirectionOnFlip', 'sx', 'ta', 'td', 'top', 'transitionProps', 'tt', 'unstyled', 'value', 'variant', 'w', 'withAsterisk', 'withinPortal', 'wrapperProps', 'zIndex']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Autocomplete, self).__init__(**args)
