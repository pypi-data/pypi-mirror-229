from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="censius",
    version="1.9.0",
    description="API for Censius",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["censius/client"],
    package_dir={"": "src"},
    packages=[
        "censius",
        "censius.nlp",
        "censius.ml",
        "censius.validation",
        "censius.validation.train_test",
        "censius.validation.train_test.detectors",
    ],
    install_requires=[
        "requests>=2.25",
        "jsonschema==3.2",
        "pandas>=1.3,<2.0",
        "numpy>=1.21",
        "elemeta==1.0.6",
        "pyyaml>=5.4",
        "pydantic>=1.8,<2.0",
        "textstat>=0.7.3",
    ],
    extras_require={"dev": ["pytest>=3.7", "pdoc3==0.9.2"]},
    url="https://github.com/Censius/censius-logs-python-sdk",
    author="Censius",
    author_email="dev@censius.ai",
    keywords=[],
)
