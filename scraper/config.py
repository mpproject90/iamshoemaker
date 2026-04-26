"""
iamshoemaker.com — Scraper Configuration
Misaki Zuno 造 | Where Craftsmanship Meets Intelligence

All settings, sources, keywords, and prompts live here.
Never hardcode these values in other files.
"""

import os

# ─── API KEYS ─────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")

# ─── GITHUB SETTINGS ──────────────────────────────────────────────────────
GITHUB_REPO           = "mpproject90/iamshoemaker"
GITHUB_FEED_PATH      = "feed.json"
GITHUB_BULLETIN_PATH  = "bulletin.json"
GITHUB_BRANCH         = "main"

# ─── SCRAPER SETTINGS ─────────────────────────────────────────────────────
MAX_ARTICLES           = 150
ARTICLES_PER_RUN_MAX   = 80
ARTICLE_MAX_AGE_DAYS   = 7
MIN_RELEVANCE_SCORE    = 3
SUMMARY_MAX_CHARS      = 800
REQUEST_TIMEOUT        = 8
RETRY_WAIT_SECONDS     = 10

# ─── BULLETIN SETTINGS ────────────────────────────────────────────────────
BULLETIN_CLAUDE_MODEL  = "claude-sonnet-4-6"
BULLETIN_MAX_ARTICLES  = 10   # top N articles per weekly bulletin
BULLETIN_MAX_HISTORY   = 10   # keep this many past bulletins in bulletin.json

