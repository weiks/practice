import logging
import platform
import os

from twilio.exceptions import TwilioException
from twilio.rest.resources import Connection
from twilio.rest.resources import UNSET_TIMEOUT
from twilio.rest.resources import make_request
from twilio.version import __version__ as LIBRARY_VERSION


def find_credentials(environ=None):
    """
    Look in the current environment for Twilio credentials

    :param environ: the environment to check
    """
    environment = environ or os.environ
    try:
        account = environment["TWILIO_ACCOUNT_SID"]
        token = environment["TWILIO_AUTH_TOKEN"]
        return account, token
    except KeyError:
        return None, None


def set_twilio_proxy(proxy_url, proxy_port):
    Connection.set_proxy_info(proxy_url, proxy_port)


class TwilioClient(object):
    def __init__(self, account=None, token=None, base="https://api.twilio.com",
                 version="2010-04-01", timeout=UNSET_TIMEOUT,
                 request_account=None):
        """
        Create a Twilio API client.
        """

        # Get account credentials
        if not account or not token:
            account, token = find_credentials()
            if not account or not token:
                raise TwilioException("""
Twilio could not find your account credentials. Pass them into the
TwilioRestClient constructor like this:

    client = TwilioRestClient(account='AC38135355602040856210245275870',
                              token='2flnf5tdp7so0lmfdu3d')

Or, add your credentials to your shell environment. From the terminal, run

    echo "export TWILIO_ACCOUNT_SID=AC3813535560204085626521" >> ~/.bashrc
    echo "export TWILIO_AUTH_TOKEN=2flnf5tdp7so0lmfdu3d7wod" >> ~/.bashrc

and be sure to replace the values for the Account SID and auth token with the
values from your Twilio Account at https://www.twilio.com/user/account.
""")
        self.base = base
        self.auth = (account, token)
        self.timeout = timeout
        req_account = request_account if request_account else account
        self.account_uri = "{0}/{1}/Accounts/{2}".format(base,
                                                         version, req_account)

    def request(self, path, method=None, vars=None):
        """sends a request and gets a response from the Twilio REST API

        .. deprecated:: 3.0

        :param path: the URL (relative to the endpoint URL, after the /v1
        :param url: the HTTP method to use, defaults to POST
        :param vars: for POST or PUT, a dict of data to send

        :returns: Twilio response in XML or raises an exception on error
        :raises: a :exc:`ValueError` if the path is invalid
        :raises: a :exc:`NotImplementedError` if the method is unknown

        This method is only included for backwards compatability reasons.
        It will be removed in a future version
        """
        logging.warning(":meth:`TwilioRestClient.request` is deprecated and "
                        "will be removed in a future version")

        vars = vars or {}
        params = None
        data = None

        if not path or len(path) < 1:
            raise ValueError('Invalid path parameter')
        if method and method not in ['GET', 'POST', 'DELETE', 'PUT']:
            raise NotImplementedError(
                'HTTP %s method not implemented' % method)

        if path[0] == '/':
            uri = self.base + path
        else:
            uri = self.base + '/' + path

        if method == "GET":
            params = vars
        elif method == "POST" or method == "PUT":
            data = vars

        user_agent = "twilio-python %s (python-%s)" % (
            LIBRARY_VERSION,
            platform.python_version(),
        )

        headers = {
            "User-Agent": user_agent,
            "Accept-Charset": "utf-8",
        }

        resp = make_request(method, uri, auth=self.auth, data=data,
                            params=params, headers=headers)

        return resp.content
from twilio.rest.base import TwilioClient
from twilio.rest.resources import (
    UNSET_TIMEOUT,
    Accounts,
    Addresses,
    Applications,
    AuthorizedConnectApps,
    CallFeedback,
    CallFeedbackFactory,
    CallerIds,
    Calls,
    Conferences,
    ConnectApps,
    DependentPhoneNumbers,
    Keys,
    MediaList,
    Members,
    Messages,
    Notifications,
    Participants,
    PhoneNumbers,
    Queues,
    Recordings,
    Sandboxes,
    Sip,
    Sms,
    Tokens,
    Transcriptions,
    Usage,
)


