import asyncio
import csv
import io
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BRVM")

BASE_URL = "https://raw.githubusercontent.com/Fredysessie/brvm-data-public/main/data"

STOCK_TICKERS = [
    "ABJC", "BICB", "BICC", "BNBC", "BOAB", "BOABF", "BOAC", "BOAM", "BOAN", "BOAS",
    "CABC", "CBIBF", "CFAC", "CIEC", "ECOC", "ETIT", "FTSC", "LNBB", "NEIC", "NSBC",
    "NTLC", "ONTBF", "ORAC", "ORGT", "PALC", "PRSC", "SAFC", "SCRC", "SDCC", "SDSC",
    "SEMC", "SGBC", "SHEC", "SIBC", "SICC", "SIVC", "SLBC", "SMBC", "SNTS", "SOGC",
    "SPHC", "STAC", "STBC", "SVOC", "TTLC", "TTLS", "UNLC", "UNXC",
]

INDEX_TICKERS = [
    "BRVM-CB", "BRVM-CD", "BRVM-EN", "BRVM-IN", "BRVM-SF", "BRVM-SP", "BRVM-TEL",
    "BRVM30", "BRVMAG", "BRVMAS", "BRVMC", "BRVMDI", "BRVMFI", "BRVMIN",
    "BRVMPA", "BRVMPR", "BRVMSP", "BRVMTR",
]

ALL_TICKERS = STOCK_TICKERS + INDEX_TICKERS


def _parse_float(val) -> float:
    try:
        return float(str(val).replace("%", "").replace(",", ".").strip())
    except Exception:
        return 0.0


@mcp.tool()
def get_all_tickers() -> dict:
    """Retourne la liste de tous les tickers disponibles à la BRVM (actions et indices)."""
    return {"stocks": STOCK_TICKERS, "indices": INDEX_TICKERS}


@mcp.tool()
async def get_ticker_data(ticker: str, period: str = "daily", limit: int = 60) -> str:
    """
    Récupère l'historique de prix OHLCV d'un ticker.

    Args:
        ticker: Symbole boursier (ex: SGBC, ONTBF, BOABF)
        period: Période — daily, weekly, monthly, quarterly, yearly
        limit: Nombre de lignes les plus récentes à retourner (défaut 60)
    """
    url = f"{BASE_URL}/{ticker}/{ticker}.{period}.csv"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
    lines = r.text.strip().split("\n")
    header = lines[0]
    recent = lines[max(1, len(lines) - limit):]
    return "\n".join([header] + recent)


@mcp.tool()
async def get_indicators(ticker: str) -> dict:
    """
    Récupère les indicateurs techniques actuels d'un ticker :
    RSI, Beta, cours actuel, variation du jour, volumes, plages de prix
    sur 1 semaine / 1 mois / YTD / 1 an / 3 ans / 5 ans.

    Args:
        ticker: Symbole boursier (ex: SGBC, ONTBF)
    """
    url = f"{BASE_URL}/{ticker}/{ticker}.indicator.csv"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
    return dict(next(csv.DictReader(io.StringIO(r.text))))


