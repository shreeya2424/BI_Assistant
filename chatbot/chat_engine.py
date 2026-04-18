from chatbot.query_parser import QueryParser
from chatbot.query_executor import QueryExecutor
from chatbot.response_formatter import ResponseFormatter


class ChatEngine:
    """
    Structured BI assistant:
    question -> intent -> execution -> formatted response
    """

    def __init__(self):
        self.parser = QueryParser()
        self.executor = QueryExecutor()
        self.formatter = ResponseFormatter()

    def answer_question(self, question, results, data, vector_store=None, chat_history=None):
        intent = self.parser.parse(question, data)
        execution_result = self.executor.execute(intent, results, data)
        return self.formatter.format(intent, execution_result)