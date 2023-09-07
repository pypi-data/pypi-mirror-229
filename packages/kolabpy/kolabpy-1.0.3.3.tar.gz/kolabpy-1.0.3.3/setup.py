from setuptools import setup
setup(
	  name='kolabpy', #module 이름
	  version='1.0.3.3',  
	  description='',
	  long_description= 'Contributor:apjh2529@naver.com,kkd8326@snu.ac.kr', 
	  author='Kolab',
	  author_email='kkd8326@snu.ac.kr',
	  url='https://aric.snu.ac.kr/',
	  license='MIT',
	  py_modules=['pymodule'], #업로드할 module
	  python_requires='>=3', #파이썬 버전 
	  install_requires=['saspy==5.3.0', 'geopandas>=0.10', 'folium>=0.8'], #module 필요한 다른 module
	  packages=['kolabpy'] #업로드할 module이 있는 폴더
)