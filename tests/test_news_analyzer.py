from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from utils.news_analyzer import NewsAnalyzer


def make_analyzer(client):
    """Construct an analyzer without creating a real Gemini client."""
    analyzer = NewsAnalyzer.__new__(NewsAnalyzer)
    analyzer.client = client
    analyzer.model_name = "gemini-2.5-flash"
    analyzer.config = object()
    return analyzer


def make_response(parsed=None, text="", candidates=True):
    return SimpleNamespace(
        parsed=parsed,
        text=text,
        candidates=[object()] if candidates else [],
        usage_metadata=None,
    )


def test_parse_structured_response_accepts_valid_sdk_parsed_value():
    analyzer = make_analyzer(client=None)
    response = make_response(parsed={
        "description": "Tin tích cực về một dự án cộng đồng.",
        "is_toxic": False,
        "sentiment": 1,
    })

    assert analyzer._parse_structured_response(response) == {
        "description": "Tin tích cực về một dự án cộng đồng.",
        "is_toxic": False,
        "sentiment": 1,
    }


@pytest.mark.parametrize(
    "parsed",
    [
        {"description": "Tóm tắt", "is_toxic": False, "sentiment": -2},
        {"description": "Tóm tắt", "is_toxic": "false", "sentiment": 0},
        {"description": "", "is_toxic": False, "sentiment": 0},
        {"description": "Tóm tắt", "is_toxic": False, "sentiment": 0, "extra": "not allowed"},
    ],
)
def test_parse_structured_response_rejects_invalid_contract(parsed):
    analyzer = make_analyzer(client=None)

    assert analyzer._parse_structured_response(make_response(parsed=parsed)) is None


def test_parse_structured_response_does_not_repair_pre_schema_markdown_payload():
    analyzer = make_analyzer(client=None)
    malformed_response = make_response(
        text='***\n"description": "Robot mất kiểm soát",\n"is_toxic": false,\n"sentiment": -1\n***'
    )

    assert analyzer._parse_structured_response(malformed_response) is None


def test_call_gemini_retries_transient_error_then_returns_valid_result(monkeypatch):
    successful_response = make_response(parsed={
        "description": "Bài viết cung cấp thông tin an toàn.",
        "is_toxic": False,
        "sentiment": 0,
    })
    generate_content = Mock(side_effect=[Exception("503 UNAVAILABLE"), successful_response])
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    analyzer = make_analyzer(client)
    monkeypatch.setattr("utils.news_analyzer.time.sleep", lambda _: None)
    monkeypatch.setattr("utils.news_analyzer.random.uniform", lambda _start, _end: 0)

    result, metrics = analyzer._call_gemini_direct("Tiêu đề", "Nội dung")

    assert result["sentiment"] == 0
    assert generate_content.call_count == 2
    assert metrics["attempts"] == 2
    assert metrics["retry_count"] == 1


def test_parse_structured_response_truncates_overlong_description():
    analyzer = make_analyzer(client=None)
    response = make_response(parsed={
        "description": "x" * 201,
        "is_toxic": False,
        "sentiment": 0,
    })

    result = analyzer._parse_structured_response(response)

    assert result["description"] == "x" * 200


def test_call_gemini_does_not_retry_invalid_request(monkeypatch):
    generate_content = Mock(side_effect=Exception("400 INVALID_ARGUMENT"))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    analyzer = make_analyzer(client)
    monkeypatch.setattr("utils.news_analyzer.time.sleep", lambda _: None)

    result, metrics = analyzer._call_gemini_direct("Tiêu đề", "Nội dung")

    assert result is None
    assert generate_content.call_count == 1
    assert metrics["retry_count"] == 0
