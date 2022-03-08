import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import csv
import codecs

RESPONSES_DICT = pd.read_csv('responses.csv', header=0)
RESPONSES = RESPONSES_DICT.drop(columns=['Timestamp', 'Rate Luv is Rage 2 by Lil Uzi Vert'])
RESPONSES = RESPONSES.drop_duplicates()

def getPerfectMatches(responses):
    '''
        Takes an input called 'responses' which should be a dictionary

        Should return a tuple of: a list of indexes that have been matched and a list of 'match' objects
        structured like: [{'name':'Pierre', email:'pierre.rodgers@columbia.edu'}, {'name':'Pierre's match',
        'email':'email@columbia.edu}]

    '''
    responses_dict = responses.copy()
    responses = responses.drop(columns=['Email Address', 'Name'])
    responses = responses.to_numpy()
    
    index_to_matches = {}
    final_matches = dict()
    matchesToReturn = []
    matchedIndices = []



    for idx, row in enumerate(responses):
        temp = np.array(responses)
        temp[idx] = np.repeat(-10000, 17)
        responsesTree = cKDTree(temp)
        matches = responsesTree.query(row, k=1)[1]
        index_to_matches[idx] = matches
    
    for index in index_to_matches.keys():
        if index in final_matches.values():
            continue
        first_choice = index_to_matches[index]
        first_choice_match = index_to_matches[first_choice]
        if index == first_choice_match:
          # Matches match!
          final_matches[index] = first_choice
          matchedIndices.append(index)
          matchedIndices.append(first_choice)
    
    for match in final_matches.keys():
        idx = final_matches[match]

        match = {
            'match':responses_dict.iloc[match]['Name'], 'match_email':responses_dict.iloc[match]['Email Address'],
            'with':responses_dict.iloc[idx]['Name'],'with_email':responses_dict.iloc[idx]['Email Address']
        }
        matchesToReturn.append(match)
    
    
    return (matchedIndices, matchesToReturn)


all_responses = RESPONSES.copy()
iterations = 0
MATCHES = []

while all_responses.empty == False and iterations < 100:
    matchedIndices, matches = getPerfectMatches(all_responses)
    rows = all_responses.index[matchedIndices]
    all_responses.drop(rows, inplace=True)
    MATCHES = MATCHES + matches
    iterations = iterations + 1

print(len(MATCHES))
print(len(RESPONSES_DICT))
print(len(RESPONSES))

with open('matches.csv', 'w',) as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Email', 'Matched With', 'Email'])
    for match in MATCHES:
        #print(match)
        writer.writerow([match['match'], match['match_email'], match['with'], match['with_email']])


import smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
sender_email = "press@cubacchanal.com"
port = 465  # For SSL
password = input("Type your password and press enter: ")

# Create a secure SSL context
context = ssl.create_default_context()

html_file = codecs.open("email.html", "r", "utf-8")
html = html_file.read()


def sendEmail(match):
    match_message_html = html.replace("[NAME]", match["match"]).replace("[MATCH NAME]", match["with"]).replace("[MATCH'S EMAIL]", match["with_email"])
    with_message_html = html.replace("[NAME]", match["with"]).replace("[MATCH NAME]", match["match"]).replace("[MATCH'S EMAIL]", match["match_email"])
    
    
    match_message = MIMEMultipart("alternative")
    match_message["Subject"] = "Your Bacchanal Music Match"
    match_message["From"] = sender_email
    match_message["To"] = match['match_email']
    match_message.attach(MIMEText(match_message_html, "html"))


    with_message = MIMEMultipart("alternative")
    with_message["Subject"] = "Your Bacchanal Music Match"
    with_message["From"] = sender_email
    with_message["To"] = match['with_email']
    with_message.attach(MIMEText(with_message_html, "html"))


    with smtplib.SMTP_SSL("mail.cubacchanal.com", port, context=context) as server:
        server.login("press@cubacchanal.com", password)
        server.sendmail(
            sender_email, match['match_email'], match_message.as_string()
        )
        server.sendmail(
            sender_email, match['with_email'], with_message.as_string()
        )
        

for match in MATCHES:
    sendEmail(match)

#sendEmail({"match":"Pierre", "match_email":"pierre.rodgers@columbia.edu", "with":"Gillian", "with_email":"grc2130@columbia.edu"})
