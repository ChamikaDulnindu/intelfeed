#!/usr/bin/env python3
"""
intelFEED.sh — Tech Intelligence Dashboard for Kali Linux
Real RSS feeds: cybersecurity, bug bounty, web3, blockchain, ML, Linux, CTF
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
import feedparser
import threading
import webbrowser
import time
import json
import os
from datetime import datetime, timezone
from html import unescape
import re

# ─── Feed Sources ────────────────────────────────────────────────────────────
FEEDS = {
    "cybersecurity": [
        ("The Hacker News",      "https://feeds.feedburner.com/TheHackersNews"),
        ("Bleeping Computer",    "https://www.bleepingcomputer.com/feed/"),
        ("Krebs on Security",    "https://krebsonsecurity.com/feed/"),
        ("Dark Reading",         "https://www.darkreading.com/rss.xml"),
        ("NVD Recent CVEs",      "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss-analyzed.xml"),
    ],
    "web2-bugs": [
        ("PortSwigger Research", "https://portswigger.net/research/rss"),
        ("HackerOne Hacktivity", "https://hackerone.com/hacktivity.rss"),
        ("Bug Bounty Forum",     "https://bugbountyforum.com/feed/"),
        ("InfoSecWriteups",      "https://infosecwriteups.com/feed"),
    ],
    "web3-bugs": [
        ("Rekt News",            "https://rekt.news/rss/"),
        ("SlowMist",             "https://slowmist.medium.com/feed"),
        ("PeckShield Alert",     "https://peckshield.medium.com/feed"),
    ],
    "blockchain": [
        ("CoinDesk",             "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Decrypt",              "https://decrypt.co/feed"),
        ("The Block",            "https://www.theblock.co/rss.xml"),
    ],
    "ml-ai": [
        ("Towards Data Science", "https://towardsdatascience.com/feed"),
        ("ML Safety Newsletter", "https://newsletter.mlsafety.org/feed"),
        ("Hugging Face Blog",    "https://huggingface.co/blog/feed.xml"),
        ("The Gradient",         "https://thegradient.pub/rss/"),
    ],
    "linux": [
        ("LWN.net",              "https://lwn.net/headlines/rss"),
        ("Phoronix",             "https://www.phoronix.com/rss.php"),
        ("Linux Security",       "https://linuxsecurity.com/linuxsecurity_advisories.rdf"),
        ("OMG Ubuntu",           "https://www.omgubuntu.co.uk/feed"),
    ],
    "ctf": [
        ("CTFtime Events",       "https://ctftime.org/event/list/upcoming/rss/"),
        ("CTF Writeups",         "https://ctf-writeups.ru/?feed=rss2"),
        ("0day.work",            "https://0day.work/feed.xml"),
    ],
    "resources": [
        ("Hacker News",          "https://news.ycombinator.com/rss"),
        ("Security Weekly",      "https://feeds.megaphone.fm/securityweekly"),
        ("SANS Internet Storm",  "https://isc.sans.edu/rssfeed_full.xml"),
        ("Reddit netsec",        "https://www.reddit.com/r/netsec/.rss"),
    ],
}

CAT_COLORS = {
    "cybersecurity": "#ff4444",
    "web2-bugs":     "#f5a623",
    "web3-bugs":     "#4db8ff",
    "blockchain":    "#b388ff",
    "ml-ai":         "#40e0d0",
    "linux":         "#ff69b4",
    "ctf":           "#00e5ff",
    "resources":     "#39ff6a",
}

CAT_LABELS = {
    "cybersecurity": "CYBER",
    "web2-bugs":     "WEB2",
    "web3-bugs":     "WEB3",
    "blockchain":    "CHAIN",
    "ml-ai":         "ML/AI",
    "linux":         "LINUX",
    "ctf":           "CTF",
    "resources":     "RES",
}

CSS = b"""
* { font-family: 'JetBrains Mono', 'Fira Code', 'Monospace'; }

