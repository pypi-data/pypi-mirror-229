from setuptools import find_packages, setup

setup(
    name="stacking_fmri",
    version="0.1.1",
    description="An implementation of stacked regression for functional MRI (fMRI) data",
    author="Ruogu Lin",
    author_email="ruogulin@cs.cmu.edu",
    platforms=["any"],
    url="https://github.com/brainML/Stacking",
    packages=find_packages(),
    download_url="https://github.com/brainML/Stacking/archive/refs/heads/main.zip",
    keywords=["stacking", "brain", "fmri"],
    install_requires=[
        "numpy",
        "cvxopt",
        "scikit-learn",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
