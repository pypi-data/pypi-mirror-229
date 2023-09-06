from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='Leap Labs',
    version='0.1.0',
    url='https://www.leap-labs.com/',
    license='Closed-source',
    author='Jessica Rumbelow',
    author_email='jessica@leap-labs.com',
    description='Leap Labs Universal Interpretability Engine',  
    packages=find_packages(),
    ext_modules=cythonize("leap_temp/*.py", language_level="3", compiler_directives={'warn.unreachable': False}),
    install_requires=['tensorflow', 'atexit', 'copy', 'numpy', 'wandb', 'subprocess', 'requests', 'pandas', 'IPython', 'threading', 'os', 'json', 'random', 'tqdm', 'torch', 'shutil', 'leap', 'PIL', 'torchvision'],
)