from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()
setup(
    name='phonegpt',
    version='1.9.2',
    packages=find_packages(),
    install_requires=[
        'twilio',
        'openai',
        'vosk'
    ],

    author='Ehsan Amiri',
    author_email='e.amiri89@gmail.com',
    description='Make interactive phone call, using Twilio and OpenAI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ensood/phone-gpt',
)