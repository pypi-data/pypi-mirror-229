import logging
import traceback
from tempfile import NamedTemporaryFile
from typing import List, Optional

from ipykernel.kernelbase import Kernel
from swiplserver.prologmqi import PrologMQI, PrologThread


class SWIPrologLogger(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages: List[str] = []

    def __enter__(self):
        self.messages = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def emit(self, record):
        self.messages.append(record.msg)


class SWIPrologKernel(Kernel):
    implementation = 'SWI Prolog'
    implementation_version = '1.0.2.1'
    banner = 'SWI Prolog Kernel'
    language_info = {
        'name': 'prolog',
        'mimetype': 'application/prolog',
        'file_extension': '.pl',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # create placeholders
        self._mqi: Optional[PrologMQI] = None
        self._thread: Optional[PrologThread] = None

    # output related functions
    def print(self, text: str, name: str = 'stdout'):
        self.send_response(self.iopub_socket, 'stream', {
            'name': name,
            'text': text
        })

    def print_exception(self, e: Exception):
        text = traceback.format_exc()
        self.print(text, 'stderr')

    def print_data(self, *data: str, mime: str = 'text/plain'):
        for v in data:
            self.send_response(self.iopub_socket, 'display_data', {
                'data': {
                    mime: v
                },
                # `metadata` is required. Otherwise, Jupyter Lab does not display any output.
                # This is not the case when using Jupyter Notebook btw.
                'metadata': {}
            })

    # magic methods / statements
    @staticmethod
    def _is_consult(code: str) -> bool:
        lower_code = code.lower()
        for command in 'consult', 'fact', 'facts', 'rule', 'rules':
            for prefix in '%', '%%':
                if lower_code.startswith(f'{prefix}{command}'):
                    return True

        return False

    # prolog mqi related functions
    def _load(self):
        if self._mqi is None:
            # create prolog instance
            self._mqi = PrologMQI().__enter__()
            self._thread = self._mqi.create_thread().__enter__()

            # create logger
            self._logger: SWIPrologLogger = SWIPrologLogger()
            logging.getLogger('swiplserver').addHandler(self._logger)

    def _unload(self):
        if self._mqi is not None:
            # remove logger
            logging.getLogger('swiplserver').removeHandler(self._logger)

            # shutdown prolog instance
            self._thread.__exit__(None, None, None)
            self._mqi.__exit__(None, None, None)

            self._thread = None
            self._mqi = None

    def _execute(self, code: str):
        with self._logger:
            result = self._thread.query(code)
            logs = self._logger.messages

        if len(logs) > 0:
            self.print('\n'.join(logs), name='stderr')

        if isinstance(result, bool):
            if result:
                self.print_data('true', mime='text/html')
            else:
                self.print_data('<span style="color: red">false</span>', mime='text/html')
        elif isinstance(result, list):
            self.print_data('\n'.join(', '.join(f'{k} = {v}' for k, v in d.items()) for d in result))
        else:
            self.print_data(f'{type(result)}: {result}')

    # jupyter related functions
    def do_execute(self, code: str, silent: bool,
                   store_history: bool = True, user_expressions: dict = None, allow_stdin: bool = False,
                   **kwargs):
        try:
            # load prolog instance
            self._load()

            # consult
            if self._is_consult(code):
                # remove first line from code
                _, code = code.split('\n', 1)

                # open temporary file
                with NamedTemporaryFile(mode='w', suffix='.pl', encoding='utf-8') as file:
                    # store code to file
                    file.write(code)
                    file.flush()

                    # execute consult query
                    self._execute(f"consult('{file.name}')")

            # standard query
            else:
                self._execute(code)

            # print output and return response
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }

        except Exception as e:
            self.print_exception(e)

            return {
                'status': 'error',
                'ename': str(type(e)),
                'evalue': str(e),
                'traceback': traceback.format_exc()
            }

    def do_shutdown(self, restart):
        self._unload()
        return super().do_shutdown(restart)
