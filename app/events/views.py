import re
from datetime import datetime

from flask import request, jsonify

from app.auth.views import token_required
from app.events import event
from app.models.event import Event


def date_validation(date_hosted):
    """check that the event date is not past"""
    try:
        date = datetime.strptime(date_hosted, '%m-%d-%Y').date()

    except ValueError:
        return "You have entered an incorrect date format, date should be MM-DD-YY format"

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
    if len(data['name'].strip()) < 5 or not re.match("^[a-zA-Z0-9_]*$", data['name'].strip()):
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
        if not re.match("^[a-zA-Z0-9_]*$", data['name']) or len(data['name']) < 5:
            return "The event name should only contain alphanumeric characters,an underscore and be at least 5 " \
                   "characters in length without any empty spaces and special characters"
    if data['location'] != '':
        if not data['location'].isalpha() and len(data['location']) < 3:
            return "The event location should only contain alphabetic characters and be at least 3 characters in length" \
                   " excluding empty spaces"

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
        return jsonify({"message": validation_output}), 400

    elif date_validation_output is not date_hosted:
        return jsonify({"message": date_validation_output}), 400

    try:
        event_found = current_user.create_event(name=name, category=category, location=location,
                                                date_hosted=date_hosted,
                                                description=description)

        response = jsonify({"Success": "Event created successfully",
                            "event": {"name": event_found.name, "category": event_found.category,
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
    name = data['name']
    category = data['category']
    location = data['location']
    date_hosted = data['date_hosted']
    description = data['description']
    if name != '' or category != '' or location != '' or date_hosted != '' or description != '':
        validation_output = update_data_validation(data)
        date_validation_output = update_date_validation(data['date_hosted'])

        if validation_output is not data:
            return jsonify({"message": validation_output}), 400

        elif date_validation_output is not date_hosted:
            return jsonify({"message": date_validation_output}), 400

    try:
        event_found = current_user.update_event(event_id, name=name, category=category, location=location,
                                                date_hosted=date_hosted,
                                                description=description)
        if type(event_found) is str:
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
        return jsonify({'Info': "No event created so far"})


# Route to display all individual events
@event.route('/my_events', methods=['GET'])
@event.route('/my_events/<int:page>', methods=['GET'])
@token_required
def get_an_individuals_all_events(current_user, page=1):
    if current_user.get_number_of_events() > 0:
        event_found = Event.query.filter_by(owner=current_user.id).paginate(page, per_page=3, error_out=True).items
        output = []
        for s_event in event_found:
            event_data = {'name': s_event.name, 'category': s_event.category, 'location': s_event.location,
                          'description': s_event.description}
            output.append(event_data)
        return jsonify({'events': output})
    return jsonify({'Message': 'So far you have not created any events'})


# Route to display all events
@event.route('/events', methods=['GET'])
@event.route('/events/<int:page>', methods=['GET'])
def get_all_events(page=1):
    if Event.query.count() > 0:
        event_found = Event.query.paginate(page, per_page=4, error_out=True).items
        output = []
        for s_event in event_found:
            event_data = {'name': s_event.name, 'category': s_event.category, 'location': s_event.location,
                          'description': s_event.description}
            output.append(event_data)
        return jsonify({'events': output})
    return jsonify({'Message': 'So far you have not created any events'})


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
                               'reservation to your own event'}), 302
        return jsonify({'warning': 'The event you are trying to make a reservation to does not exist'})
    if request.method == 'GET':
        event_found = Event.query.filter_by(id=event_id).filter_by(owner=current_user.id).first_or_404()
        if event_found:
            event_rsvps = event_found.rsvps.all()
            if event_rsvps:
                reservations = []
                for user in event_rsvps:
                    user_data = {'username': user.username, 'email': user.email}
                    reservations.append(user_data)
                return jsonify({'Attendants': reservations})
            return jsonify({"Message": "No reservations have been made to this event yet"})
        return jsonify({'Warning': 'The event you are searching for does not exist'})


@event.route('/search', methods=['POST'])
@event.route('/search/<int:page>', methods=['POST'])
@token_required
def search(current_user, page=1):
    data = request.get_json()
    try:
        category = data['category']
        events_returned = current_user.search_event_by_category(category, page)
        events_list = []
        if events_returned:
            for s_event in events_returned:
                event_data = {'name': s_event.name, 'category': s_event.category, 'description': s_event.description}
                events_list.append(event_data)
            return jsonify({'Events belonging to this category': events_list}), 200

        return jsonify({'message': 'There are no events related to this category'})
    except KeyError:
        try:
            location = data['location']
            events_returned = current_user.search_event_by_location(location, page)
            events_list = []
            if events_returned:
                for s_event in events_returned:
                    event_data = {'name': s_event.name, 'category': s_event.category,
                                  'description': s_event.description}
                    events_list.append(event_data)
                return jsonify({'Events found in this location': events_list}), 200

            return jsonify({'message': 'There are no events organized in this location so far'})
        except KeyError:
            try:
                name = data['name']
                events_returned = current_user.search_event_by_name(name, page)
                events_list = []
                if events_returned:
                    for s_event in events_returned:
                        event_data = {'name': s_event.name, 'category': s_event.category,
                                      'description': s_event.description}
                        events_list.append(event_data)
                    return jsonify({'The following events were found': events_list}), 200

                return jsonify({'message': 'There are no events with such a name'})
            except KeyError:
                return jsonify({'Warning': 'Cannot comprehend the given search parameter'})
