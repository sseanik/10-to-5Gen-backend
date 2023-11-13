import json
import os
import re
from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    make_response,
    request,
)
from flask_cors import CORS
import docx
from openai import APIError
from ai import (
    ai_assistant_question,
    generate_details,
    generate_minutes,
    generate_actions,
    generate_next_agenda,
    generate_tickets,
)
from nlp import NLP_processing
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": os.getenv("DB_URL")})

db = firestore.client()

app = Flask(__name__)
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# Constants for file types
TXT_FILE_TYPE = "text/plain"
VTT_FILE_TYPE = "application/octet-stream"
DOCX_FILE_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


@app.route("/upload", methods=(["POST"]))
def upload():
    if "file" not in request.files:
        make_error(400, "File not provided in the request")

    try:
        uploaded_file = dict(request.files)["file"]
        file_type = uploaded_file.content_type
    except Exception as e:
        make_error(400, str(e))
    if file_type == TXT_FILE_TYPE:  # .txt
        try:
            text_content = uploaded_file.read().decode("cp1252")  # for ai, saving
        except Exception as e:
            make_error(400, str(e))
    elif file_type == VTT_FILE_TYPE:  # .vtt
        try:
            text_content = uploaded_file.read().decode()  # for ai
        except Exception as e:
            make_error(400, str(e))
    elif file_type == DOCX_FILE_TYPE:
        try:
            text_content = process_docx_file(uploaded_file)
        except Exception as e:
            make_error(400, str(e))
    else:
        make_error(400, "Invalid file type provided")
    name_arg, type_arg = request.form.get("name"), request.form.get("meetingType")
    if name_arg is None or type_arg is None:
        make_error(400, "Name or Meeting Type argument is missing")

    # Generate NLP Data
    try:
        (
            sentences,  # string array
            word_freq,  # counter
            common_topics,  # array of tuples
            topics,  # array string
            sentiment,  # number
            named_entities,  # array of dicts
            summary,  # string
            questions,  # string array
        ) = NLP_processing(text_content)

    except Exception as e:
        make_error(400, str(e))

    # Generate Summary
    try:
        attendees, date, time, duration = generate_details(text_content)
    except APIError as e:
        make_error(400, json.loads(e.response.text)["error"]["message"])

    # DB Upload
    summary_db = {
        "title": name_arg,
        "type": type_arg,
        "time": time,
        "date": date,
        "duration": duration,
        "attendees": attendees,
    }
    nlpData = {
        "namedEntities": named_entities,
        "wordFreq": word_freq,
        "topics": topics,
        "sentences": sentences,
        "commonTopics": dict(common_topics),
        "sentiment": sentiment,
        "questions": questions,
        "summary": summary,
    }
    transcript = {
        "transcript": str(text_content),
        "aiGenerated": False,
    }
    minute = {
        "agenda": [],
        "summaryPoints": [],
        "attendeeSummary": [],
        "overallSummary": "",
        "aiGenerated": False,
    }
    action = {"aiGenerated": False, "actionItems": []}
    ticket = {
        "aiGenerated": False,
        "tickets": [],
    }
    agenda = {
        "agendaItems": [],
        "proposedSchedule": {
            "attendees": [],
            "date": "",
        },
        "aiGenerated": False,
    }

    try:
        generated_id = upload_to_fire_store(
            summary_db, nlpData, transcript, minute, action, ticket, agenda
        )
        return jsonify({"id": generated_id})
    except Exception as e:
        make_error(400, str(e))


@app.route("/meetings", methods=(["GET"]))
def meetings():
    try:
        # Assuming your summaries are stored in a collection named "summaries"
        summaries_ref = db.collection("summaries")
        docs = summaries_ref.stream()

        meetings = []
        for doc in docs:
            meeting_data = doc.to_dict()
            meeting_data["id"] = doc.id
            meetings.append(meeting_data)

        return jsonify({"meetings": meetings})

    except Exception as e:
        make_error(400, str(e))


@app.route("/summary/<id>", methods=(["GET"]))
def summary(id):
    db_data = read_from_fire_store(id, ["summaries"])
    return jsonify(db_data)


@app.route("/transcript/<id>", methods=(["GET"]))
def transcript(id):
    try:
        db_data = read_from_fire_store(id, ["transcripts"])
    except Exception as e:
        make_error(400, str(e))

    # if not bool(db_data["transcripts"]["aiGenerated"]):
    #     try:
    #         return Response(
    #             parse_transcript(db_data, db, id), mimetype="text/event-stream"
    #         )
    #     except Exception as e:
    #         return make_error(500, f"Error parsing transcript: {e}")
    return jsonify(db_data["transcripts"])


@app.route("/minutes/<id>", methods=(["GET"]))
def minutes(id):
    try:
        db_data = read_from_fire_store(id, ["nlpData", "summaries", "minutes"])
    except Exception as e:
        make_error(400, str(e))

    if not bool(db_data["minutes"]["aiGenerated"]):
        try:
            return Response(
                generate_minutes(db_data, db, id), mimetype="text/event-stream"
            )
        except APIError as e:
            abort(
                make_response(
                    jsonify(error=json.loads(e.response.text)["error"]["message"]), 400
                )
            )
    return jsonify(db_data["minutes"])


