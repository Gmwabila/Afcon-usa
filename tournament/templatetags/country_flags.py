from django import template

register = template.Library()

COUNTRY_CODES = {
    "algeria": "DZ",
    "angola": "AO",
    "benin": "BJ",
    "botswana": "BW",
    "burkina faso": "BF",
    "burundi": "BI",
    "cabo verde": "CV",
    "cameroon": "CM",
    "central african republic": "CF",
    "chad": "TD",
    "comoros": "KM",
    "côte d'ivoire": "CI",
    "democratic republic of the congo": "CD",
    "djibouti": "DJ",
    "egypt": "EG",
    "equatorial guinea": "GQ",
    "eritrea": "ER",
    "eswatini": "SZ",
    "ethiopia": "ET",
    "gabon": "GA",
    "gambia": "GM",
    "ghana": "GH",
    "guinea": "GN",
    "guinea-bissau": "GW",
    "kenya": "KE",
    "lesotho": "LS",
    "liberia": "LR",
    "libya": "LY",
    "madagascar": "MG",
    "malawi": "MW",
    "mali": "ML",
    "mauritania": "MR",
    "mauritius": "MU",
    "morocco": "MA",
    "mozambique": "MZ",
    "namibia": "NA",
    "niger": "NE",
    "nigeria": "NG",
    "republic of the congo": "CG",
    "rwanda": "RW",
    "são tomé and príncipe": "ST",
    "senegal": "SN",
    "seychelles": "SC",
    "sierra leone": "SL",
    "somalia": "SO",
    "south africa": "ZA",
    "south sudan": "SS",
    "sudan": "SD",
    "tanzania": "TZ",
    "togo": "TG",
    "tunisia": "TN",
    "uganda": "UG",
    "zambia": "ZM",
    "zimbabwe": "ZW",
}

ALIASES = {
    "cape verde": "cabo verde",
    "congo brazzaville": "republic of the congo",
    "congo kinshasa": "democratic republic of the congo",
    "cote d'ivoire": "côte d'ivoire",
    "dr congo": "democratic republic of the congo",
    "drc": "democratic republic of the congo",
    "guinea bissau": "guinea-bissau",
    "ivory coast": "côte d'ivoire",
    "republic of congo": "republic of the congo",
    "sao tome and principe": "são tomé and príncipe",
    "senegale": "senegal",
    "the gambia": "gambia",
}


@register.filter
def country_flag(team_name):
    name = team_name.casefold().replace(".", "").replace("’", "'")
    name = " ".join(name.split())
    code = COUNTRY_CODES.get(ALIASES.get(name, name))

    if code is None:
        return ""

    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code)