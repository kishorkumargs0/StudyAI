import importlib


def test_data_folder_can_be_moved(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDYAI_DATA", str(tmp_path / "studyai"))
    from app import db

    db = importlib.reload(db)
    db.init()
    lecture_id = db.add_lecture("Week 1", "CS 112", "Stacks push and pop items.")
    assert db.get_lecture(lecture_id)["title"] == "Week 1"
    assert (tmp_path / "studyai" / "studyai.db").exists()
    monkeypatch.delenv("STUDYAI_DATA")
    importlib.reload(db)


def test_default_folder_is_outside_the_project():
    from app import db

    assert "StudyAI" in str(db.DATA_DIR)
    assert db.DATA_DIR != db.Path(__file__).parent.parent / "data"
