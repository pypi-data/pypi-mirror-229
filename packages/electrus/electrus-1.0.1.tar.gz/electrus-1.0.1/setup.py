from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read the contents of LICENSE file
with open('LICENSE', 'r', encoding='utf-8') as f:
    license_text = f.read()

setup(
    name='electrus',
    version='1.0.1',
    author='Pawan kumar',
    author_email='confict.con@gmail.com',
    description='This project provides a reliable database, allowing you to perform CRUD operations and more on collections of documents.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/embrake/electrus',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='your, keywords, here',
    python_requires='>=3.6',
    install_requires=[
        'requests', 'bson'
    ],
)
