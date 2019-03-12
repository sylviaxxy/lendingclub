#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import datetime
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


def str_process(data):

    """
        Formalize some columns that need to be coverted into float/int

    """
    data['term'] = data['term'].str.replace('months','').astype('int')
    data['emp_length'] = data['emp_length'].str.replace('< 1 year','0').str.replace('10+ years','11').str.replace('n/a','-1').str.strip()
    data['emp_length'] = data['emp_length'].str.replace('years',' ').str.replace('year',' ').str.strip()
    data['emp_length'][data['emp_length'] == '10+'] = 11
    data['emp_length'] = data['emp_length'].astype('float64')
    data['annual_inc'] = data['annual_inc'].astype('float64')

    return data


def time_process(data):

    """

        Transform datatime columns into datatime type

    """

    data['issue_d'] = pd.to_datetime(data['issue_d'])
    data['earliest_cr_line'] = pd.to_datetime(data['earliest_cr_line'])
    data['last_credit_pull_d'] = pd.to_datetime(data['last_credit_pull_d'])
    data['last_pymnt_d'] = pd.to_datetime(data['last_pymnt_d'])
    data['next_pymnt_d'] = pd.to_datetime(data['next_pymnt_d'])

    return data


def desc_rename(data):

    # since the column desc conflicts with sql function, we need to rename this column

    """
            Rename column 'desc' as 'descripton'

    """
    data = data.rename(index=str, columns={"desc": "description"})

    return data


def data_clean(data):

    """
            Clean raw dataset

    """

    data_1 = str_process(data)
    data_2 = time_process(data_1)
    data_3 = desc_rename(data_2)
    # data_4 =  missing_impute(data) # Future Improvement
    return data_3


def wirte_to_loans(df_clean):

    """
            Write dataframe into postgresql database

    """

    engine = create_engine('postgresql://analyst:12345678@localhost:5432/lendingclub')

    df_clean.to_sql(name = 'loans',
                    con = engine,
                    if_exists = 'replace',
                    chunksize = 10000,
                    index = False,
                    method = 'multi')

def main(path):

    #data_path = "./input/loan.csv"

    df = pd.read_csv(path, low_memory=False)
    df_clean = data_clean(df)
    write_to_loans(df_clean)


if __name__ == "__main__":
    main(sys.argv[1])
