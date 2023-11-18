from setuptools import setup, find_packages

setup(
    name='droidbot_assistant_gpt',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'uiautomator2==2.16.23',
        'openai',
        'packaging==20.9'
    ],
    entry_points={
        'console_scripts': [
            # command line executor
        ],
    },
)
