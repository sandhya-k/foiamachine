"""
validates stuff
"""

from decimal import Decimal
from meta import *


def validate_line(line):
    """
    takes line dict keywords
    and verifies existence
    and types of data
    """
    field_headers = get_field_headers()

    if not validate_salary_format(line):
        return False
    
    if not validate_agency_name(line):
        return False
    
    return line
    

def validate_salary_format(line):
    salary = line['salary']
    try:
        line['salary'] = Decimal(salary) # if it doesn't fit, you must acquit
    except:
        return None
    return line

def validate_agency_name(line):
    """
    this feels redundant
    but existence of values
    should validate here
    """
    if not line['agency']:
        return False
    return True
