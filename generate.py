#!/usr/bin/env python3
"""Render "The World" front page for Tuesday, 25 November 2026.

The edition carries 46 reports verified for 24-25 November 2026 (see
stories.md): one lead story plus seven regional sections, set as a
classic three-column broadsheet. The picture is painted entirely with
Pillow — DejaVu type on an off-white sheet, no network, no photographs,
no outside artwork.

This file is an independent re-implementation written for the
competition window: the layout is driven by a page specification and a
region table, and the drawing is organised as a small page object
rather than a flat script.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Page specification: sheet size, palette, type table, grid.
# --------------------------------------------------------------------------

SHEET_W, SHEET_H = 1024, 1024
PAPER = (253, 253, 248)
INK = (12, 12, 12)
MUTED = (70, 70, 70)
DARK_RULE = (30, 30, 30)
FLAG_RED = (140, 20, 20)
BANNER_FILL = (18, 18, 18)
HAIRLINE = (190, 190, 185)
CONT_RULE = (150, 150, 145)
COLUMN_RULE = (200, 200, 195)
WHITE = (255, 255, 255)

GLYPH_DIR = Path("/usr/share/fonts/truetype/dejavu")

# Role -> (file, point size). Roles are referenced by name everywhere
# below, so the type choices live in exactly one place.
TYPE_TABLE = {
    "nameplate": ("DejaVuSerif-Bold.ttf", 64),
    "dateline": ("DejaVuSans-Bold.ttf", 18),
    "small": ("DejaVuSans.ttf", 11),
    "kicker": ("DejaVuSans-Bold.ttf", 12),
    "lead_head": ("DejaVuSerif-Bold.ttf", 29),
    "lead_dek": ("DejaVuSerif.ttf", 14),
    "banner": ("DejaVuSans-Bold.ttf", 12),
    "headline": ("DejaVuSerif-Bold.ttf", 13),
    "dek": ("DejaVuSans.ttf", 11),
}

MARGIN = 22
COLUMN_W = 320
GUTTER = 12
COLUMN_LEFTS = [MARGIN + i * (COLUMN_W + GUTTER) for i in range(3)]
ITEMS_PER_COLUMN = 15

LEAD = {
    "kicker": "LEAD STORY  \u00b7  TECHNOLOGY  \u00b7  MARKETS",
    "headline": "Nvidia rally fades as Trump role probed",
    "deck": "Shares fall; Huang admits conduct breach, pardon floated.",
}

MASTHEAD = {
    "title": "The World",
    "date": "Tuesday, 25 November 2026",
    "left": "Vol. CXII  \u00b7  No. 329",
    "right": "World News  \u00b7  46 Stories",
}

FOOTER_TEXT = (
    "The World  \u00b7  Tuesday, 25 November 2026  \u00b7  "
    "All stories from reports published 24-25 November 2026"
)

# --------------------------------------------------------------------------
# Edition content: region name plus (headline, standfirst) pairs.
# --------------------------------------------------------------------------

REGIONS = [
    {
        "name": "NORTH AMERICA",
        "stories": [
            ("Abrego Garcia leaves US for Spain",
             "Mistaken deportation saga ends in voluntary exit."),
            ("Six die in Gulf plane crash",
             "Cessna bound for Florida; two boys among six aboard."),
            ("CIA open-source system breached",
             "Unclassified network hit; no classified data involved."),
            ("Fort Hood shooter seeks execution stay",
             "Hasan asks court to delay firing-squad execution."),
            ("Shein pays $100m in FTC settlement",
             "Misleading shipping, review and cotton claims alleged."),
            ("Army to detonate Iowa explosives",
             "Relocation urged for Wednesday lead-azide blast."),
            ("Trump pardons Freedom and Feathers",
             "Thanksgiving turkeys spared at White House ceremony."),
            ("Carney roasts Trump with impersonator",
             "Canada PM enlists comedians at press-gallery dinner."),
        ],
    },
    {
        "name": "LATIN AMERICA",
        "stories": [
            ("Cartagena hostages freed in raid",
             "All freed after siege; one captor killed, police say."),
            ("Car bomb wounds 23 in Villavicencio",
             "Blast outside Meta governor's offices; no deaths reported."),
            ("Venezuela reveals $237.5bn debt pile",
             "First full framework in years; restructuring eyed."),
            ("Mexico to try El Chapo Isidro at home",
             "Attorney general resists US extradition request for now."),
            ("WHO chief urges end to Cuba fuel blockade",
             "Tedros cites shortages, surgery backlog in Havana."),
            ("Polish president meets Milei in Buenos Aires",
             "First Polish presidential visit to Argentina in 31 years."),
        ],
    },
    {
        "name": "EUROPE",
        "stories": [
            ("Sarkozy and Bruni ordered to trial",
             "Corruption case over witness-retraction plot proceeds."),
            ("Spain split ahead of snap election",
             "Far right could enter government for first time."),
            ("Russian war deaths near 500,000",
             "BBC/Mediazona analysis puts toll at 490,334."),
            ("Drones hit Samara refineries; Putin vows reply",
             "Fires at oil sites; Putin says retaliation inevitable."),
            ("Sweden sets Kristersson PM vote",
             "Vote on 30 Nov after 72 days without a government."),
            ("UK energy bills to soar 26% from January",
             "Ofgem cap hits highest in almost four years."),
            ("Hera returns to asteroid crash scene",
             "ESA craft to study Dimorphos after 2022 DART hit."),
        ],
    },
    {
        "name": "AFRICA",
        "stories": [
            ("Senegal regain Africa Cup title",
             "CAS overturns ruling that gave trophy to Morocco."),
            ("Congo plane missing; rebels claim shoot-down",
             "Army cites weather; rebel claim unverified."),
            ("Nollywood legend Pete Edochie dies at 79",
             "Actor dies in Enugu after prostate illness, family says."),
            ("Amnesty urges Tigray shelling probe",
             "14 civilians verified killed in Alamata strikes."),
            ("Cameroon conflict scars its children",
             "BBC hears victims of a decade of fighting."),
            ("Nigerian monarch, 92, suspended",
             "Traditional ruler suspended amid assault claims."),
        ],
    },
    {
        "name": "MIDDLE EAST",
        "stories": [
            ("Houthis hit Riyadh tower; 11 wounded",
             "Second strike on tallest tower in less than a week."),
            ("Gaza strike kills Hamas security chief",
             "Seven killed in strikes despite ceasefire, medics say."),
            ("Iran claims tankers hit Hormuz mines",
             "IRGC says two tankers caught fire; claim unverified."),
            ("Iran flogs singer over unveiled concert",
             "Parastoo Ahmadi, four colleagues lashed in Qom."),
            ("Coalition orders Hodeidah port cleared",
             "Warning as Houthis threaten Red Sea ports."),
            ("Katz warns Iran seeks chemical arms",
             "Israel will stop Tehran acquiring them, minister says."),
        ],
    },
    {
        "name": "ASIA-PACIFIC",
        "stories": [
            ("Shenzhou-24 lifts off with Pakistani astronaut",
             "First foreigner aboard China's Tiangong station."),
            ("China probes Shanghai party chief",
             "Chen Jining is 4th Politburo member probed since 2025."),
            ("Bangladesh garment wage up 36%",
             "Minimum rises to Tk17,000; fresh protests follow."),
            ("Dozens feared trapped in Indonesian mine",
             "Floods inundate illegal gold mine shaft in West Java."),
            ("Myanmar tops world landmine toll again",
             "1,891 casualties in 2025, Landmine Monitor says."),
            ("Huawei convicted on 10 US counts",
             "Guilty on fraud, secrets theft; cleared of racketeering."),
            ("Hong Kong marks year since Tai Po fire",
             "Survivors mourn 168 dead; accountability questioned."),
        ],
    },
    {
        "name": "OCEANIA",
        "stories": [
            ("Australia, Solomons sign security treaty",
             "Canberra named primary partner; no foreign bases."),
            ("Ex-policeman guilty of Sydney double murder",
             "Jury convicts Beau Lamarre over 2024 killings."),
            ("Fiji drought emergency may run into 2027",
             "Water shortages expected into early 2027."),
            ("Brookfield bid lifts Reliance Worldwide",
             "Shares hit 20-month high on pension-fund backing."),
            ("El Nino raises Guam drought risk",
             "Guam, Northern Marianas face dry start to 2027."),
        ],
    },
]


# --------------------------------------------------------------------------
# Text fitting: greedy lines measured on the joined string, so kerning
# is honoured exactly as the rasteriser sees it.
# --------------------------------------------------------------------------

def fit_lines(measure, text, limit):
    """Split *text* into the longest runs of words that fit *limit*.

    A lone over-long word still occupies a line of its own. The
    measurement callback receives the joined candidate string.
    """
    words = text.split()
    lines = []
    start = 0
    while start < len(words):
        end = start + 1
        while end <= len(words):
            if measure(" ".join(words[start:end])) > limit and end > start + 1:
                break
            end += 1
        lines.append(" ".join(words[start:end - 1]))
        start = end - 1
    return lines


def load_type():
    """Build the role -> font map from TYPE_TABLE."""
    faces = {}
    for role, (filename, size) in TYPE_TABLE.items():
        faces[role] = ImageFont.truetype(str(GLYPH_DIR / filename), size)
    return faces


def plan_columns(regions, budget):
    """Flow regions into columns of at most *budget* stories.

    The first story of a region opens with a banner; a region that
    spills into a fresh column resumes under a "CONTINUED" flag.
    Entries are ("banner", name), ("continued", name) or
    ("story", headline, standfirst).
    """
    columns = []
    current = []
    used = 0
    for region in regions:
        for position, (headline, standfirst) in enumerate(region["stories"]):
            if used >= budget:
                columns.append(current)
                current = []
                used = 0
            if position == 0:
                current.append(("banner", region["name"]))
            elif used == 0:
                current.append(("continued", region["name"]))
            current.append(("story", headline, standfirst))
            used += 1
    if current:
        columns.append(current)
    return columns


class FrontPage:
    """Owns the sheet, the pen, and the vertical cursor."""

    def __init__(self):
        self.sheet = Image.new("RGB", (SHEET_W, SHEET_H), PAPER)
        self.pen = ImageDraw.Draw(self.sheet)
        self.faces = load_type()
        self.cursor = 0

    # -- small drawing primitives --------------------------------------

    def rule(self, x0, x1, y, weight, colour=DARK_RULE):
        self.pen.line([(x0, y), (x1, y)], fill=colour, width=weight)

    def centred(self, text, role, y, colour):
        face = self.faces[role]
        width = self.pen.textlength(text, font=face)
        self.pen.text(((SHEET_W - width) / 2, y), text, font=face, fill=colour)

    # -- page furniture --------------------------------------------------

    def paint_masthead(self):
        self.rule(MARGIN, SHEET_W - MARGIN, 12, 3)
        self.centred(MASTHEAD["title"], "nameplate", 16, INK)
        self.centred(MASTHEAD["date"], "dateline", 86, FLAG_RED)
        meta = self.faces["small"]
        self.pen.text((MARGIN, 88), MASTHEAD["left"], font=meta, fill=MUTED)
        right = MASTHEAD["right"]
        self.pen.text(
            (SHEET_W - MARGIN - self.pen.textlength(right, font=meta), 88),
            right,
            font=meta,
            fill=MUTED,
        )
        self.rule(MARGIN, SHEET_W - MARGIN, 110, 2)
        self.rule(MARGIN, SHEET_W - MARGIN, 114, 1)

    def paint_lead(self):
        self.cursor = 122
        self.pen.text(
            (MARGIN, self.cursor),
            LEAD["kicker"],
            font=self.faces["kicker"],
            fill=FLAG_RED,
        )
        self.cursor += 18
        measure = lambda s: self.pen.textlength(s, font=self.faces["lead_head"])
        for line in fit_lines(measure, LEAD["headline"], SHEET_W - 2 * MARGIN):
            self.pen.text(
                (MARGIN, self.cursor), line, font=self.faces["lead_head"], fill=INK
            )
            self.cursor += 33
        measure_dek = lambda s: self.pen.textlength(s, font=self.faces["lead_dek"])
        for line in fit_lines(measure_dek, LEAD["deck"], SHEET_W - 2 * MARGIN):
            self.pen.text(
                (MARGIN, self.cursor), line, font=self.faces["lead_dek"], fill=MUTED
            )
            self.cursor += 18
        self.cursor += 2
        self.rule(MARGIN, SHEET_W - MARGIN, self.cursor, 2)
        return self.cursor + 8

    def paint_footer(self):
        baseline = SHEET_H - 26
        self.rule(MARGIN, SHEET_W - MARGIN, baseline - 6, 1)
        self.centred(FOOTER_TEXT, "small", baseline + 2, MUTED)

    # -- column content ---------------------------------------------------

    def paint_banner(self, left, top, name):
        self.pen.rectangle(
            [left, top, left + COLUMN_W, top + 18], fill=BANNER_FILL
        )
        self.pen.text(
            (left + 7, top + 3), name, font=self.faces["banner"], fill=WHITE
        )
        return top + 25

    def paint_continued(self, left, top, name):
        self.pen.text(
            (left, top),
            name + "  -  CONTINUED",
            font=self.faces["banner"],
            fill=MUTED,
        )
        self.pen.line(
            [(left, top + 16), (left + COLUMN_W, top + 16)],
            fill=CONT_RULE,
            width=1,
        )
        return top + 23

    def paint_story(self, left, top, headline, standfirst):
        measure = lambda s: self.pen.textlength(s, font=self.faces["headline"])
        rows = fit_lines(measure, headline, COLUMN_W)
        if len(rows) > 2:
            raise ValueError(f"headline needs more than two lines: {headline!r}")
        y = top
        for row in rows:
            self.pen.text((left, y), row, font=self.faces["headline"], fill=INK)
            y += 17
        if self.pen.textlength(standfirst, font=self.faces["dek"]) > COLUMN_W:
            raise ValueError(f"standfirst too long: {standfirst!r}")
        self.pen.text((left, y), standfirst, font=self.faces["dek"], fill=MUTED)
        y += 16
        self.pen.line(
            [(left, y + 2), (left + COLUMN_W, y + 2)], fill=HAIRLINE, width=1
        )
        return y + 10

    def paint_column(self, left, top, entries, floor):
        y = top
        for entry in entries:
            kind = entry[0]
            if kind == "banner":
                y = self.paint_banner(left, y, entry[1])
            elif kind == "continued":
                y = self.paint_continued(left, y, entry[1])
            else:
                y = self.paint_story(left, y, entry[1], entry[2])
            if y > floor - 4:
                raise ValueError(f"column overflow at {entry!r}")
        self.pen.line([(left, top - 4), (left, y)], fill=COLUMN_RULE, width=1)

    # -- assembly ---------------------------------------------------------

    def build(self):
        self.paint_masthead()
        body_top = self.paint_lead()
        floor = SHEET_H - 26
        for left, entries in zip(
            COLUMN_LEFTS, plan_columns(REGIONS, ITEMS_PER_COLUMN)
        ):
            self.paint_column(left, body_top, entries, floor)
        self.paint_footer()
        return self.sheet


def main():
    page = FrontPage()
    image = page.build()
    target = Path(__file__).with_name("entry.png")
    image.save(target, optimize=True)
    print(f"wrote {target} {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
