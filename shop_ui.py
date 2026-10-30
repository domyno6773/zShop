"""HTML pages for the original Wii U eShop browser/applet.

No paid-content URLs, credentials, personal data, external assets, or modern
framework dependencies. All untrusted catalog fields are HTML-escaped.
"""
from html import escape
from urllib.parse import urlencode

PATH = "/ninja/wood_index.html"
VIEWS = {"home", "best", "new", "mario", "all", "search", "profile", "detail"}
GENRES = {
    "puzzle": "Rompicapo", "platform": "Avventura", "race": "Corse",
    "retro": "Classici", "mario": "Mario", "action": "Azione",
    "adventure": "Avventura", "sports": "Sport", "strategy": "Strategia",
}
PALETTES = {"puzzle", "platform", "race", "retro", "mario",
            "action", "adventure", "sports", "strategy"}


def safe(value):
    return escape(str(value), quote=True)


def link(view="home", **params):
    if view not in VIEWS:
        view = "home"
    return PATH + "?" + urlencode({"view": view, **params})


def genre(item):
    return GENRES.get(item["category"], "Gioco")


def cover(item, big=False):
    category = item["category"]
    if category not in PALETTES:
        category = "adventure"
    name = safe(item["name"])
    return (
        '<div class="cover cover-%s%s" aria-hidden="true">'
        '<span class="cover-symbol"></span>'
        '<span class="cover-label">zShop / DEMO</span>'
        '<span class="cover-name">%s</span>'
        "</div>"
    ) % (category, " cover-large" if big else "", name)


def tile(item, source="home"):
    href = safe(link("detail", title=item["id"], frm=source))
    return (
        '<a class="game-tile" href="%s">'
        '%s<span class="tile-text"><strong>%s</strong>'
        '<small>%s · Scheda dimostrativa</small></span></a>'
    ) % (href, cover(item), safe(item["name"]), safe(genre(item)))


def shelf(title, subtitle, entries, more_view, current_view="home"):
    cards = "".join(tile(item, current_view) for item in entries) or (
        '<div class="empty">Non ci sono giochi in questa categoria.</div>'
    )
    return (
        '<section class="shelf"><div class="section-heading"><div>'
        '<h2>%s</h2><p>%s</p></div><a class="more-link" href="%s">Vedi tutti <b>›</b></a>'
        '</div><div class="game-grid">%s</div></section>'
    ) % (safe(title), safe(subtitle), safe(link(more_view)), cards)


def categories():
    tabs = (
        ("all", "Software Wii U", "Tutti i titoli"),
        ("mario", "Mario", "Giochi di Mario"),
        ("new", "Novità", "Ultime uscite"),
        ("best", "Classifiche", "I più popolari"),
    )
    return (
        '<section class="category-strip" aria-label="Categorie">'
        + "".join(
            '<a class="category-box category-%s" href="%s"><strong>%s</strong>'
            '<small>%s</small><span class="category-arrow">›</span></a>'
            % (v, safe(link(v)), safe(title), safe(desc))
            for v, title, desc in tabs
        )
        + "</section>"
    )


def search_form(query=""):
    return (
        '<form class="search-form" action="%s" method="get" role="search">'
        '<input type="hidden" name="view" value="search">'
        '<label for="find-game">Cerca un software</label>'
        '<div class="search-controls">'
        '<input id="find-game" type="search" name="q" maxlength="60" '
        'value="%s" placeholder="Nome del gioco o genere">'
        '<button type="submit">Cerca</button></div></form>'
    ) % (PATH, safe(query))


def home(catalog):
    featured = sorted(catalog, key=lambda item: -int(item["popularity"]))
    latest = sorted(catalog, key=lambda item: item["release"], reverse=True)
    return (
        '<div class="home-banner"><div class="home-banner-text">'
        '<span class="eyebrow">BENVENUTO SU ZSHOP</span>'
        '<h1>Scopri il catalogo Wii U</h1>'
        '<p>Esplora la nostra anteprima del negozio, direttamente '
        'dall’eShop originale della console.</p>'
        '<a class="banner-cta" href="%s">Esplora i giochi <b>›</b></a>'
        '</div><div class="banner-illustration" aria-hidden="true">'
        '<div class="banner-disc"><span class="banner-bag"></span></div></div></div>'
        '%s'
        '%s'
        '%s'
        '%s'
    ) % (
        safe(link("all")), categories(),
        shelf("In evidenza", "Titoli dimostrativi selezionati", featured[:4], "best"),
        shelf("Ultime uscite", "Scopri i nuovi arrivi", latest[:4], "new"),
        '<div class="bottom-note">Il catalogo è una dimostrazione. '
        'Non sono disponibili acquisti o download.</div>',
    )


