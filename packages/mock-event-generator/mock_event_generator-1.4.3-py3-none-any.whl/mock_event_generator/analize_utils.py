"""Utility to analize S-events.

From ...
"""

import re
from datetime import datetime
from typing import Any

import numpy as np
from astropy.time import Time


class FarThresholds:
    """Class that define the threshould for alerts.

    The value are determined by the ``thresholds`` static dictionary.
    """

    one_day = 1 / 3600 / 24
    one_month = 1 / 3600 / 24 / 30
    one_year = 1 / 3600 / 24 / 365
    thresholds_cbc = 2 * one_day
    thresholds_burst = 2 * one_day
    thresholds: dict[tuple[str, str, str], tuple[float, float]] = {
        # CBC AllSKy searches
        ('cbc', 'mbta', 'allsky'): (2 * one_day, one_month / 6),
        ('cbc', 'gstlal', 'allsky'): (2 * one_day, one_month / 6),
        ('cbc', 'pycbc', 'allsky'): (2 * one_day, one_month / 6),
        ('cbc', 'spiir', 'allsky'): (2 * one_day, one_month / 6),
        # CBC EarlyWarning searches
        ('cbc', 'mbta', 'earlywarning'): (one_month, one_month / 6),
        ('cbc', 'gstlal', 'earlywarning'): (one_month, one_month / 6),
        ('cbc', 'pycbc', 'earlywarning'): (one_month, one_month / 6),
        ('cbc', 'spiir', 'earlywarning'): (one_month, one_month / 6),
        # CBC SSM searches
        ('cbc', 'mbta', 'ssm'): (one_month / 6, one_year / 4),
        ('cbc', 'gstlal', 'ssm'): (one_month / 6, one_year / 4),
        # BURST BBH searches
        ('burst', 'cwb', 'bbh'): (one_month, one_month / 6),
        # BURST AllSky searches
        ('burst', 'cwb', 'allsky'): (one_month / 6, one_year / 4),
        ('burst', 'olib', 'allsky'): (one_month / 6, one_year / 4),
    }

    def get(self, group: str, pipeline: str, search: str) -> float:
        """Method that return the far threshould for generating alerts.

        Parameters
        ----------
        group : str
        pipeline : str
        search : str

        Returns
        -------
        far : float
        """
        return self.thresholds.get((group, pipeline, search), (0.0, 0.0))[0]

    def significant(self, group: str, pipeline: str, search: str) -> float:
        """Method that return the far threshould for significant alerts.

        Parameters
        ----------
        group : str
        pipeline : str
        search : str

        Returns
        -------
        far : float
        """
        return self.thresholds.get((group, pipeline, search), (0.0, 0.0))[1]


alert_far_thresholds = FarThresholds()


def is_significant(event: dict[str, Any]) -> bool:
    """Determine whether an event should be considered a significant event.

    All of the following conditions must be true for a public alert:

    *   The event's ``offline`` flag is not set.
    *   The event's is not an injection.
    *   The event's false alarm rate is less than or equal to
        :obj:`~gwcelery.conf.alert_far_thresholds`

    or the event has been marked to generate a RAVEN alert.

    Parameters
    ----------
    event : dict
        Event dictionary (e.g., the return value from
        :meth:`gwcelery.tasks.gracedb.get_event`, or
        ``preferred_event_data`` in igwn-alert packet.)

    Returns
    -------
    _is_significant : bool
        :obj:`True` if the event meets the criteria for a signifincat alert.
        :obj:`False` if it does not.

    """
    ev_group = event.get('group', '').lower()
    ev_pipeline = event.get('pipeline', '').lower()
    ev_search = event.get('search', '').lower()
    ev_far = event.get('far', 0.0)
    far_threshold = alert_far_thresholds.significant(ev_group, ev_pipeline, ev_search)
    _is_significant = (
        (not event['offline'])
        and ('INJ' not in event['labels'])
        and (ev_far < far_threshold)
    ) or ('RAVEN_ALERT' in event['labels'])

    return _is_significant


