from functools import wraps
from flask import flash, redirect, url_for, session


class Enterprise():
    def __init__(self, id):
        self.id =id


