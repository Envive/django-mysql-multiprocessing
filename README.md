# Django MySQL Multiprocessing

A Django MySQL patch to support python multiprocessing

## Installation
```
$ pip install git+https://github.com/Envive/django-mysql-multiprocessing.git
```

## Usage

```python
# config/__init__.py
import pymysql

from django_mysql_multiprocessing import connections

pymysql.install_as_MySQLdb()
connections.apply_patch()
```
