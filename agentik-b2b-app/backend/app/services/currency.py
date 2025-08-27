from typing import Dict


DEFAULT_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "TRY": 0.030,
}


def convert(amount: float, from_currency: str, to_currency: str, rates_to_usd: Dict[str, float] | None = None) -> float:
    rates = {k.upper(): v for k, v in (rates_to_usd or DEFAULT_RATES_TO_USD).items()}
    f = from_currency.upper()
    t = to_currency.upper()
    if f not in rates or t not in rates:
        raise ValueError("Unsupported currency")
    # Convert via USD as base
    amount_usd = amount * rates[f]
    return round(amount_usd / rates[t], 4)