@mcp.tool()
async def screen_market(
    rsi_max: Optional[float] = None,
    rsi_min: Optional[float] = None,
    variation_1m_min: Optional[float] = None,
    variation_1m_max: Optional[float] = None,
    variation_1y_min: Optional[float] = None,
    variation_1y_max: Optional[float] = None,
    stocks_only: bool = True,
) -> list:
    """
    Scanne le marché BRVM et filtre les titres selon des critères.
    Les variations sont en décimales (ex: -0.10 = -10%, 0.05 = +5%).

    Args:
        rsi_max: RSI maximum (ex: 35 pour trouver les titres survendus)
        rsi_min: RSI minimum (ex: 70 pour trouver les titres surachetés)
        variation_1m_min: Variation 1 mois minimum (ex: 0.05 = +5%)
        variation_1m_max: Variation 1 mois maximum (ex: -0.05 = -5%)
        variation_1y_min: Variation 1 an minimum
        variation_1y_max: Variation 1 an maximum
        stocks_only: Si True, exclut les indices (défaut True)
    """
    tickers = STOCK_TICKERS if stocks_only else ALL_TICKERS

    async def fetch_one(client: httpx.AsyncClient, ticker: str):
        try:
            url = f"{BASE_URL}/{ticker}/{ticker}.indicator.csv"
            r = await client.get(url, timeout=15)
            if r.status_code != 200:
                return None
            row = dict(next(csv.DictReader(io.StringIO(r.text))))
            return ticker, row
        except Exception:
            return None

    async with httpx.AsyncClient() as client:
        results_raw = await asyncio.gather(*[fetch_one(client, t) for t in tickers])

    results = []
    for item in results_raw:
        if item is None:
            continue
        ticker, row = item
        rsi = _parse_float(row.get("RSI", 0))
        var_1m = _parse_float(row.get("1_Mois_Variation", 0))
        var_1y = _parse_float(row.get("1_An_Variation", 0))

        if rsi_max is not None and rsi > rsi_max:
            continue
        if rsi_min is not None and rsi < rsi_min:
            continue
        if variation_1m_min is not None and var_1m < variation_1m_min:
            continue
        if variation_1m_max is not None and var_1m > variation_1m_max:
            continue
        if variation_1y_min is not None and var_1y < variation_1y_min:
            continue
        if variation_1y_max is not None and var_1y > variation_1y_max:
            continue

        results.append({
            "ticker": ticker,
            "cours": row.get("Cours_Actuel"),
            "variation_jour": row.get("Variation_Cours"),
            "rsi": round(rsi, 2),
            "beta_1an": row.get("Beta_1_An"),
            "variation_1m": f"{var_1m:.2%}",
            "variation_1y": f"{var_1y:.2%}",
            "volume_xof": row.get("Volume_XOF"),
            "valorisation": row.get("Valorisation"),
        })

    results.sort(key=lambda x: float(x["rsi"] or 0))
    return results


@mcp.tool()
async def get_market_overview() -> dict:
    """
    Donne un aperçu rapide du marché BRVM :
    nombre de titres en hausse/baisse/stable, RSI moyen, top 5 hausses et baisses du jour.
    """
    async def fetch_one(client: httpx.AsyncClient, ticker: str):
        try:
            url = f"{BASE_URL}/{ticker}/{ticker}.indicator.csv"
            r = await client.get(url, timeout=15)
            if r.status_code != 200:
                return None
            return dict(next(csv.DictReader(io.StringIO(r.text))))
        except Exception:
            return None

    async with httpx.AsyncClient() as client:
        rows_raw = await asyncio.gather(*[fetch_one(client, t) for t in STOCK_TICKERS])

    rows = [r for r in rows_raw if r is not None]

    hausse, baisse, stable = [], [], []
    rsi_values = []

    for row in rows:
        var_str = str(row.get("Variation_Cours", "0%")).replace(",", ".").replace("%", "").strip()
        try:
            var = float(var_str)
        except Exception:
            var = 0.0
        entry = {"ticker": row.get("Ticker"), "variation_jour": row.get("Variation_Cours"), "cours": row.get("Cours_Actuel")}
        if var > 0:
            hausse.append(entry)
        elif var < 0:
            baisse.append(entry)
        else:
            stable.append(entry)
        rsi = _parse_float(row.get("RSI", 0))
        if rsi > 0:
            rsi_values.append(rsi)

    hausse.sort(key=lambda x: _parse_float(str(x["variation_jour"]).replace(",", ".")), reverse=True)
    baisse.sort(key=lambda x: _parse_float(str(x["variation_jour"]).replace(",", ".")))

    return {
        "titres_en_hausse": len(hausse),
        "titres_en_baisse": len(baisse),
        "titres_stables": len(stable),
        "rsi_moyen_marche": round(sum(rsi_values) / len(rsi_values), 2) if rsi_values else None,
        "top5_hausses": hausse[:5],
        "top5_baisses": baisse[:5],
    }


if __name__ == "__main__":
    mcp.run()
