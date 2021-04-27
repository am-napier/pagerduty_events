#   Version 8.1.1
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure te alert action for PagerDuty.  The TA writes to the PagerDuty
# events API (v2).   Details for values passed are described in
# https://developer.pagerduty.com/docs/events-api-v2/trigger-events/
# Note that the TA will use the values passed:
# first as tags to extract from the message
# then as static values
# and finally if niether yield a result it will fall back to the values
# defined in the alert_actions.conf

[pagerduty_events]
param.pd_url = <string>
* (Optional) The url called by the TA.  To execute an update/resolve specify
  ...v2/change/enqueue
* Default: https://events.pagerduty.com/v2/enqueue

param.pd_key = <string>
* (Required) The integration key for either the service or the the
* account wide value.  Default behaviour is to create suppressed alert
* when the account wide key is used
* Default: pd_key

param.pd_dedup_key = <string>
* (Optional) Used to deduplicate on the PagerDuty side.  Repeated
* alerts carrying this value will not create new incidents
* Default: pd_dedup_key

param.pd_source = <string>
* (Required) The object about which this alert is being raised
*
* Default: pd_source

param.pd_summary = <string>
* (Required) The short description of the problem, < 1024 chars
*
* Default: pd_summary

param.pd_severity = <string>
* (Required) One of the ket PagerDuty values
* critical, error, warning or info
*
* Default: pd_severity

param.pd_link_text = <string>
* (Optional) Ordered list of names for the link hrefs supplied
* These will be displayed as hyperlinks in PagerDuty
* Must match the number
* Default: pd_link_text

param.pd_link_href = <string>
* (Optional) Ordered list of hyperlinks for this event
* See link_text
* Default: pd_link_href

param.pd_class = <string>
* (Optional) Class of the event
* Default: pd_class

param.pd_component = <string>
* (Optional) Component is the parameter, eg CPU on host X
* CPU is the component to the source 'host X'
* Default: pd_component

param.pd_group = <string>
* (Optional) Major grouping, ie application/service
* Default: pd_group
