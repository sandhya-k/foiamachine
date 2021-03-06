"""
put functions here that
combine, transform or derive
data from raw source
"""
from decimal import Decimal
from special_cases import *

import probablepeople 

test_pp = True

# TODO: Handle salary and hourly

def do_all_transformations(data_row, header, attachment):
    """
    a little wrapper
    to do all transformations;
    always safe to call
    """
    data_row = split_single_name_field(data_row, attachment)
    data_row = caps_to_title(data_row, header)
    data_row = salaries_to_decimals(data_row) # goes before other transformations
    data_row = put_hourly_in_salary(data_row)
    data_row = pop_unreported_headers(data_row, header)
    data_row = strip_commas_out_of_names(data_row)
    return data_row


def strip_commas_out_of_names(data_row):
    """
    simple enough
    """
    data_row['first_name'] = data_row['first_name'].replace(',',' ')
    data_row['last_name'] = data_row['last_name'].replace(',',' ')
    return data_row

def disambiguate_first_and_last(data_row):
    """
    indicies for first,
    last names overlap so sort
    them out distinctly
    """
    # check if first and last exist 
    if data_row['first_name']['indices'] and data_row['last_name']['indices']:
        # check if first and last share any indices
        if len(list(data_row['first_name']['indices']) + list(data_row['last_name']['indices'])) \
        > len(set(list(data_row['first_name']['indices']) + list(data_row['last_name']['indices']))):
            # uh ... just gonna really inelegantly assume the overlap belongs to first name 
            # due to stricter keyword searches on first and 'last name, first name' common ambiguity
            # TODO: fix this bad hack
            print 'disambiguating first, last', data_row['first_name']['indices'], data_row['last_name']['indices']
            overlap = [x for x in data_row['first_name']['indices'] \
                       if x in data_row['last_name']['indices']]
            # don't leave last name with nothing
            if set(overlap) == set(data_row['last_name']['indices']):
                data_row['last_name']['indices'] = overlap
                data_row['first_name']['indices'] = set()
                return data_row 
            data_row['first_name']['indices'] = overlap
            data_row['last_name']['indices'] = [x for x in data_row['last_name']['indices'] \
                                                if x not in overlap]
            
            print data_row['first_name']['indices'], data_row['last_name']['indices']


    return data_row


def split_single_name_field(data_row, attachment):
    """
    split names into two
    fields: first and last, by comma
    or by ordering
    """
    if data_row['last_name'] and not data_row['first_name']:
        # TODO: this totally belongs elsewhere in transformations
        try:
            data_row['last_name'] = data_row['last_name'].decode('utf-8')
            data_row['first_name'] = data_row['first_name'].decode('utf-8')
        except:
            print 'failed to decode name to utf-8'
        # just testing out probablepeople
        if test_pp and '/' not in data_row['last_name'] and attachment.id not in first_name_first and attachment.id not in last_name_first:
            parsed_name = probablepeople.parse(data_row['last_name'])
            last_names = [x[0] for x in parsed_name if x[1] == 'Surname']
            if last_names:
                last_name = last_names[0]
            else:
                last_name = ''
            first_names = [x[0] for x in parsed_name if x[1] == 'GivenName']
            if first_names:
                first_name = first_names[0]
            else:
                first_name = ''
            middle_inits = [x[0] for x in parsed_name if x[1] == 'MiddleInitial']
            if middle_inits:
                middle_init = middle_inits[0]
            else:
                middle_init = ''
            suffixes = [x[0] for x in parsed_name if x[1] == 'SuffixGenerational']
            if suffixes:
                suffix = suffixes[0]
            else:
                suffix = ''
            data_row['last_name'] = ' '.join([last_name, suffix])
            data_row['first_name'] = ' '.join([first_name, middle_init])
            #test_file = open('test_pp.txt','a')
            #test_file.write(data_row['first_name'] + '    ' + data_row['last_name'] + '\n')
            #test_file.close()
            if data_row['last_name'].strip() and data_row['first_name'].strip():
                return data_row




        comma_delimited = data_row['last_name'].split(',')
        if len(comma_delimited) == 2:
            data_row['last_name'] = comma_delimited[0]
            data_row['first_name'] = comma_delimited[1]
        elif len(comma_delimited) > 2:
            data_row['first_name'] = comma_delimited[-1].lstrip()
            data_row['last_name'] = ' '.join(comma_delimited[:-1])
        else:
            space_delimited = data_row['last_name'].split(' ')
            #hack
            if '/' in data_row['last_name']:
                space_delimited = data_row['last_name'].split('/')
            if len(space_delimited) > 1:
                data_row = set_order_single_name(data_row, attachment)
                if not data_row['first_name']:
                    msg = ' fuuuuuuuuuuuuck ... how did they split this up? better special case it ... \n'
                    msg += data_row['last_name'] + '\n'
                    msg += ' '.join(['attachment.id:', str(attachment.id)])
                    raw_input(msg)
    return data_row


def caps_to_title(data_row, header):
    for field in data_row:
        if header[field]['title_case']:
            if data_row[field].isupper():
                data_row[field] = data_row[field].title()
    return data_row
        

def salaries_to_decimals(data_row):
    """
    dollar amounts must
    be converted to proper
    format for reports
    """

    for field in data_row:
        if field in ('salary','hourly'):
            # strip formatting
            data_row[field] = data_row[field].replace('$','').replace(',','')
            if data_row[field]:
                try:
                    data_row[field] = Decimal(data_row[field]) # if it doesn't fit, you must acquit
                except:
                    pass # this will get tossed in separate validation later ... TODO: DRY this
     
    return data_row


def pop_unreported_headers(data_row, header):
    """
    headers that are not
    reported should not go
    into the report
    """
    new_row = {}
    for key in data_row:
        if header[key]['reported']:
            new_row[key] = data_row[key]
    return new_row
            


def put_hourly_in_salary(data_row):
    """
    don't want hourly
    data if salary is
    available here
    """
    # copy hourly to salary if salary
    # TODO: optimize to return converted salary elsewhere
    try:
        converted_salary = Decimal(data_row['salary'])
    except:
        converted_salary = None
    if data_row['hourly'] and not converted_salary:
        data_row['salary'] = data_row['hourly']
    return data_row

