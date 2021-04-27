import sys
import json
import time
import re
from datetime import datetime
from splunk.clilib.bundle_paths import make_splunkhome_path
sys.path.append(make_splunkhome_path(['etc', 'apps', 'SA-ITOA', 'lib']))

'''
from ITOA.itoa_config import get_supported_objects
import itsi_path
from itsi_py23 import _
from itsi.event_management.sdk.grouping import EventGroup
from itsi.event_management.sdk.custom_group_action_base import CustomGroupActionBase

Note: while the ITOA libraries are used here for logging only, the plan is
to extend this app to also link back to external tickets integration at a later stage.
At that point these libraries will be required therefore the ITOA logging has been used in
anticipation of that change.
'''
import logging
from ITOA.setup_logging import getLogger
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse


if sys.version < '3':
    from ConfigParser import ConfigParser
    from StringIO import StringIO
else:
    from configparser import ConfigParser
    from io import StringIO

# compile this once then reuse
TOKEN_RE = re.compile("^%(.+)%$")

def get_property(config, result, tag):
    '''
    The tag is the name of a property that must resolve to the string value to pass to PagerDuty.
    tag yields a token from config.
    If the token is bounded by % signs it represents a search field
    that will be extracted from result.
    If the token is not found in config we attempt to get it from result
    If the token is a literal value (not bounded by % signs) it is used as is.
    :param config: dict, the payload configuration object
    :param result: dict, the search result row
    :param tag: string, the tag we are searching for
    :return: string or None
    '''
    # token could be empty, a token like '%my_key%' or literal value '01abc..32'
    token = config.get(tag).strip()
    if token is None or len(token)==0:
        # try and get the value from result, its OK if this is None, caller will handle it
        return result.get(tag)

    # is the value a token?
    match = TOKEN_RE.match(token)
    if match:
        # yes its a token so try to get the token value ie 'my_key' from result
        return result.get(match.group(1))
    # lastly its a literal value
    return token

def execute(payload):
    '''

    :param payload:
    :return: 0 success,
    1 - Error processing API call
    2
    3 - missing required args
    4 - insecure URL
    '''
    # conf are the param.<...> properties from alert_actions.conf
    conf = payload.get('configuration')
    result = payload.get("result")

    del payload['session_key'] # make cloud compatible

    logger.info("Input Params are %s" % json.dumps(payload, indent=4))
    url = get_property(conf, result, "pd_url")
    if url is None or len(url)==0:
        url = "https://events.pagerduty.com/v2/enqueue"
    elif not url.startswith('https://'):
        logger.error("Possible insecure network communication")
        return 4

    links = [{"href": get_property(conf, result, "pd_link_href"),
              "text": get_property(conf, result, "pd_link_text")}]
    body = {
        "event_action":"trigger",
        # while routing key looks like a secret it is not and must be present in the payload for the integration to work
        "routing_key": get_property(conf, result, "pd_routing_key"),
        "dedup_key": get_property(conf, result, "pd_dedup_key"),
        "payload": {
            "source": get_property(conf, result, "pd_source"),
            "severity": get_property(conf, result, "pd_severity"),
            "summary": get_property(conf, result, "pd_summary"),
            "class": get_property(conf, result, "pd_class"),
            "component": get_property(conf, result, "pd_component"),
            "group": get_property(conf, result, "pd_group"),
            "custom_details": result
        }
    }
    # improve this test and allow for multiple links
    if links[0]["href"] is not None and links[0]["text"] is not None:
        body['links'] = links
    else:
        logger.warn("Verify links are as expected, they look incorrect or missing %s " % str(links))

    try:
        timestamp = get_property(conf, result, "pd_timestamp")
        body["payload"]["timestamp"] = datetime.fromtimestamp(int(float(timestamp))).isoformat()
    except Exception as e:
        logger.warn("Can't parse timestamp %s as iso-8601 date: %s" % (timestamp, str(e)))

    def check_usage(obj, key):
        if obj[key] is None:
            logger.error("No value provided for '%s', review search results " % key)
            return True
        return False

    # make sure required properties have been set
    if (check_usage(body, "routing_key") or check_usage(body["payload"], "source")
            or check_usage(body["payload"], "severity") or check_usage(body["payload"], "summary")):
        return 3

    logger.info('Output Params are url="%s" body=%s' % (url, json.dumps(body, indent=4)))

    body = json.dumps(body).encode('utf-8')

    req = six.moves.urllib.request.Request(url, body, {"Content-Type": "application/json"})
    try:
        res = six.moves.urllib.request.urlopen(req)
        response = res.read()
        logger.info("PagerDuty HTTP status=%d, response: %s" % (res.code, response))
        return 0

    except six.moves.urllib.error.HTTPError as e:
        logger.error("Error message: %s (%s)" % (e, str(dir(e))))
        logger.error("Server response: %s" % e.read())
        return 1


if __name__ == "__main__":
    logger = getLogger(logger_name="pagerduty.event_api_v2", level=logging.INFO)
    start = time.time()
    logger.warn("PagerDuty API call starts")
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        rc = execute(payload)
    else:
        logger.error("no --execute? WTF!")
        rc = 2
    logger.info("PagerDuty API call ends in: %f secs, return code:%d" % (time.time()-start, rc))
    sys.exit(rc)