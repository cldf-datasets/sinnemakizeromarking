from setuptools import setup


setup(
    name='cldfbench_sinnemakizeromarking',
    py_modules=['cldfbench_sinnemakizeromarking'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'sinnemakizeromarking=cldfbench_sinnemakizeromarking:Dataset',
        ]
    },
    install_requires=[
        'cldfbench[glottolog]',
        'pyyaml',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
