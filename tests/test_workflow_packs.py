

from pathlib import Path

from a11yway.core.workflow_packs import (
    list_workflow_packs,
    list_workflows,
    load_workflow_pack,
)
from a11yway.main import main


EXPECTED_PACK_IDS = {
    "education",
    "college_applications",
    "ngo_services",
    "government_services",
    "ai_products",
    "scholarships",
    "public_resources",
}


def test_env_example_exists_with_groq_placeholder() -> None:

    env_example = Path(".env.example")

    assert env_example.exists()
    text = env_example.read_text(encoding="utf-8")
    assert "GROQ_API_KEY=your_groq_api_key_here" in text
    assert "A11YWAY_AI_SCOUT_ENABLED=false" in text
    assert "deterministic audits work without any key" in text


def test_gitignore_keeps_env_example_trackable() -> None:

    lines = Path(".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in lines
    assert ".env.*" in lines
    assert "!.env.example" in lines
    assert lines.index("!.env.example") > lines.index(".env.*")


def test_workflow_pack_files_exist() -> None:

    for pack_id in EXPECTED_PACK_IDS:
        assert Path("a11yway/workflow_packs", f"{pack_id}.json").exists()


def test_list_workflow_packs_returns_expected_packs() -> None:

    packs = list_workflow_packs()

    assert {pack["pack_id"] for pack in packs} == EXPECTED_PACK_IDS


def test_load_workflow_pack_returns_known_pack() -> None:

    pack = load_workflow_pack("college_applications")

    assert pack is not None
    assert pack["name"] == "College Applications"
    assert pack["workflows"]


def test_load_workflow_pack_returns_none_for_invalid_pack() -> None:

    assert load_workflow_pack("not_a_real_pack") is None
    assert load_workflow_pack("../education") is None


def test_each_pack_has_required_workflow_shape() -> None:

    required_fields = {
        "id",
        "name",
        "description",
        "required_actions",
        "relevant_issue_types",
    }

    for pack_id in EXPECTED_PACK_IDS:
        workflows = list_workflows(pack_id)
        assert workflows, pack_id
        for workflow in workflows:
            assert required_fields.issubset(workflow), workflow
            assert workflow["id"]
            assert workflow["name"]
            assert workflow["description"]
            assert workflow["required_actions"]
            assert workflow["relevant_issue_types"]


def test_cli_list_packs_works(capsys) -> None:

    exit_code = main(["--list-packs"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "A11yway workflow packs" in captured.out
    assert "ngo_services" in captured.out
    assert "Issues found" not in captured.out


def test_cli_show_pack_works(capsys) -> None:

    exit_code = main(["--show-pack", "ngo_services"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "NGO Services" in captured.out
    assert "Responsible use" in captured.out
    assert "submit_contact_form" in captured.out
    assert "Required actions" in captured.out


def test_cli_suggest_tasks_works(capsys) -> None:

    exit_code = main(["--suggest-tasks", "ai_products"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "AI Products" in captured.out
    assert "deterministic templates" in captured.out
    assert "open_chat_interface" in captured.out
    assert "Relevant issue types" in captured.out
    assert "browser_steps" in captured.out


def test_cli_suggest_tasks_with_source_does_not_run_audit(capsys) -> None:

    exit_code = main(["https://example.org", "--suggest-tasks", "ngo_services"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Source provided: https://example.org" in captured.out
    assert "can be audited separately" in captured.out
    assert "Issues found" not in captured.out
