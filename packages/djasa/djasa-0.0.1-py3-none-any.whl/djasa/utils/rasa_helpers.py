from io import StringIO

from djasa.conf import djasa_settings
from ruamel.yaml import YAML


def generate_training_data():
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(sequence=4, offset=2)

    # Extract entity types
    entity_types = set()
    for model in djasa_settings.DJASA_ENTITIES:
        entity_types.update(model.DjasaMeta.entities)

    # Extract intent examples
    intent_examples = {}
    for model in djasa_settings.DJASA_INTENTS:
        intent_name = model.DjasaMeta.name
        for intent_instance in model.objects.all():
            phrases = intent_instance.training_phrases.replace(',', '\n').split('\n')
            if intent_name not in intent_examples:
                intent_examples[intent_name] = []
            intent_examples[intent_name].extend([f"- {phrase.strip()}" for phrase in phrases])

    training_data = {
        "version": "3.1",
        "entities": list(entity_types)
    }

    # Convert the Python data structure to a YAML string
    output_stream = StringIO()
    yaml.dump(training_data, output_stream)

    # Manually construct the nlu section
    output_stream.write("\nnlu:")
    for intent, examples in intent_examples.items():
        output_stream.write(f"\n  - intent: {intent}\n    examples: |\n      " + "\n      ".join(examples))

    return output_stream.getvalue()
