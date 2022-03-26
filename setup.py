import re
from setuptools import setup
import sdist_upip


def long_desc_from_readme():
    with open('README.rst', 'r') as fd:
        long_description = fd.read()

        # remove badges
        long_description = re.compile(r'^\.\. start-badges.*^\.\. end-badges', re.M | re.S).sub('', long_description)

        # strip links. keep link name and use literal text formatting
        long_description = re.sub(r'`([^<`]+) </[^>]+>`_', '``\\1``', long_description)

        return long_description


setup(
    name="micropython-esp32-ulp",
    use_scm_version={
        'local_scheme': 'no-local-version',
    },
    description="Assembler toolchain for the ESP32 ULP co-processor, written in MicroPython",
    long_description=long_desc_from_readme(),
    long_description_content_type='text/x-rst',
    url="https://github.com/micropython/micropython-esp32-ulp",
    license="MIT",
    author="micropython-esp32-ulp authors",
    author_email="tw@waldmann-edv.de",
    maintainer="micropython-esp32-ulp authors",
    maintainer_email="tw@waldmann-edv.de",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    setup_requires=['setuptools_scm'],
    platforms=["esp32", "linux", "darwin"],
    cmdclass={"sdist": sdist_upip.sdist},
    packages=["esp32_ulp"],
)
