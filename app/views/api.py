from flask import Blueprint, jsonify
from app.controllers.api_controller import ApiController
from app import csrf

api_bp = Blueprint('api', __name__)

@api_bp.route('/toilets')
@csrf.exempt
def get_toilets():
    """
    Get all toilets
    ---
    tags:
      - Toilets
    responses:
      200:
        description: A list of all toilets
        schema:
          type: object
          properties:
            toilets:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  latitude:
                    type: number
                  longitude:
                    type: number
                  description:
                    type: string
                  accessible:
                    type: boolean
                  has_toilet_paper:
                    type: boolean
                  cleanliness:
                    type: integer
                  review_count:
                    type: integer
                  author:
                    type: string
      401:
        description: Unauthorized
    """
    data, status = ApiController.get_toilets()
    return jsonify(data) if status != 200 else data

@api_bp.route('/toilet/<int:toilet_id>')
@csrf.exempt
def get_toilet_details(toilet_id):
    """
    Get details of a specific toilet
    ---
    tags:
      - Toilets
    parameters:
      - name: toilet_id
        in: path
        type: integer
        required: true
        description: ID of the toilet
    responses:
      200:
        description: Details of the toilet with reviews
      401:
        description: Unauthorized
    """
    data, status = ApiController.get_toilet_details(toilet_id)
    return jsonify(data) if status != 200 else data