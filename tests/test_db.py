from pathlib import Path

from app import db


def test_data_goes_in_the_chosen_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDYAI_DATA", str(tmp_path / "studyai"))
    db.init()
    lecture_id = db.add_lecture("Week 1", "CS 112", "Stacks push and pop items.")
    assert db.get_lecture(lecture_id)["title"] == "Week 1"
    assert (tmp_path / "studyai" / "studyai.db").exists()


def test_default_folder_is_outside_the_project(monkeypatch):
    monkeypatch.delenv("STUDYAI_DATA")
    assert "StudyAI" in str(db.data_dir())
    assert db.data_dir() != Path(__file__).parent.parent / "data"


def test_settings_round_trip():
    assert db.get_setting("gemini_api_key") is None
    db.set_setting("gemini_api_key", "abc")
    db.set_setting("gemini_api_key", "def")
    assert db.get_setting("gemini_api_key") == "def"
    db.delete_setting("gemini_api_key")
    assert db.get_setting("gemini_api_key") is None