def should_publish(event: dict[str, Any]) -> bool:
    """Determine whether an event should be published as a public alert.

    All of the following conditions must be true for a public alert:

    *   The event's ``offline`` flag is not set.
    *   The event's is not an injection.
    *   The event's false alarm rate is less than or equal to
        :obj:`~gwcelery.conf.alert_far_thresholds`

    or the event has been marked to generate a RAVEN alert.

    Parameters
    ----------
    event : dict
        Event dictionary (e.g., the return value from
        :meth:`gwcelery.tasks.gracedb.get_event`, or
        ``preferred_event_data`` in igwn-alert packet.)

    Returns
    -------
    should_publish : bool
        :obj:`True` if the event meets the criteria for a public alert or
        :obj:`False` if it does not.

    """
    ev_group = event.get('group', '').lower()
    ev_pipeline = event.get('pipeline', '').lower()
    ev_search = event.get('search', '').lower()
    ev_far = event.get('far', 0.0)
    far_threshold = alert_far_thresholds.get(ev_group, ev_pipeline, ev_search)
    _should_publish = (
        (not event['offline'])
        and ('INJ' not in event['labels'])
        and (ev_far < far_threshold)
    ) or ('RAVEN_ALERT' in event['labels'])

    return _should_publish


def _convert_created(timestr: str) -> datetime:
    return datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S UTC')


