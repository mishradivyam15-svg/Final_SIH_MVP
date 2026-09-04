from ai.preprocessing import normalize_text


def test_whitespace_cleanup():
    text = "Worker   fell\nfrom a ladder.\t"
    result = normalize_text(text)

    assert result == "Worker fell from a ladder."


def test_empty_text():
    assert normalize_text("") == ""


def test_safety_information_preserved():
    text = "Worker fell approximately 30 feet from an unguarded platform."

    result = normalize_text(text)

    assert "30 feet" in result
    assert "unguarded platform" in result