def list_page(view, catalog, query):
    if view == "best":
        heading, subtitle, entries = (
            "Classifiche", "Best Sellers · Titoli più popolari",
            sorted(catalog, key=lambda item: -int(item["popularity"]))
        )
    elif view == "new":
        heading, subtitle, entries = (
            "Ultime uscite", "New Releases · Ordinati per data",
            sorted(catalog, key=lambda item: item["release"], reverse=True)
        )
    elif view == "mario":
        heading, subtitle, entries = (
            "Giochi di Mario", "Mario Games · Collezione dimostrativa",
            [item for item in catalog if item["category"] == "mario"]
        )
    elif view == "search":
        heading, subtitle = "Risultati di ricerca", "Search · Cerca nel catalogo"
        needle = query.strip().casefold()
        entries = [
            item for item in catalog
            if needle and needle in (
                item["name"] + " " + item["description"] + " " + genre(item)
            ).casefold()
        ]
    else:
        heading, subtitle, entries = (
            "Tutti i giochi", "Software Wii U · Catalogo dimostrativo",
            sorted(catalog, key=lambda item: item["name"].casefold())
        )

    body = (
        '<div class="page-intro"><span class="eyebrow">CATALOGO SOFTWARE</span>'
        '<h1>%s</h1><p>%s</p></div>'
    ) % (safe(heading), safe(subtitle))
    if view == "search":
        body += search_form(query)
        if query.strip():
            body += '<p class="result-count">%d risultati per “%s”</p>' % (
                len(entries), safe(query.strip())
            )
        else:
            body += '<p class="result-count">Inserisci un termine per cercare.</p>'
    else:
        body += '<div class="results-toolbar"><span>%d titoli</span>' % len(entries)
        body += '<a href="%s">Torna alla Home</a></div>' % safe(link("home"))

    body += (
        '<div class="game-grid listing-grid">%s</div>'
        % ("".join(tile(item, view) for item in entries) if entries else
           '<div class="empty">Nessun titolo trovato. '
           '<a href="%s">Torna alla Home</a></div>' % safe(link("home")))
    )
    return body


def detail(catalog, title_id, frm):
    item = next((entry for entry in catalog if entry["id"] == title_id), None)
    if not item:
        return (
            '<div class="page-intro"><h1>Gioco non trovato</h1>'
            '<p>Questa scheda non esiste.</p>'
            '<a class="light-button" href="%s">Torna al catalogo</a></div>'
        ) % safe(link("all"))
    if frm not in VIEWS or frm == "detail":
        frm = "all"
    return (
        '<div class="crumbs"><a href="%s">‹ Torna all’elenco</a>'
        '<span> / Scheda software</span></div>'
        '<div class="detail-layout"><div class="detail-cover">%s</div>'
        '<div class="detail-info"><span class="eyebrow">SOFTWARE WII U · DEMO</span>'
        '<h1>%s</h1><p class="detail-category">%s</p>'
        '<div class="detail-description">%s</div>'
        '<table class="spec-table"><tr><th>Genere</th><td>%s</td></tr>'
        '<tr><th>Data</th><td>%s</td></tr>'
        '<tr><th>Distribuzione</th><td>Non disponibile in questa anteprima</td></tr>'
        '</table><div class="disabled-download">Download non disponibile</div>'
        '<p class="fine-print">Installation and downloads are disabled. '
        'Questa è una scheda di prova, senza acquisti o licenze.</p>'
        '</div></div>'
    ) % (
        safe(link(frm)), cover(item, True), safe(item["name"]),
        safe(genre(item)), safe(item["description"]), safe(genre(item)),
        safe(item["release"]),
    )


