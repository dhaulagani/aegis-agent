from setuptools import setup, find_packages

setup(
    name="aegis-agent",
    version="1.0.0",
    description="Autonomous AI Coding Agent Safety, Blast-Radius Auditor & Hallucination Shield",
    author="dhaulagani",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aegis = aegis.cli:main",
        ],
    },
)
