import sys
import eel
import python.align

real_stdout = sys.stdout

class WriteProcessor:
    def __init__(self):
        self.buf = ""

    def write(self, buf):
        # emit on each newline
        while buf:
            try:
                newline_index = buf.index("\n")
            except ValueError:
                # no newline, buffer for next call
                self.buf += buf
                break
            # get data to next newline and combine with any buffered data
            data = self.buf + buf[:newline_index + 1]
            self.buf = ""
            buf = buf[newline_index + 1:]
            real_stdout.write(data)

            eel.add_log_entry('info', data)

sys.stdout = WriteProcessor()

class Commands:
    def __init__(self, app):
        self.app = app
        self.setup_hooks()

    def setup_hooks(self):
        @eel.expose
        def send_command(command):
            return self.execute_command(command)

    def execute_command(self, cmd):
        print(f"Executing command: {cmd}")
        if cmd == "align":
            return python.align.align(self.app)
        