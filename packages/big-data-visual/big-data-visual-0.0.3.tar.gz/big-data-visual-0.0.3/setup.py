from setuptools import setup

def readme_file():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(name='big-data-visual',
      version='v0.0.3',
      author='武汉美宸时科科技有限公司',
      author_email='28206254@qq.com',
      maintainer='金飞',
      maintainer_email='28206254@qq.com',
      description='方便进行大数据处理、呈现的工具类封装包',
      packages=['plot'], 
      py_modules=[''],
      long_description=readme_file(),
      install_requires=['matplotlib', 'numpy'],
      url='https://www.fashiontech.top')