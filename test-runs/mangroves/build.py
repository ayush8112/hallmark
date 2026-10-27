#!/usr/bin/env python3
"""Builds the four Kandalvan pages from src/ snippets and the shared chrome below.

index.html (summary), mangroves.html, credits.html, contact.html, plus a
single-file bundle of each in dist/ for sharing without the stylesheets.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"


def snip(name):
    return (SRC / name).read_text(encoding="utf-8")


PAGES = [
    ("index.html", "Overview"),
    ("mangroves.html", "Mangroves"),
    ("credits.html", "Carbon credits"),
    ("contact.html", "Contact"),
]

FONTS = "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap"

DONATO = 'Donato, D. C. et al. (2011). Mangroves among the most carbon-rich forests in the tropics. Nature Geoscience 4, 293 to 297. <a href="https://doi.org/10.1038/ngeo1123">doi:10.1038/ngeo1123</a>.'
BREIT = 'Breithaupt, J. L. and Steinmuller, H. E. (2022). Refining the global estimate of mangrove carbon burial rates using sedimentary and geomorphic settings. Geophysical Research Letters 49, e2022GL100177. <a href="https://doi.org/10.1029/2022GL100177">doi:10.1029/2022GL100177</a>.'
ISFR = 'Mangrove cover: India State of Forest Report 2023, via <a href="https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146358">PIB, 21 July 2025</a>.'
VERRA = 'Methodology: <a href="https://verra.org/methodologies/vm0033-methodology-for-tidal-wetland-and-seagrass-restoration-v2-1/">Verra, VM0033 v2.1</a>.'
CCTS = 'Indian scheme: <a href="https://beeindia.gov.in/show_content.php?lang=1&amp;level=1&amp;ls_id=189&amp;lid=294">Bureau of Energy Efficiency, Carbon Market</a>.'
CONV = "CO<sub>2</sub> figures converted at 44/12."

PHOTO_CREDITS = {
    "fisher": '<a href="https://commons.wikimedia.org/wiki/File:Shrimp_fisherman.jpg">Tomas Castelazo</a> (CC BY-SA 3.0)',
    "mudflat": '<a href="https://commons.wikimedia.org/wiki/File:Fisherman_at_Gullmarsvik_mudflats.jpg">W.carter</a> (CC0)',
    "boat": '<a href="https://commons.wikimedia.org/wiki/File:Low_tide_in_Rivedoux,_R%C3%A9_island,_august_2015.jpg">Jebulon</a> (CC0)',
}


def head(title, desc):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
"""


def nav(current):
    items = []
    for href, label in PAGES[1:]:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'        <li><a href="{href}"{cur}>{label}</a></li>')
    cur = ' aria-current="page"' if current == "index.html" else ""
    return f"""
<header class="nav">
  <div class="container">
    <a class="wordmark" href="index.html"{cur}>Kandalvan</a>
    <nav aria-label="Pages">
      <ul>
{chr(10).join(items)}
      </ul>
    </nav>
    <a class="btn" href="contact.html">Get in touch</a>
  </div>
</header>

<main id="top">
"""


def footer(head_line, lead, action, sources, photos):
    links = "\n".join(f'        <li><a href="{h}">{l}</a></li>' for h, l in PAGES)
    photo_line = ""
    if photos:
        photo_line = f'      <p>Photographs: {", ".join(PHOTO_CREDITS[p] for p in photos)}, Wikimedia Commons.</p>\n'
    return f"""</main>

<footer class="footer">
  <div class="container">
    <div class="letter">
      <h2>{head_line}</h2>
      <p>{lead}</p>
      <div class="actions">{action}</div>
    </div>
    <nav class="footer-pages" aria-label="All pages">
      <ul>
{links}
      </ul>
    </nav>
    <div class="small">
      <p>Sources: {" ".join(sources)}</p>
{photo_line}    </div>
  </div>
</footer>
"""


