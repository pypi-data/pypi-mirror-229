from setuptools import setup, find_packages


setup(
    author="Megagon Labs, Tokyo.",
    author_email="vecscan@megagon.ai",
    description="vecscan: linear-scan based dense vector search engine",
    entry_points={
    },
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.1",
        "numpy",
        "safetensors>=0.3.1",
        "tqdm",
    ],
    license="MIT",
    name="vecscan",
    packages=find_packages(include=["vecscan"]),
    url="https://github.com/megagonlabs/vecscan",
    version='0.0.0',
)
