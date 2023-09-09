from setuptools import setup

setup(
    name='rabbit_handler_kvg',
    version='1.0.0',
    description='A handler for rabbitMQ',
    author='Vyacheslav Kosarev',
    author_email='vyach.kosarev@gmail.com',
    packages=['rabbit_handler_kvg'],
    install_requires=['pika','python-dotenv','requests']
)

