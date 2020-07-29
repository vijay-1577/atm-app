import random

from flask import request
from flask_restful import Resource, reqparse, marshal

from app.resources import create_or_update_resource, delete_resource
from app.models import Atm, Subject
from app.serializers import Atm_serializer


class AtmListAPI(Resource):
    """View all Atms; add new Atm
    URL: /api/v1/Atms
    Request methods: POST, GET
    """

    def get(self):

        args = request.args.to_dict()
        page = int(args.get("page", 1))
        limit = int(args.get("limit", 20))
        kwargs = {}

        Atms = Atm.query.filter_by(**kwargs).paginate(
                             page=page, per_page=limit, error_out=False)
        page_count = Atms.pages
        has_next = Atms.has_next
        has_previous = Atms.has_prev
        if has_next:
            next_page = str(request.url_root) + "api/v1.0/Atms?" + \
                "limit=" + str(limit) + "&page=" + str(page + 1)
        else:
            next_page = "None"
        if has_previous:
            previous_page = request.url_root + "api/v1.0/Atms?" + \
                "limit=" + str(limit) + "&page=" + str(page - 1)
        else:
            previous_page = "None"
        Atms = Atms.items

        output = {"Atms": marshal(Atms, Atm_serializer),
                  "has_next": has_next,
                  "page_count": page_count,
                  "previous_page": previous_page,
                  "next_page": next_page
                  }

        if Atms:
            return output
        else:
            return {"error": "There are no registered Atms. "
                             "Add a new one and try again!"}, 404

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            "first_name",
            required=True,
            help="Please enter a first name.")
        parser.add_argument(
            "last_name",
            required=True,
            help="Please enter a last name.")
        parser.add_argument(
            "email_address",
            required=True,
            help="Please enter an email address.")
        parser.add_argument(
            "major_id",
            help="Please enter only one subject ID.")
        parser.add_argument(
            "minors",
            help="Separate multiple subject IDs with a comma.")
        args = parser.parse_args()
        first_name, last_name, email_address, major_id, minors = \
            args["first_name"], args["last_name"], args["email_address"], \
            args["major_id"], args["minors"]
        Atm = Atm(first_name=first_name,
                          last_name=last_name,
                          email_address=email_address,
                          Atm_id="ST" + str(random.randint(1, 999)))

        if major_id:
            Atm.major_id = major_id

        if minors:
            minors_list = [minor.strip() for minor in minors.split(',')]
            for subject_id in minors_list:
                try:
                    minor = Subject.query.get(subject_id)
                    if minor:
                        Atm.minors.append(minor)
                    else:
                        return {"error": "One or more minor subject IDs you "
                                "entered is invalid."}, 400
                except:
                    return {"error": "The minors field should only contain "
                            "integers separated by a comma."}, 400
        return create_or_update_resource(
            resource=Atm,
            resource_type="Atm",
            serializer=Atm_serializer,
            create=True)


class AtmAPI(Resource):
    """View, update and delete a single Atm.
    URL: /api/v1/Atms/<id>
    Request methods: GET, PUT, DELETE
    """

    def get(self, id):

        Atm = Atm.query.filter_by(Atm_id=id).first()
        if Atm:
            return marshal(Atm, Atm_serializer)
        else:
            return {"error": "A Atm with ID " + id + " does "
                             "not exist."}, 404

    def put(self, id):

        Atm = Atm.query.filter_by(Atm_id=id).first()
        if Atm:
            parser = reqparse.RequestParser()
            parser.add_argument("first_name")
            parser.add_argument("last_name")
            parser.add_argument("email_address")
            parser.add_argument("major_id")
            parser.add_argument("minors")
            args = parser.parse_args()

            for field in args:
                if args[field] is not None:
                    if field == "minors":
                        # Clear the Atm's list of minors
                        for subject in Atm.minors:
                            subject.minor_Atms.remove(Atm)
                        Atm.minors = []
                        minors = args["minors"]
                        minors_list = [minor.strip() for minor in
                                       minors.split(',')]
                        # Append new minors into list
                        if minors_list != [u'']:
                            for subject_id in minors_list:
                                try:
                                    minor = Subject.query.get(subject_id)
                                    if minor:
                                        Atm.minors.append(minor)
                                    else:
                                        return {"error": "One or more subject "
                                                "IDs you entered is "
                                                "invalid."}, 400
                                except:
                                    return {"error": "The minors field should "
                                            "only contain subject IDs "
                                            "separated by a comma."}, 400
                    elif field == "email_address":
                        return {"error": "You can't update the email address "
                                "field."}, 400
                    else:
                        updated_field = args[field]
                        setattr(Atm, field, updated_field)
        else:
            return {"error": "A Atm with ID " + id + " does "
                             "not exist."}, 404

        return create_or_update_resource(
            resource=Atm,
            resource_type="Atm",
            serializer=Atm_serializer,
            create=False)

    def delete(self, id):

        Atm = Atm.query.filter_by(Atm_id=id).first()
        if Atm:
            return delete_resource(resource=Atm,
                                   resource_type="Atm",
                                   id=id)
        else:
            return {"error": "A Atm with ID " + id + " does "
                             "not exist."}, 404