window {
    background-color: #0d0f0e;
}

#topbar {
    background-color: #141714;
    border-bottom: 1px solid #1f2e1f;
    padding: 10px 16px;
}

#logo {
    color: #39ff6a;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}

#statuslabel {
    color: #3a5a3a;
    font-size: 11px;
}

#filterbar {
    background-color: #0d0f0e;
    padding: 8px 14px;
    border-bottom: 1px solid #1a2a1a;
}

button.filter-btn {
    background: #141714;
    color: #3a5a3a;
    border: 1px solid #1f2e1f;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 11px;
    min-height: 0;
    min-width: 0;
}

button.filter-btn:hover {
    background: #1a2a1a;
    color: #c8d8c8;
}

button.filter-btn.active {
    background: #0d1a0d;
}

#searchbar {
    background-color: #0d0f0e;
    padding: 8px 14px;
    border-bottom: 1px solid #1a2a1a;
}

#search-entry {
    background-color: #141714;
    color: #c8d8c8;
    border: 1px solid #1f2e1f;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    caret-color: #39ff6a;
}

#search-entry:focus {
    border-color: #2a4a2a;
    outline: none;
}

#refresh-btn {
    background: #141714;
    color: #39ff6a;
    border: 1px solid #1f2e1f;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 11px;
    min-height: 0;
}

#refresh-btn:hover {
    background: #1a2a1a;
}

#refresh-btn:disabled {
    color: #2a4a2a;
}

#scrollwin {
    background-color: #0d0f0e;
}

.article-row {
    background-color: #141714;
    border: 1px solid #1a2a1a;
    border-radius: 8px;
    margin: 4px 12px;
    padding: 12px 14px;
}

.article-row:hover {
    border-color: #2a4a2a;
    background-color: #161e16;
}

.cat-badge {
    border-radius: 3px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

.article-title {
    color: #c8d8c8;
    font-size: 13px;
    font-weight: 500;
}

.article-desc {
    color: #4a6a4a;
    font-size: 11px;
}

.article-meta {
    color: #3a5a3a;
    font-size: 10px;
}

.open-btn {
    background: transparent;
    color: #39ff6a;
    border: 1px solid #1f2e1f;
    border-radius: 4px;
    font-size: 10px;
    padding: 3px 8px;
    min-height: 0;
    min-width: 0;
}

.open-btn:hover {
    background: #0d1a0d;
    border-color: #39ff6a;
}

#statusbar {
    background-color: #0a0c0a;
    border-top: 1px solid #1a2a1a;
    padding: 4px 14px;
}