@app.route("/actions/<id>", methods=(["GET"]))
def actions(id):
    try:
        db_data = read_from_fire_store(id, ["nlpData", "summaries", "actions"])
    except Exception as e:
        make_error(400, str(e))

    if not bool(db_data["actions"]["aiGenerated"]):
        try:
            return Response(
                generate_actions(db_data, db, id), mimetype="text/event-stream"
            )
        except APIError as e:
            abort(
                make_response(
                    jsonify(error=json.loads(e.response.text)["error"]["message"]), 400
                )
            )
    return jsonify(db_data["actions"])


@app.route("/tickets/<id>", methods=(["GET"]))
def tickets(id):
    try:
        db_data = read_from_fire_store(id, ["nlpData", "summaries", "tickets"])
    except Exception as e:
        make_error(500, f"Error reading from database: {e}")

    if not bool(db_data["tickets"]["aiGenerated"]):
        try:
            return Response(
                generate_tickets(db_data, db, id), mimetype="text/event-stream"
            )
        except APIError as e:
            abort(
                make_response(
                    jsonify(error=json.loads(e.response.text)["error"]["message"]), 400
                )
            )
    return jsonify(db_data["tickets"])


@app.route("/agenda/<id>", methods=(["GET"]))
def agenda(id):
    try:
        db_data = read_from_fire_store(id, ["nlpData", "summaries", "agendas"])
    except Exception as e:
        make_error(500, f"Error reading from database: {e}")

    if not bool(db_data["agendas"]["aiGenerated"]):
        try:
            return Response(
                generate_next_agenda(db_data, db, id), mimetype="text/event-stream"
            )
        except APIError as e:
            abort(
                make_response(
                    jsonify(error=json.loads(e.response.text)["error"]["message"]), 400
                )
            )
    return jsonify(db_data["agendas"])


@app.route("/assistant", methods=(["POST"]))
def assistant():
    body = json.loads(request.get_data())
    db_data = read_from_fire_store(
        body["meetingId"], ["summaries", "minutes", "actions"]
    )
    try:
        return Response(
            ai_assistant_question(body["message"], db_data),
            mimetype="text/event-stream",
        )
    except APIError as e:
        abort(
            make_response(
                jsonify(error=json.loads(e.response.text)["error"]["message"]), 400
            )
        )


@app.route("/dashboard", methods=(["GET"]))
def dashboard():
    collections = ["actions", "agendas", "minutes", "summaries", "tickets"]
    overall_data = {}

    for collection in collections:
        docs = db.collection(collection).stream()
        for doc in docs:
            doc_id = doc.id
            if doc_id not in overall_data:
                overall_data[doc_id] = {
                    "actions": {},
                    "agendas": {},
                    "minutes": {},
                    "summaries": {},
                    "tickets": {},
                }
            overall_data[doc_id][collection] = doc.to_dict()

    return jsonify(overall_data)


def read_from_fire_store(document_id, collections):
    data = {}
    for collection_name in collections:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            data[collection_name] = doc.to_dict()
        else:
            print(f"No document found in {collection_name} with ID: {document_id}")
    return data


def upload_to_fire_store(
    summary_db, nlpData, transcript, minute, action, ticket, agenda
):
    # Create a batched write operation
    batch = db.batch()

    # Create a new document ID
    summary_doc_ref = db.collection("summaries").document()
    new_id = summary_doc_ref.id

    # Add summary data
    batch.set(summary_doc_ref, summary_db)

    nlp_doc_ref = db.collection("nlpData").document(new_id)
    batch.set(nlp_doc_ref, nlpData)
    transcript_doc_ref = db.collection("transcripts").document(new_id)
    batch.set(transcript_doc_ref, transcript)
    minute_doc_ref = db.collection("minutes").document(new_id)
    batch.set(minute_doc_ref, minute)
    action_doc_ref = db.collection("actions").document(new_id)
    batch.set(action_doc_ref, action)
    ticket_doc_ref = db.collection("tickets").document(new_id)
    batch.set(ticket_doc_ref, ticket)
    agenda_doc_ref = db.collection("agendas").document(new_id)
    batch.set(agenda_doc_ref, agenda)

    # Commit the batch
    batch.commit()

    return new_id


def process_docx_file(uploaded_file):
    temp_file_path = f"./db/temp/{uploaded_file.filename}"
    uploaded_file.save(temp_file_path)
    doc = docx.Document(temp_file_path)
    full_text_array = [para.text for para in doc.paragraphs]
    os.remove(temp_file_path)
    return "\n".join(full_text_array)


def parse_vtt(vtt_text):
    lines = vtt_text.split("\r")
    no_inner_new_lines = list(
        map(lambda x: x.replace("\n", "").replace("WEBVTT", ""), lines)
    )
    no_new_lines = list(filter(lambda x: x != "", no_inner_new_lines))
    result = []  # saving
    for destination, source in zip(*[iter(no_new_lines)] * 2):
        parsed_time = destination.split(" --> ")[0].split(".")[0]
        broken_name = source.split(">")[0].split("<v ")[1]
        name = re.sub(" +", " ", broken_name)
        text = source.split(">")[1].split("</v")[0]
        result.append({"time": parsed_time, "name": name, "text": text})
    return result


def make_error(status_code, error_message):
    app.logger.error(f"ERROR LOGGER: {error_message}\n")
    abort(make_response(jsonify(error=error_message), status_code))
