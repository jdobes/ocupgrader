from jsonschema import validate
from jsonschema.exceptions import ValidationError
import logging
import yaml

log = logging.getLogger(__name__)

SCHEMA = yaml.safe_load("""
type: object
properties:
  services:
    type: array
    items:
      type: string
      example: vulnerability-engine-manager
  tasks:
    type: object
    additionalProperties:
      type: object
      properties:
        arguments:
          type: array
          items:
            type: string
            example: version
        commands:
          type: array
          items:
            type: string
            example: get pods
        description:
          type: string
      required:
        - commands
        - description
required:
  - services
  - tasks
""")


def validate_schema(project_spec):
    try:
        validate(project_spec, SCHEMA)
        return True
    except ValidationError as e:
        log.error(e)
    return False
