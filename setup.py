from setuptools import setup, find_packages


f = open('README.txt')
readme = f.read()
f.close()

setup(
    name='vkontakte-spy',
    version='0.1.0',
    description='Vkontakte-spy is a set of classes that can parse vkontakte.ru web site. Also it integrates with Django.',
    long_description=readme,
    author='Alexander Nosov',
    author_email='trashgenerator@gmail.com',
    url='http://github.com/trashgenerator/vkontakte-spy',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    package_data={
        'vkontakte_spy': [
            'fixtures/*.json',
        ],
    },
    zip_safe=False,
)
