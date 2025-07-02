"""
=========================
preparing conflicts
=========================

Use the affiliation column to find mentor and mentees that belong to the same university / organization
Generates then a PersonID for mentees and PaperID - PeresonIDList for mentors, where PersonIDList is a ;
separated list of people with the same affiliation

Added: Because it was hard to have standard names for institutions, there is the possibility to use the
email address provided as a unique id for that. Problems with this is that insitution server names can
be not unique (multiple in same insitution or shared address across institutions), this also does not
handle personal email addresses (which we encourage not to use).
"""
import argparse
import sys
import logging

import numpy as np
import pandas as pd
import pathlib
from functools import partial

file_path = pathlib.Path(__file__).parent

EMAIL_COL = 'email_address'
INSTITUTION_COLUMNS = ['std_institution_1', 'std_institution_2']

def main(mentor_file, mentee_file, out_mentor_file, out_mentee_file, use_email_as_institution=False):
    mentors = pd.read_csv(mentor_file)
    mentees = pd.read_csv(mentee_file)

    if use_email_as_institution:
        INSTITUTION_COLUMNS = ['email_id']
        mentors['email_id'] = mentors[EMAIL_COL].astype('string').apply(get_email_id)
        mentees['email_id'] = mentees[EMAIL_COL].astype('string').apply(get_email_id)
    
    mentees['PersonID'] = mentees.index
    mentors['PaperID'] = mentors.index

    mentors = compute_conflicts(mentors, mentees, INSTITUTION_COLUMNS)

    mentees.to_csv(out_mentee_file, index=False)
    mentors.to_csv(out_mentor_file, index=False)

def _parse_args(argv):
    parser = argparse.ArgumentParser(description='path of mentors/mentees files')
    parser.add_argument('--mentor-file', help='Path to data directory.',
                        default=file_path / '../raw_data/StandardizedMentorList.csv')
    parser.add_argument('--mentee-file', help='Path to metadata file base on path-data',
                        default=file_path / '../raw_data/StandardizedMenteeList.csv')
    parser.add_argument('--out-mentor-file', help='name of the classification file',
                        default=file_path / '../preprocessed_data/Mentors.csv')
    parser.add_argument('--out-mentee-file', help='Prefix output file.',
                        default=file_path / '../preprocessed_data/Mentees.csv')
    parser.add_argument('--use-email-as-institution','--email-id','-e',
                        help='use the server email name as the institution column',action='store_true')
    args = parser.parse_args(argv)
    args = vars(args)

    return args

def get_email_id(address):
    id = address.split('@')[-1]
    return id if not id.endswith('.com') else pd.NA

def compute_conflicts(mentors, mentees, columns):
    """
    Compute conflict for a given dataframe
    """
    find_corresponding_conflicts_people = partial(find_corresponding_conflicts, df=mentees, columns=columns)
    mentors['PersonIDList'] = mentors.apply(find_corresponding_conflicts_people, axis=1)

    return mentors

def find_corresponding_conflicts(affi, df, columns):
    """
    find conflicts and append them for this row
    """
    conflicts = set()
    for coltee in columns:
        for coltor in columns:
            conflicts.update(df[df[coltee] == affi[coltor]].index)
    conflicts = df.loc[list(conflicts)]
    return ';'.join(conflicts['PersonID'].astype(str).to_list())

if __name__ == '__main__':
    pgrm_name, argv = sys.argv[0], sys.argv[1:]
    args = _parse_args(argv)

    main(**args)

