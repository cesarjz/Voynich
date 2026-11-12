#!/usr/bin/env bash
# Fetch the third-party data used by the re-analysis that cannot be redistributed in this repository
# (unclear or restrictive licences). Everything goes into reanalysis/external/ (ignored by git).
# Sources are pinned to the exact commits / files used in the analysis.
#
#   Gaskell & Bowern (2022) 'meaningful' texts   github.com/danielgaskell/voynich   (onset/coda controls, ctl_NAIB)
#   Naibbe cipher tables (Greshko 2025, MIT)      github.com/greshko/naibbe-cipher   (specificity control ctl_NAIB)
#   Stolfi word grammar (word.grx)                github.com/mzattera/v4j            (word-model comparison)
#   Sefaria: Targum Onkelos, Zohar (Sulam 1945)   storage.googleapis.com/sefaria-export (Models 9 and 16)
#
# TraCES Ge'ez corpus (CC BY-NC-ND 4.0, doi:10.25592/uhhfdm.707): download it yourself, unpack it as
#   reanalysis/external/traces/traces_v1_raw/TraCES_corpus/  and run  python geez/traces_v1_extract.py
#
# Usage (from the reanalysis/ folder):  bash fetch_external.sh
set -euo pipefail
cd "$(dirname "$0")"
EXT=external
mkdir -p "$EXT"

GASKELL_COMMIT=d076a7d081f35098fa405928239595afd2e75927
NAIBBE_COMMIT=5145f52
V4J_COMMIT=dd061388e2e9e5330abcad84b5755195c05d01d2
SEFARIA=https://storage.googleapis.com/sefaria-export

echo "== Gaskell & Bowern meaningful texts"
mkdir -p "$EXT/gaskell_bowern"
curl -fsSL -o "$EXT/gaskell_bowern/meaningful.zip" \
  "https://raw.githubusercontent.com/danielgaskell/voynich/$GASKELL_COMMIT/data/meaningful.zip"
(cd "$EXT/gaskell_bowern" && rm -rf meaningful && mkdir meaningful && unzip -q meaningful.zip -d meaningful)

echo "== Naibbe cipher tables"
mkdir -p "$EXT/naibbe-cipher/references"
curl -fsSL -o "$EXT/naibbe-cipher/references/naibbe_tables.csv" \
  "https://raw.githubusercontent.com/greshko/naibbe-cipher/$NAIBBE_COMMIT/references/naibbe_tables.csv"
curl -fsSL -o "$EXT/naibbe-cipher/LICENSE" \
  "https://raw.githubusercontent.com/greshko/naibbe-cipher/$NAIBBE_COMMIT/LICENSE"

echo "== Stolfi word grammar (v4j)"
mkdir -p "$EXT/v4j"
curl -fsSL -o "$EXT/v4j/word.grx" \
  "https://raw.githubusercontent.com/mzattera/v4j/$V4J_COMMIT/resources/Stolfi/word.grx"

echo "== Sefaria: Targum Onkelos and Zohar"
mkdir -p "$EXT/sefaria/onkelos_aramaic" "$EXT/sefaria/zohar_sulam"
for b in Genesis Exodus Leviticus Numbers Deuteronomy; do
  curl -fsSL -o "$EXT/sefaria/onkelos_aramaic/Onkelos_$b.json" \
    "$SEFARIA/cltk-flat/Tanakh/Targum/Onkelos/Torah/Onkelos%20$b/Hebrew/merged.json"
done
curl -fsSL -o "$EXT/sefaria/zohar_sulam/Zohar_Sulam_1945.json" \
  "$SEFARIA/json/Kabbalah/Zohar/Zohar/Hebrew/Sulam%20Edition%2C%20Jerusalem%201945.json"

echo "== done; checking checksums"
sha256sum -c checksums_external.sha256