def photo(key, slot, alt, slot_alt, caption, sizes, pos):
    srcs = {
        "fisher": ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Shrimp_fisherman.jpg/{w}px-Shrimp_fisherman.jpg", 4707, 3138),
        "mudflat": ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Fisherman_at_Gullmarsvik_mudflats.jpg/{w}px-Fisherman_at_Gullmarsvik_mudflats.jpg", 4192, 2358),
        "boat": ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Low_tide_in_Rivedoux%2C_R%C3%A9_island%2C_august_2015.jpg/{w}px-Low_tide_in_Rivedoux%2C_R%C3%A9_island%2C_august_2015.jpg", 4458, 2967),
    }
    url, w, h = srcs[key]
    srcset = ", ".join(f"{url.format(w=x)} {x}w" for x in (960, 1280, 1920))
    return f"""<figure>
        <div class="photo" data-slot="{slot}" data-alt="{slot_alt}">
          <img src="{url.format(w=1280)}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{alt}" style="object-position: {pos}">
        </div>
        <figcaption>{caption}</figcaption>
      </figure>"""


def q(sid, heading, answer, cls="q"):
    return f"""  <section class="{cls}" id="{sid}">
    <div class="container">
      <h2>{heading}</h2>
      <div class="answer">
{answer}
      </div>
    </div>
  </section>

"""


def more(href, text):
    return f'        <p><a class="text" href="{href}">{text}</a></p>'


def add_more(section, link):
    return section.replace("\n      </div>\n    </div>\n  </section>", "\n" + link + "\n      </div>\n    </div>\n  </section>", 1)


# Overview: the summary page, every section pointing to the page that goes deeper.
def page_index():
    body = snip("hero.html")
    body = body.replace('<a class="btn" href="https://doi.org/10.1038/ngeo1123">Read the study</a>', '<a class="btn" href="mangroves.html">Meet the mangroves</a>')
    body += "\n" + snip("how-much.html") + "\n"
    body += add_more(snip("where.html"), more("mangroves.html#store", "How the mud stores it")) + "\n"
    body += add_more(snip("cut.html"), more("mangroves.html#threats", "What is clearing them")) + "\n"
    body += add_more(snip("credits.html"), more("credits.html", "How a mangrove credit is made")) + "\n"
    body += add_more(snip("maharashtra.html"), more("mangroves.html#maharashtra", "Maharashtra’s coast in detail")) + "\n"
    body += snip("coast.html")
    return (head("Kandalvan, the carbon in the mud", "Why Maharashtra’s mangroves are some of the most carbon-rich forests in the tropics, in plain answers.")
            + nav("index.html") + body
            + footer("Take this to your panchayat.", "Every figure here comes from two peer-reviewed studies and the Government of India. Share it, and ask what your creek holds.",
                     '<a class="btn btn--primary" href="contact.html">Get in touch</a>', [DONATO, BREIT, ISFR, CONV], ["fisher", "mudflat"])
            + snip("slots.js.html") + "</body>\n</html>\n")


def burial_chart():
    # Three published global totals, Tg organic carbon a year, with 95% intervals. Scale 0 to 30.
    rows = [("One global rate", 20.18, 17.52, 23.12), ("By sediment type", 22.10, 18.26, 26.05), ("By sediment and landform", 24.17, 19.77, 25.50)]
    x = lambda v: 40 + v * 920 / 30
    out = []
    for i, (label, v, lo, hi) in enumerate(rows):
        y = 30 + i * 56
        out.append(f'<text x="40" y="{y - 8}">{label}</text>')
        out.append(f'<rect class="series" x="40" y="{y}" width="{x(v) - 40:.1f}" height="20"></rect>')
        out.append(f'<line class="ci" x1="{x(lo):.1f}" y1="{y + 10}" x2="{x(hi):.1f}" y2="{y + 10}"></line>')
        out.append(f'<text class="mark" x="{x(hi) + 10:.1f}" y="{y + 15}">{v:.2f}</text>')
    ticks = []
    for t in (0, 10, 20, 30):
        ticks.append(f'<line class="tick" x1="{x(t):.1f}" y1="196" x2="{x(t):.1f}" y2="204"></line><text x="{x(t):.1f}" y="222" text-anchor="middle">{t}</text>')
    return f"""        <div class="sheet">
          <svg class="chart" viewBox="0 0 1000 236" role="img" aria-labelledby="burial-title">
            <title id="burial-title">Global mangrove carbon burial, three estimates in teragrams of organic carbon a year: 20.18, 22.10 and 24.17, with 95 percent intervals</title>
            {"".join(out)}
            <line class="axis" x1="40" y1="196" x2="960" y2="196"></line>
            {"".join(ticks)}
          </svg>
          <p class="note">Million tonnes of carbon buried a year, worldwide. Bars are the estimate, lines the 95% interval.</p>
        </div>"""


