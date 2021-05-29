
import sys
import io


class TeeOutput(object):
    def __init__(self, outputs):
        self.outputs = outputs

    def write(self, text):
        for output in self.outputs:
            output.write(text)

    def flush(self):
        for output in self.outputs:
            output.flush()


class ScopeTee(object):
    def __init__(self, aux_output):
        self.aux_stdout = aux_output
        self.aux_stderr = aux_output

    def __enter__(self):
        self.saved_stdout = sys.stdout
        self.saved_stderr = sys.stderr
        sys.stdout = TeeOutput([self.saved_stdout, self.aux_stdout])
        sys.stderr = TeeOutput([self.saved_stderr, self.aux_stderr])

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.saved_stdout
        sys.stderr = self.saved_stderr


if __name__ == '__main__':
    print('begin')
    aux_output = io.StringIO()
    with ScopeTee(aux_output):
        print('work')
    print('end')
    print('aux', aux_output.getvalue())
