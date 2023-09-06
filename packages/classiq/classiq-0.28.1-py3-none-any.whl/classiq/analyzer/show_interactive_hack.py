import tempfile
import webbrowser
from urllib.parse import urljoin

from classiq.interface.generator.generated_circuit import GeneratedCircuit

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function
from classiq.analyzer.url_utils import circuit_page_uri, client_ide_base_url
from classiq.exceptions import ClassiqValueError

_LOGO_HTML = '<p>\n    <img src="https://classiq-public.s3.amazonaws.com/logo/Green/classiq_RGB_Green.png" alt="Classiq logo" height="40">\n    <br>\n  </p>\n'


def handle_jupyter(circuit: GeneratedCircuit) -> None:
    # We assume that we're inside a jupyter-notebook We cannot test it, since this is
    # a part of the interface, while the jupyter-related code is in the SDK
    from IPython.core.display import HTML, display  # type: ignore[import]

    clean_html: str = circuit.interactive_html.replace(_LOGO_HTML, "")  # type: ignore[union-attr]
    h = HTML(clean_html)

    display(h)


def handle_local(circuit: GeneratedCircuit) -> None:
    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix="_interactive_circuit.html"
    ) as f:
        url = f"file://{f.name}"
        f.write(circuit.interactive_html)  # type: ignore[arg-type]
    webbrowser.open(url)


async def handle_remote_app(circuit: GeneratedCircuit) -> None:
    circuit_dataid = await ApiWrapper.call_analyzer_app(circuit)
    app_url = urljoin(
        client_ide_base_url(),
        circuit_page_uri(circuit_id=circuit_dataid.id, circuit_version=circuit.version),
    )
    print(f"Opening: {app_url}")
    webbrowser.open_new_tab(app_url)


async def _show_interactive(
    self: GeneratedCircuit, jupyter: bool = False, local: bool = False
) -> None:
    if not jupyter and not local:
        await handle_remote_app(circuit=self)
        return

    if self.interactive_html is None:
        raise ClassiqValueError("Missing interactive html")

    if jupyter:  # show inline in jupyter
        handle_jupyter(circuit=self)
        return
    if local:  # open web browser
        handle_local(circuit=self)
        return


GeneratedCircuit.show = syncify_function(_show_interactive)  # type: ignore[attr-defined]
GeneratedCircuit.show_async = _show_interactive  # type: ignore[attr-defined]
