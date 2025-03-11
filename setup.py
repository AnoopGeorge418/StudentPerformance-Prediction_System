from setuptools import find_packages, setup  # type: ignore

HYPHEN_E_DOT = '-e .'

def get_requirements(path:str) -> list[str]:
    '''This function will return the list of requirements'''
    requirements = []
    with open(path) as file_path:
        requirements = (file_path.readlines())
        requirements = ([requirement.replace('\n', '') for requirement in requirements])

        # removing -e . from list cause it is used to trigger the setup.py
        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)

    return requirements

setup(
    name = 'StudentPerformance-Prediction_System',
    version = '0.0.1',
    description = 'A Model that allows users to predict the student performance absed on their scores.',
    author = 'Anoop George',
    author_email = 'anoopgeorge418@gmail.com',
    maintainer = 'Anoop George',
    maintainer_email = 'anoopgeorge418@gmail.com',
    license = 'MIT',
    packages = find_packages(),
    install_requires = get_requirements('./requirements.txt')
)