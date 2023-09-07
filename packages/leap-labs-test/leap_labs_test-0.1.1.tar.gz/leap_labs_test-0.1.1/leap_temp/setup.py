from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='leap_labs_test',
    version='0.1.1',
    url='https://www.leap-labs.com/',
    license='Closed-source',
    author='Jessica Rumbelow',
    author_email='jessica@leap-labs.com',
    description='Leap Labs Universal Interpretability Engine',  
    packages=find_packages(),
    ext_modules=cythonize("leap_temp/*.py", language_level="3", compiler_directives={'warn.unreachable': False}),
    install_requires=['tensorflow', 'json', 'pandas', 'IPython', 'tqdm', 'torchvision', 'copy', 'threading', 'torch', 'os', 'random', 'requests', 'leap_labs_test', 'wandb', 'atexit', 'numpy', 'PIL', 'subprocess', 'shutil'],
)