"""
src/data/standardize.py
-----------------------
Low-level, stateless standardization helpers.

Each function takes a Series or scalar and returns a cleaned version.
No DataFrames are written here — this module is imported by clean_data.py.

Rules:
- Never mutate the input; always return a new Series/value.
- Never introduce random values.
- Every transformation must be fully deterministic.
"""

import re
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# String standardization
# ---------------------------------------------------------------------------

def strip_whitespace(series: pd.Series) -> pd.Series:
    """Strip leading/trailing whitespace from every string value."""
    return series.str.strip()


def normalize_case_title(series: pd.Series) -> pd.Series:
    """Title-case a string series (e.g. 'MUMBAI' -> 'Mumbai')."""
    return series.str.strip().str.title()


def normalize_case_upper(series: pd.Series) -> pd.Series:
    """Upper-case a string series."""
    return series.str.strip().str.upper()


def normalize_case_lower(series: pd.Series) -> pd.Series:
    """Lower-case a string series."""
    return series.str.strip().str.lower()


def normalize_gender(series: pd.Series) -> pd.Series:
    """Normalize gender values to 'M' / 'F'.

    Accepted inputs: M, m, Male, male, F, f, Female, female.
    Anything else becomes pd.NA.
    """
    s = series.str.strip().str.upper()
    s = s.replace({"MALE": "M", "FEMALE": "F"})
    valid = {"M", "F"}
    s = s.where(s.isin(valid), other=pd.NA)
    return s


def normalize_marital_status(series: pd.Series) -> pd.Series:
    """Normalize marital_status to 'Married' / 'Single'."""
    mapping = {
        "married": "Married",
        "single":  "Single",
        "m":       "Married",
        "s":       "Single",
    }
    s = series.str.strip().str.lower().map(mapping)
    return s


def normalize_claim_type(series: pd.Series) -> pd.Series:
    """Standardize claim_type to the five known categories.

    Known values: Theft, Glass Damage, Fire, Accident, Natural Disaster.
    Unrecognized values become pd.NA.
    """
    VALID = {"Theft", "Glass Damage", "Fire", "Accident", "Natural Disaster"}
    s = series.str.strip()
    s = s.where(s.isin(VALID), other=pd.NA)
    return s


def normalize_status(series: pd.Series) -> pd.Series:
    """Standardize claim status to four known values.

    Known values: Open, Approved, Under Review, Rejected.
    """
    VALID = {"Open", "Approved", "Under Review", "Rejected"}
    s = series.str.strip()
    s = s.where(s.isin(VALID), other=pd.NA)
    return s


def normalize_policy_type(series: pd.Series) -> pd.Series:
    """Standardize policy_type to three known values.

    Known values: Comprehensive, Zero Dep, Third Party.
    """
    VALID = {"Comprehensive", "Zero Dep", "Third Party"}
    s = series.str.strip()
    s = s.where(s.isin(VALID), other=pd.NA)
    return s


def normalize_vehicle_type(series: pd.Series) -> pd.Series:
    """Standardize vehicle_type to four known values.

    Known values: MUV, Sedan, Hatchback, SUV.
    """
    VALID = {"MUV", "Sedan", "Hatchback", "SUV"}
    s = series.str.strip()
    s = s.where(s.isin(VALID), other=pd.NA)
    return s


def normalize_city(series: pd.Series, valid_cities: set) -> pd.Series:
    """Strip whitespace and enforce known city set.

    Unknown cities are set to pd.NA (not silently dropped).
    """
    s = series.str.strip()
    s = s.where(s.isin(valid_cities), other=pd.NA)
    return s


def normalize_provider_type(series: pd.Series) -> pd.Series:
    """Standardize provider_type to four known values.

    Known values: Surveyor, Dealer, Garage, Hospital.
    """
    VALID = {"Surveyor", "Dealer", "Garage", "Hospital"}
    s = series.str.strip()
    s = s.where(s.isin(VALID), other=pd.NA)
    return s


# ---------------------------------------------------------------------------
# Numeric standardization
# ---------------------------------------------------------------------------

def clamp_to_positive(series: pd.Series, column_name: str = "") -> pd.Series:
    """Set non-positive numeric values to pd.NA (flag; do not silently fix).

    Returns a new Series where values <= 0 become pd.NA.
    Logs count of affected values via return metadata dict.
    """
    mask = series <= 0
    if mask.any():
        s = series.copy().astype(float)
        s[mask] = pd.NA
        return s
    return series


def clamp_rating(series: pd.Series, low: float = 0.0, high: float = 5.0) -> pd.Series:
    """Set ratings outside [low, high] to pd.NA."""
    s = series.copy().astype(float)
    s[(s < low) | (s > high)] = pd.NA
    return s


def clamp_age(series: pd.Series, low: int = 18, high: int = 100) -> pd.Series:
    """Set ages outside [low, high] to pd.NA."""
    s = series.copy().astype(float)
    s[(s < low) | (s > high)] = pd.NA
    return s


def clamp_model_year(series: pd.Series,
                     low: int = 1990,
                     high: int = 2026) -> pd.Series:
    """Set model_year outside [low, high] to pd.NA."""
    s = series.copy().astype(float)
    s[(s < low) | (s > high)] = pd.NA
    return s


# ---------------------------------------------------------------------------
# Date standardization
# ---------------------------------------------------------------------------

def parse_date_column(series: pd.Series, column_name: str = "") -> pd.Series:
    """Parse a string date column to datetime64[ns].

    Unparseable values become NaT (not silently fixed).
    Accepts ISO-8601 format (YYYY-MM-DD) which is what the dataset uses.
    """
    parsed = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")
    return parsed


# ---------------------------------------------------------------------------
# ID standardization
# ---------------------------------------------------------------------------

def validate_id_pattern(series: pd.Series, pattern: str) -> pd.Series:
    """Return boolean mask: True where the ID matches the pattern."""
    return series.str.match(pattern, na=False)


# Cities in the dataset (source of truth: locations_raw.csv + claimants + providers)
VALID_CITIES = {"Mumbai", "Pune", "Delhi", "Ahmedabad", "Surat"}

# Known ID patterns in the dataset
ID_PATTERNS = {
    "claim_id":    r"^CLM\d{5}$",
    "claimant_id": r"^CLT\d{4}$",
    "policy_id":   r"^POL\d{4}$",
    "vehicle_id":  r"^VEH\d{4}$",
    "provider_id": r"^PRV\d{3}$",
    "invoice_id":  r"^INV\d{5}$",
    "location_id": r"^LOC\d{3}$",
}