def AnalizeLogsSuperEvents(
    LOGS: list[Any], t0: float = 0.0
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Analize the logs of a supervent to find out labels and alerts.

    Returns:
    - history_properties: list of (time-t0 , object)
       'initial'  : Event that create the super-event
       'added'    : Hystory of added event
       'prefered' : Hystory of prefered event changes
       'labels'   : History of the applyed labels
       'rlabels'  : History of the removes labels
    - history_alerts: list of (time-t0, kind ,filename, version)
       'xml'      : alerts as VO event
       'avro'     : alerts as avro over kafka to SCiMMA
       'json'     : alerts as json over kafka to GCN
       'txt'      : alerts as email text
    - history_dataproducts: list of (time-t0, kind ,filename, version)
       'multiorder' : multiorder skymap (*.multiorder.fits)
       'p_astro'    : p_astro data (*.pastro.json)
       'em_bright'  : em_bright data (*em_bright.json)
       'gwskynet'   : gwskynet annotation ()
       # Auxiliary data products (not in alerts)
       'flatten'    : flattened skymap (*.fits.gz)
    """
    history_properties: dict[str, Any] = dict()
    history_alerts: dict[str, Any] = dict()
    history_dataproducts: dict[str, Any] = dict()

    comment_match = {
        'prefered': re.compile('.*preferred_event: \\S\\d* -> (\\S\\d*).*'),
        'lables': re.compile('Added label: (\\S*)|.*label (\\S*) applied'),
        'rlables': re.compile('.*label (\\S*) removed.*'),
        'added': re.compile('Added event: (\\S*)'),
        'initial': re.compile('Superevent created.*preferred_event=(\\S*)'),
    }
    comments = [log['comment'] for log in LOGS]
    for kind in comment_match:
        history_properties[kind] = []
        for idx, comment in enumerate(comments):
            regout = comment_match[kind].match(comment)
            if regout:
                alert = ''
                for matchvalue in regout.groups():
                    if matchvalue is not None:
                        alert = matchvalue
                alerttime = Time(_convert_created(LOGS[idx]['created'])).gps - t0
                history_properties[kind].append([alerttime, alert, idx])
        # print('KIND --- {}'.format(kind))
        # for data in history_properties[kind]:
        #    print(data)

    alert_match = {
        'xml': re.compile('.*-\\d*-(\\S*).xml'),
        'json': re.compile('\\S\\d\\d\\d\\d\\d\\d\\S*-(\\S*).json'),
        'avro': re.compile('.*-(\\S*).avro'),
        'txt': re.compile('.*-\\d*-(\\S*).txt'),
    }
    fnames = [log['filename'] for log in LOGS]
    for kind in alert_match:
        history_alerts[kind] = []
        for idx, fname in enumerate(fnames):
            regout = alert_match[kind].match(fname)
            if regout:
                alert = regout.group(1)
                alerttime = Time(_convert_created(LOGS[idx]['created'])).gps - t0
                history_alerts[kind].append(
                    [
                        alerttime,
                        alert.lower(),
                        LOGS[idx]['filename'],
                        LOGS[idx]['file_version'],
                        idx,
                    ]
                )

    dataproducts_match = {
        'multiorder': re.compile('.*multiorder.fits'),
        'p_astro': re.compile('.*p_astro.json'),
        'em_bright': re.compile('.*em_bright.json'),
        'gwskynet': re.compile('.*gwskynet.json'),
        # Auxiliary data products (not in alerts)
        'flatten': re.compile('.*fits.gz'),
        'png_p_astro': re.compile('.*p_astro.png'),
        'png_em_bright': re.compile('.*em_bright.png'),
    }
    fnames = [log['filename'] for log in LOGS]
    for kind in dataproducts_match:
        history_dataproducts[kind] = []
        for idx, fname in enumerate(fnames):
            regout = dataproducts_match[kind].match(fnames[idx])
            if regout:
                creation_time = Time(_convert_created(LOGS[idx]['created'])).gps - t0
                history_dataproducts[kind].append(
                    [
                        creation_time,
                        LOGS[idx]['filename'],
                        LOGS[idx]['file_version'],
                        LOGS[idx]['comment'],
                        idx,
                    ]
                )
        # print('KIND --- {}'.format(kind))
        # for data in alerts_properties[kind]:
        #    print(data)

    return history_properties, history_alerts, history_dataproducts


def AnalizePipelinesSEvents(
    sev: dict[str, Any], gevs: dict[str, Any], log: bool = False
) -> tuple[dict[tuple[Any, Any], Any], dict[tuple[Any, Any], Any]]:
    """Analize the the kind of events in a supervent.

    Returns two group dictionary with entry (pipeline,search) containing
    - group_events : the list of G-events in the group
    - group_fars   : the list of FAR of the G-events in the group.
    """
    gw_events = sev['gw_events']
    events_data = [gevs[evid] for evid in gw_events]
    events_far = np.array([ev['far'] for ev in events_data])
    # events_group = np.array([ev['group'] for ev in events_data])
    events_pipeline = np.array([ev['pipeline'] for ev in events_data])
    events_search = np.array([ev['search'] for ev in events_data])
    searches = set(events_search)
    pipelines = set(events_pipeline)
    group_events: dict[tuple[Any, Any], Any] = {}
    group_fars: dict[tuple[Any, Any], Any] = {}
    for search in searches:
        for pipeline in pipelines:
            count = np.where((events_search == search) * (events_pipeline == pipeline))[
                0
            ]
            if len(count) > 0:
                group_events[(pipeline, search)] = list(
                    np.array(sev['gw_events'])[count]
                )
                group_fars[(pipeline, search)] = events_far[count]

    if log:
        print(
            'sev {:10}  FAR {:.4}  #ev={}'.format(
                sev['superevent_id'], sev['far'], len(gw_events)
            )
        )
        print(f'  min FAR {np.min(events_far):6.4} max FAR {np.max(events_far):6.4}')
        for evset in group_events:
            count = group_events[evset]
            print(
                '  --- {:8} {:8} #{:2}  min FAR {:6.4} - {}'.format(
                    evset[0],
                    evset[1],
                    len(count),
                    np.min(group_fars[evset]),
                    group_fars[evset],
                )
            )
    return group_events, group_fars
