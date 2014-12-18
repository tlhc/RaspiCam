#!/usr/bin/env python
""" run all tests """
import os
def main():
    """ run all """
    os.system("python -m unittest discover -s '.' -p 'test_*.py'")

if __name__ == '__main__':
    main()
