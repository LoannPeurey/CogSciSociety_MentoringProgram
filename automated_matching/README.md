# Automated matching of mentor-mentees for Cogsci

This folder contains scripts and modules put together to faciliate the matching of mentor mentees for the cogsci conference.

## Content

In it you will find the following:
  - raw_data : folder meant to contain data gotten from the forms, one csv for mentees, one csv for mentors
  - preproccessed_data : folder receiving the cleaned up data from raw_data, this will also contain 1 csv for mentees and one for mentors
  - output : folder receiving the results of the matching, it will contain 1 visual matching (putting together the mentor with its mentees), this is a practical format for people to read and review the matches. The second file is a matching with just the numbers of the participants to match
  - scripts : folder containing the scripts:
        - match_mentor_mentees.py : this is the main script for matching, it needs the 2 input folders (preprocessed), how many mentees can a mentor have and wether to match only people without too much time difference
        - preprocess.py : this is meant to prepare the data and conflicts between participants (conflicts are just 2 people not being suitable to be matched together, e.g. rom same uni or at the same academic level)
        - static.py : mappings used to get data from the csvs, if the names of the fields change between years, this should be updated
        - matching.py : the actual script that does the matching, should not need much update unless wanting to change the way the matchin is done

## Step by step

To run the matching on a new year you can follow this step by step :

clone this repo:
```bash
git clone --recurse-submodules https://github.com/monicado/CogSciSociety_MentoringProgram.git
```

Make sure you have python installed, the dependencies used here were computed for python 3.7 so it could be a good idea to use that version. We strongly advise using the same version

install the pip dependencies
```bash
pip install -r requirements.txt
```

Get the csv datain the raw_data folder, in the repo, we put `example_mentors.csv` and `example_mentees.csv` as an example for demonstration.

Run the preprocessing. As an example, this command will run it on our 2 example files and create 2 output example files
```python
python scripts/preprocess.py --mentor-file raw_data/example_mentors.csv --mentee-file raw_data/example_mentees.csv --out-mentor-file preprocessed_data/example_mentors_ppd.csv --out-mentee-file preprocessed_data/example_mentees_ppd.csv -e
```

Then run the matching. Once again for our example, we run it on our 2 preprocessed example files, with 3 mentees max per mentor and no check on timezone
```python
python scripts/match_mentor-tees.py --mentor-file preprocessed_data/example_mentors_ppd.csv --mentee-file preprocessed_data/example_mentees_ppd.csv --output-visual output/example_visual.csv --output-list output/example_list.csv --max-mentees 3
```

The results are output in the output folder
