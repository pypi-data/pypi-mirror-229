import setuptools
PACKAGE_NAME = "gender-detection-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.2.17',
    author="Circles",
    author_email="info@circles.zone",
    description="PyPI Package for gender detection",
    long_description="This is a package for running gender detection and predicting gender",
    long_description_content_type="text/markdown",
    url="https://github.com/circles-zone/gender-detection-local-python-package",
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "tensorflow>=2.13.0",
        "logzio-python-handler>=4.1.0",
        "opencv_python>=4.7.0.72",
        "opencv_python_headless>=4.7.0.72",
        "PyMySQL>=1.0.2",
        "python-dotenv>=1.0.0",
        "scikit-learn>=1.3.0",
        "tqdm>=4.66.1",
        "database-infrastructure-local>=0.0.11",
        "gender-local>=0.0.3",
        "logger-local>=0.0.51"
    ]
)
