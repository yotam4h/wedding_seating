from pathlib import Path

import pytest

from wedding_seating.__main__ import main


@pytest.fixture
def sample_guest_csv(tmp_path: Path) -> Path:
	csv_content = (
		"name,group,vip,avoid,friends\n"
		"Alice,,1,,Bob\n"
		"Bob,,0,,Alice\n"
		"Carol,Family1,0,,\n"
	)
	csv_path = tmp_path / "guests.csv"
	csv_path.write_text(csv_content)
	return csv_path


def test_cli_exports_csv(
	sample_guest_csv: Path,
	tmp_path: Path,
	capsys: pytest.CaptureFixture[str],
) -> None:
	output_prefix = tmp_path / "seating_plan"
	exit_code = main(
		[
			str(sample_guest_csv),
			"--table-size",
			"2",
			"--vip-tables",
			"1",
			"--max-iter",
			"5",
			"--export-prefix",
			str(output_prefix),
			"--export-format",
			"csv",
			"--no-print",
		]
	)

	captured = capsys.readouterr()

	assert exit_code == 0
	assert (tmp_path / "seating_plan.csv").exists()
	# --no-print suppresses table output
	assert captured.out.strip() == ""


def test_cli_missing_file_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
	exit_code = main(["/tmp/does-not-exist.csv", "--no-print"])
	captured = capsys.readouterr()

	assert exit_code == 1
	assert "does-not-exist" in captured.err
