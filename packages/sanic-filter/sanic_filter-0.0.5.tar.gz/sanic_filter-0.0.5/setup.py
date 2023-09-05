from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(name='sanic_filter',
      version='0.0.5',
      description='Query filter for Sanic',
      long_description=readme(),
      long_description_content_type='text/markdown',
      packages=['sanic_filter'],
      author_email='lolkin4777@gmail.com',
      # install_requires=['SQLAlchemy>=2.0.20'],
      classifiers=[
          'Programming Language :: Python :: 3.9',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent'
      ],
      python_requires='>=3.9',
      zip_safe=False)