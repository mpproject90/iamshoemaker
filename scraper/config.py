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
ARTICLES_PER_RUN_MAX   = 50
ARTICLE_MAX_AGE_DAYS   = 7
MIN_RELEVANCE_SCORE    = 3
SUMMARY_MAX_CHARS      = 800
REQUEST_TIMEOUT        = 10
RETRY_WAIT_SECONDS     = 60

# ─── BULLETIN SETTINGS ────────────────────────────────────────────────────
BULLETIN_CLAUDE_MODEL  = "claude-sonnet-4-6"
BULLETIN_MAX_ARTICLES  = 10   # top N articles per weekly bulletin
BULLETIN_MAX_HISTORY   = 10   # keep this many past bulletins in bulletin.json

# ─── NEWS SOURCES ─────────────────────────────────────────────────────────
SOURCES = [
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
        "name": "Leather News",
        "rss": "https://leathernews.org/feed/",
        "domain": "leathernews.org",
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

