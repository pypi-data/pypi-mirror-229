from .handlers import RouteHandler
from jupyter_server.extension.application import ExtensionApp
from traitlets import List

class JupyterLabTelemetryRouterApp(ExtensionApp):

    name = "jupyterlab_telemetry_router"

    exporters = List([]).tag(config=True)

    def initialize_settings(self):
        try:
            assert self.exporters, "The c.JupyterLabTelemetryRouterApp.exporters configuration must be set, please see the configuration example"
            for exporter in self.exporters:
                assert exporter.get('type'), "The type of the exporter must be set, please see the configuration example"
                assert exporter.get('type') in (['console', 'file', 'remote']) or callable(exporter.get('type')), "The type of the exporter must be 'console', 'file', 'remote', or is a customized callable function"
                assert exporter.get('id'), "The id of the exporter must be set, please see the configuration example"
                if (exporter.get('type') == 'file'):
                    assert exporter.get('path'), "The path of the file exporter must be set, please see the configuration example"
                if (exporter.get('type') == 'remote'):
                    assert exporter.get('url'), "The url of the remote exporter must be set, please see the configuration example"

        except Exception as e:
            self.log.error(str(e))
            raise e

    def initialize_handlers(self):
        try:
            self.handlers.extend([(r"/jupyterlab-telemetry-router/(.*)", RouteHandler)])
        except Exception as e:
            self.log.error(str(e))
            raise e
