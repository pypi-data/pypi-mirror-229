from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='pdf_table2json',
    version='0.0.1',
    description='PDF Table to JSON Converter',
    author='hielosan',
    author_email='hielosan@naver.com',
    url='https://github.com/yousojeong/pdf-table-extract/',
    install_requires=[
        'opencv-python',
        'numpy',
        'PyMuPDF',
        'pdf_table2json',
    ],
    packages=find_packages(exclude=[]),
    keywords=['pdf', 'table', 'json', 'converter', 'cv', 'openCV'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
