from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from vaxila.opentelemetry.util import enable_exc_local_variables_recording

enable_exc_local_variables_recording()


def create_tracer():
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    return tracer_provider.get_tracer("my.tracer.name")


def raise_exception(text_arg, int_arg):
    bool_var = True
    raise Exception(f"exception: {text_arg}, {int_arg}, {bool_var}")


tracer = create_tracer()

try:
    with tracer.start_as_current_span(
        "example for enable_exc_local_variables_recording"
    ):
        raise_exception("hello", 1234)
except Exception:
    pass
