from pathlib import Path
from setuptools import setup
import sdist_upip


HERE = Path(__file__).parent
README = (HERE / 'README.rst').read_text()

VERSION = "1.0.0"

setup(
    name="micropython-py-esp32-ulp",
    version=VERSION,
    description="Assembler toolchain for the ESP32 ULP co-processor, written in MicroPython",
    long_description=README,
    long_description_content_type='text/x-rst',
    url="https://github.com/ThomasWaldmann/py-esp32-ulp",
    license="MIT",
    author="py-esp32-ulp authors",
    author_email="tw@waldmann-edv.de",
    maintainer="py-esp32-ulp authors",
    maintainer_email="tw@waldmann-edv.de",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    platforms=["esp32"],
    cmdclass={"sdist": sdist_upip.sdist},
    packages=["esp32_ulp"],
)
