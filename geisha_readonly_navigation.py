"""Read-only navigation in the archived Geisha DOM.

The original Nintendo CSS and page structure remain local/user-supplied.
No archived JavaScript, user accounts, commerce, external URLs or console
installation APIs are involved. The results use local placeholder titles.
"""
import re
from html import escape
from urllib.parse import quote

from geisha_preview_renderer import original_style_menu

SEARCH_HEADER = re.compile(
    r'(?is)(<div\s+id=["\']header["\']\s*>)(.*?)(</div\s*>)'
)
SEARCH_LINK = re.compile(
    r'(?is)<a\b(?=[^>]*class=["\'][^"\']*\bsearch-submit\b)[^>]*>(.*?)</a\s*>'
)
RESULTS_LIST = re.compile(
    r'(?is)<ul\b(?=[^>]*\bid=["\']shelf-list["\'])[^>]*>.*?</ul\s*>'
)
PAGINATION = re.compile(
    r'(?is)<div\s+class=["\']pagenation["\']\s*>.*?</div\s*>'
)
ARCHIVE_MENU = re.compile(
    r'(?is)<div\s+id=["\']sel_menu_bar["\']\s*>'
    r'\s*<ul\s+id=["\']ft_navi["\']\s*>.*?</ul\s*></div\s*>'
)


def hydrate_search(page):
    """Make the archived search field submit with a native GET form.

    Preserve the actual Geisha header, search-submit and search-label CSS
    classes. Do not re-enable the archive's modified environment.js.
    """
    def transform(match):
        raw = match.group(2)
        if not SEARCH_LINK.search(raw) or 'name="freeword"' not in raw:
            return match.group(0)
        raw = SEARCH_LINK.sub(
            lambda item: '<button type="submit" class="search-submit se">'
                         + item.group(1) + '</button>',
            raw, count=1,
        )
        return (match.group(1) +
                '<form method="get" action="shelf02_01.html" '
                'id="zshop-safe-search">' +
                raw + '</form>' + match.group(3))

    result = SEARCH_HEADER.sub(transform, page, count=1)
    return ARCHIVE_MENU.sub(lambda _: original_style_menu(), result, count=1)


def _local_titles(catalog, query):
    keyword = query.strip().casefold()
    if keyword:
        return [entry for entry in catalog if keyword in (
            str(entry.get("name", "")) + " " +
            str(entry.get("category", "")) + " " +
            str(entry.get("description", ""))
        ).casefold()]
    return sorted(catalog, key=lambda entry: -int(entry.get("popularity", 0)))


def _row(entry):
    """Use class names from Geisha's historical shelf templates."""
    name = escape(str(entry.get("name", "")))
    category = escape(str(entry.get("category", "")))
    release = escape(str(entry.get("release", "")))
    return (
        '<li class="m-list-item">'
        '<div class="list-title-outline">'
        '<div class="list-title-icon"><div class="p-icon-wup-L">'
        '<img src="image/placeholder/place_icon_wii_u.png" '
        'width="128" height="128"></div></div>'
        '<div class="list-title-summary">'
        '<div class="name">%s</div>'
        '<div class="platform text-wup">Wii U · Demo</div>'
        '<div class="information"><span class="publisher">%s</span>'
        '<span class="rating">%s</span></div>'
        '</div></div>'
        '<div class="list-title-action"><div class="el-purchase">'
        '<div class="disable"><span>Anteprima, nessun download</span>'
        '</div></div></div></li>'
    ) % (name, category, release)


def hydrate_shelf(page, catalog, query=""):
    """Populate #shelf-list from a local demo catalog; no network/API calls."""
    if not RESULTS_LIST.search(page):
        return page
    query = query[:50]
    items = _local_titles(catalog, query)[:32]
    contents = "".join(_row(item) for item in items)
    if not items:
        contents = (
            '<li class="no-result">Nessun risultato nel catalogo demo.</li>'
        )
    shelf = ('<ul id="shelf-list" class="shelf-list-item" '
             'data-isloaded="true">' + contents + '</ul>')
    result = RESULTS_LIST.sub(lambda _: shelf, page, count=1)
    result = PAGINATION.sub("", result)
    result = re.sub(
        r'(?is)<span\s+class=["\']total-results["\'][^>]*>.*?</span>',
        lambda _: '<span class="total-results">Results: %d</span>' % len(items),
        result, count=1,
    )
    if query.strip():
        result = result.replace('<h1>Charts</h1>', '<h1>Search Results</h1>', 1)
    result = ARCHIVE_MENU.sub(lambda _: original_style_menu(), result, count=1)
    # Archived shelf pages contain TWO wrappers: a hidden bootstrap #wrapper
    # plus the real original js-shelf wrapper. The former must not overlay the
    # latter when the diagnostic visibility override reveals #wrapper.
    result = re.sub(
        r'(?i)</head\s*>',
        '<style id="zshop-shelf-visibility">'
        '#wrapper.js-top{display:none!important}'
        '#wrapper.js-shelf{display:block!important}'
        '</style></head>',
        result, count=1,
    )
    # Original sort control requires JavaScript; prevent an inert interaction.
    result = result.replace('<select id="el-sort">',
                            '<select id="el-sort" disabled="disabled">', 1)
    return result
