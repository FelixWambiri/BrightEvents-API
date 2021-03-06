import re
from datetime import datetime

from flask import request, jsonify
from sqlalchemy import or_
from app.auth.views import token_required
from app.events import event
from app.models.event import Event
import arrow

def date_validation(date_hosted):
    """check that the event date is not past"""
    
    new_date = arrow.get(date_hosted).format('MM-DD-YYYY')
    try:
        date = datetime.strptime(new_date, '%m-%d-%Y').date()

    except ValueError as e:
        print("e",e)
        return "You have entered an incorrect date format, date should be MM-DD-YY format"
    
    # date = date_hosted
    if date < date.today():
        return "The event cannot have a past date as the date it is going to be hosted"
    return date_hosted


def update_date_validation(date_hosted):
    """check that the event date is not past"""
    if len(date_hosted) > 3:
        try:
            date = datetime.strptime(date_hosted, '%m-%d-%Y').date()

        except ValueError:
            return "You have entered an incorrect date format, date should be MM-DD-YY format"

        if date < date.today():
            return "The event cannot have a past date as the date it is going to be hosted"
    return date_hosted


def data_validation(data):
    if len(data['name'].strip()) < 5 or not re.match("^[a-zA-Z0-9_ ]*$", data['name'].strip()):
        return "The event name should only contain alphanumeric characters,an underscore and be at least 5 " \
               "characters in length without any empty spaces and special characters"

    elif len(data['location'].strip()) < 3 or not data['location'].strip().isalpha():
        return "The event location should only contain alphabetic characters and be at least 3 characters in length" \
               " excluding empty spaces"

    elif len(data['category'].strip()) < 5 or not data['category'].strip().isalpha():
        return "The event category should only contain alphabetic characters and be at least 5 characters in length " \
               "excluding empty spaces"

    else:
        return data


def update_data_validation(data):
    if data['name'] != '':
        if not re.match("^[a-zA-Z0-9_ ]*$", data['name']) or len(data['name']) < 5:
            return "The event name should only contain alphanumeric characters,an underscore and be at least 5 " \
                   "characters in length without any empty spaces and special characters"
    if data['location'] != '':
        if not data['location'].isalpha() and len(data['location']) < 3:
            return "The event location should only contain alphabetic characters and be at least 3 characters in" \
                   " length excluding empty spaces"

    if data['category'] != '':
        if not data['category'].isalpha() or len(data['category']) < 5:
            return "The event category should only contain alphabetic characters and be at least 5 characters in " \
                   "length excluding empty spaces"
    return data


@event.route('/events', methods=['POST'])
@token_required
def create_events(current_user):
    data = request.get_json()
    name = data['name']
    category = data['category']
    location = data['location']
    date_hosted = data['date_hosted']
    description = data['description']

    validation_output = data_validation(data)
    date_validation_output = date_validation(data['date_hosted'])

    if validation_output is not data:
        return jsonify({"Warning": validation_output}), 400

    elif date_validation_output is not date_hosted:
        return jsonify({"Warning": date_validation_output}), 400

    try:
        event_found = current_user.create_event(name=name, category=category, location=location,
                                                date_hosted=date_hosted,
                                                description=description)

        response = jsonify({"Success": "Event created successfully",
                            "event": {"name": event_found.name, "id":event_found.id,"category": event_found.category,
                                      "location": event_found.location, "date_hosted": event_found.date_hosted,
                                      "description": event_found.description}})

        response.status_code = 201  # Created
        return response
    except AttributeError:
        return jsonify({"Warning": 'The event already exists'})  # Update an Event


@event.route('/events/<string:event_id>', methods=['PUT'])
@token_required
def update_events(current_user, event_id):
    data = request.get_json()
    print("the data is ", data, event_id)
    name = data['name']
    category = data['category']
    location = data['location']
    date_hosted = data['date_hosted']
    description = data['description']
    if name != '' or category != '' or location != '' or date_hosted != '' or description != '':
        validation_output = update_data_validation(data)
        date_validation_output = date_validation(data['date_hosted'])

        if validation_output is not data:
            return jsonify({"message": validation_output}), 400

        elif date_validation_output is not date_hosted:
            return jsonify({"message": date_validation_output}), 400

    try:
        event_found = current_user.update_event(event_id, name=name, category=category, location=location,
                                                date_hosted=date_hosted,
                                                description=description)
        if isinstance(event_found, str):
            return jsonify({'Warning': "You cannot update an event to duplicate an existing event"})
        else:
            return jsonify({'success': 'The event has been updated successfully',
                            "event": {"name": event_found.name, "category": event_found.category,
                                      "location": event_found.location, "date_hosted": event_found.date_hosted,
                                      "description": event_found.description}}), 200

    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Delete an event from both the personal events list and the public events list"
