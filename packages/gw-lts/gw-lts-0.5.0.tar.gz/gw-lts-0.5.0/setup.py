import setuptools
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

install_requires = [
    "confluent-kafka>=1.7.0",
    "pyyaml",
    "htcondor",
    "htcondor-dags",
    "python-ligo-lw>=1.8.0",
    "lalsuite>=6.82",
    "cronut>=0.1.0",
    "ligo-scald>=0.8.4",
    "ligo.skymap",
    "igwn-alert>=0.2.2",
    "hop-client>=0.6.0",
    "poetry",
    "ligo.em_bright",
]

extras_requires = {
   "docs": [
            "mkdocs >= 1.3",
            "mkdocs-coverage >= 0.2",
            "mkdocs-gen-files >= 0.3",
            "mkdocs-literate-nav >= 0.4",
            "mkdocs-material-igwn",
            "mkdocs-section-index >= 0.3",
            "mkdocstrings[python]",
            "markdown-callouts >= 0.2",
            "markdown-exec >= 0.5",
            "toml >= 0.10",
   ],
}

setuptools.setup(
    name="gw-lts",
    description="Gravitational Wave Low-Latency Test Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.5.0",
    author="Becca Ewing",
    author_email="rebecca.ewing@ligo.org",
    url="https://git.ligo.org/rebecca.ewing/gw-lts.git",
    license="MIT",
    packages=["gw", "gw.lts", "gw.lts.utils", "gw.lts.dags"],
    entry_points={
        "console_scripts": [
            "igwn-alert-listener=gw.lts.igwn_alert_listener:main",
            "send-inj-stream=gw.lts.send_inj_stream:main",
            "inspinjmsg-find=gw.lts.inspinjmsg_find:main",
            "inj-missed-found=gw.lts.inj_missed_found:main",
            "vt=gw.lts.vt:main",
            "snr-consistency=gw.lts.snr_consistency:main",
            "inj-accuracy=gw.lts.inj_accuracy:main",
            "p-astro=gw.lts.p_astro:main",
            "skymap=gw.lts.skymap:main",
            "latency=gw.lts.latency:main",
            "likelihood=gw.lts.likelihood:main",
            "em-bright=gw.lts.em_bright:main",
            "test-suite-workflow=gw.lts.dags.test_suite_workflow:main",
        ],
    },
    data_files=[
        ("etc",
            ["etc/example_config.yml", "etc/example_fake_data_config.yml"]),
        ("injections",
            ["injections/fake_data_injections.xml.gz"]),
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_requires,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
)
