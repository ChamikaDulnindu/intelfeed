# intelFEED.sh — Tech Intelligence Dashboard

A native GTK desktop app for Kali Linux that aggregates real-time RSS feeds
across all your tech interests.

## Categories & Sources

| Category     | Sources |
|-------------|---------|
| cybersecurity | The Hacker News, Bleeping Computer, Krebs on Security, Dark Reading, NVD CVEs |
| web2-bugs    | PortSwigger Research, HackerOne Hacktivity, InfoSec Writeups |
| web3-bugs    | Rekt News, SlowMist, PeckShield |
| blockchain   | CoinDesk, Decrypt, The Block |
| ml-ai        | Towards Data Science, Hugging Face Blog, The Gradient |
| linux        | LWN.net, Phoronix, Linux Security, OMG Ubuntu |
| ctf          | CTFtime Events, CTF Writeups |
| resources    | Hacker News, SANS Internet Storm, Reddit /r/netsec |

## Install

```bash
cd intelfeed
chmod +x install.sh
./install.sh
```

## Run

```bash
intelfeed          # from any terminal after install
```

Or find it in your Applications menu under Security/Network.

## Usage

- **Filter buttons** — click any category tag to filter
- **Search box** — live search across titles, descriptions, sources
- **⟳ refresh feed** — pull latest articles
- **Click any article** — opens in your browser
- **open → button** — same thing, opens article in browser

## Requirements

- Python 3.8+
- GTK 3 (pre-installed on Kali)
- `python3-gi` (pre-installed on Kali)
- `feedparser` (installed automatically by install.sh)

## Uninstall

```bash
rm -rf ~/.local/share/intelfeed
rm ~/.local/bin/intelfeed
rm ~/.local/share/applications/intelfeed.desktop
```
