# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Drawer(Component):
    """A Drawer component.
play overlay area at any side of the screen

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Drawer Content *   Child component.

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
        Props added to Loader component (only visible when `loading`
        prop is set).

        `loaderProps` is a dict with keys:

        - color (string; optional):

            Loader color from theme.

        - size (string

              Or number; optional):

            Defines width of loader.

        - variant (a value equal to: 'bars', 'oval', 'dots'; optional):

            Loader appearance. | dict with keys:

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

    - n_clicks (number; optional):
        An integer that represents the number of times that this
        element has been clicked on.

    - radius (string | number; optional):
        Key of theme.radius or any valid CSS value to set
        border-radius, theme.defaultRadius by default.

    - size (string | number; optional):
        Predefined button size or any valid CSS value to set width and
        height.

    - variant (a value equal to: 'subtle', 'filled', 'outline', 'light', 'default', 'transparent', 'gradient'; optional):
        Controls appearance, subtle by default. | dict with keys:

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
        Remove all Mantine styling from the component. | dict with keys:

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
        Inline style.

- closeOnClickOutside (boolean; optional):
    Determines whether the modal/drawer should be closed when user
    clicks on the overlay, True by default.

- closeOnEscape (boolean; optional):
    Determines whether onClose should be called when user presses
    escape key, True by default.

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

- keepMounted (boolean; optional):
    If set modal/drawer will not be unmounted from the DOM when it is
    hidden, display: none styles will be added instead.

- left (string | number; optional):
    left.

- lh (string | number; optional):
    lineHeight.

- lockScroll (boolean; optional):
    Determines whether scroll should be locked when opened={True},
    defaults to True.

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

- opened (boolean; default False):
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
        Overlay z-index, 200 by default. | dict with keys:

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

- p (string | number; optional):
    padding.

- padding (string | number; optional):
    Key of theme.spacing or any valid CSS value to set content, header
    and footer padding, 'md' by default.

- pb (string | number; optional):
    paddingBottom.

- pl (string | number; optional):
    paddingLeft.

- pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
    position.

- position (a value equal to: 'left', 'right', 'top', 'bottom'; optional):
    Side of the screen where drawer will be opened, 'left' by default.

- pr (string | number; optional):
    paddingRight.

- pt (string | number; optional):
    paddingTop.

- px (string | number; optional):
    paddingRight, paddingLeft.

- py (string | number; optional):
    paddingTop, paddingBottom.

- returnFocus (boolean; optional):
    Determines whether focus should be returned to the last active
    element onClose is called, True by default.

- right (string | number; optional):
    right.

- shadow (string; optional):
    Key of theme.shadows or any valid css box-shadow value, 'xl' by
    default.

- size (string | number; optional):
    Controls content width, 'md' by default.

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

- target (string; optional):
    Target element selector where Portal should be rendered, by
    default new element is created and appended to the document.body.

- td (a value equal to: 'initial', 'inherit', 'none', 'underline', 'overline', 'line-through'; optional):
    textDecoration.

- title (a list of or a singular dash component, string or number; optional):
    Modal title.

- top (string | number; optional):
    top.

- transitionProps (dict; optional):
    Props added to Transition component that used to animate overlay
    and body, use to configure duration and animation type, {
    duration: 200, transition: 'pop' } by default.

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

- trapFocus (boolean; optional):
    Determines whether focus should be trapped, True by default.

- tt (a value equal to: 'initial', 'inherit', 'none', 'capitalize', 'uppercase', 'lowercase'; optional):
    textTransform.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- w (string | number; optional):
    width.

- withCloseButton (boolean; optional):
    Determines whether close button should be rendered, True by
    default.

- withOverlay (boolean; optional):
    Determines whether overlay should be rendered, True by default.

- withinPortal (boolean; optional):
    Determines whether component should be rendered inside Portal,
    True by default.

- zIndex (number; optional):
    z-index CSS property of root element, 200 by default."""
    _children_props = ['title', 'closeButtonProps.children']
    _base_nodes = ['title', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'Drawer'
    @_explicitize_args
    def __init__(self, children=None, position=Component.UNDEFINED, title=Component.UNDEFINED, withOverlay=Component.UNDEFINED, overlayProps=Component.UNDEFINED, withCloseButton=Component.UNDEFINED, closeButtonProps=Component.UNDEFINED, keepMounted=Component.UNDEFINED, opened=Component.UNDEFINED, closeOnClickOutside=Component.UNDEFINED, transitionProps=Component.UNDEFINED, withinPortal=Component.UNDEFINED, target=Component.UNDEFINED, lockScroll=Component.UNDEFINED, trapFocus=Component.UNDEFINED, zIndex=Component.UNDEFINED, padding=Component.UNDEFINED, returnFocus=Component.UNDEFINED, closeOnEscape=Component.UNDEFINED, size=Component.UNDEFINED, shadow=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeButtonProps', 'closeOnClickOutside', 'closeOnEscape', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'keepMounted', 'left', 'lh', 'lockScroll', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'opened', 'overlayProps', 'p', 'padding', 'pb', 'pl', 'pos', 'position', 'pr', 'pt', 'px', 'py', 'returnFocus', 'right', 'shadow', 'size', 'style', 'styles', 'sx', 'ta', 'target', 'td', 'title', 'top', 'transitionProps', 'trapFocus', 'tt', 'unstyled', 'w', 'withCloseButton', 'withOverlay', 'withinPortal', 'zIndex']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'closeButtonProps', 'closeOnClickOutside', 'closeOnEscape', 'data-*', 'display', 'ff', 'fs', 'fw', 'fz', 'h', 'inset', 'keepMounted', 'left', 'lh', 'lockScroll', 'lts', 'm', 'mah', 'maw', 'mb', 'mih', 'miw', 'ml', 'mr', 'mt', 'mx', 'my', 'opacity', 'opened', 'overlayProps', 'p', 'padding', 'pb', 'pl', 'pos', 'position', 'pr', 'pt', 'px', 'py', 'returnFocus', 'right', 'shadow', 'size', 'style', 'styles', 'sx', 'ta', 'target', 'td', 'title', 'top', 'transitionProps', 'trapFocus', 'tt', 'unstyled', 'w', 'withCloseButton', 'withOverlay', 'withinPortal', 'zIndex']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Drawer, self).__init__(children=children, **args)