class TwilioRestClient(TwilioClient):
    """
    A client for accessing the Twilio REST API

    :param str account: Your Account SID from `your dashboard
        <https://twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None, base="https://api.twilio.com",
                 version="2010-04-01", timeout=UNSET_TIMEOUT,
                 request_account=None):
        """
        Create a Twilio REST API client.
        """
        super(TwilioRestClient, self).__init__(account, token, base, version,
                                               timeout, request_account)

        version_uri = "%s/%s" % (base, version)

        self.accounts = Accounts(version_uri, self.auth, timeout)
        self.applications = Applications(self.account_uri, self.auth, timeout)
        self.authorized_connect_apps = AuthorizedConnectApps(
            self.account_uri,
            self.auth,
            timeout
        )
        self.addresses = Addresses(self.account_uri, self.auth, timeout)
        self.calls = Calls(self.account_uri, self.auth, timeout)
        self.caller_ids = CallerIds(self.account_uri, self.auth, timeout)
        self.connect_apps = ConnectApps(self.account_uri, self.auth, timeout)
        self.notifications = Notifications(self.account_uri, self.auth,
                                           timeout)
        self.recordings = Recordings(self.account_uri, self.auth, timeout)
        self.transcriptions = Transcriptions(self.account_uri, self.auth,
                                             timeout)
        self.sms = Sms(self.account_uri, self.auth, timeout)
        self.phone_numbers = PhoneNumbers(self.account_uri, self.auth, timeout)
        self.conferences = Conferences(self.account_uri, self.auth, timeout)
        self.queues = Queues(self.account_uri, self.auth, timeout)
        self.sandboxes = Sandboxes(self.account_uri, self.auth, timeout)
        self.usage = Usage(self.account_uri, self.auth, timeout)
        self.messages = Messages(self.account_uri, self.auth, timeout)
        self.media = MediaList(self.account_uri, self.auth, timeout)
        self.sip = Sip(self.account_uri, self.auth, timeout)
        self.tokens = Tokens(self.account_uri, self.auth, timeout)
        self.keys = Keys(self.account_uri, self.auth, timeout)

    def participants(self, conference_sid):
        """
        Return a :class:`~twilio.rest.resources.Participants` instance for the
        :class:`~twilio.rest.resources.Conference` with given conference_sid
        """
        base_uri = "%s/Conferences/%s" % (self.account_uri, conference_sid)
        return Participants(base_uri, self.auth, self.timeout)

    def members(self, queue_sid):
        """
        Return a :class:`Members <twilio.rest.resources.Members>` instance for
        the :class:`Queue <twilio.rest.resources.Queue>` with the
        given queue_sid
        """
        base_uri = "%s/Queues/%s" % (self.account_uri, queue_sid)
        return Members(base_uri, self.auth, self.timeout)

    def feedback(self, call_sid):
        """
        Return a :class:`CallFeedback <twilio.rest.resources.CallFeedback>`
        instance for the :class:`Call <twilio.rest.resources.calls.Call>`
        with the given call_sid
        """
        base_uri = "%s/Calls/%s/Feedback" % (self.account_uri, call_sid)
        call_feedback_list = CallFeedbackFactory(
            base_uri,
            self.auth,
            self.timeout
        )
        return CallFeedback(call_feedback_list)

    def dependent_phone_numbers(self, address_sid):
        """
        Return a :class:`DependentPhoneNumbers
        <twilio.rest.resources.DependentPhoneNumbers>` instance for the
        :class:`Address <twilio.rest.resources.Address>` with the given
        address_sid
        """
        base_uri = "%s/Addresses/%s" % (self.account_uri, address_sid)
        return DependentPhoneNumbers(base_uri, self.auth, self.timeout)
# -*- coding: utf-8 -*-
import sys

from six import u

# Backwards compatibility.
from ..version import __version__, __version_info__

from ..exceptions import TwilioException


class TwilioRestException(TwilioException):
    """ A generic 400 or 500 level exception from the Twilio API

    :param int status: the HTTP status that was returned for the exception
    :param str uri: The URI that caused the exception
    :param str msg: A human-readable message for the error
    :param str method: The HTTP method used to make the request
    :param int|None code: A Twilio-specific error code for the error. This is
         not available for all errors.
    """

    def __init__(self, status, uri, msg="", code=None, method='GET'):
        self.uri = uri
        self.status = status
        self.msg = msg
        self.code = code
        self.method = method

    def __str__(self):
        """ Try to pretty-print the exception, if this is going on screen. """

        def red(words):
            return u("\033[31m\033[49m%s\033[0m") % words

        def white(words):
            return u("\033[37m\033[49m%s\033[0m") % words

        def blue(words):
            return u("\033[34m\033[49m%s\033[0m") % words

        def teal(words):
            return u("\033[36m\033[49m%s\033[0m") % words

        def get_uri(code):
            return "https://www.twilio.com/docs/errors/{0}".format(code)

        # If it makes sense to print a human readable error message, try to
        # do it. The one problem is that someone might catch this error and
        # try to display the message from it to an end user.
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            msg = (
                "\n{red_error} {request_was}\n\n{http_line}"
                "\n\n{twilio_returned}\n\n{message}\n".format(
                    red_error=red("HTTP Error"),
                    request_was=white("Your request was:"),
                    http_line=teal("%s %s" % (self.method, self.uri)),
                    twilio_returned=white(
                        "Twilio returned the following information:"),
                    message=blue(str(self.msg))
                ))
            if self.code:
                msg = "".join([msg, "\n{more_info}\n\n{uri}\n\n".format(
                    more_info=white("More information may be available here:"),
                    uri=blue(get_uri(self.code))),
                ])
            return msg
        else:
            return "HTTP {0} error: {1}".format(self.status, self.msg)
from .base import set_twilio_proxy
from .client import TwilioRestClient
from .ip_messaging import TwilioIpMessagingClient
from .lookups import TwilioLookupsClient
from .pricing import TwilioPricingClient
from .task_router import TwilioTaskRouterClient
from .trunking import TwilioTrunkingClient

_hush_pyflakes = [set_twilio_proxy, TwilioRestClient, TwilioIpMessagingClient,
                  TwilioLookupsClient, TwilioPricingClient,
                  TwilioTaskRouterClient, TwilioTrunkingClient]
from twilio.rest.base import TwilioClient
from twilio.rest.resources import UNSET_TIMEOUT
from twilio.rest.resources.ip_messaging.services import Services
from twilio.rest.resources.ip_messaging.credentials import Credentials


class TwilioIpMessagingClient(TwilioClient):
    """
    A client for accessing the Twilio IP Messaging API.

    The Twilio IP Messaging API provides information about events. For more
    information, see the
    `IP Messaging API documentation <https://www.twilio.com/docs/XXX>`_.

    :param str account: Your Account Sid from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://ip-messaging.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):

        super(TwilioIpMessagingClient, self).__init__(account, token, base,
                                                      version, timeout,
                                                      request_account)

        self.version_uri = "%s/%s" % (base, version)
        self.services = Services(self.version_uri, self.auth, timeout)
        self.credentials = Credentials(self.version_uri, self.auth, timeout)