def page_mangroves():
    hero = f"""  <section class="hero">
    <div class="container">
      <div class="hero-text">
        <h1>A forest that grows into the mud</h1>
        <p class="lead">Roots in salt water, carbon stacked metres deep below them.</p>
        <div class="actions">
          <a class="btn btn--primary" href="#store">How it stores carbon</a>
          <a class="btn" href="credits.html">Why it counts as a credit</a>
        </div>
      </div>
      {photo("mudflat", "mangrove-hero", "A fisherman wading beyond dark mudflats", "A Maharashtra mangrove creek at low tide", "Mudflat at low water. Stand-in photograph; a Konkan creek goes here.", "(max-width: 60rem) 100vw, 58vw", "10% 15%")}
    </div>
  </section>

"""
    store = q("store", "Where does a mangrove keep its carbon?", """        <p>Mostly underground. Across 25 Indo-Pacific forests, the soil held between 49% and 98% of the total store.</p>
        <div class="sheet">
          <table>
            <thead><tr><th scope="col">One hectare, on average</th><th scope="col" class="num">Figure</th></tr></thead>
            <tbody>
              <tr class="point"><td>Carbon stored, trees to soil</td><td class="num">1,023 t</td></tr>
              <tr><td>Share held in the soil</td><td class="num">49 to 98%</td></tr>
              <tr><td>Depth of the organic soil</td><td class="num">0.5 to 3+ m</td></tr>
            </tbody>
          </table>
        </div>""")
    burial = q("burial", "Does it keep adding more?", f"""        <p>Yes. Tides bring in sediment and the forest buries carbon in it every year, about 139 grams a square metre on average.</p>
{burial_chart()}
        <p>Setting matters: mangroves on carbonate coasts bury less than those fed by river sediment.</p>""")
    threats = q("threats", "What is clearing them?", """        <p>Coastal development, aquaculture ponds and over-harvesting. Between them, the world lost 30 to 50% of its mangrove area in half a century.</p>
        <table>
          <thead><tr><th scope="col">The cost of clearing</th><th scope="col" class="num">Figure</th></tr></thead>
          <tbody>
            <tr><td>Share of tropical forest area</td><td class="num">0.7%</td></tr>
            <tr><td>Share of deforestation emissions, up to</td><td class="num">10%</td></tr>
          </tbody>
        </table>""", cls="q band--ink")
    mh = snip("maharashtra.html").replace('id="maharashtra"', 'id="maharashtra"')
    life = q("life", "What else does a mangrove do?", """        <p>It holds up the fishery and cycles nutrients through the creek. Lose the forest and the catch goes with the carbon.</p>""")
    body = hero + store + burial + threats + mh + "\n" + life
    return (head("Mangroves, Kandalvan", "How mangroves store and bury carbon, what is clearing them, and Maharashtra’s mangrove cover.")
            + nav("mangroves.html") + body
            + footer("Protect the forest, keep the store.", "The next question is how that store becomes a credit someone can buy.",
                     '<a class="btn btn--primary" href="credits.html">How credits work</a>', [DONATO, BREIT, ISFR], ["mudflat"])
            + snip("slots.js.html") + "</body>\n</html>\n")


