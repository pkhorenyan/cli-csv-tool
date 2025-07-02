import sys
import pytest
from main import apply_filter, apply_order, aggregate, parse_condition, is_number, main

sample_data = [
    {"name": "iphone 15 pro", "brand": "apple", "price": "999", "rating": "4.9"},
    {"name": "galaxy s23 ultra", "brand": "samsung", "price": "1199", "rating": "4.8"},
    {"name": "redmi note 12", "brand": "xiaomi", "price": "199", "rating": "4.6"},
    {"name": "poco x5 pro", "brand": "xiaomi", "price": "299", "rating": "4.4"},
]

def test_apply_filter_numeric_greater():
    result = apply_filter(sample_data, "rating>4.7")
    assert len(result) == 2
    assert result[0]["name"] == "iphone 15 pro"

def test_apply_filter_numeric_equal():
    result = apply_filter(sample_data, "price=199")
    assert len(result) == 1
    assert result[0]["brand"] == "xiaomi"

def test_apply_filter_string_equal():
    result = apply_filter(sample_data, "brand=apple")
    assert len(result) == 1
    assert result[0]["name"] == "iphone 15 pro"

def test_parse_condition_valid():
    col, op, val = parse_condition("rating<=4.5")
    assert col == "rating"
    assert op == "<="
    assert val == "4.5"

def test_is_number():
    assert is_number("4.5") is True
    assert is_number("abc") is False

def test_apply_order_asc():
    result = apply_order(sample_data, "price=asc")
    assert result[0]["price"] == "199"
    assert result[-1]["price"] == "1199"

def test_apply_order_desc():
    result = apply_order(sample_data, "rating=desc")
    assert result[0]["rating"] == "4.9"
    assert result[-1]["rating"] == "4.4"

def test_aggregate_avg():
    result = aggregate(sample_data, "rating=avg")
    assert round(result["avg"], 2) == 4.67

def test_aggregate_min():
    result = aggregate(sample_data, "price=min")
    assert result["min"] == 199.0

def test_aggregate_max():
    result = aggregate(sample_data, "price=max")
    assert result["max"] == 1199.0

def test_parse_condition_invalid():
    with pytest.raises(ValueError, match="Invalid filter condition"):
        parse_condition("price!500")

def test_apply_order_by_string():
    result = apply_order(sample_data, "name=asc")
    assert result[0]["name"] == "galaxy s23 ultra"
    assert result[-1]["name"] == "redmi note 12"

def test_apply_filter_invalid_column():
    with pytest.raises(KeyError):
        apply_filter(sample_data, "nonexistent=apple")

def test_invalid_aggregate_operation():
    with pytest.raises(ValueError, match="Invalid aggregation operation"):
        aggregate(sample_data, "price=median")

def test_main_cli_rating_filter_order(monkeypatch, capsys, tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_content = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8
redmi note 12,xiaomi,199,4.6
poco x5 pro,xiaomi,299,4.4"""

    csv_file.write_text(csv_content)

    monkeypatch.setattr(sys, 'argv', [
        'main.py',
        '--file', str(csv_file),
        '--where', 'rating>4.5',
        '--order-by', 'rating=desc'
    ])

    main()
    captured = capsys.readouterr()

    assert "iphone 15 pro" in captured.out
    assert "iphone 45" not in captured.out
    assert "blah-blah" not in captured.out
    assert "poco x5 pro" not in captured.out