from twilio.rest.base import TwilioClient
from twilio.rest.resources import UNSET_TIMEOUT
from twilio.rest.resources.lookups.phone_numbers import PhoneNumbers


class TwilioLookupsClient(TwilioClient):
    """
    A client for accessing the Twilio Lookups API.

    The Twilio Lookups API provides information about phone numbers,
    including non-Twilio numbers. For more information, see the
    `Lookups API documentation <https://www.twilio.com/docs/XXX>`_.

    :param str account: Your Account Sid from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://lookups.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):

        super(TwilioLookupsClient, self).__init__(account, token, base,
                                                  version, timeout,
                                                  request_account)

        self.version_uri = "%s/%s" % (base, version)
        self.phone_numbers = PhoneNumbers(self.version_uri, self.auth, timeout)
from twilio.rest.base import TwilioClient
from twilio.rest.resources import UNSET_TIMEOUT
from twilio.rest.resources.monitor.alerts import Alerts
from twilio.rest.resources.monitor.events import Events


class TwilioMonitorClient(TwilioClient):
    """
    A client for accessing the Twilio Monitor API.

    The Twilio Monitor API provides information about events. For more
    information, see the
    `Monitor API documentation <https://www.twilio.com/docs/XXX>`_.

    :param str account: Your Account Sid from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://www.twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://monitor.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):

        super(TwilioMonitorClient, self).__init__(account, token, base,
                                                  version, timeout,
                                                  request_account)

        self.version_uri = "%s/%s" % (base, version)
        self.events = Events(self.version_uri, self.auth, timeout)
        self.alerts = Alerts(self.version_uri, self.auth, timeout)
