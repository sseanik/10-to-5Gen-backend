import json
import re
import logging
import time
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)


def generate_details(text):
    messages = [
        {
            "role": "user",
            "content": f"Extract the time, date, duration, and attendees from the following meeting transcript:\n{text}",
        }
    ]

    functions = [
        {
            "name": "extract_meeting_details",
            "description": "Extract the time, date, duration, and attendees from the transcript text",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "Time of when the meeting took place",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of when the meeting took place",
                    },
                    "duration": {
                        "type": "integer",
                        "description": "In minutes, how long did the meeting take",
                    },
                    "attendees": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Unique user who attended the meeting",
                        },
                    },
                },
                "required": ["attendees"],
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        functions=functions,
        function_call="auto",
    )

    response_message = response.choices[0].message
    extracted_details = json.loads(response_message.function_call.arguments)

    # Function to check for placeholder text and replace with an empty string
    def replace_placeholder(text):
        if re.match(r"\[Insert .+\]", text):
            return ""
        return text

    extracted_details["date"] = replace_placeholder(extracted_details.get("date", ""))
    extracted_details["time"] = replace_placeholder(extracted_details.get("time", ""))
    extracted_details["duration"] = extracted_details.get("duration", 0)

    if (
        len(extracted_details["attendees"]) == 0
        and extracted_details["date"] == ""
        and extracted_details["time"] == ""
    ):
        raise Exception("Invalid response format")

    return (
        extracted_details["attendees"],
        extracted_details["date"],
        extracted_details["time"],
        extracted_details["duration"],
    )


def generate_minutes(db_data, db, meeting_id):
    prompt = make_prompt(
        db_data,
        f"Based on the above data, generate a detailed analysis and summary of the meeting, focusing on the main points discussed, decisions made, and action items.",
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_meeting_minutes",
                "description": "Generate agenda, summary and overall details from the meeting data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "overallSummary": {
                            "type": "string",
                            "description": "Short paragraph string on the overall summary of the meeting.",
                        },
                        "summaryPoints": {
                            "type": "array",
                            "description": "Small amount of dot points detailing the main points of the meeting",
                            "items": {
                                "type": "string",
                                "description": "Dot point analysis of an important part of the meeting",
                            },
                        },
                        "agenda": {
                            "type": "array",
                            "description": "The predicted agenda items based on what happened during the meeting.",
                            "items": {
                                "type": "string",
                                "description": "Dot point of one of the agenda items predicted.",
                            },
                        },
                        "attendeeSummary": {
                            "type": "object",
                            "description": "Every single attendee will also have their own summary of what happened for them.",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the attendee",
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "The attendee's unique summary",
                                },
                            },
                        },
                    },
                    "required": [
                        "summaryPoints",
                        "agenda",
                        "attendeeSummary",
                        "overallSummary",
                    ],
                },
            },
        }
    ]
    return stream_and_save(prompt, tools, meeting_id, db, "minutes")


