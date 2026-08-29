from types import SimpleNamespace

from utils.active_learner import ActiveLearner


def test_extract_keyword_pattern_uses_validated_sdk_parsed_value():
    learner = ActiveLearner.__new__(ActiveLearner)
    learner.model_name = "gemini-2.5-flash"
    learner.client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_kwargs: SimpleNamespace(parsed={"pattern": "lừa đảo"}, text="")
        )
    )

    assert learner._extract_keyword_pattern("Cảnh báo", "Người dùng báo lừa đảo") == "lừa đảo"


def test_extract_keyword_pattern_rejects_invalid_structured_value():
    learner = ActiveLearner.__new__(ActiveLearner)
    learner.model_name = "gemini-2.5-flash"
    learner.client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_kwargs: SimpleNamespace(parsed={"pattern": 123}, text="")
        )
    )

    assert learner._extract_keyword_pattern("Cảnh báo", "Người dùng báo lừa đảo") is None
