
UNITS = {
    "m": "meter", "s": "second", "g": "gram", "l": "liter", "A": "ampere", "K": "kelvin", "mol": "mole", "cd": "candela"
}

SPECIAL_UNITS = { 
    "min": [60, "s"], 
    "hours": [60*60, "s"], "hour": [60*60, "s"], "h": [60*60, "s"]
}

PREFIXES = {
    "d": 10**-1, "c": 10**-2, "m": 10**-3, "µ": 10**-6, "n": 10**-9, "p": 10**-12, "f": 10**-15,
    "da": 10**1, "h": 10**2, "k": 10**3, "M": 10**6, "G": 10**9, "T": 10**12, "P": 10**15
}

SPECIAL_TEN_EXPONENTS = {
    "ton": [10**6, "g"], "tons": [10**6, "g"]
}

TEN_EXPONENTS = {
    "d": -1, "c": -2, "m": -3, "µ": -6, "n": -9, "p": -12, "f": -15,
    "da": 1, "h": 2, "k": 3, "M": 6, "G": 9, "T": 12, "P": 15
}

PREFIXES_SINGLE_LETTER = {
    "d": "deci", "c": "centi", "m": "milli", "µ": "micro", "n": "nano", "p": "pico", "f": "femto",
    "da": "deca", "h": "hecto", "k": "kilo", "M": "mega", "G": "giga", "T": "tera", "P": "peta"
}
PREFIXES_SINGLE_LETTER_REVERSE = {value: key for key, value in PREFIXES_SINGLE_LETTER.items()}