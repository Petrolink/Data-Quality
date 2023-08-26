from setuptools import setup
  
setup(
    name='dq_dimensions',
    version='0.1',
    description='open source callable curve-level dimension functions that implement the Petrolink data quality algorithms dimension logic, allowing for a more direct representation of how Petrolink determines their dimension values. ',
    author='PetroLink',
    author_email='allan.gonzalez@colostate.edu',
    packages=['dq_dimensions'],
    install_requires=[
        'datetime',
        'typing',
        'copy',
    ],
)