from twilio.rest.base import TwilioClient
from twilio.rest.resources import UNSET_TIMEOUT
from twilio.rest.resources.pricing import (
    PhoneNumbers,
    Voice,
    MessagingCountries,
)


class TwilioPricingClient(TwilioClient):
    """
    A client for accessing the Twilio Pricing API.

    :param str account: Your Account SID from `your dashboard
        <https://twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://twilio.com/user_account>`_
    :param float timeout: The socket connect and read timeout for requests
    to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://pricing.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):
        super(TwilioPricingClient, self).__init__(account, token, base,
                                                  version, timeout,
                                                  request_account)

        self.uri_base = "{}/{}".format(base, version)

        self.voice = Voice(self.uri_base, self.auth, self.timeout)
        self.phone_numbers = PhoneNumbers(self.uri_base, self.auth,
                                          self.timeout)

    def messaging_countries(self):
        """
        Returns a :class:`MessagingCountries` resource
        :return: MessagingCountries
        """
        messaging_countries_uri = "{0}/Messaging".format(
            self.uri_base)
        return MessagingCountries(messaging_countries_uri, self.auth,
                                  self.timeout)
from twilio.rest.base import TwilioClient
from twilio.rest.resources import (
    UNSET_TIMEOUT,
    Activities,
    Events,
    Reservations,
    TaskQueues,
    Tasks,
    Workers,
    Workflows,
    Workspaces,
)


class TwilioTaskRouterClient(TwilioClient):
    """
    A client for accessing the Twilio TaskRouter API

    :param str account: Your Account SID from `your dashboard
        <https://twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://taskrouter.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):
        """
        Create a Twilio REST API client.
        """
        super(TwilioTaskRouterClient, self).__init__(account, token, base,
                                                     version, timeout,
                                                     request_account)
        self.base_uri = "{0}/{1}".format(base, version)
        self.workspace_uri = "{0}/Workspaces".format(self.base_uri)

        self.workspaces = Workspaces(self.base_uri, self.auth, timeout)

    def activities(self, workspace_sid):
        """
        Return a :class:`Activities` instance for the :class:`Activity`
        with the given workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return Activities(base_uri, self.auth, self.timeout)

    def events(self, workspace_sid):
        """
        Return a :class:`Events` instance for the :class:`Event` with the given
        workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return Events(base_uri, self.auth, self.timeout)

    def reservations(self, workspace_sid, task_sid):
        """
        Return a :class:`Reservations` instance for the :class:`Reservation`
        with the given workspace_sid ans task_sid
        """
        base_uri = "{0}/{1}/Tasks/{2}".format(self.workspace_uri,
                                              workspace_sid, task_sid)
        return Reservations(base_uri, self.auth, self.timeout)

    def worker_reservations(self, workspace_sid, worker_sid):
        """
        Return a :class:`Reservations` instance for the :class:`Reservation`
        with the given workspace_sid ans worker_sid
        """
        base_uri = "{0}/{1}/Workers/{2}".format(self.workspace_uri,
                                                workspace_sid, worker_sid)
        return Reservations(base_uri, self.auth, self.timeout)

    def task_queues(self, workspace_sid):
        """
        Return a :class:`TaskQueues` instance for the :class:`TaskQueue` with
        the given workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return TaskQueues(base_uri, self.auth, self.timeout)

    def tasks(self, workspace_sid):
        """
        Return a :class:`Tasks` instance for the :class:`Task` with the given
        workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return Tasks(base_uri, self.auth, self.timeout)

    def workers(self, workspace_sid):
        """
        Return a :class:`Workers` instance for the :class:`Worker` with the
        given workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return Workers(base_uri, self.auth, self.timeout)

    def workflows(self, workspace_sid):
        """
        Return a :class:`Workflows` instance for the :class:`Workflow` with the
        given workspace_sid
        """
        base_uri = "{0}/{1}".format(self.workspace_uri, workspace_sid)
        return Workflows(base_uri, self.auth, self.timeout)
from twilio.rest import TwilioRestClient

account_sid = "AC3e783a500263a689cc4c417ccc79ad26" # Your Account SID from www.twilio.com/console
auth_token  = "ecf74a6c2cf79ac2cf57b3601eece109"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+6504693457",    # Replace with your phone number
    from_="+9179333551") # Replace with your Twilio number

print(message.sid)
from twilio.rest.base import TwilioClient
from twilio.rest.resources.trunking import (
    CredentialLists,
    IpAccessControlLists,
    OriginationUrls,
    PhoneNumbers,
    Trunks
)
from twilio.rest.resources import UNSET_TIMEOUT


class TwilioTrunkingClient(TwilioClient):
    """
    A client for accessing the Twilio Trunking API

    :param str account: Your Account SID from `your dashboard
        <https://twilio.com/user/account>`_
    :param str token: Your Auth Token from `your dashboard
        <https://twilio.com/user/account>`_
    :param float timeout: The socket and read timeout for requests to Twilio
    """

    def __init__(self, account=None, token=None,
                 base="https://trunking.twilio.com", version="v1",
                 timeout=UNSET_TIMEOUT, request_account=None):
        """
        Create a Twilio REST API client.
        """
        super(TwilioTrunkingClient, self).__init__(account, token, base,
                                                   version, timeout,
                                                   request_account)
        self.trunk_base_uri = "{0}/{1}".format(base, version)

    def credential_lists(self, trunk_sid):
        """
        Return a :class:`CredentialList` instance
        """
        credential_lists_uri = "{0}/Trunks/{1}".format(
            self.trunk_base_uri, trunk_sid)
        return CredentialLists(credential_lists_uri, self.auth, self.timeout)

    def ip_access_control_lists(self, trunk_sid):
        """
        Return a :class:`IpAccessControlList` instance
        """
        ip_access_control_lists_uri = "{0}/Trunks/{1}".format(
            self.trunk_base_uri, trunk_sid)
        return IpAccessControlLists(ip_access_control_lists_uri, self.auth,
                                    self.timeout)

    def origination_urls(self, trunk_sid):
        """
        Return a :class:`OriginationUrls` instance
        """
        origination_urls_uri = "{0}/Trunks/{1}".format(
            self.trunk_base_uri, trunk_sid)
        return OriginationUrls(origination_urls_uri, self.auth, self.timeout)

    def phone_numbers(self, trunk_sid):
        """
        Return a :class:`PhoneNumbers` instance
        """
        phone_numbers_uri = "{0}/Trunks/{1}".format(self.trunk_base_uri,
                                                    trunk_sid)
        return PhoneNumbers(phone_numbers_uri, self.auth, self.timeout)

    def trunks(self):
        """
        Return a :class:`Trunks` instance
        """
        return Trunks(self.trunk_base_uri, self.auth, self.timeout)