def profile():
    return (
        '<div class="page-intro"><span class="eyebrow">IL MIO MENU / MY PROFILE</span>'
        '<h1>Il mio menu</h1><p>Questa anteprima non accede al profilo Nintendo '
        'né all’account Pretendo.</p></div>'
        '<div class="profile-panel"><div class="profile-avatar" aria-hidden="true">?</div>'
        '<div class="profile-copy"><h2>Profilo non collegato</h2>'
        '<p>Nessun dato personale viene richiesto o salvato.</p>'
        '<p class="fine-print">Demo only: no Nintendo or Pretendo profile data is accessed.</p>'
        '</div></div>'
        '<div class="profile-links"><a href="%s">Torna alla Home <b>›</b></a>'
        '<a href="%s">Esplora il catalogo <b>›</b></a></div>'
    ) % (safe(link("home")), safe(link("all")))


def sidebar(view, frm='all'):
    home_active = ' class="selected"' if view == "home" else ""
    profile_active = ' class="selected"' if view == "profile" else ""
    search_active = ' class="selected"' if view == "search" else ""
    fallback = (frm if frm in VIEWS and frm != "detail" else "all") if view == "detail" else "home"
    return (
        '<aside class="side-menu" aria-label="Menu principale">'
        '<a href="%s"%s><span class="side-icon side-home">⌂</span>'
        '<span>Home</span><small>X</small></a>'
        '<a href="%s"%s title="My Profile"><span class="side-icon side-person">◉</span>'
        '<span>Il mio menu</span><small>Y</small></a>'
        '<div class="side-static"><span class="side-icon side-wallet">▣</span>'
        '<span>Anteprima</span><small>—</small></div>'
        '<a href="%s"%s><span class="side-icon side-search">⌕</span>'
        '<span>Cerca</span><small>–</small></a>'
        '<a id="back-button" href="%s"><span class="side-icon side-back">↶</span>'
        '<span>Indietro</span><small>B</small></a>'
        '</aside>'
    ) % (
        safe(link("home")), home_active,
        safe(link("profile")), profile_active,
        safe(link("search")), search_active,
        safe(link(fallback)),
    )


def topbar(view):
    items = (
        ("home", "Inizio"),
        ("all", "Giochi Wii U"),
        ("best", "Classifiche"),
        ("new", "Novità"),
        ("search", "Ricerca"),
    )
    return (
        '<div class="top-shell"><div class="shop-brand">'
        '<span class="bag-logo" aria-hidden="true">▣</span>'
        '<span><strong>zShop</strong><small>Wii U eShop experience</small></span>'
        '</div><nav class="top-tabs" aria-label="Navigazione negozio">'
        + "".join(
            '<a href="%s"%s>%s</a>' % (
                safe(link(v)), ' class="active"' if v == view else "", safe(label)
            ) for v, label in items
        )
        + '</nav></div>'
    )


def render_page(view, catalog, query="", title_id="", frm="all"):
    if view not in VIEWS:
        view = "home"
    if view == "home":
        content, page_title = home(catalog), "Home"
    elif view == "profile":
        content, page_title = profile(), "Il mio menu"
    elif view == "detail":
        content, page_title = detail(catalog, title_id, frm), "Scheda software"
    else:
        content, page_title = list_page(view, catalog, query), {
            "best": "Classifiche", "new": "Ultime uscite",
            "mario": "Giochi di Mario", "all": "Tutti i giochi",
            "search": "Cerca",
        }[view]

    return (
        '<!doctype html><html lang="it"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>%s — zShop Wii U</title>'
        '<link rel="stylesheet" type="text/css" href="/static/shop.css">'
        '</head><body data-view="%s"><div class="screen">'
        '%s<div class="shop-area">%s'
        '<div class="content-area">%s</div>'
        '<footer class="footer"><span>zShop · Anteprima non ufficiale</span>'
        '<span>Download e acquisti disattivati</span></footer></div></div>'
        '<script type="text/javascript" src="/static/shop.js"></script>'
        '</body></html>'
    ) % (safe(page_title), safe(view), sidebar(view, frm), topbar(view), content)