# ─── NEWS SOURCES ─────────────────────────────────────────────────────────
SOURCES = [

    # ── ORIGINAL CORE ────────────────────────────────────────────────────

    {
        "name": "Footwear News",
        "rss": "https://footwearnews.com/feed/",
        "domain": "footwearnews.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Just Style",
        "rss": "https://www.just-style.com/feed/",
        "domain": "just-style.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Business of Fashion",
        "rss": "https://www.businessoffashion.com/rss/news/",
        "domain": "businessoffashion.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Hypebeast",
        "rss": "https://hypebeast.com/feed",
        "domain": "hypebeast.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Sneaker News",
        "rss": "https://sneakernews.com/feed/",
        "domain": "sneakernews.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Reuters Lifestyle",
        "rss": "https://feeds.reuters.com/reuters/lifestyle",
        "domain": "reuters.com",
        "priority": 3,
        "active": True
    },
    {
        "name": "Google News - Footwear Industry",
        "rss": "https://news.google.com/rss/search?q=footwear+industry&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Sneaker Brand",
        "rss": "https://news.google.com/rss/search?q=sneaker+brand+news&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Shoe Manufacturing",
        "rss": "https://news.google.com/rss/search?q=shoe+manufacturing+factory&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Leather Industry",
        "rss": "https://news.google.com/rss/search?q=leather+industry+trade&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Footwear Exports",
        "rss": "https://news.google.com/rss/search?q=footwear+exports+imports+tariff&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },

    # ── TIER 1: Core Footwear Trade ──────────────────────────────────────

    {
        "name": "Sourcing Journal",
        "rss": "https://sourcingjournal.com/feed/",
        "domain": "sourcingjournal.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "World Footwear",
        "rss": "https://www.worldfootwear.com/rss.aspx",
        "domain": "worldfootwear.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Footwear Plus Magazine",
        "rss": "https://footwearplus.com/feed/",
        "domain": "footwearplus.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Shoe Intelligence",
        "rss": "https://www.shoeintelligence.com/feed/",
        "domain": "shoeintelligence.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Footwear Insight",
        "rss": "https://footwearinsight.com/feed/",
        "domain": "footwearinsight.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Two Ten Footwear Foundation",
        "rss": "https://www.twoten.org/feed/",
        "domain": "twoten.org",
        "priority": 2,
        "active": True
    },
    {
        "name": "Sports Insight",
        "rss": "https://sportsinsightmag.com/feed/",
        "domain": "sportsinsightmag.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 2: Leather & Materials ──────────────────────────────────────

    {
        "name": "Leather Biz",
        "rss": "https://www.leatherbiz.com/rss/",
        "domain": "leatherbiz.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "APLF News",
        "rss": "https://www.aplf.com/en/news/rss",
        "domain": "aplf.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Ecotextile News",
        "rss": "https://www.ecotextile.com/rss/",
        "domain": "ecotextile.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Leather Naturally",
        "rss": "https://www.leathernaturally.org/feed/",
        "domain": "leathernaturally.org",
        "priority": 2,
        "active": True
    },
    {
        "name": "Leather Working Group",
        "rss": "https://www.leatherworkinggroup.com/feed/",
        "domain": "leatherworkinggroup.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Tanning Tech",
        "rss": "https://www.tanningtech.com/feed/",
        "domain": "tanningtech.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Materials Today",
        "rss": "https://www.materialstoday.com/rss/",
        "domain": "materialstoday.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 3: Fashion & Apparel Supply Chain ────────────────────────────

    {
        "name": "Fashion United",
        "rss": "https://fashionunited.com/rss/",
        "domain": "fashionunited.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Apparel Insider",
        "rss": "https://apparelinsider.com/feed/",
        "domain": "apparelinsider.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Supply Chain Dive",
        "rss": "https://www.supplychaindive.com/feeds/news/",
        "domain": "supplychaindive.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Fashion Dive",
        "rss": "https://www.fashiondive.com/feeds/news/",
        "domain": "fashiondive.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Retail Dive",
        "rss": "https://www.retaildive.com/feeds/news/",
        "domain": "retaildive.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Fashion United UK",
        "rss": "https://fashionunited.uk/rss/",
        "domain": "fashionunited.uk",
        "priority": 2,
        "active": True
    },
    {
        "name": "Drapers",
        "rss": "https://www.drapersonline.com/rss",
        "domain": "drapersonline.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Retail Gazette",
        "rss": "https://www.retailgazette.co.uk/feed/",
        "domain": "retailgazette.co.uk",
        "priority": 2,
        "active": True
    },
    {
        "name": "Vogue Business",
        "rss": "https://www.voguebusiness.com/rss",
        "domain": "voguebusiness.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 4: Sneaker & Consumer Footwear ──────────────────────────────

    {
        "name": "Sole Collector",
        "rss": "https://solecollector.com/rss/news",
        "domain": "solecollector.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "The Sole Supplier",
        "rss": "https://thesolesupplier.co.uk/feed/",
        "domain": "thesolesupplier.co.uk",
        "priority": 2,
        "active": True
    },
    {
        "name": "Highsnobiety",
        "rss": "https://www.highsnobiety.com/feed/",
        "domain": "highsnobiety.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Sneaker Freaker",
        "rss": "https://www.sneakerfreaker.com/feed/",
        "domain": "sneakerfreaker.com",
        "priority": 2,
        "active": False
    },
    {
        "name": "Kicks on Fire",
        "rss": "https://www.kicksonfire.com/feed/",
        "domain": "kicksonfire.com",
        "priority": 3,
        "active": False
    },
    {
        "name": "Nice Kicks",
        "rss": "https://www.nicekicks.com/feed/",
        "domain": "nicekicks.com",
        "priority": 3,
        "active": False
    },

    # ── TIER 5: Trade Data & Economics ───────────────────────────────────

    {
        "name": "Fibre2Fashion",
        "rss": "https://www.fibre2fashion.com/rss/news.xml",
        "domain": "fibre2fashion.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Apparel Resources",
        "rss": "https://apparelresources.com/feed/",
        "domain": "apparelresources.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Textile Today",
        "rss": "https://www.textiletoday.com.bd/feed/",
        "domain": "textiletoday.com.bd",
        "priority": 1,
        "active": True
    },
    {
        "name": "Global Trade Magazine",
        "rss": "https://www.globaltrademag.com/feed/",
        "domain": "globaltrademag.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Import Genius Blog",
        "rss": "https://blog.importgenius.com/feed/",
        "domain": "importgenius.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Trade Arabia",
        "rss": "https://www.tradearabia.com/rss/",
        "domain": "tradearabia.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 6: Manufacturing & Operations ───────────────────────────────

    {
        "name": "Manufacturing Dive",
        "rss": "https://www.manufacturingdive.com/feeds/news/",
        "domain": "manufacturingdive.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Industry Week",
        "rss": "https://www.industryweek.com/rss/all",
        "domain": "industryweek.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Manufacturing Today",
        "rss": "https://www.manufacturingtoday.com/feed/",
        "domain": "manufacturingtoday.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Sourcing at Magic",
        "rss": "https://www.sourcingatmagic.com/feed/",
        "domain": "sourcingatmagic.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 7: Regional Manufacturing Hubs ──────────────────────────────

    # Vietnam
    {
        "name": "Vietnam Investment Review",
        "rss": "https://vir.com.vn/rss/",
        "domain": "vir.com.vn",
        "priority": 1,
        "active": True
    },
    {
        "name": "Vietnam News",
        "rss": "https://vietnamnews.vn/rss/",
        "domain": "vietnamnews.vn",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Vietnam Manufacturing",
        "rss": "https://news.google.com/rss/search?q=vietnam+manufacturing+footwear+factory&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },

    # Indonesia
    {
        "name": "Jakarta Post Business",
        "rss": "https://www.thejakartapost.com/business.rss",
        "domain": "thejakartapost.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Indonesia Footwear",
        "rss": "https://news.google.com/rss/search?q=indonesia+footwear+export+factory&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },

    # Bangladesh
    {
        "name": "The Daily Star Bangladesh",
        "rss": "https://www.thedailystar.net/rss.xml",
        "domain": "thedailystar.net",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Bangladesh Garment",
        "rss": "https://news.google.com/rss/search?q=bangladesh+garment+footwear+factory&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },

    # India
    {
        "name": "CLE - Council for Leather Exports",
        "rss": "https://www.cle.org.in/rss/news.xml",
        "domain": "cle.org.in",
        "priority": 1,
        "active": True
    },
    {
        "name": "FDDI - Footwear Design Development Institute",
        "rss": "https://fddiindia.com/feed/",
        "domain": "fddiindia.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "ISF - Indian Shoe Federation",
        "rss": "https://www.indianshoefederation.in/feed/",
        "domain": "indianshoefederation.in",
        "priority": 1,
        "active": True
    },
    {
        "name": "Leather Panel India",
        "rss": "https://leatherpanel.org/feed/",
        "domain": "leatherpanel.org",
        "priority": 1,
        "active": True
    },
    {
        "name": "Financial Express India",
        "rss": "https://www.financialexpress.com/feed/",
        "domain": "financialexpress.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - CLE Leather Exports India",
        "rss": "https://news.google.com/rss/search?q=CLE+council+leather+exports+india&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Indian Shoe Federation",
        "rss": "https://news.google.com/rss/search?q=indian+shoe+federation+footwear+india&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - India Leather",
        "rss": "https://news.google.com/rss/search?q=india+leather+footwear+export&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },

    # China
    {
        "name": "China Daily Business",
        "rss": "https://www.chinadaily.com.cn/rss/bizchina_rss.xml",
        "domain": "chinadaily.com.cn",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - China Footwear",
        "rss": "https://news.google.com/rss/search?q=china+footwear+export+manufacturing&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },

    # ── TIER 8: Sustainability & Compliance ──────────────────────────────

    {
        "name": "Sustainable Brands",
        "rss": "https://sustainablebrands.com/feed/",
        "domain": "sustainablebrands.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Edie Sustainability",
        "rss": "https://www.edie.net/rss/",
        "domain": "edie.net",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Footwear Sustainability",
        "rss": "https://news.google.com/rss/search?q=footwear+sustainability+ESG+circular&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - ZDHC Leather",
        "rss": "https://news.google.com/rss/search?q=ZDHC+leather+chemical+compliance&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },

    # ── TIER 9: Google News Power Queries ────────────────────────────────

    {
        "name": "Google News - Major Brand Earnings",
        "rss": "https://news.google.com/rss/search?q=Nike+OR+Adidas+OR+Puma+earnings+revenue+2026&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Footwear Recall",
        "rss": "https://news.google.com/rss/search?q=footwear+shoe+recall+defect+quality&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Leather Tannery",
        "rss": "https://news.google.com/rss/search?q=leather+tannery+production+industry&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Supply Chain Disruption",
        "rss": "https://news.google.com/rss/search?q=supply+chain+disruption+apparel+footwear&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 1,
        "active": True
    },
    {
        "name": "Google News - Footwear Innovation",
        "rss": "https://news.google.com/rss/search?q=footwear+innovation+technology+material&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Sneaker Market",
        "rss": "https://news.google.com/rss/search?q=sneaker+market+resale+industry+2026&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Shoe Factory Workers",
        "rss": "https://news.google.com/rss/search?q=shoe+factory+workers+labor+conditions&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },
    {
        "name": "Google News - Luxury Footwear",
        "rss": "https://news.google.com/rss/search?q=luxury+footwear+leather+goods+market&hl=en&gl=US&ceid=US:en",
        "domain": "news.google.com",
        "priority": 2,
        "active": True
    },

]

# ─── KEYWORDS ─────────────────────────────────────────────────────────────
PRIMARY_KEYWORDS = [
    # Core product terms
    "footwear", "sneakers", "shoes",
    "shoe manufacturing", "athletic footwear",
    "footwear industry", "shoe brand",
    "shoe factory", "outsole", "upper",
    "lasting", "shoemaking", "leather goods",
    "boot", "sandal", "sole", "insole",
    "midsole", "welt", "cobbler",
    # Leather industry
    "tannery", "leather industry",
    "leather tanning", "leather exports",
    "leather tannage", "hide", "skin processing",
    "chrome tanning", "vegetable tan",
    "wet blue", "crust leather",
    # Supply chain and trade
    "fashion supply chain", "apparel exports",
    "footwear exports", "footwear imports",
    "shoe tariff", "footwear quality",
    "shoe defect",
]

# ─── BRANDS ───────────────────────────────────────────────────────────────
BRANDS = [
    # Athletic / performance
    "Nike", "Adidas", "Puma", "Reebok",
    "New Balance", "ASICS", "Skechers",
    "Under Armour", "Brooks", "Hoka",
    "On Running", "Salomon", "Merrell",
    "Keen", "Mizuno", "Diadora",
    # Casual / lifestyle
    "Vans", "Converse", "Timberland",
    "Dr. Martens", "Clarks", "Ecco",
    "Birkenstock", "UGG", "Crocs",
    "Steve Madden", "Cole Haan", "Geox",
    "K-Swiss", "Lacoste", "Bata",
    "Wolverine", "Rockport",
    # Luxury
    "Golden Goose", "Louboutin",
    "Jimmy Choo", "Gucci", "Balenciaga",
    "Alexander McQueen", "Off-White",
    "Hermès", "Prada", "Tod's",
    "Ferragamo", "Mephisto",
    # Streetwear / hype
    "Jordan", "Yeezy", "Fila", "Kappa",
    "Umbro", "Hummel", "Lotto",
    # Work / outdoor
    "Caterpillar", "Red Wing", "Vibram",
    # Sustainability / DTC
    "Allbirds",
    # Corporate groups
    "Wolverine Worldwide", "Authentic Brands",
    "VF Corporation", "Tapestry", "Capri",
]

# ─── CATEGORY RULES ───────────────────────────────────────────────────────
# First matching category wins (ordered by specificity)
CATEGORY_RULES = {
    "Quality": [
        "quality", "defect", "recall",
        "testing", "inspection", "standard",
        "compliance", "certification", "ISO",
        "audit", "QC", "QA", "SATRA",
        "delamination", "failure", "durability",
    ],
    "Leather": [
        "leather", "tannery", "hide", "skin",
        "tanning", "suede", "nubuck",
        "chrome tanning", "vegetable tan",
        "wet blue", "crust leather", "LWG",
        "leather working group",
    ],
    "Manufacturing": [
        "factory", "manufacturing",
        "production", "shopfloor", "assembly",
        "supplier", "vendor", "capacity",
        "output", "plant", "facility",
        "automation", "workforce", "tooling",
    ],
    "Trade Data": [
        "export", "import", "tariff", "trade",
        "customs", "duty", "shipment",
        "volume", "market share",
        "million pairs", "trade data",
        "trade statistics", "HTS",
    ],
    "Supply Chain": [
        "supply chain", "logistics",
        "sourcing", "procurement", "inventory",
        "shortage", "disruption", "port",
        "shipping", "freight", "nearshoring",
        "reshoring", "Vietnam", "Bangladesh",
        "Cambodia", "Indonesia", "China",
    ],
    "Sustainability": [
        "sustainable", "eco", "recycled",
        "carbon", "circular", "vegan",
        "environmental", "green", "bio",
        "net zero", "ESG", "emissions",
        "chrome-free", "ZDHC", "CSRD",
    ],
    "Brand News": [
        "acquisition", "merger", "revenue",
        "earnings", "CEO", "partnership",
        "collaboration", "launch", "brand",
        "quarterly", "annual results",
        "financial", "stock", "IPO",
        "appointment", "strategy",
    ],
    "Retail": [
        "retail", "store", "sales",
        "consumer", "market", "trend",
        "fashion", "style", "DTC",
        "ecommerce", "online sales",
        "wholesale", "distribution",
    ],
}

