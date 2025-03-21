from rest_framework.exceptions import ValidationError


class PersonListValidator:

    def __call__(self, persons):

        for person in persons:

            if not isinstance(person, dict):
                raise ValidationError("the person field must be a JSON Field")

            affiliations = person.get("affiliations", [])

            if isinstance(affiliations, list):
                for affiliation in affiliations:

                    if isinstance(affiliation, dict):
                        if affiliation != {}: # if not empty dict should have at least affiliation name
                            affiliation_name = affiliation.get("affiliation", None)

                            if affiliation_name is None:
                                raise ValidationError('affiliation needs at least a name: "affiliation": <name>')
                        else:
                            raise ValidationError("empty affiliations are not valid")
                    else:
                        raise ValidationError("each affiliation must be a JSON field")

            else:
                raise ValidationError("affiliations must be a list of JSON Fields")
