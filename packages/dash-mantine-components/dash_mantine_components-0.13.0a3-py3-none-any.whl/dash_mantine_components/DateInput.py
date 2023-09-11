# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DateInput(Component):
    """A DateInput component.
e, multiple dates and dates range picker input.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allowDeselect (boolean; optional):
    Determines whether value can be deselected when the user clicks on
    the selected date in the calendar or erases content of the input,
    True if clearable prop is set, False by default.

- aria-* (string; optional):
    Wild card aria attributes.

- ariaLabels (dict; optional):
    aria-label attributes for controls on different levels.

    `ariaLabels` is a dict with keys:

    - monthLevelControl (string; optional)

    - nextDecade (string; optional)

    - nextMonth (string; optional)

    - nextYear (string; optional)

    - previousDecade (string; optional)

    - previousMonth (string; optional)

    - previousYear (string; optional)

    - yearLevelControl (string; optional)

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

- clearButtonProps (dict; optional):
    Props added to clear button.

- clearable (boolean; optional):
    Determines whether input value can be cleared, adds clear button
    to right section, False by default.

- closeOnChange (boolean; optional):
    Determines whether dropdown should be closed when date is
    selected, not applicable when type=\"multiple\", True by default.

- columnsToScroll (number; optional):
    Number of columns to scroll when user clicks next/prev buttons,
    defaults to numberOfColumns.

- data-* (string; optional):
    Wild card data attributes.

- debounce (number; default 0):
    Debounce time in ms.

- decadeLabelFormat (string; optional):
    dayjs label format to display decade label.

- description (a list of or a singular dash component, string or number; optional):
    Input description, displayed after label.

- descriptionProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to description element.

- disabled (boolean; optional):
    Disabled input state.

- disabledDates (list of strings; optional):
    Specifies days that should be disabled.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- dropdownType (a value equal to: 'popover', 'modal'; optional):
    Type of dropdown, defaults to popover.

- error (a list of or a singular dash component, string or number; optional):
    Displays error message after input.

- errorProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to error element.

- ff (string; optional):
    fontFamily.

- firstDayOfWeek (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional):
    number 0-6, 0 – Sunday, 6 – Saturday, defaults to 1 – Monday.

- fixOnBlur (boolean; optional):
    Determines whether input value should be reverted to last known
    valid value on blur, True by default.

- fs (a value equal to: 'initial', 'inherit', 'normal', 'italic', 'oblique'; optional):
    fontStyle.

- fw (number; optional):
    fontWeight.

- fz (string | number; optional):
    fontSize.

- h (string | number; optional):
    height.

- hasNextLevel (boolean; optional):
    Determines whether next level button should be enabled, defaults
    to True.

- hideOutsideDates (boolean; optional):
    Determines whether outside dates should be hidden, defaults to
    False.

- hideWeekdays (boolean; optional):
    Determines whether weekdays row should be hidden, defaults to
    False.

- icon (a list of or a singular dash component, string or number; optional):
    Adds icon on the left side of input.

- iconWidth (string | number; optional):
    Width of icon section.

- inputWrapperOrder (list of a value equal to: 'label', 'description', 'error', 'input's; optional):
    Controls order of the Input.Wrapper elements.

- inset (string | number; optional):
    inset.

- label (a list of or a singular dash component, string or number; optional):
    Input label, displayed before input.

- labelProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props spread to label element.

- labelSeparator (string; optional):
    Separator between range value.

- left (string | number; optional):
    left.

- level (a value equal to: 'month', 'year', 'decade'; optional):
    Current level displayed to the user (decade, year, month), used
    for controlled component.

- lh (string | number; optional):
    lineHeight.

- locale (string; optional):
    dayjs locale, defaults to value defined in DatesProvider.

- lts (string | number; optional):
    letterSpacing.

- m (string | number; optional):
    margin.

- mah (string | number; optional):
    minHeight.

- maw (string | number; optional):
    maxWidth.

- maxDate (string; optional):
    Maximum possible date   Maximum possible string.

- maxLevel (a value equal to: 'month', 'year', 'decade'; optional):
    Max level that user can go up to (decade, year, month), defaults
    to decade.

- mb (string | number; optional):
    marginBottom.

- mih (string | number; optional):
    minHeight.

- minDate (string; optional):
    Minimum possible date.

- miw (string | number; optional):
    minWidth.

- ml (string | number; optional):
    marginLeft.

- modalProps (dict; optional):
    Props added to Modal component.

    `modalProps` is a dict with keys:

    - centered (boolean; optional):
        Determines whether the modal should be centered vertically,
        False by default.

    - closeButtonProps (dict; optional):
        Props added to close button.

        `closeButtonProps` is a dict with keys:

        - children (a list of or a singular dash component, string or number; optional):
            Icon.

        - color (string; optional):
            Key of theme.colors.

        - disabled (boolean; optional):
            Indicates disabled state.

        - gradient (dict; optional):
            Gradient input, only used when variant=\"gradient\",
            theme.defaultGradient by default.

            `gradient` is a dict with keys:

            - deg (number; optional)

            - from (string; required)

            - to (string; required)

        - iconSize (string

          Or number; optional):
            Width and height of X icon.

        - loaderProps (dict; optional):
            Props added to Loader component (only visible when
            `loading` prop is set).

            `loaderProps` is a dict with keys:

    - color (string; optional):
        Loader color from theme.

    - size (string

              Or number; optional):
        Defines width of loader.

    - variant (a value equal to: 'bars', 'oval', 'dots'; optional):
        Loader appearance.

      Or dict with keys:

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

        - n_clicks (number; optional):
            An integer that represents the number of times that this
            element has been clicked on.

        - radius (string | number; optional):
            Key of theme.radius or any valid CSS value to set
            border-radius, theme.defaultRadius by default.

        - size (string | number; optional):
            Predefined button size or any valid CSS value to set width
            and height.

        - variant (a value equal to: 'default', 'filled', 'transparent', 'subtle', 'outline', 'light', 'gradient'; optional):
            Controls appearance, subtle by default.

    - closeOnClickOutside (boolean; optional):
        Determines whether the modal/drawer should be closed when user
        clicks on the overlay, True by default.

    - closeOnEscape (boolean; optional):
        Determines whether onClose should be called when user presses
        escape key, True by default.

    - fullScreen (boolean; optional):
        Determines whether the modal should take the entire screen.

    - keepMounted (boolean; optional):
        If set modal/drawer will not be unmounted from the DOM when it
        is hidden, display: none styles will be added instead.

    - lockScroll (boolean; optional):
        Determines whether scroll should be locked when opened={True},
        defaults to True.

    - opened (boolean; optional):
        Determines whether modal/drawer is opened.

    - overlayProps (dict; optional):
        Props added to Overlay component, use configure opacity,
        background color, styles and other properties.

        `overlayProps` is a dict with keys:

        - transitionProps (dict; optional):

            Props added to Transition component.

            `transitionProps` is a dict with keys:

            - duration (number; optional):

                Transition duration in ms.

            - exitDuration (number; optional):

                Exit transition duration in ms.

            - keepMounted (boolean; optional):

                If set element will not be unmounted from the DOM when it

                is hidden, display: none styles will be added instead.

            - mounted (boolean; required):

                When True, component will be mounted.

            - timingFunction (string; optional):

                Transition timing function, defaults to

                theme.transitionTimingFunction.

            - transition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; required):

                Predefined transition name or transition styles.

              Or dict with keys:

        - blur (string | number; optional):

            Overlay background blur, 0 by default.

        - center (boolean; optional):

            Determines whether content inside overlay should be vertically

            and horizontally centered, False by default.

        - color (string; optional):

            Overlay background-color, #000 by default.

        - fixed (boolean; optional):

            Determines whether overlay should have fixed position instead

            of absolute, False by default.

        - gradient (string; optional):

            Changes overlay to gradient, if set color prop is ignored.

        - opacity (number; optional):

            Overlay background-color opacity 0–1, disregarded when

            gradient prop is set, 0.6 by default.

        - radius (string | number; optional):

            Key of theme.radius or any valid CSS value to set

            border-radius, theme.defaultRadius by default.

        - variant (string; optional)

        - zIndex (number; optional):

            Overlay z-index, 200 by default.

    - padding (string | number; optional):
        Key of theme.spacing or any valid CSS value to set content,
        header and footer padding, 'md' by default.

    - radius (string | number; optional):
        Key of theme.radius or any valid CSS value to set
        border-radius, theme.defaultRadius by default.

    - returnFocus (boolean; optional):
        Determines whether focus should be returned to the last active
        element onClose is called, True by default.

    - shadow (string; optional):
        Key of theme.shadows or any valid css box-shadow value, 'xl'
        by default.

    - size (string | number; optional):
        Controls content width, 'md' by default.

    - target (string; optional):
        Target element selector where Portal should be rendered, by
        default new element is created and appended to the
        document.body.

    - title (a list of or a singular dash component, string or number; optional):
        Modal title.

    - transitionProps (dict; optional):
        Props added to Transition component that used to animate
        overlay and body, use to configure duration and animation
        type, { duration: 200, transition: 'pop' } by default.

        `transitionProps` is a dict with keys:

        - duration (number; optional):
            Transition duration in ms.

        - exitDuration (number; optional):
            Exit transition duration in ms.

        - keepMounted (boolean; optional):
            If set element will not be unmounted from the DOM when it
            is hidden, display: none styles will be added instead.

        - mounted (boolean; required):
            When True, component will be mounted.

        - timingFunction (string; optional):
            Transition timing function, defaults to
            theme.transitionTimingFunction.

        - transition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; required):
            Predefined transition name or transition styles.

    - trapFocus (boolean; optional):
        Determines whether focus should be trapped, True by default.

    - withCloseButton (boolean; optional):
        Determines whether close button should be rendered, True by
        default.

    - withOverlay (boolean; optional):
        Determines whether overlay should be rendered, True by
        default.

    - withinPortal (boolean; optional):
        Determines whether component should be rendered inside Portal,
        True by default.

    - xOffset (string | number; optional):
        Left/right modal offset, 5vw by default.

    - yOffset (string | number; optional):
        Top/bottom modal offset, 5vh by default.

    - zIndex (number; optional):
        z-index CSS property of root element, 200 by default.

- monthLabelFormat (string; optional):
    dayjs label format to display month label.

- monthsListFormat (string; optional):
    dayjs format for months list.

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

- nextDisabled (boolean; optional):
    Determines whether next control should be disabled, defaults to
    True.

- nextIcon (a list of or a singular dash component, string or number; optional):
    Change next icon.

- nextLabel (string; optional):
    aria-label for next button.

- numberOfColumns (number; optional):
    Number of columns to render next to each other.

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

- popoverProps (dict; optional):
    Props added to Popover component.

    `popoverProps` is a dict with keys:

    - arrowOffset (number; optional):
        Arrow offset.

    - arrowPosition (a value equal to: 'center', 'side'; optional):
        Arrow position *.

    - arrowRadius (number; optional):
        Arrow border-radius.

    - arrowSize (number; optional):
        Arrow size.

    - clickOutsideEvents (list of strings; optional):
        Events that trigger outside clicks.

    - closeOnClickOutside (boolean; optional):
        Determines whether dropdown should be closed on outside
        clicks, default to True.

    - closeOnEscape (boolean; optional):
        Determines whether dropdown should be closed when Escape key
        is pressed, defaults to True.

    - defaultOpened (boolean; optional):
        Initial opened state for uncontrolled component.

    - disabled (boolean; optional):
        If set, popover dropdown will not render.

    - id (string; optional):
        id base to create accessibility connections.

    - keepMounted (boolean; optional):
        If set dropdown will not be unmounted from the DOM when it is
        hidden, display: none styles will be added instead.

    - middlewares (dict; optional):
        Floating ui middlewares to configure position handling.

        `middlewares` is a dict with keys:

        - flip (boolean; required)

        - inline (boolean; optional)

        - shift (boolean; required)

    - offset (number; optional):
        Default Y axis or either (main, cross, alignment) X and Y axis
        space between target element and dropdown.

    - opened (boolean; optional):
        Controls dropdown opened state.

    - position (a value equal to: 'left', 'right', 'top', 'bottom', 'left-end', 'left-start', 'right-end', 'right-start', 'top-end', 'top-start', 'bottom-end', 'bottom-start'; optional):
        Dropdown position relative to target.

    - positionDependencies (list of boolean | number | string | dict | lists; optional):
        useEffect dependencies to force update dropdown position.

    - radius (string | number; optional):
        Key of theme.radius or any valid CSS value to set
        border-radius, theme.defaultRadius by default.

    - returnFocus (boolean; optional):
        Determines whether focus should be automatically returned to
        control when dropdown closes, False by default.

    - shadow (string; optional):
        Key of theme.shadow or any other valid css box-shadow value.

    - transitionProps (dict; optional):
        Props added to Transition component that used to animate
        dropdown presence, use to configure duration and animation
        type, { duration: 150, transition: 'fade' } by default.

        `transitionProps` is a dict with keys:

        - duration (number; optional):
            Transition duration in ms.

        - exitDuration (number; optional):
            Exit transition duration in ms.

        - keepMounted (boolean; optional):
            If set element will not be unmounted from the DOM when it
            is hidden, display: none styles will be added instead.

        - timingFunction (string; optional):
            Transition timing function, defaults to
            theme.transitionTimingFunction.

        - transition (a value equal to: 'fade', 'skew-up', 'skew-down', 'rotate-right', 'rotate-left', 'slide-down', 'slide-up', 'slide-right', 'slide-left', 'scale-y', 'scale-x', 'scale', 'pop', 'pop-top-left', 'pop-top-right', 'pop-bottom-left', 'pop-bottom-right'; required):
            Predefined transition name or transition styles.

    - trapFocus (boolean; optional):
        Determines whether focus should be trapped within dropdown,
        default to False.

    - width (number; optional):
        Dropdown width, or 'target' to make dropdown width the same as
        target element.

    - withArrow (boolean; optional):
        Determines whether component should have an arrow.

    - withRoles (boolean; optional):
        Determines whether dropdown and target element should have
        accessible roles, defaults to True.

    - withinPortal (boolean; optional):
        Determines whether dropdown should be rendered within Portal,
        defaults to False.

    - zIndex (number; optional):
        Dropdown z-index.

- pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
    position.

- pr (string | number; optional):
    paddingRight.

- preserveTime (boolean; optional):
    Determines whether time (hours, minutes, seconds and milliseconds)
    should be preserved when new date is picked, True by default.

- previousDisabled (boolean; optional):
    Determines whether previous control should be disabled, defaults
    to True.

- previousIcon (a list of or a singular dash component, string or number; optional):
    Change previous icon.

- previousLabel (string; optional):
    aria-label for previous button.

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
    Determines whether the user can modify the value.

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

- size (string; optional):
    Input size   Component size   Controls size.

- sortDates (boolean; optional):
    Determines whether dates value should be sorted before onChange
    call, only applicable when type=\"multiple\", True by default.

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

- value (string; optional):
    Value for controlled component.

- valueFormat (string; optional):
    Dayjs format to display input value, \"MMMM D, YYYY\" by default.

- variant (a value equal to: 'default', 'filled', 'unstyled'; optional):
    Defines input appearance, defaults to default in light color
    scheme and filled in dark.

- w (string | number; optional):
    width.

- weekdayFormat (string; optional):
    dayjs format for weekdays names, defaults to \"dd\".

- weekendDays (list of a value equal to: 0, 1, 2, 3, 4, 5, 6s; optional):
    Indices of weekend days, 0-6, where 0 is Sunday and 6 is Saturday,
    defaults to value defined in DatesProvider.

- withAsterisk (boolean; optional):
    Determines whether required asterisk should be rendered, overrides
    required prop, does not add required attribute to the input.

- withCellSpacing (boolean; optional):
    Determines whether controls should be separated by spacing, True
    by default.

- withNext (boolean; optional):
    Determines whether next control should be rendered, defaults to
    True.

- withPrevious (boolean; optional):
    Determines whether previous control should be rendered, defaults
    to True.

- wrapperProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Properties spread to root element.

- yearLabelFormat (string; optional):
    dayjs label format to display year label.

- yearsListFormat (string; optional):
    dayjs format for years list."""
    _children_props = ['icon', 'rightSection', 'label', 'description', 'error', 'nextIcon', 'previousIcon', 'modalProps.title', 'modalProps.closeButtonProps.children']
    _base_nodes = ['icon', 'rightSection', 'label', 'description', 'error', 'nextIcon', 'previousIcon', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'DateInput'
    @_explicitize_args
    def __init__(self, disabledDates=Component.UNDEFINED, n_submit=Component.UNDEFINED, debounce=Component.UNDEFINED, value=Component.UNDEFINED, popoverProps=Component.UNDEFINED, clearable=Component.UNDEFINED, clearButtonProps=Component.UNDEFINED, valueFormat=Component.UNDEFINED, fixOnBlur=Component.UNDEFINED, allowDeselect=Component.UNDEFINED, preserveTime=Component.UNDEFINED, maxLevel=Component.UNDEFINED, level=Component.UNDEFINED, numberOfColumns=Component.UNDEFINED, columnsToScroll=Component.UNDEFINED, ariaLabels=Component.UNDEFINED, icon=Component.UNDEFINED, iconWidth=Component.UNDEFINED, rightSection=Component.UNDEFINED, rightSectionWidth=Component.UNDEFINED, rightSectionProps=Component.UNDEFINED, wrapperProps=Component.UNDEFINED, radius=Component.UNDEFINED, variant=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, placeholder=Component.UNDEFINED, name=Component.UNDEFINED, label=Component.UNDEFINED, description=Component.UNDEFINED, error=Component.UNDEFINED, required=Component.UNDEFINED, withAsterisk=Component.UNDEFINED, labelProps=Component.UNDEFINED, descriptionProps=Component.UNDEFINED, errorProps=Component.UNDEFINED, inputWrapperOrder=Component.UNDEFINED, decadeLabelFormat=Component.UNDEFINED, yearsListFormat=Component.UNDEFINED, withCellSpacing=Component.UNDEFINED, minDate=Component.UNDEFINED, maxDate=Component.UNDEFINED, locale=Component.UNDEFINED, nextIcon=Component.UNDEFINED, previousIcon=Component.UNDEFINED, nextLabel=Component.UNDEFINED, previousLabel=Component.UNDEFINED, nextDisabled=Component.UNDEFINED, previousDisabled=Component.UNDEFINED, hasNextLevel=Component.UNDEFINED, withNext=Component.UNDEFINED, withPrevious=Component.UNDEFINED, yearLabelFormat=Component.UNDEFINED, monthsListFormat=Component.UNDEFINED, monthLabelFormat=Component.UNDEFINED, firstDayOfWeek=Component.UNDEFINED, weekdayFormat=Component.UNDEFINED, weekendDays=Component.UNDEFINED, hideOutsideDates=Component.UNDEFINED, hideWeekdays=Component.UNDEFINED, closeOnChange=Component.UNDEFINED, dropdownType=Component.UNDEFINED, modalProps=Component.UNDEFINED, readOnly=Component.UNDEFINED, sortDates=Component.UNDEFINED, labelSeparator=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allowDeselect', 'aria-*', 'ariaLabels', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'clearButtonProps', 'clearable', 'closeOnChange', 'columnsToScroll', 'data-*', 'debounce', 'decadeLabelFormat', 'description', 'descriptionProps', 'disabled', 'disabledDates', 'display', 'dropdownType', 'error', 'errorProps', 'ff', 'firstDayOfWeek', 'fixOnBlur', 'fs', 'fw', 'fz', 'h', 'hasNextLevel', 'hideOutsideDates', 'hideWeekdays', 'icon', 'iconWidth', 'inputWrapperOrder', 'inset', 'label', 'labelProps', 'labelSeparator', 'left', 'level', 'lh', 'locale', 'lts', 'm', 'mah', 'maw', 'maxDate', 'maxLevel', 'mb', 'mih', 'minDate', 'miw', 'ml', 'modalProps', 'monthLabelFormat', 'monthsListFormat', 'mr', 'mt', 'mx', 'my', 'n_submit', 'name', 'nextDisabled', 'nextIcon', 'nextLabel', 'numberOfColumns', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'placeholder', 'popoverProps', 'pos', 'pr', 'preserveTime', 'previousDisabled', 'previousIcon', 'previousLabel', 'pt', 'px', 'py', 'radius', 'readOnly', 'required', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'size', 'sortDates', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'value', 'valueFormat', 'variant', 'w', 'weekdayFormat', 'weekendDays', 'withAsterisk', 'withCellSpacing', 'withNext', 'withPrevious', 'wrapperProps', 'yearLabelFormat', 'yearsListFormat']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'allowDeselect', 'aria-*', 'ariaLabels', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'clearButtonProps', 'clearable', 'closeOnChange', 'columnsToScroll', 'data-*', 'debounce', 'decadeLabelFormat', 'description', 'descriptionProps', 'disabled', 'disabledDates', 'display', 'dropdownType', 'error', 'errorProps', 'ff', 'firstDayOfWeek', 'fixOnBlur', 'fs', 'fw', 'fz', 'h', 'hasNextLevel', 'hideOutsideDates', 'hideWeekdays', 'icon', 'iconWidth', 'inputWrapperOrder', 'inset', 'label', 'labelProps', 'labelSeparator', 'left', 'level', 'lh', 'locale', 'lts', 'm', 'mah', 'maw', 'maxDate', 'maxLevel', 'mb', 'mih', 'minDate', 'miw', 'ml', 'modalProps', 'monthLabelFormat', 'monthsListFormat', 'mr', 'mt', 'mx', 'my', 'n_submit', 'name', 'nextDisabled', 'nextIcon', 'nextLabel', 'numberOfColumns', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'placeholder', 'popoverProps', 'pos', 'pr', 'preserveTime', 'previousDisabled', 'previousIcon', 'previousLabel', 'pt', 'px', 'py', 'radius', 'readOnly', 'required', 'right', 'rightSection', 'rightSectionProps', 'rightSectionWidth', 'size', 'sortDates', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'unstyled', 'value', 'valueFormat', 'variant', 'w', 'weekdayFormat', 'weekendDays', 'withAsterisk', 'withCellSpacing', 'withNext', 'withPrevious', 'wrapperProps', 'yearLabelFormat', 'yearsListFormat']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DateInput, self).__init__(**args)