def generate_actions(db_data, db, meeting_id):
    retro = db_data["summaries"]["type"] == "Retrospective"  # every sentence
    prompt = make_prompt(
        db_data,
        f"Based on the above data, generate {'agile retrospective' if retro else 'meeting'} action items with a focus on who carries what action item out",
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_retro_action_items",
                "description": "Generate retrospective action items derived from the agile retrospective meeting transcript",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actionItems": {
                            "type": "array",
                            "description": "A list of retro action items to be carried out",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "assignee": {
                                        "type": "string",
                                        "description": "The assigned person who the action item should belong to (can be assigned to an no one, individual or multiple people)",
                                    },
                                    "actions": {
                                        "type": "array",
                                        "description": "An array of 1 Retro Action Item",
                                        "items": {
                                            "type": "string",
                                            "description": "The single entry tied to an attendee. The Action Item is derived from the meeting",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "required": [
                        "actionItems",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_general_action_items",
                "description": "Generate meeting specific action items derived from the transcript of the meeting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actionItems": {
                            "type": "array",
                            "description": "Generate multiple list of meeting action items for different assignees",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "assignee": {
                                        "type": "string",
                                        "description": "The assigned person who the action item should belong to (can be assigned to an individual or multiple people)",
                                    },
                                    "actions": {
                                        "type": "array",
                                        "description": "The list of action items designated to the assignee",
                                        "items": {
                                            "type": "string",
                                            "description": "Action Item derived from the meeting, to be specifically carried out by the attendee as a general completion item",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "required": [
                        "actionItems",
                    ],
                },
            },
        },
    ]
    return stream_and_save(prompt, tools, meeting_id, db, "actions")


def generate_tickets(db_data, db, meeting_id):
    prompt = make_prompt(
        db_data,
        f"Based on the above data, generate suggested JIRA tickets that may be further created, edited or discarded by the team",
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_jira_ticket",
                "description": "Given a meeting, generate suggested Jira Ticket tasks that the team may want to act on",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tickets": {
                            "type": "array",
                            "description": "A list of the Jira Ticket Objects",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "The title of the suggested ticket",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The overall summary of the task",
                                    },
                                    "estimate": {
                                        "type": "integer",
                                        "description": "In days, how long would this potentially take to complete",
                                    },
                                    "priority": {
                                        "type": "string",
                                        "enum": ["Low", "Medium", "High", "Critical"],
                                        "description": "",
                                    },
                                    "assignee": {
                                        "type": "string",
                                        "description": "The attendee from the meeting best suited to the task",
                                    },
                                    "userStory": {
                                        "type": "string",
                                        "description": "The Jira ticket's user story (As a <ROLE>, I want a <GOAL>, so that I can <BENEFIT>)",
                                    },
                                    "storyPoints": {
                                        "type": "number",
                                        "description": "The integer number of story points (Fibonacci system)",
                                    },
                                    "acceptanceCriteria": {
                                        "type": "array",
                                        "description": "A list of Acceptance Criteria dot point strings",
                                        "items": {
                                            "type": "string",
                                            "description": "Acceptance critera in the scenario based format (GIVEN, WHEN, THE)",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "required": [
                        "jiraTickets",
                    ],
                },
            },
        }
    ]
    return stream_and_save(prompt, tools, meeting_id, db, "tickets")


def generate_next_agenda(db_data, db, meeting_id):
    prompt = make_prompt(
        db_data,
        f"Based on the given meeting, suggest an appropriate next agenda would be for an predicted upcoming next meeting. The agenda be derived from the questions and potential action items generated by the transcript.",
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_next_meeting",
                "description": "Given a meeting, suggested what the next meeting agenda and schedule should be",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "proposedSchedule": {
                            "type": "object",
                            "description": "An object to detail the next suggested meeting's timeframe",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "The proposed date for the next meeting",
                                },
                                "attendees": {
                                    "type": "array",
                                    "description": "The proposed people who should attend the meeting",
                                    "items": {
                                        "type": "string",
                                        "description": "Name of the proposed attendee",
                                    },
                                },
                            },
                        },
                        "agendaItems": {
                            "type": "array",
                            "description": "A list of upcoming agenda items",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "The content of the suggested agenda item",
                                    },
                                    "agendaItems": {
                                        "type": "array",
                                        "description": "Dot point strings expanding upon the agenda item title",
                                        "items": {
                                            "type": "string",
                                            "description": "Dot point string detailing a part of the agenda",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "required": ["agendaItems", "proposedSchedule"],
                },
            },
        }
    ]
    return stream_and_save(prompt, tools, meeting_id, db, "agendas")


def ai_assistant_question(question, db_data):
    attendees = db_data["summaries"]["attendees"]
    title = db_data["summaries"]["title"]
    meeting_type = db_data["summaries"]["type"]
    #
    meetingAgenda = db_data["minutes"]["agenda"]
    overallSummary = db_data["minutes"]["overallSummary"]
    #
    actionItems = db_data["actions"]["actionItems"]

    assignee = "assignee"
    data = (
        f"Meeting Title: {title}\n"
        f"Meeting Type: {meeting_type}\n"
        f"Attendees: {', '.join(attendees)}\n"
        f"Meeting Summary: {overallSummary}\n\n"
        f"Meeting Agenda:\n{' '.join(meetingAgenda)}\n\n"
        f"Action Items:\n{' '.join([f'{action[assignee]}:' + ' '.join(action['actions']) for action in actionItems])}\n\n"
        f"Based on the given transcript data above, can you answer the following question: {question}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Imagine you are an AI assistant specialized in analyzing and providing insights on meeting data."
                    f"A user is seeking information about their recent meetings, including summaries, action items, tickets, or agendas. The user may ask questions like:"
                    f"Can you summarize the key points from our last team meeting?"
                    f"What were the action items assigned to me from the sprint retrospective?"
                    f"Are there any high-priority tickets that came out of the recent project meeting?"
                    f"What is on the agenda for the next marketing team meeting?"
                    f"Your task is to understand these questions and provide clear, concise, and relevant responses based on the meeting data. You should utilize the information from meeting transcripts, summaries, action items, tickets, and agendas to accurately answer the user's queries. Be informative and precise in your responses"
                ),
            },
            {
                "role": "user",
                "content": data,
            },
        ],
        stream=True,
    )

    overall_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content)
            yield f"data: {chunk.choices[0].delta.content}\n\n"  # Format for SSE
            overall_text += chunk.choices[0].delta.content
    yield "END"