def page_credits():
    hero = """  <section class="hero">
    <div class="container">
      <div class="hero-text">
        <h1>One credit, one tonne of CO<sub>2</sub></h1>
        <p class="lead">A credit is proof that carbon stayed out of the air.</p>
        <div class="actions">
          <a class="btn btn--primary" href="#calc">Try your creek</a>
          <a class="btn" href="#steps">How one is made</a>
        </div>
      </div>
      <div class="hero-sheet sheet">
        <table>
          <thead><tr><th scope="col">One hectare of mangrove, on average</th><th scope="col" class="num">Tonnes CO<sub>2</sub></th></tr></thead>
          <tbody>
            <tr><td>Already stored</td><td class="num">3,751</td></tr>
            <tr class="point"><td>Added each year</td><td class="num">5.08</td></tr>
          </tbody>
        </table>
        <p class="note">From the study averages; real sites vary.</p>
      </div>
    </div>
  </section>

"""
    steps = q("steps", "How does a mangrove project earn credits?", """        <ol class="steps">
          <li><h3>Pick a methodology</h3><p>The rulebook for counting. For tidal wetlands under Verra’s standard, that is VM0033.</p></li>
          <li><h3>Measure the baseline</h3><p>What the site would hold if nothing were done.</p></li>
          <li><h3>Restore or protect</h3><p>Plant, reconnect tides, stop the clearing.</p></li>
          <li><h3>Monitor and verify</h3><p>An independent auditor checks the carbon gained against the baseline.</p></li>
          <li><h3>Issue credits</h3><p>Only verified tonnes become credits on a registry.</p></li>
        </ol>""")
    markets = q("markets", "Which market would a credit sell in?", """        <div class="sheet">
          <table>
            <thead><tr><th scope="col">Market</th><th scope="col">Rulebook</th><th scope="col" class="num">In force</th></tr></thead>
            <tbody>
              <tr><td>Voluntary, Verra</td><td>VM0033 v2.1, tidal wetland and seagrass restoration</td><td class="num">4 Sep 2023</td></tr>
              <tr><td>India, compliance</td><td>Carbon Credit Trading Scheme, Ministry of Power</td><td class="num">28 Jun 2023</td></tr>
            </tbody>
          </table>
        </div>
        <p>Verra is consulting on a version 3.0 of VM0033, so the rules are still moving.</p>""")
    calc = snip("calc.html").replace("What would your creek hold?", "What would your creek hold?")
    caveat = q("caveat", "What should a panchayat ask first?", """        <ul class="asks">
          <li>Who holds the rights to the land and the credits?</li>
          <li>Which standard and methodology, and which version?</li>
          <li>Who verifies, and how often?</li>
          <li>How much of the income reaches the village?</li>
        </ul>""", cls="q well")
    body = hero + steps + markets + calc + "\n" + caveat
    return (head("Carbon credits, Kandalvan", "How mangrove carbon becomes a credit, which rulebooks apply, and what your creek might hold.")
            + nav("credits.html") + body
            + footer("Weighing up a project?", "Bring your questions about a site, a standard or a proposal.",
                     '<a class="btn btn--primary" href="contact.html">Get in touch</a>', [DONATO, BREIT, VERRA, CCTS, CONV], [])
            + snip("calc.js.html") + "</body>\n</html>\n")


DISTRICTS = ["Palghar", "Thane", "Mumbai City", "Mumbai Suburban", "Raigad", "Ratnagiri", "Sindhudurg"]


