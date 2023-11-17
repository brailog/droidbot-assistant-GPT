from setuptools import setup, find_packages

setup(
    name='droidbot_assistant_gpt',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'uiautomator2',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            # command line executor
        ],
    },
)
