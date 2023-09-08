from setuptools import find_packages, setup
import glob
from pathlib import Path

package_data = []
for file in glob.glob('formatChecker/res/*/*/*'):
    package_data.append(file)   
print(package_data)

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
    
setup(
    name='igs-toolbox',
    version='1.3.1',    
    description='A toolbox to check whether files follow a predefined schema.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.rki.de/DE/Content/Infekt/IGS/IGS_node.html',
    author='IMS Developers',
    author_email='IMS-Developers@rki.de',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts':[
            'jsonChecker=formatChecker.jsonChecker:main',
            'convertSeqMetadata=converters.convertSeqMetadata:main',
            'convertAnswerSet=converters.convertAnswerSets:main'
        ]
    },
    python_requires='>=3',
    install_requires=[                
                'jsonschema>=4.16.0',
                'pandas'
                ],
    package_data={'formatChecker': package_data},
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
