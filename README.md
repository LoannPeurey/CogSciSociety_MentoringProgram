# CogSciSociety_MentoringProgram
Resources created for the Cognitive Science Society's Annual Pop-Up Mentoring Program

## Documents for Mentors and Mentees
### Match Email & Guidelines
These document contains the email template for mentors/mentees that include match information. They mentors with an email template for their initial contact with their mentees. And, for mentees, the documents provide suggestions for ways to have a fruitful meetings.

### Mentor Recruitment
These are email templates in English and in various other languages (thanks to our contributors) for mentor recruitment. 

## Matching Algorithm

In an effort to faciliate the matching of mentees to mentors, work from [Paper-Reviewer Matcher](https://github.com/titipata/paper-reviewer-matcher)
is used to generate a first automated matching.
Given the answers to the sign up form of mentees and mentors, as well as other parameters (such as the maximum number of
mentees a mentor can receive and the constraint to only match people with less than 5 hours timezone difference),
the automated matching will use the main areas of research and topics of interest (including specific locations) as the main
base for matching people together. It will forbid matching mentors to a higher academic position mentee (a full professor can
not be given a postdoc as a mentor) and can not match people from the same institution.

The produced matching is meant to be a good starting place but is expected to undergo review before final attributions

Code is located in the `automated_matching` folder and procedure is further described in the [README](./automated_matching/README.md)

## References

Paper-Reviewer Matcher [[1]](https://github.com/titipata/paper-reviewer-matcher) : A python package for paper-reviewer matching algorithm based on topic modeling and linear programming

The Paper-Reviewer Matcher as been implemented based on this work:
On the Optimal Assignment of Conference Papers to Reviewers [[2]](https://www.cis.upenn.edu/~cjtaylor/PUBLICATIONS/pdfs/TaylorTR08.pdf)