@event.route('/events/<string:event_id>', methods=['DELETE'])
@token_required
def delete_events(current_user, event_id):
    try:
        current_user.delete_event(event_id)
        response = jsonify({"Success": "Event deleted successfully"})
        response.status_code = 200
        return response
    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Retrieves an individual event
@event.route('/event/<event_id>', methods=['GET'])
@token_required
def get_user_specific_event(current_user, event_id):
    if current_user.get_number_of_events() > 0:
        try:
            event_found = current_user.get_specific_event(event_id)
            return jsonify(
                {"event": {"name": event_found.name, "category": event_found.category, "location": event_found.location,
                           "date_hosted": event_found.date_hosted,
                           "description": event_found.description}})
        except AttributeError:
            response = jsonify({'warning': 'There is no such event'})
            response.status_code = 404  # Not found
            return response
    else:
        return jsonify({'Info': "No Events Found"})


# Route to display all individual events
@event.route('/my_events', methods=['GET'])
@event.route('/my_events/page=<int:page>', methods=['GET'])
@event.route('/my_events/page=<int:page>&limit=<int:limit>', methods=['GET'])
@token_required
def get_an_individuals_all_events(current_user, limit=6, page=1):
    if current_user.get_number_of_events() > 0:
        event_found = Event.query.filter_by(owner=current_user.id).paginate(page, per_page=limit, error_out=False).items
        output = []
        if event_found:
            for s_event in event_found:
                event_data = {'name': s_event.name, "id":s_event.id, 'category': s_event.category, 'location': s_event.location,
                              'date_hosted':
                                  s_event.date_hosted, 'description': s_event.description}
                output.append(event_data)
            return jsonify({'events': output})
        return jsonify({'events': []}), 200
    return jsonify({'events': []}), 200


# Route to display all events
@event.route('/events', methods=['GET'])
@event.route('/events/page=<int:page>', methods=['GET'])
@event.route('/events/page=<int:page>&limit=<int:limit>', methods=['GET'])
def get_all_events(limit=6, page=1):
    if Event.query.count() > 0:
        event_found = Event.query.paginate(page, per_page=limit, error_out=False).items
        output = []
        if event_found:
            for s_event in event_found:
                event_data = {'id':s_event.id, 'name': s_event.name, 'category': s_event.category, 'location': s_event.location,
                              'date_hosted':
                                  s_event.date_hosted, 'description': s_event.description}
                output.append(event_data)
            return jsonify({'events': output})
        return jsonify({'Message': 'No Events Found'}), 404
    return jsonify({'Message': 'No Events Found'}), 404


# Route to rsvp to an event
@event.route('/event/<event_id>/rsvp', methods=['GET', 'POST'])
@token_required
def rsvp_event(current_user, event_id):
    if request.method == 'POST':
        event_found = Event.query.filter_by(id=event_id).first_or_404()
        if event_found:
            try:
                event_found.make_rsvp(current_user)
                return jsonify({'success': 'You have made a reservation successfully'}), 201
            except AttributeError:
                return jsonify({
                    'warning': 'You cannot make a reservation twice and you cannot make a '
                               'reservation to your own event'}), 403  # forbidden
        return jsonify({'warning': 'The event you are trying to make a reservation to does not exist'}), 404
    if request.method == 'GET':
        event_found = Event.query.filter_by(id=event_id).filter_by(owner=current_user.id).first()
        if event_found:
            event_rsvps = event_found.rsvps.all()
            if event_rsvps:
                reservations = []
                for user in event_rsvps:
                    user_data = {'username': user.username, 'email': user.email}
                    reservations.append(user_data)
                return jsonify({'Attendants': reservations})
            return jsonify({'Attendants': []})
        return jsonify({'Warning': 'The event you are to view a reservations for does not exist'}), 404

# Route for searching events
@event.route('/search', methods=['POST'])
@event.route('/search/page=<int:page>&limit=<int:limit>', methods=['POST'])
@event.route('/search/page=<int:page>', methods=['POST'])
# @token_required
def combined_search(limit=9, page=1):
    q = request.args.get('q')
    if q and len(q)>0:
        events = Event.query.filter(or_(Event.name.ilike('%{}%'.format(q)),Event.category.ilike('%{}%'.format(q)),Event.location.ilike('%{}%'.format(q)))).all()
        events_list = []
        if events:
            for s_event in events:
                event_data = {'name': s_event.name, 'category': s_event.category, 'location': s_event.location,
                            'date_hosted': s_event.date_hosted, 'description': s_event.description}
                events_list.append(event_data)
            return jsonify({'events': events_list}), 200
        return jsonify({'message': 'No such event Found'}), 404
    else:
        events = Event.query.all()
        events_list = []
        if events:
            for s_event in events:
                event_data = {'name': s_event.name, 'category': s_event.category, 'location': s_event.location,
                            'date_hosted': s_event.date_hosted, 'description': s_event.description}
                events_list.append(event_data)
            return jsonify({'events': events_list}), 200
        return jsonify({'message':"Something went terribly wrong"}), 400
