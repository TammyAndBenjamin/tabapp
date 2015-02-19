""" TABApp """
# -*- coding: utf-8 -*-

from tabapp import create_app

tabapp = create_app()

if __name__ == '__main__':
    tabapp.run(host='62.210.207.214', port=5050, debug=True)
