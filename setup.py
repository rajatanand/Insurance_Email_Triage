from setuptools import setup, find_packages

setup(
    name="insurance-email-triage",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.28.0",
        "langchain>=0.0.267",
        "langchain-openai>=0.0.2",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="An insurance email triage system using CrewAI",
    keywords="insurance, email, triage, crewai, ai",
    python_requires=">=3.9",
)