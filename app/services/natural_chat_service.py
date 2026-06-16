from dataclasses import dataclass
from app.domain.chat import ChatIntent
from app.services.ai_response_service import AIResponseService
from app.services.chat_service import ChatService

_UNKNOWN_ANSWER = 'No dispongo de datos empresariales para responder esa pregunta en el sistema actual.'

@dataclass(frozen=True)
class NaturalChatResult:
    question: str
    intent: str
    answer: str

class NaturalChatService:

    def __init__(self, chat_service: ChatService, ai_response_service: AIResponseService):
        self._chat_service = chat_service
        self._ai_response_service = ai_response_service

    def process(self, question: str) -> NaturalChatResult:
        chat_result = self._chat_service.process(question)
        intent_value = chat_result.intent.value
        if chat_result.intent is ChatIntent.UNKNOWN:
            return NaturalChatResult(question=question, intent=intent_value, answer=_UNKNOWN_ANSWER)
        answer = self._ai_response_service.generate(question=question, intent=intent_value, data=chat_result.data)
        return NaturalChatResult(question=question, intent=intent_value, answer=answer.strip())
