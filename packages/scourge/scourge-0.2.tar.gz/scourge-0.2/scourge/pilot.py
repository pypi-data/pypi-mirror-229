from requests import Session
from deceit.adapters import RetryAdapter
from zeep.cache import Base as BaseCache
from zeep.client import Client
from zeep.plugins import HistoryPlugin
from zeep.proxy import OperationProxy
from zeep.proxy import ServiceProxy as ZeepServiceProxy
from zeep.settings import Settings
from zeep.transports import Transport


class SoapTransport(Transport):
    def __init__(self, session=None):
        # operation timeout specifies how long we are  willing to wait
        # for netsuite to get back to us
        # some operations can take a while, so we may need to adjust this.
        # the worst offenders are the custom list actions
        super().__init__(
            session=session,
            timeout=24 * 60 * 60,
            operation_timeout=600)


class PilotApi:
    def __init__(self, conf, user=None, password=None, **kwargs):
        self.username = user or conf.get('user')
        self.password = password or conf.get('password')
        zeep_settings = Settings(strict=False)
        self.base_url = f'https://www.pilotssl.com/pilotpartnertracking.asmx'
        self.wsdl_url = f'{self.base_url}?WSDL'
        self.session = Session()
        self.adapter = RetryAdapter(max_retries=5, timeout=300)
        self.session.mount('https://', self.adapter)
        self.transport = SoapTransport(session=self.session)

        # for debugging raw xml envelopes
        self._history = None
        self._enable_history = conf.get('history')
        plugins = None
        if self._enable_history:
            self._history = HistoryPlugin()
            plugins = [self._history, ]

        self.client = Client(
            self.wsdl_url, transport=self.transport,
            settings=zeep_settings, plugins=plugins)

    @property
    def factory(self):
        return self.client.type_factory('https://www.pilotssl.com')

    def validation(self):
        return self.factory.PilotTrackingRequestValidation(
            UserID=self.username,
            Password=self.password)

    @property
    def service(self):
        return self.client.service

    def hello(self):
        return self.service.HelloWorld()

    def raw_track(self, tracking_number):
        tr = self.factory.PilotTrackingRequest(
            Validation=self.validation(),
            APIVersion=1.0,
        )
        tr.TrackingNumber.append(tracking_number)
        return self.service.PilotAPITracking(tr=tr)

