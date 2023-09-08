class StatusMessage:
    PREPARING = None
    RUNNING = None


class JobTimeoutError(Exception):
    def __init__(self, job_id, timeout):
        super().__init__(f"Burla job with id: '{job_id}' timed out after {timeout} seconds.")


class InstallError(Exception):
    def __init__(self, stdout: str):
        super().__init__(
            f"The following error occurred attempting to pip install packages:\n{stdout}"
        )


class ServerError(Exception):
    def __init__(self):
        super().__init__(
            (
                "An unknown error occurred in Burla's cloud, this is not an error with your code. "
                "Someone has been notified, please try again later."
            )
        )


def nopath_warning(message, category, filename, lineno, line=None):
    return f"{category.__name__}: {message}\n"


def concurrency_warning_message(n_batches, n_inputs, max_concurrency, gpu=False):
    msg = f"Because the current maximum concurrency is {max_concurrency} "
    msg += f"{'(when using GPUs)' if gpu else ''} and you submitted {n_inputs} inputs, "
    msg += f"these inputs will be processed in {n_batches} separate batches.\n"
    msg += "Please email jake@burla.dev to request a concurrency limit increase."
    return msg