#statustext {
    color: #2a4a2a;
    font-size: 10px;
}
"""

def strip_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:200]

def time_ago(entry):
    try:
        t = entry.get('published_parsed') or entry.get('updated_parsed')
        if not t:
            return "recent"
        pub = datetime(*t[:6], tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - pub
        s = diff.total_seconds()
        if s < 3600:   return f"{int(s//60)}m ago"
        if s < 86400:  return f"{int(s//3600)}h ago"
        return f"{int(s//86400)}d ago"
    except:
        return "recent"


class IntelFeed(Gtk.Window):
    def __init__(self):
        super().__init__(title="intelFEED.sh")
        self.set_default_size(1100, 750)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Apply CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.articles = []
        self.active_filter = "all"
        self.search_query = ""
        self.loading = False

        self._build_ui()
        self.connect("destroy", Gtk.main_quit)
        GLib.timeout_add(500, self._start_fetch)

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Top bar
        topbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        topbar.set_name("topbar")
        logo = Gtk.Label(label="// intelFEED.sh")
        logo.set_name("logo")
        topbar.pack_start(logo, False, False, 0)
        self.status_label = Gtk.Label(label="● initializing...")
        self.status_label.set_name("statuslabel")
        topbar.pack_end(self.status_label, False, False, 0)
        vbox.pack_start(topbar, False, False, 0)

        # Filter bar
        filterbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        filterbar.set_name("filterbar")
        self.filter_btns = {}
        for cat in ["all"] + list(FEEDS.keys()):
            label = "ALL" if cat == "all" else CAT_LABELS.get(cat, cat.upper())
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("filter-btn")
            if cat == "all":
                btn.get_style_context().add_class("active")
                color_css = f"button.filter-btn.active {{ color: #39ff6a; border-color: #39ff6a; }}"
            color = CAT_COLORS.get(cat, "#39ff6a")
            btn.connect("clicked", self._on_filter, cat)
            filterbar.pack_start(btn, False, False, 0)
            self.filter_btns[cat] = (btn, color)
        vbox.pack_start(filterbar, False, False, 0)

        # Search bar
        searchbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        searchbar.set_name("searchbar")
        self.search_entry = Gtk.Entry()
        self.search_entry.set_name("search-entry")
        self.search_entry.set_placeholder_text("grep articles...")
        self.search_entry.connect("changed", self._on_search)
        searchbar.pack_start(self.search_entry, True, True, 0)
        self.refresh_btn = Gtk.Button(label="⟳  refresh feed")
        self.refresh_btn.set_name("refresh-btn")
        self.refresh_btn.connect("clicked", self._on_refresh)
        searchbar.pack_start(self.refresh_btn, False, False, 0)
        vbox.pack_start(searchbar, False, False, 0)

        # Scrollable article list
        scrollwin = Gtk.ScrolledWindow()
        scrollwin.set_name("scrollwin")
        scrollwin.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.article_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.article_list.set_margin_top(8)
        self.article_list.set_margin_bottom(8)
        scrollwin.add(self.article_list)
        vbox.pack_start(scrollwin, True, True, 0)

        # Status bar
        statusbar = Gtk.Box()
        statusbar.set_name("statusbar")
        self.statustext = Gtk.Label(label="")
        self.statustext.set_name("statustext")
        statusbar.pack_start(self.statustext, False, False, 0)
        vbox.pack_start(statusbar, False, False, 0)

        self._show_placeholder("Initializing feed sources...")

    def _show_placeholder(self, msg):
        for child in self.article_list.get_children():
            self.article_list.remove(child)
        lbl = Gtk.Label(label=f"\n\n{msg}\n\n")
        lbl.set_name("statuslabel")
        self.article_list.pack_start(lbl, False, False, 20)
        self.article_list.show_all()

    def _start_fetch(self):
        self._fetch_feeds()
        return False

    def _on_refresh(self, btn):
        if not self.loading:
            self._fetch_feeds()

    def _fetch_feeds(self):
        self.loading = True
        self.refresh_btn.set_sensitive(False)
        self.status_label.set_text("● fetching...")
        self._show_placeholder("Querying intelligence sources...")
        thread = threading.Thread(target=self._fetch_worker, daemon=True)
        thread.start()

    def _fetch_worker(self):
        results = []
        cats_to_fetch = list(FEEDS.keys()) if self.active_filter == "all" else [self.active_filter]

        for cat in cats_to_fetch:
            sources = FEEDS.get(cat, [])
            for name, url in sources:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:
                        title = strip_html(entry.get('title', 'No title'))
                        link  = entry.get('link', '')
                        desc  = strip_html(entry.get('summary', entry.get('description', '')))
                        age   = time_ago(entry)
                        results.append({
                            'title':    title,
                            'desc':     desc[:150] + ('...' if len(desc) > 150 else ''),
                            'url':      link,
                            'source':   name,
                            'time':     age,
                            'category': cat,
                        })
                except Exception as e:
                    pass  # silently skip dead feeds

        # Sort newest-ish first (those with "m ago" or "h ago" first)
        def sort_key(a):
            t = a['time']
            if 'm ago' in t: return 0
            if 'h ago' in t: return 1
            return 2
        results.sort(key=sort_key)

        GLib.idle_add(self._on_fetch_done, results)

    def _on_fetch_done(self, articles):
        self.articles = articles
        self.loading = False
        self.refresh_btn.set_sensitive(True)
        now = datetime.now().strftime("%H:%M")
        self.status_label.set_text(f"● updated {now}")
        self._render_feed()
        return False

    def _on_filter(self, btn, cat):
        self.active_filter = cat
        for c, (b, color) in self.filter_btns.items():
            ctx = b.get_style_context()
            ctx.remove_class("active")
        self.filter_btns[cat][0].get_style_context().add_class("active")
        if self.articles:
            self._render_feed()
        else:
            self._fetch_feeds()

    def _on_search(self, entry):
        self.search_query = entry.get_text().lower()
        self._render_feed()

    def _render_feed(self):
        for child in self.article_list.get_children():
            self.article_list.remove(child)

        articles = self.articles
        if self.active_filter != "all":
            articles = [a for a in articles if a['category'] == self.active_filter]
        if self.search_query:
            articles = [a for a in articles if
                        self.search_query in a['title'].lower() or
                        self.search_query in a['desc'].lower() or
                        self.search_query in a['source'].lower()]

        self.statustext.set_text(f"  {len(articles)} articles  |  {len(self.articles)} total loaded")

        if not articles:
            self._show_placeholder("No articles found.")
            return

        for art in articles:
            row = self._make_article_row(art)
            self.article_list.pack_start(row, False, False, 0)

        self.article_list.show_all()

    def _make_article_row(self, art):
        cat   = art['category']
        color = CAT_COLORS.get(cat, "#39ff6a")
        label = CAT_LABELS.get(cat, cat.upper())

        outer = Gtk.EventBox()
        outer.get_style_context().add_class("article-row")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_margin_start(2)
        vbox.set_margin_end(2)

        # Top row: badge + title + open btn
        hbox_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        badge = Gtk.Label(label=label)
        badge.get_style_context().add_class("cat-badge")
        # Inline color via markup
        badge.set_markup(f'<span foreground="{color}" weight="bold" size="8000">{label}</span>')
        hbox_top.pack_start(badge, False, False, 0)

        title_lbl = Gtk.Label()
        title_lbl.set_markup(f'<span foreground="#c8d8c8" size="9500">{GLib.markup_escape_text(art["title"])}</span>')
        title_lbl.set_xalign(0)
        title_lbl.set_line_wrap(True)
        title_lbl.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        title_lbl.set_max_width_chars(80)
        hbox_top.pack_start(title_lbl, True, True, 0)

        open_btn = Gtk.Button(label="open →")
        open_btn.get_style_context().add_class("open-btn")
        url = art['url']
        open_btn.connect("clicked", lambda b, u=url: webbrowser.open(u))
        hbox_top.pack_end(open_btn, False, False, 0)

        vbox.pack_start(hbox_top, False, False, 0)

        # Description
        if art['desc']:
            desc_lbl = Gtk.Label()
            desc_lbl.set_markup(f'<span foreground="#4a6a4a" size="8500">{GLib.markup_escape_text(art["desc"])}</span>')
            desc_lbl.set_xalign(0)
            desc_lbl.set_line_wrap(True)
            desc_lbl.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            desc_lbl.set_max_width_chars(100)
            vbox.pack_start(desc_lbl, False, False, 0)

        # Meta row: source + time
        meta_lbl = Gtk.Label()
        meta_lbl.set_markup(f'<span foreground="#2a4a2a" size="8000">{GLib.markup_escape_text(art["source"])}  ·  {art["time"]}</span>')
        meta_lbl.set_xalign(0)
        vbox.pack_start(meta_lbl, False, False, 0)

        outer.add(vbox)
        outer.connect("button-press-event", lambda w, e, u=url: webbrowser.open(u) if e.button == 1 else None)

        return outer


def main():
    app = IntelFeed()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
