#!/usr/bin/env python3
"""Entry point for example chatbot application using Infermedica API.

Example:
    To start the application simply type::

        $ python3 chat.py APP_ID:APP_KEY

    where `APP_ID` and `APP_KEY` are Application Id and Application Key from
    your Infermedica account respectively.

Note:
    If you don't have an Infermedica account, please register at
    https://developer.infermedica.com.

"""
import argparse
import uuid

import conversation
import apiaccess




def new_case_id():
    """Generates an identifier unique to a new session.

    Returns:
        str: Unique identifier in hexadecimal form.

    Note:
        This is not user id but an identifier that is generated anew with each
        started "visit" to the bot.

    """
    return uuid.uuid4().hex



def run():
    """Runs the main application."""
    
    auth_string = "719f2ba6:3aa363e21546a0fb03daed12aae8f3a8"
    case_id = new_case_id()

    # Read patient's age and sex; required by /diagnosis endpoint.
    # Alternatively, this could be done after learning patient's complaints
    age, sex = conversation.read_age_sex()
    print(f"Ok, {age} year old {sex}.")
    age = {'value':  age, 'unit': 'year'}

    # Query for all observation names and store them. In a real chatbot, this
    # could be done once at initialisation and used for handling all events by
    # one worker. This is an id2name mapping.
    naming = apiaccess.get_observation_names(age, auth_string, case_id, args.model)

    # Read patient's complaints by using /parse endpoint.
    mentions = conversation.read_complaints(age, sex, auth_string, case_id, args.model)

    # Keep asking diagnostic questions until stop condition is met (all of this
    # by calling /diagnosis endpoint) and get the diagnostic ranking and triage
    # (the latter from /triage endpoint).
    evidence = apiaccess.mentions_to_evidence(mentions)
    evidence, diagnoses, triage = conversation.conduct_interview(evidence, age,
                                                                 sex, case_id,
                                                                 auth_string,
                                                                 args.model)

    # Add `name` field to each piece of evidence to get a human-readable
    # summary.
    apiaccess.name_evidence(evidence, naming)

    # Print out all that we've learnt about the case and finish.
    print()
    conversation.summarise_all_evidence(evidence)
    conversation.summarise_diagnoses(diagnoses)
    conversation.summarise_triage(triage)


if __name__ == "__main__":
    run()