def page_contact():
    opts = "\n".join(f'              <option>{d}</option>' for d in DISTRICTS)
    hero = f"""  <section class="hero hero--contact">
    <div class="container">
      <div class="hero-text">
        <h1>Talk to us about your creek</h1>
        <p class="lead">Questions from villages, panchayats and departments all welcome.</p>
        <div class="actions">
          <a class="btn btn--primary" href="#write">Write to us</a>
          <a class="btn" href="https://mangroves.maharashtra.gov.in">Mangrove Cell, Maharashtra</a>
        </div>
      </div>
      <form class="sheet form" id="write" novalidate>
        <div class="field">
          <label for="f-name">Your name</label>
          <input id="f-name" name="name" type="text" autocomplete="name" required>
          <p class="error" id="e-name" hidden>Tell us your name.</p>
        </div>
        <div class="field">
          <label for="f-email">Email or phone</label>
          <input id="f-email" name="reach" type="text" autocomplete="email" required>
          <p class="error" id="e-email" hidden>Add a way to reach you.</p>
        </div>
        <div class="field-row">
          <div class="field">
            <label for="f-role">You are</label>
            <select id="f-role" name="role">
              <option>From a coastal village</option>
              <option>From a gram panchayat</option>
              <option>From a government department</option>
              <option>A student or researcher</option>
              <option>Something else</option>
            </select>
          </div>
          <div class="field">
            <label for="f-district">Coastal district</label>
            <select id="f-district" name="district">
              <option>Not sure</option>
{opts}
            </select>
          </div>
        </div>
        <div class="field">
          <label for="f-msg">Your question</label>
          <textarea id="f-msg" name="message" rows="5" required></textarea>
          <p class="error" id="e-msg" hidden>Write your question.</p>
        </div>
        <button class="btn btn--primary" type="submit">Send</button>
        <p class="status" id="f-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </section>

"""
    who = q("who", "Who looks after Maharashtra’s mangroves?", """        <p>The state Forest Department’s Mangrove Cell and the Mangrove Foundation it works with. Their official site carries the current contacts.</p>
        <p><a class="text" href="https://mangroves.maharashtra.gov.in">mangroves.maharashtra.gov.in</a></p>""")
    before = q("before", "What helps us answer fast?", """        <ul class="asks">
          <li>The creek or village name, and its district.</li>
          <li>Whether a project has already approached you.</li>
          <li>Any papers you were given, as a photo.</li>
        </ul>""")
    js = """<script>
(() => {
  const f = document.getElementById('write');
  const checks = [['f-name', 'e-name'], ['f-email', 'e-email'], ['f-msg', 'e-msg']];
  f.addEventListener('submit', (e) => {
    e.preventDefault();
    let first = null;
    for (const [i, er] of checks) {
      const input = document.getElementById(i), msg = document.getElementById(er);
      const bad = !input.value.trim();
      input.setAttribute('aria-invalid', bad ? 'true' : 'false');
      bad ? input.setAttribute('aria-describedby', er) : input.removeAttribute('aria-describedby');
      msg.hidden = !bad;
      if (bad && !first) first = input;
    }
    const st = document.getElementById('f-status');
    if (first) { first.focus(); st.textContent = ''; return; }
    st.textContent = 'This form is not connected yet, so nothing was sent. Please use the Mangrove Cell site for now.';
  });
})();
</script>
"""
    body = hero + who + before
    return (head("Contact, Kandalvan", "Questions about mangroves and carbon credits on the Maharashtra coast.")
            + nav("contact.html") + body
            + footer("Start with the forest.", "New to mangroves? Read how the mud stores carbon before you write.",
                     '<a class="btn btn--primary" href="mangroves.html">Meet the mangroves</a>', [ISFR], [])
            + js + "</body>\n</html>\n")


def bundle(html):
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    css = css.replace('@import url("./tokens.css");', (ROOT / "tokens.css").read_text(encoding="utf-8"))
    css = css.replace('@import url("./base.css");', (ROOT / "base.css").read_text(encoding="utf-8"))
    return html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "\n</style>")


def main():
    built = {"index.html": page_index(), "mangroves.html": page_mangroves(), "credits.html": page_credits(), "contact.html": page_contact()}
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    for name, html in built.items():
        (ROOT / name).write_text(html, encoding="utf-8")
        (dist / name).write_text(bundle(html), encoding="utf-8")
    print("built", ", ".join(built))


if __name__ == "__main__":
    main()
