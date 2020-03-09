from setuptools import find_packages, setup

setup(name='dynamo-size',
      version='1.0.1',
      url='https://github.com/tallesl/py-dynamo-size',
      author='Talles Lasmar',
      author_email='talleslasmar@gmail.com',
      description='Roughly calculates DynamoDB item size.',
      long_description=open('README.md', 'r').read(),
      long_description_content_type='text/markdown',
      packages=find_packages())
