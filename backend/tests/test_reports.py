from app.services import build_respectful_roast


def test_roast_uses_the_complete_category_aggregate_not_raw_messages():
    data = {"total_complaints": 12, "average_frustration": 7.4, "categories": [{"name": "Wi-Fi", "count": 6}, {"name": "Timetable", "count": 4}, {"name": "Canteen", "count": 2}]}
    roast = build_respectful_roast(data)
    assert "12 reports" in roast
    assert "7.4/10" in roast
    assert "Wi-Fi: 6" in roast
    assert "Timetable: 4" in roast
    assert "Canteen: 2" in roast
