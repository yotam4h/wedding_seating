from pathlib import Path
from setuptools import find_packages, setup  # type: ignore[import-not-found]


def read_requirements() -> list[str]:
	requirements_path = Path(__file__).parent / "requirements.txt"
	if requirements_path.exists():
		return [line.strip() for line in requirements_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
	return []


def read_long_description() -> str:
	readme_path = Path(__file__).parent / "README.md"
	if readme_path.exists():
		return readme_path.read_text(encoding="utf-8")
	return "Plan wedding seating charts with VIP, group, and friend constraints."


setup(
	name="wedding-seating",
	version="0.2.0",
	description="Optimize wedding seating arrangements with VIP, conflict, and friend heuristics.",
	long_description=read_long_description(),
	long_description_content_type="text/markdown",
	author="Wedding Seating Contributors",
	url="https://github.com/yotam4h/wedding_seating",
	license="MIT",
	packages=find_packages(exclude=("tests", "examples")),
	python_requires=">=3.9",
	install_requires=read_requirements(),
	extras_require={
		"dev": [
			"pytest>=8.0",
		],
	},
	include_package_data=True,
	entry_points={
		"console_scripts": [
			"wedding-seating=wedding_seating.__main__:main",
		]
	},
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.11",
		"Programming Language :: Python :: 3.12",
		"Programming Language :: Python :: 3.13",
		"Topic :: Office/Business :: Scheduling",
	],
	keywords=["wedding", "seating", "optimization", "events"],
)
