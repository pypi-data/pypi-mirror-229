from setuptools import setup, find_packages
#https://betterscientificsoftware.github.io/python-for-hpc/tutorials/python-pypi-packaging/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

setup(
    name='truthometer',
    version='0.1.16',
    description='Fact checker for GPT and other LLMs',
    url='https://github.com/bgalitsky/Truth-O-Meter-Making-ChatGPT-Truthful',
    author='Boris Galitsky',
    author_email='bgalitsky@hotmail.com',
    license='BSD 2-clause',
    #packages=find_packages(where="truthometer"),
    packages=['truthometer', 'truthometer.external_apis', 'truthometer.nlp_utils', 'truthometer.html',
                'truthometer.nlp_utils.allow_list_manager', 'truthometer.nlp_utils.ner', 'truthometer.nlp_utils.allow_list_manager.resources',
              'truthometer.third_party_models' ],
    package_data={
        "truthometer": [
            "**/*.txt"
        ],
    },
    install_requires=[
                      'numpy',
                      'spacy',
                    'requests',
                    'pandas'
                      ],
    #include_package_data=True,
    #package_dir={"": "truthometer.nlp_utils.allow_list_manager/resources"},
    #include_package_data=True
    #package_data={'truthometer':['truthometer/nlp_utils/allow_list_manager/resources/*']},
    #                        'truthometer/*.txt']},
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
    ],
)