# Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

from flask import current_app, request, url_for
import flask_restful
from flask_restful import fields, marshal_with, marshal, reqparse, types
import sqlalchemy
from chaos import models, db, utils
from jsonschema import validate, ValidationError
from flask.ext.restful import abort
import logging

__all__ = ['Disruptions']


class FieldDateTime(fields.Raw):
    def format(self, value):
        if value:
            return value.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return 'null'


disruption_fields = {'id': fields.Raw,
                     'self': {'href': fields.Url('disruption', absolute=True)},
                     'reference': fields.Raw,
                     'note': fields.Raw,
                     'status': fields.Raw,
                     'created_at': FieldDateTime,
                     'updated_at': FieldDateTime,
                     }


disruptions_fields = {'disruptions': fields.List(fields.Nested(disruption_fields))
                     }

one_disruption_fields = {'disruption': fields.Nested(disruption_fields)
                     }

error_fields = {'error': fields.Nested({'message': fields.String})}


#see http://json-schema.org/
disruptions_input_format = {'type': 'object',
                            'properties': {'reference': {'type': 'string', 'maxLength': 250},
                                           'note': {'type': 'string'}
                            },
                            'required': ['reference']
        }


class Index(flask_restful.Resource):

    def get(self):
        url = url_for('disruption', _external=True)
        response = {
            "disruptions": {"href": url},
            "disruption": {"href": url + '/{id}', "templated": True}
        }
        return response, 200

class Disruptions(flask_restful.Resource):
    def __init__(self):
        self.parsers = {}
        self.parsers["get"] = reqparse.RequestParser()
        parser_get = self.parsers["get"]
        parser_get.add_argument("start_page", type=int, default=1)
        parser_get.add_argument("count", type=int, default=20)

    def get(self, id=None):
        if id:
            return marshal({'disruption': models.Disruption.get(id)},
                           one_disruption_fields)
        else:
            args = self.parsers['get'].parse_args()
            start_index = args['start_page']
            if start_index == 0:
                abort(400, message="page_index argument value is not valid")
            items_per_page = args['count']
            if items_per_page == 0:
                abort(400, message="items_per_page argument value is not valid")
            result = models.Disruption.paginate(start_index, items_per_page)

            response = marshal({'disruptions': result.items},
                            disruptions_fields)
            response["meta"] = utils.get_meta(result)
            return response

    def post(self):
        json = request.get_json()
        logging.getLogger(__name__).debug(json)
        try:
            validate(json, disruptions_input_format)
        except ValidationError, e:
            logging.debug(str(e))
            #TODO: generate good error messages
            return marshal({'error': {'message': str(e).replace("\n", " ")}},
                           error_fields), \
                    400

        disruption = models.Disruption()
        disruption.fill_from_json(json)
        db.session.add(disruption)
        db.session.commit()
        return marshal({'disruption': disruption}, one_disruption_fields), 201


    def put(self, id):
        disruption = models.Disruption.get(id)
        json = request.get_json()
        logging.getLogger(__name__).debug(json)

        try:
            validate(json, disruptions_input_format)
        except ValidationError, e:
            logging.getLogger(__name__).debug(str(e))
            #TODO: generate good error messages
            return marshal({'error': {'message': str(e).replace("\n", " ")}},
                           error_fields), \
                    400

        disruption.fill_from_json(json)
        db.session.commit()
        return marshal({'disruption': disruption}, one_disruption_fields), 200

    def delete(self, id):
        disruption = models.Disruption.get(id)
        disruption.archive()
        db.session.commit()
        return None, 204
