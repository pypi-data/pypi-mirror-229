from velikafkaclient.decorators import ctracing


class BaseHandler:
    web_integrator = None
    ios_integrator = None
    android_integrator = None
    event_model = None
    params_methods_mapper = {}
    base_params_method = None
    params_method = None

    def __init__(self, event_name):
        self.event_name = event_name
        self.params_method = self.params_methods_mapper[event_name] if event_name in self.params_methods_mapper else \
            self.base_params_method

    def set_data(self, event_data, source):
        return self.event_model(**event_data)

    @ctracing
    async def send_data(self, event_data):
        event_data = event_data.dict()
        source = event_data.get('source')
        model = self.set_data(event_data, source)
        integrator_instances = {
            'web': self.web_integrator,
            'ios': self.ios_integrator,
            'android': self.android_integrator
        }
        await integrator_instances[source](model=model).create_object()
