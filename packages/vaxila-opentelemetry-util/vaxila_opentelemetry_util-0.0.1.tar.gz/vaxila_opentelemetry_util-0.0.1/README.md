# OpenTelemetry utilities for Python by Vaxila
[![PyPI version](https://badge.fury.io/py/vaxila-opentelemetry-util.svg)](https://badge.fury.io/py/vaxila-opentelemetry-util)

This repository contains a set of utilities for OpenTelemetry for Python.

# Installation

```bash
pip install vaxila-opentelemetry-util
```

# Usage

## Add local variables to attributes of exception's event

```python
from vaxila.opentelemetry.util import enable_exc_local_variables_recording

enable_exc_local_variables_recording()
```

When exception is raised, OpenTelemetry automatically creates an event for exception.  
`enable_exc_local_variables_recording()` adds local variables to the event's attributes automatically by decorating `Span.record_exception()`.  
This helps you find the situation where exception happened.

You can see example [here](example/enable_exc_local_variables_recording).

:warning: When using pre-fork server like Gunicorn, you should call `enable_exc_local_variables_recording()` before fork to not run same thing multiple times.