def parse_transcript(transcript_data, db, meeting_id):
    transcript = transcript_data["transcripts"]["transcript"]
    prompt = f"Could you take the follow transcript and make it more presentable and readable, for output on a website:\n{transcript}"

    return stream_and_save_normal(prompt, meeting_id, db, "transcripts")


def make_prompt(db_data, custom):
    # Summaries
    title = db_data["summaries"]["title"]
    meeting_type = db_data["summaries"]["type"]
    attendees = db_data["summaries"]["attendees"]
    # NLP
    common_topics = db_data["nlpData"]["commonTopics"]  # word count
    word_freq = db_data["nlpData"]["wordFreq"]  # word count
    sentiment = db_data["nlpData"]["sentiment"]
    named_entities = db_data["nlpData"]["namedEntities"]  # word identifier and count
    questions = db_data["nlpData"]["questions"]
    summary = db_data["nlpData"]["summary"]
    sentences = db_data["nlpData"]["sentences"]  # every sentence

    text, type_text = "text", "type"
    return (
        f"Meeting Title: {title}\n"
        f"Meeting Type: {meeting_type}\n"
        f"Attendees: {', '.join(attendees)}\n"
        f"Key Topics: {', x'.join([f'{k} ({v} mentions)' for k, v in common_topics.items()])}\n"
        f"Key Words Frequency: {', '.join([f'{k} ({v} times)' for k, v in word_freq.items()])}\n"
        f"Sentiment Score: {sentiment}\n"
        f"Named Entities: {', '.join([f'{entity[text]} ({entity[type_text]})' for entity in named_entities])}\n"
        f"Questions Discussed: {'; '.join(questions)}\n"
        f"Meeting Summary: {summary}\n\n"
        f"Transcript:\n{' '.join(sentences)}\n\n"
        f"{custom}"
    )


def stream_and_save(prompt, tools, meeting_id, db, document):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": "You are a project management assistant, skilled in extracting information from meeting transcripts.",
            },
            {"role": "user", "content": prompt},
        ],
        tools=tools,
        tool_choice="auto",
        stream=True,  # this time, we set stream=True
    )

    overall_text = ""
    for chunk in response:
        try:
            yield chunk.choices[0].delta.tool_calls[0].function.arguments
            overall_text += chunk.choices[0].delta.tool_calls[0].function.arguments
        except Exception as e:
            logging.error(f"Error in stream chunk: {e}")

    try:
        parsed_response = json.loads(overall_text)
        parsed_response["aiGenerated"] = True
        db.collection(document).document(meeting_id).set(parsed_response)
    except Exception as e:
        logging.error(f"Error parsing JSON or writing to DB: {e}")
    yield "COMPLETED_STREAM"


def stream_and_save_normal(prompt, meeting_id, db, document):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "system",
                "content": "You are a project management assistant, skilled in extracting information from meeting transcripts.",
            },
            {"role": "user", "content": prompt},
        ],
        stream=True,  # this time, we set stream=True
    )

    overall_text = ""
    for chunk in response:
        try:
            yield chunk.choices[0].delta.content
            overall_text += chunk.choices[0].delta.content
            time.sleep(0.5)  # Add a delay of 0.5 seconds (adjust as necessary)
        except Exception as e:
            logging.error(f"Error in stream chunk: {e}")

    try:
        parsed_response = json.loads(overall_text)
        parsed_response["aiGenerated"] = True
        db.collection(document).document(meeting_id).set(parsed_response)
    except Exception as e:
        logging.error(f"Error parsing JSON or writing to DB: {e}")
