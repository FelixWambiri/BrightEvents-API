import re

from flask import request, jsonify, abort

from app.auth.views import token_required
from app.events import event
from app.models.event import Event


@event.route('/events', methods=['POST'])
@token_required
def create_events(current_user):
    data = request.get_json()
    name = data['name'].strip()
    category = data['category'].strip()
    location = data['location'].strip()
    description = data['description'].strip()

    # Validate these fields against being empty
    if name is None or category is None or location is None:
        abort(400)

    # Validate the length of these fields to be more than five characters
    if len(name) < 5 or len(category) < 5 or len(location) < 5:
        return jsonify({"Warning": "This fields must be more than 5 characters and not empty spaces"})

    # Validate the name against special characters and spaces
    if not re.match("^[a-zA-Z0-9_]*$", name):
        return jsonify({
            "Warning": "Invalid event name.The event name can contain letters, digits and underscore but no special"
                       " characters or space"})

    # Validate the category, location and owner fields to be comprised of only alphabetic characters
    if not category.isalpha() or not location.isalpha():
        return jsonify({"Warning": "Please enter a valid input"})
    try:
        event = current_user.create_event(name=name, category=category, location=location, description=description)
        response = jsonify({"Success": "Event created successfully",
                            "event": {"name": event.name, "category": event.category, "location": event.location,
                                      "description": event.description}})
        response.status_code = 201  # Created
        return response
    except AttributeError:
        return jsonify({"Warning": 'The event already exists'})


# Update an Event
@event.route('/events/<string:name>', methods=['PUT'])
@token_required
def update_events(current_user, name):
    data = request.get_json()
    new_name = data['new_name']
    category = data['category']
    location = data['location']
    description = data['description']
    try:
        event = current_user.update_event(name, new_name=new_name, category=category, location=location,
                                          description=description)
        return jsonify({'success': 'The event has been updated successfully',
                        "event": {"name": event.name, "category": event.category, "location": event.location,
                                  "description": event.description}}), 200

    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Delete an event from both the personal events list and the public events list"
@event.route('/events/<string:event_name>', methods=['DELETE'])
@token_required
def delete_events(current_user, event_name):
    try:
        current_user.delete_event(event_name)
        response = jsonify({"Success": "Event deleted successfully"})
        response.status_code = 200
        return response
    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Retrieves an individual event
@event.route('/events/<event_name>', methods=['GET'])
@token_required
def get_user_specific_event(current_user, event_name):
    if current_user.get_number_of_events() > 0:
        try:
            event = current_user.get_specific_event(event_name)
            return jsonify({"event": {"name": event.name, "category": event.category, "location": event.location,
                                      "description": event.description}})
        except AttributeError:
            response = jsonify({'warning': 'There is no such event'})
            response.status_code = 404  # Not found
            return response
    else:
        return jsonify({'Info': "No event created so far"})


# Route to display all events
@event.route('/events', methods=['GET'])
@event.route('/api/events/<int:page>', methods=['GET'])
@token_required
def get_an_individuals_all_events(current_user, page=1):
    if current_user.get_number_of_events() > 0:
        events_r = Event.query.filter_by(owner=current_user.id).paginate(page, per_page=3, error_out=True).items
        output = []
        for event in events_r:
            event_data = {'name': event.name, 'category': event.category, 'location': event.location,
                          'description': event.description}
            output.append(event_data)
        return jsonify({'events': output})
    return jsonify({'Message': 'So far you have not created any events'})


# Route to rsvp to an event
@event.route('/event/<name>/rsvp', methods=['GET', 'POST'])
@token_required
def rsvp_event(current_user, name):
    if request.method == 'POST':
        event = Event.query.filter_by(name=name).first_or_404()
        if event:
            try:
                event.make_rsvp(current_user)
                return jsonify({'success': 'You have made a reservation successfully'}), 201
            except AttributeError:
                return jsonify({
                    'warning': 'You cannot make a reservation twice and you cannot make a '
                               'reservation to your own event'}), 302
        return jsonify({'warning': 'The event you are trying to make a reservation to does not exist'})
    if request.method == 'GET':
        event = Event.query.filter_by(name=name).filter_by(owner=current_user.id).first_or_404()
        if event:
            event_rsvps = event.rsvps.all()
            if event_rsvps:
                reservations = []
                for user in event_rsvps:
                    user_data = {'username': user.username, 'email': user.email}
                    reservations.append(user_data)
                return jsonify({'Attendants': reservations})
            return jsonify({"Message": "No reservations have been made to this event yet"})
        return jsonify({'Warning': 'The event you are searching for does not exist'})


@event.route('/event/search_by_loc/<location>', methods=['GET'])
@event.route('/event/search_by_loc/<location>/<int:page>', methods=['GET'])
@token_required
def search_by_location(current_user, location, page=1):
    events_returned = current_user.search_event_by_location(location, page)
    events_r = []
    if events_returned:
        for event in events_returned:
            event_data = {'name': event.name, 'category': event.category, 'description': event.description}
            events_r.append(event_data)
        return jsonify({'Events found in this location': events_r}), 200

    return jsonify({'message': 'There are no events that have been organized here so far'})


@event.route('/event/search_by_cat/<category>', methods=['GET'])
@event.route('/event/search_by_cat/<category>/<int:page>', methods=['GET'])
@token_required
def search_by_category(current_user, category, page=1):
    events_returned = current_user.search_event_by_category(category, page)
    events_r = []
    if events_returned:
        for event in events_returned:
            event_data = {'name': event.name, 'category': event.category, 'description': event.description}
            events_r.append(event_data)
        return jsonify({'Events found in this category': events_r}), 200

    return jsonify({'message': 'There are no events that have been organized here so far'})