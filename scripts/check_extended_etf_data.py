"""Test an expanded real ETF data source. Never replace missing data with synthetic prices.

Run --limit 12 for network validation first. Full 160-ETF selection requires
at least 160 distinct, validated, complete price histories.
"""
import argparse
from pathlib import Path
import pandas as pd
import yfinance as yf
from large_etf_feasibility import CANDIDATES

# Further ETF candidates, deliberately broader than the 160 needed.
EXTRA = """
VXF VONE VTHR VONG VONV VOE VOT VIOO VIOG VIOV VSS VPL VGK VEU VIGI VYMI
FNDF FNDE FNDC FNDA FNDX FNDR FNDB
SCHF SCHC SCHY SCHM SCHI SCHJ SCHQ SCHP
IEMG IEFA IDEV IAU IEUR IEV EURL EEMV EFAV EFA
IAGG IUSB USIG IGIB SLQD FLOT NEAR ICSH TFLO SHYG HYLB FALN IHY
SPAB SPTI SPTS SPTL SPIP SPBO SPHY SPEM BWX BWZ PCY VWOB
IEI GOVT TTT EDV ZROZ TLO TBF MINT JPST BKLN SRLN EMB VTEI
EWT EWA EWC EWH EWS EWY EWI EWL EWP EWQ EWU EWG EWN EWD EWO EWM EWW EZA
EPU ECH EIDO EIS EPHE ENZL EWM EWK EWM EEM EFA
AAXJ VNM THD TUR GREK EIDO EZA INDA INDY SMIN EPI
IXUS ACWI ACWX URTH AOA AOR AOM AOK VT
IHI IHF IBB IHE IHF IGV SOXX SMH FTEC FENY FSTA FNCL FIDU FUTY FHLC FMAT FREL
XLC XCOM XNTK XITK XMMO XMHQ XSMO XSLV XMLV
PAVE CIBR HACK BUG CLOU SKYY BOTZ ROBO LIT REMX
USCI DBC PDBC DBA DBB DBO BCI COMT GSG GLDM SGOL SIVR
MOO PBJ TAN ICLN QCLN PBW FAN GRID
""".split()
UNIVERSE = list(dict.fromkeys(CANDIDATES + EXTRA))
OUT = Path("results/large_etf_feasibility")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=12, help="0 means all candidates")
    parser.add_argument("--batch", type=int, default=8)
    args = parser.parse_args()
    symbols = UNIVERSE[:args.limit] if args.limit else UNIVERSE
    successes = {}
    failures = []
    for offset in range(0, len(symbols), args.batch):
        batch = symbols[offset:offset + args.batch]
        print("Downloading", batch, flush=True)
        try:
            raw = yf.download(batch, start="2020-01-01", end="2025-02-01",
                              auto_adjust=True, progress=False,
                              threads=False, group_by="column")
            close = raw["Close"]
            if isinstance(close, pd.Series):
                close = close.to_frame(name=batch[0])
            for symbol in batch:
                if symbol not in close.columns:
                    failures.append(symbol)
                    continue
                series = close[symbol].dropna()
                if series.empty:
                    failures.append(symbol)
                    continue
                monthly = series.resample("ME").last()
                validation = monthly.loc["2022-01-31":"2024-12-31"]
                complete = (len(validation) == 36 and validation.notna().all()
                            and (validation > 0).all()
                            and pd.Timestamp("2021-12-31") in monthly.index
                            and pd.notna(monthly.loc["2021-12-31"]))
                if complete:
                    successes[symbol] = monthly
                else:
                    failures.append(symbol)
        except Exception as exc:
            print("Batch download error", repr(exc), flush=True)
            failures += batch
    print("Requested:", len(symbols), " | Valid complete ETF candidates:",
          len(successes), " | Failed or incomplete:", len(failures), flush=True)
    pd.DataFrame({"ticker": symbols,
                  "complete": [t in successes for t in symbols]}).to_csv(
                      OUT / "new_data_source_coverage.csv", index=False)
    if successes:
        pd.DataFrame(successes).to_csv(OUT / "new_data_source_monthly_prices.csv")
    print("NO large optimization scores are claimed until data and methods are validated.", flush=True)


if __name__ == "__main__":
    main()
