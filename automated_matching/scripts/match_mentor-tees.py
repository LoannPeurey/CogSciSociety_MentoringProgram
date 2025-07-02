#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 09:36:18 2022
Do the matching between mentors and mentees.
This script takes csv as inputs, compute the different matching texts and attributes a number of mentees to each mentor
Mentees are matched to a mentor that:
 - isn't from the same institution
 - is at a higher academic position than them
 
@author: lpeurey
"""
import sys
import argparse
from pathlib import Path
import os

from static import POSITION_COLUMN, ACADEMIA_LEVELS, FIELDS_USED_MENTORS, FIELDS_USED_MENTEES

from matching import assign_articles_to_reviewers, preprocess
import pandas as pd

file_path = Path(__file__).parent

#complexity n*m where n=number of mentors, m=number of mentees
#using a sort and then go through the levels would be more efficient
#using a set instead of a list should be better
def add_higher_level_mentees(row,mentees):
    cur_level = ACADEMIA_LEVELS[row['status']]
    to_add=[]
    for i, mentee in mentees.iterrows():
        if ACADEMIA_LEVELS[mentee['status']] >= cur_level:
            to_add.append(str(mentee['PersonID']))
    if len(to_add):
        if len(str(row['PersonIDList'])):
            return ';'.join(list(set(str(row['PersonIDList']).split(';') + to_add)))
        else:
            return ';'.join(to_add)
    else:
        return row['PersonIDList']


MAX_TIME_DIFF_ACCEPTABLE = 5
#complexity n*m where n=number of mentors, m=number of mentees
#using a sort and then go through the levels would be more efficient
#using a set instead of a list should be better
def add_mentees_in_far_timezone(row,mentees):
    cur_tdiff = row['timediff']
    if pd.isnull(cur_tdiff): return row['PersonIDList']
    to_add=[]
    for i, mentee in mentees.iterrows():
        if not pd.isnull(mentee['timediff']) and abs(mentee['timediff'] - cur_tdiff) > MAX_TIME_DIFF_ACCEPTABLE:
            to_add.append(str(mentee['PersonID']))
    if len(to_add):
        if len(row['PersonIDList']):
            return ';'.join(list(set(str(row['PersonIDList']).split(';') + to_add)))
        else:
            return ';'.join(to_add)
    else:
        return row['PersonIDList']

def tz_to_tdiff(x):
    if pd.isnull(x) or x == '': return pd.NA
    match = re.search(r'[-+]?[0-9]+', x)
    if match:
        return match.group()
    else:
        raise ValueError(f"Could not extract timezone difference for <{x}>")

def build_abstract_mentor(row):
    """
    we build the abstract by concatenating the different area to match on
    the program uses tf-idf as a weighting solution, so the fields that should bare more importance
    should be repeated the same way for the mentor and mentee abstracts
    """
    res = ''
    res += ' ' + str(row["Main_Research_Area_1"])
    res += ' ' + str(row["Main_Research_Area_2"])
    res += ' ' + str(row["Main_Topic"])
    #res += ' ' + str(row["language"]) language was not collected for mentees
    res += ' ' + str(row["MT-health"]).replace(';', ' ')
    #res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["MT-career"]).replace(';', ' ')
    res += ' ' + str(row["Second_Topic"])
    #res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-health"]).replace(';', ' ')
    return res

def build_abstract_mentee(row):
    """
        we build the abstract by concatenating the different area to match on
        the program uses tf-idf as a weighting solution, so the fields that should bare more importance
        should be repeated the same way for the mentor and mentee abstracts
        """
    res = ''
    res += ' ' + str(row["Main_Research_Area_1"]).replace(',', ' ')
    res += ' ' + str(row["Main_Research_Area_1"]).replace(',', ' ')
    res += ' ' + str(row["Main_Research_Area_2"])
    res += ' ' + str(row["Main_Topic"])
    res += ' ' + str(row["MT-health"]).replace(';', ' ')
    #res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["MT-career"]).replace(';', ' ')
    res += ' ' + str(row["Second_Topic"])
    #res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-health"]).replace(';', ' ')
    return res

def build_locations(row):
    res = ''
    res += ' ' + str(row["MT-location-career"]).replace(';', ' ')
    res += ' ' + str(row["ST-location-career"]).replace(';', ' ')
    return res


def main(max_mentees, mentors_file, mentees_file, output_visual, output_list, restrict_timezone=False):
    """
    :param max_mentees: maximum number of mentees matched to a single mentor
    :param mentors_file: csv containing all the mentors (preprocessed already)
    :param mentees_file: csv containing all the mentees (preprocessed already)
    :param output_visual: filename to output the visual matching to
    :param output_list: filename to output the programmatic matching to (not very readable but usable programmatically)    
    """
    mentors = pd.read_csv(mentors_file)
    mentors.fillna('', inplace=True)

    mentees = pd.read_csv(mentees_file)
    mentees.fillna('', inplace=True)

    #create the people dataframe which has PersonID and FullName
    people_df = mentees[["name", "PersonID"]]
    people_df.rename(columns={"name": "FullName"}, inplace=True)

    mentees = mentees[mentees['status'] != 'Predoctoral']

    #this gives a "level" for each position, this very crude ranking is made to match mentors in higher positions to mentees
    mentees['level'] = mentees['status'].apply(lambda x: ACADEMIA_LEVELS[x])
    mentors['level'] = mentors['status'].apply(lambda x: ACADEMIA_LEVELS[x])


    ##### This block searches for people who only signed up as mentees #####
    ## this was used to ask them to also be mentors as we were short on mentors one year

    #cross = pd.concat([mentors, mentees])
    #cross['dup'] = cross.duplicated('name')
    #both = cross[cross['dup']]
    #onlee = cross.drop_duplicates('name', keep=False)
    #PostDMenteeNotMentor = onlee[onlee['level'] >=4]
    #PhdUnderMenteeNotMentor = onlee[onlee['level'] < 4]

    #print(PostDMenteeNotMentor.shape[0])
    #print(PhdUnderMenteeNotMentor.shape[0])
    #########################################################################


    print('mentees : '+ str(mentees.shape[0]))
    print('mentors : '+ str(mentors.shape[0]))


    #prepare mentor df
    mentors['Title'] = ''
    mentors.rename(columns=FIELDS_USED_MENTORS, inplace=True)

    #build the abstract for the mentors (add wanted fields)
    mentors["Abstract"] = mentors.apply(build_abstract_mentor , axis=1)
    mentors['locations'] = mentors.apply(build_locations , axis=1)

    #replace Nan values by empty string, add to the list every mentee that is higher up in level (or same) than the mentor
    mentors['PersonIDList'] = mentors.apply(add_higher_level_mentees,axis=1,mentees= mentees)


    #empty  PersonIDList is raises an error, putting a false PersonID as a placeholder
    mentors['PersonIDList'] = mentors.apply(lambda row: '99999' if row['PersonIDList'] == '' else row['PersonIDList'],axis=1)
    #print(mentors["PersonIDList"])

    mentors_mat = mentors[["PaperID","Title","PersonIDList", "Abstract"]]
    #mentors_MRA1["Title"] = mentors_MRA1['Abstract']

    #prepare mentees df
    mentees.rename(columns=FIELDS_USED_MENTEES,inplace=True)

    if restrict_timezone:
        mentees['timediff'] = mentees['timezone'].apply(tz_to_tdiff)
        mentors['timediff'] = mentors['timezone'].apply(tz_to_tdiff)

        # add to the list every mentee that has more than 5 hours of difference in timezone
        mentors['PersonIDList'] = mentors.apply(add_mentees_in_far_timezone,axis=1,mentees= mentees)

    mentees["Abstract"] = mentees.apply(build_abstract_mentee , axis=1)
    mentees['locations'] = mentees.apply(build_locations , axis=1)

    mentees_mat = mentees[["PersonID", "Abstract"]]

    # # TEST FOR TOO MANY PEOPLE
    # # this is removing all the Undergrad MA students and lower level people
    # mentees = mentees[mentees['level'] > 2]

    # # TEST first comes first serves
    # # this is removing the last mentees that signed up until their number does not go over
    # # the number of mentors x max_mentees (by mentor)
    # mentees = mentees.sort_values(by = 'Timestamp').head(mentors.shape[0] * max_mentees)

    # Computing the matching happens here    
    res = assign_articles_to_reviewers(mentors,mentees,people_df, max_mentees=max_mentees)
    #print(res)
    res.to_csv(output_list,index=False)
    #res[['PaperID','ReviewerIDList']].to_csv("testIDs_locW.csv",index=False)

    # This last blocks generates a visually better matching, in order to see better who was matched to whom and manually review those matches
    compare = pd.DataFrame()
    for i, row in res.iterrows():
        ids = row['ReviewerIDList'].split(';')
        scores = row['scores'].split(';')
        n=0
        for idp in ids:
            mentees.loc[mentees['PersonID'].astype(str) == idp,'score'] = scores[n]
            n += 1
        compare = pd.concat([compare,mentors[mentors['PaperID']==row['PaperID']],mentees[mentees['PersonID'].astype(str).isin(row['ReviewerIDList'].split(';'))],pd.DataFrame([{'PaperID':'-'}])],ignore_index=True)

    compare = compare[['PaperID','PersonID','score', 'name', 'std_institution_1','std_institution_2','status','level','Main_Research_Area_1','Main_Research_Area_2','Main_Topic','MT-health','MT-career','MT-location-career','Second_Topic','ST-career', 'ST-location-career','ST-health','onsite','timezone']]
    #compare.to_csv('test_compare.csv',index=False)
    compare.to_csv(output_visual,index=False)


def _parse_args(argv):
    parser = argparse.ArgumentParser(description='path of mentors/mentees files')
    parser.add_argument('--mentor-file', help='Path to mentor file preprocessed',
                        default=file_path / '../preprocessed_data/mentors.csv')
    parser.add_argument('--mentee-file', help='Path to mentee file  preprocessed',
                        default=file_path / '../preprocessed_data/mentees.csv')
    parser.add_argument('--output-visual', help='csv output file for visual matching',
                        default=file_path / '../output/visual_matching.csv')
    parser.add_argument('--output-list', help='csv output file for programmatic matching',
                        default=file_path / '../output/list_matching.csv.csv')
    parser.add_argument('--max-mentees-per-mentor','--max-mentees', help='maximum amount of mentees per mentor',
                        type=int)
    parser.add_argument('--match-close-timezones',help='only match together people with maximum 5h difference in timezone',
                        action='store_true')
    args = parser.parse_args(argv)
    args = vars(args)

    return args


if __name__ == '__main__':
    pgrm_name, argv = sys.argv[0], sys.argv[1:]
    args = _parse_args(argv)

    file_path = Path(__file__).parent
    mentors_file = Path(args['mentor_file'])
    mentees_file = Path(args['mentee_file'])

    output_visual = Path(args['output_visual'])
    output_list = Path(args['output_list'])
    main(args['max_mentees_per_mentor'],mentors_file,mentees_file, output_visual, output_list, args['match_close_timezones'])
