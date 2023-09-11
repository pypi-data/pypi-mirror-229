# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DatePicker(Component):
    """A DatePicker component.
ine date, multiple dates and dates range picker.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allowDeselect (boolean; optional):
    Determines whether user can deselect the date by clicking on
    selected item, applicable only when type=\"default\".

- allowSingleDateInRange (boolean; optional):
    Determines whether single year can be selected as range,
    applicable only when type=\"range\".

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

- columnsToScroll (number; optional):
    Number of columns to scroll when user clicks next/prev buttons,
    defaults to numberOfColumns.

- data-* (string; optional):
    Wild card data attributes.

- decadeLabelFormat (string; optional):
    dayjs label format to display decade label.

- disabledDates (list of strings; optional):
    Specifies days that should be disabled.

- display (a value equal to: 'initial', 'inherit', 'none', 'inline', 'block', 'contents', 'flex', 'grid', 'inline-block', 'inline-flex', 'inline-grid', 'inline-table', 'list-item', 'run-in', 'table', 'table-caption', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-row-group', 'table-cell', 'table-column', 'table-row'; optional):
    display.

- ff (string; optional):
    fontFamily.

- firstDayOfWeek (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional):
    number 0-6, 0 – Sunday, 6 – Saturday, defaults to 1 – Monday.

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

- inset (string | number; optional):
    inset.

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

- pos (a value equal to: 'initial', 'inherit', 'fixed', 'static', 'absolute', 'relative', 'sticky'; optional):
    position.

- pr (string | number; optional):
    paddingRight.

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

- right (string | number; optional):
    right.

- size (string; optional):
    Component size   Controls size.

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

- type (a value equal to: 'default', 'multiple', 'range'; optional):
    Picker type: range, multiple or default.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- value (string | list of strings; optional):
    Value for controlled component.

- variant (string; optional):
    variant.

- w (string | number; optional):
    width.

- weekdayFormat (string; optional):
    dayjs format for weekdays names, defaults to \"dd\".

- weekendDays (list of a value equal to: 0, 1, 2, 3, 4, 5, 6s; optional):
    Indices of weekend days, 0-6, where 0 is Sunday and 6 is Saturday,
    defaults to value defined in DatesProvider.

- withCellSpacing (boolean; optional):
    Determines whether controls should be separated by spacing, True
    by default.

- withNext (boolean; optional):
    Determines whether next control should be rendered, defaults to
    True.

- withPrevious (boolean; optional):
    Determines whether previous control should be rendered, defaults
    to True.

- yearLabelFormat (string; optional):
    dayjs label format to display year label.

- yearsListFormat (string; optional):
    dayjs format for years list."""
    _children_props = ['nextIcon', 'previousIcon']
    _base_nodes = ['nextIcon', 'previousIcon', 'children']
    _namespace = 'dash_mantine_components'
    _type = 'DatePicker'
    @_explicitize_args
    def __init__(self, disabledDates=Component.UNDEFINED, maxLevel=Component.UNDEFINED, level=Component.UNDEFINED, type=Component.UNDEFINED, value=Component.UNDEFINED, allowDeselect=Component.UNDEFINED, allowSingleDateInRange=Component.UNDEFINED, decadeLabelFormat=Component.UNDEFINED, yearsListFormat=Component.UNDEFINED, size=Component.UNDEFINED, withCellSpacing=Component.UNDEFINED, minDate=Component.UNDEFINED, maxDate=Component.UNDEFINED, locale=Component.UNDEFINED, yearLabelFormat=Component.UNDEFINED, monthsListFormat=Component.UNDEFINED, monthLabelFormat=Component.UNDEFINED, firstDayOfWeek=Component.UNDEFINED, weekdayFormat=Component.UNDEFINED, weekendDays=Component.UNDEFINED, hideOutsideDates=Component.UNDEFINED, hideWeekdays=Component.UNDEFINED, numberOfColumns=Component.UNDEFINED, columnsToScroll=Component.UNDEFINED, ariaLabels=Component.UNDEFINED, nextIcon=Component.UNDEFINED, previousIcon=Component.UNDEFINED, nextLabel=Component.UNDEFINED, previousLabel=Component.UNDEFINED, nextDisabled=Component.UNDEFINED, previousDisabled=Component.UNDEFINED, hasNextLevel=Component.UNDEFINED, withNext=Component.UNDEFINED, withPrevious=Component.UNDEFINED, variant=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, id=Component.UNDEFINED, m=Component.UNDEFINED, my=Component.UNDEFINED, mx=Component.UNDEFINED, mt=Component.UNDEFINED, mb=Component.UNDEFINED, ml=Component.UNDEFINED, mr=Component.UNDEFINED, p=Component.UNDEFINED, py=Component.UNDEFINED, px=Component.UNDEFINED, pt=Component.UNDEFINED, pb=Component.UNDEFINED, pl=Component.UNDEFINED, pr=Component.UNDEFINED, bg=Component.UNDEFINED, c=Component.UNDEFINED, opacity=Component.UNDEFINED, ff=Component.UNDEFINED, fz=Component.UNDEFINED, fw=Component.UNDEFINED, lts=Component.UNDEFINED, ta=Component.UNDEFINED, lh=Component.UNDEFINED, fs=Component.UNDEFINED, tt=Component.UNDEFINED, td=Component.UNDEFINED, w=Component.UNDEFINED, miw=Component.UNDEFINED, maw=Component.UNDEFINED, h=Component.UNDEFINED, mih=Component.UNDEFINED, mah=Component.UNDEFINED, bgsz=Component.UNDEFINED, bgp=Component.UNDEFINED, bgr=Component.UNDEFINED, bga=Component.UNDEFINED, pos=Component.UNDEFINED, top=Component.UNDEFINED, left=Component.UNDEFINED, bottom=Component.UNDEFINED, right=Component.UNDEFINED, inset=Component.UNDEFINED, display=Component.UNDEFINED, classNames=Component.UNDEFINED, styles=Component.UNDEFINED, unstyled=Component.UNDEFINED, sx=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allowDeselect', 'allowSingleDateInRange', 'aria-*', 'ariaLabels', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'columnsToScroll', 'data-*', 'decadeLabelFormat', 'disabledDates', 'display', 'ff', 'firstDayOfWeek', 'fs', 'fw', 'fz', 'h', 'hasNextLevel', 'hideOutsideDates', 'hideWeekdays', 'inset', 'left', 'level', 'lh', 'locale', 'lts', 'm', 'mah', 'maw', 'maxDate', 'maxLevel', 'mb', 'mih', 'minDate', 'miw', 'ml', 'monthLabelFormat', 'monthsListFormat', 'mr', 'mt', 'mx', 'my', 'nextDisabled', 'nextIcon', 'nextLabel', 'numberOfColumns', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'pos', 'pr', 'previousDisabled', 'previousIcon', 'previousLabel', 'pt', 'px', 'py', 'right', 'size', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'type', 'unstyled', 'value', 'variant', 'w', 'weekdayFormat', 'weekendDays', 'withCellSpacing', 'withNext', 'withPrevious', 'yearLabelFormat', 'yearsListFormat']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['id', 'allowDeselect', 'allowSingleDateInRange', 'aria-*', 'ariaLabels', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bottom', 'c', 'className', 'classNames', 'columnsToScroll', 'data-*', 'decadeLabelFormat', 'disabledDates', 'display', 'ff', 'firstDayOfWeek', 'fs', 'fw', 'fz', 'h', 'hasNextLevel', 'hideOutsideDates', 'hideWeekdays', 'inset', 'left', 'level', 'lh', 'locale', 'lts', 'm', 'mah', 'maw', 'maxDate', 'maxLevel', 'mb', 'mih', 'minDate', 'miw', 'ml', 'monthLabelFormat', 'monthsListFormat', 'mr', 'mt', 'mx', 'my', 'nextDisabled', 'nextIcon', 'nextLabel', 'numberOfColumns', 'opacity', 'p', 'pb', 'persisted_props', 'persistence', 'persistence_type', 'pl', 'pos', 'pr', 'previousDisabled', 'previousIcon', 'previousLabel', 'pt', 'px', 'py', 'right', 'size', 'style', 'styles', 'sx', 'ta', 'td', 'top', 'tt', 'type', 'unstyled', 'value', 'variant', 'w', 'weekdayFormat', 'weekendDays', 'withCellSpacing', 'withNext', 'withPrevious', 'yearLabelFormat', 'yearsListFormat']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DatePicker, self).__init__(**args)
