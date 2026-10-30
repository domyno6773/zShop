"""Static hydration for historical Geisha markup, without executing source JS.

This is a limited READ-ONLY preview of the actual archived layout structure:
- preserves archived index.html and its official CSS/images;
- fills the exact #el-top, #sel_menu_bar elements that the original client JS
  normally fills; uses HTML classes from the archived template and menu JS;
- supplies inert local demo data, never pretends the live shop backend exists.
"""
import re
from html import escape
from urllib.parse import quote

HOME_LIST = re.compile(
    r'(?is)<ul\b(?=[^>]*\bid\s*=\s*["\']el-top["\'])[^>]*>.*?</ul>'
)
MENU_SLOT = re.compile(
    r'(?is)<div\s+id\s*=\s*["\']sel_menu_bar["\']\s*>\s*</div>'
)

# Existing Geisha menu CSS expects exactly these IDs and element classes.
# No active NNID/PNID/account/balance/redeem or download links are enabled.
def original_style_menu():
    items = (
        ("top_link_01", "top", "Home", "index.html", ""),
        ("top_link_02", "menu off", "My Menu", None,
         '<img src="image/img_unknown_MiiIcon.png" width="70" height="70"><br>'),
        ("top_link_03", "balance off", "Balance", None, ""),
        ("top_link_04", "search", "Search", "always02_01.html", ""),
        ("top_link_05", "back", "Back", "index.html", ""),
    )
    parts = ['<div id="sel_menu_bar"><ul id="ft_navi">']
    for ident, style, label, href, prefix in items:
        start = '<li id="%s" class="%s"><div>' % (ident, style)
        if href:
            start += '<a href="%s">' % escape(href, quote=True)
        start += prefix + '<span>%s</span>' % escape(label)
        if href:
            start += "</a>"
        parts.append(start + "</div></li>")
    parts.append("</ul></div>")
    return "".join(parts)


def original_style_tiles(catalog):
    # This <li class=top-content> subtree comes from the archived
    # #template_top_content, not an invented eShop layout.
    content = []
    for item in sorted(catalog, key=lambda x: -int(x.get("popularity", 0)))[:8]:
        title = escape(str(item.get("name", "")))
        content.append(
            '<li class="top-content"><a href="shelf02_01.html?q=%s">'
            '<img src="image/placeholder/place_banner.png"'
            ' width="300" height="180" class="top-content-img lazy"></a>'
            '<span class="top-content-caption" style="width:300px;">%s</span>'
            '</li>' % (quote(str(item.get("name", ""))), title)
        )
    if not content:
        content.append(
            '<li class="top-content"><span class="top-content-caption">'
            'No local demo catalog</span></li>'
        )
    return '<ul id="el-top" class="top-main" data-isloaded="true">%s</ul>' % (
        "".join(content)
    )


def hydrate_index(page, catalog):
    """Replace archived loading placeholders using archived DOM class names.

    No JS and no original account/commercial methods are called. If an
    unrecognized archive layout is given, leave it unmodified rather than
    overlaying a mock UI.
    """
    if not HOME_LIST.search(page):
        return page
    result = HOME_LIST.sub(lambda _: original_style_tiles(catalog), page, count=1)
    return MENU_SLOT.sub(lambda _: original_style_menu(), result, count=1)
