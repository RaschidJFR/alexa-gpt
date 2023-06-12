import logging
import ask_sdk_core.utils as ask_utils
import openai
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Set your OpenAI API key
openai.api_key = "PUT YOUR OPEN API KEY HERE"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speak_output = speak_output_en = "Chat G.P.T. mode activated"
        speak_output_es = "Hola, soy Chat G. P. T."
        
        locale = handler_input.request_envelope.request.locale
        if "en-" in locale:
            speak_output = speak_output_en
        elif "es-" in locale:
            speak_output = speak_output_es

        return (
            handler_input.response_builder
                .speak(getSSML(speak_output))
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query)

        return (
                handler_input.response_builder
                    .speak(getSSML(response))
                    .ask("Any other questions?")
                    .response
            )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = speak_output_en = "Sorry, I had trouble doing what you asked. Please try again."
        speak_output_es = "Tuve problemas con esto. Intenta de nuevo."
        
        locale = handler_input.request_envelope.request.locale
        if "en-" in locale:
            speak_output = speak_output_en
        elif "es-" in locale:
            speak_output = speak_output_es

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(getSSML(speak_output))
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = speak_output_en = "Leaving Chat G.P.T. mode"
        speak_output_es = "Chat G. P. T. desactivado"
        
        locale = handler_input.request_envelope.request.locale
        if "en-" in locale:
            speak_output = speak_output_en
        elif "es-" in locale:
            speak_output = speak_output_es

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(query):
    try:
        messages = [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

def getSSML(responseText):
    return "<speak><voice name=\"Miguel\">"+responseText+"</voice></speak>"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()