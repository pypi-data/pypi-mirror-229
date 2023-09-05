import io
import sys


class GetStdOut(list):
    """
    A context manager that captures and temporarily redirects standard output (stdout) to a list.

    Usage:
        from stderrstdoutcapture import GetStdOut
        def outtest():
            try:
                x = 5 / 5
                print("five devided by five is one")
                return x
            except Exception:
                pass

        with GetStdOut() as o1:
            returnvalue1 = outtest()
        print(o1)  # Access captured stdout as a list
        print(f"{returnvalue1=}")  # Display the return value of the function

    Methods:
        __enter__(*args, **kwargs): Enter the context and redirect stdout to a StringIO buffer.
        __exit__(*args, **kwargs): Exit the context and append the captured stdout to the list.

    """

    def __enter__(self, *args, **kwargs):
        self.stdout = sys.stdout
        sys.stdout = self.string_io = io.StringIO()
        return self

    def __exit__(self, *args, **kwargs):
        self.append(self.string_io.getvalue())
        sys.stdout = self.stdout


class GetStdErr(list):
    r"""
    A context manager that captures and temporarily redirects standard error (stderr) to a list.

    Usage:
        from stderrstdoutcapture import GetStdErr

        def errtest():
        try:
            x = 5 / 0
        except Exception:
            return "error"

        with GetStdErr() as o2:
            returnvalue2 = errtest()
        print(o2)  # Access captured stderr as a list
        print(f"{returnvalue2=}")  # Display the return value of the function

    Methods:
        __enter__(*args, **kwargs): Enter the context and redirect stderr to a StringIO buffer.
        __exit__(*args, **kwargs): Exit the context and append the captured stderr to the list.

    """

    def __enter__(self, *args, **kwargs):
        self.stderr = sys.stderr
        sys.stderr = self.string_io = io.StringIO()
        return self

    def __exit__(self, *args, **kwargs):
        self.append(self.string_io.getvalue())
        sys.stderr = self.stderr
