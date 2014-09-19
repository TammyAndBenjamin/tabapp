# -*- coding: utf-8 -*-

class User:
    def __init__(self, row):
        self.__id = row.get('id')
        self.__username = row.get('username')
        self.__password = row.get('password')


    def is_authenticated(self):
        return bool(self.__id)


    def is_active(self):
        return bool(self.__id)


    def is_anonymous(self):
        return not bool(self.__id)


    def get_id(self):
        return str(self.__id)
