import pytest
import yaml

from tools.export_workbook import StrictLoader, parse_refs


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        ("SCOPE-01 / EG-01", ["SCOPE-01", "EG-01"]),
        ("NESSUNA", []),
        (None, []),
        ("FOLLOW + C05 + P01-P10", ["FOLLOW", "C05", *[f"P{i:02d}" for i in range(1, 11)]]),
        ("P08 -> P02-04", ["P08", "P02", "P03", "P04"]),
        ("MIT-* / HS01–HS09", ["MIT-*", *[f"HS0{i}" for i in range(1, 10)]]),
        ("C42-C44; C46-C48; D05-D06; RISK-*", ["C42", "C43", "C44", "C46", "C47", "C48", "D05", "D06", "RISK-*"]),
        ("RMS-9D / N01 / RISK-*", ["RMS-9D", "N01", "RISK-*"]),
        ("FRIA-27F (tutta FRIA); RMS (tutta RMS); HS01", ["FRIA-27F", "FRIA-*", "RMS-*", "HS01"]),
        ("C17; C23; C31 e altri campi reasoning", ["C17", "C23", "C31"]),
        ("Q21 / campi obbligatori", ["Q21"]),
        ("MIT-001; MIT-002", ["MIT-001", "MIT-002"]),
        ("C03B", ["C03B"]),
        ("G01-G05", ["G01", "G02", "G03", "G04", "G05"]),
    ],
)
def test_parse_refs(cell, expected):
    assert parse_refs(cell) == expected


def test_strict_loader_keeps_yes_no_as_strings():
    assert yaml.load("is: [YES, NO, ON, off]\nflag: true", Loader=StrictLoader) == {
        "is": ["YES", "NO", "ON", "off"],
        "flag": True,
    }


def test_strict_loader_rejects_duplicate_keys():
    with pytest.raises(yaml.YAMLError):
        yaml.load("C63: {a: 1}\nC63: {b: 2}", Loader=StrictLoader)


def test_strict_loader_allows_merge_override():
    doc = "base: &b {x: 1, y: 1}\nitem: {<<: *b, y: 2}"
    assert yaml.load(doc, Loader=StrictLoader)["item"] == {"x": 1, "y": 2}
