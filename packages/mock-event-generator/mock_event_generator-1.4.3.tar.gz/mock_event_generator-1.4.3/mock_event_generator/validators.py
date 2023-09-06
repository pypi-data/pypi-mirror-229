"""Classes for G-event and S-event validation."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt  # type: ignore[attr-defined]
import numpy as np
from matplotlib import colormaps  # type: ignore[attr-defined]

from .analize_utils import (
    AnalizeLogsSuperEvents,
    AnalizePipelinesSEvents,
    is_significant,
    should_publish,
)
from .cache import GEventCacheEntry, SEventCacheEntry
from .exceptions import MEGValidationFailed
from .gracedbs import GraceDBWithContext

logger = logging.getLogger(__name__)

FILES_CHECKLIST = [
    'bayestar.multiorder.fits',
    'bayestar.fits.gz',
    'bayestar.png',
    'bayestar.html',
    '{}.p_astro.json',
    '{}.p_astro.png',
    'em_bright.json',
    'em_bright.png',
]

LABELS_CHECKLIST = ['EMBRIGHT_READY', 'GCN_PRELIM_SENT', 'PASTRO_READY', 'SKYMAP_READY']

ADV_LABELS = ['ADVNO', 'ADVOK', 'ADVREQ']


class SEventValidator(SEventCacheEntry):
    """Class used to validate a cached S-event."""

    datetime_format = '%Y-%m-%d %H:%M:%S %Z'
    cmap = colormaps['tab10']
    data_template = {'found': False, 'time': 'never', 'latency': 9999.0}

    @classmethod
    def from_sevent_id(
        cls,
        sevent_id: str,
        source: GraceDBWithContext,
        disabled: bool,
        cache_path: Path,
    ) -> SEventValidator:
        """Init from S-event id.

        Fetches S-event and returns a validator instance.

        Parameters:
            sevent_id: The S-event GraceDB identifier.
            source: The GraceDB instance name from which events are downloaded,
                such as `production` or `playground`.
            disabled: If true, bypass the cache and always download the event
                data files.
            cache_path: The top-level path of the cache.
        """
        SEventCacheEntry.from_id(sevent_id, source, disabled, cache_path)

        return SEventValidator(cache_path / sevent_id)

    @classmethod
    def from_gevent_id(
        cls,
        gevent_id: str,
        source: GraceDBWithContext,
        disabled: bool,
        cache_path: Path,
    ) -> SEventValidator:
        """Init from G-event id.

        Fetches G-event info, queries for S-events in the corresponding
        search and returns a validator instance for the S-event associated to
        the input G-event.

        Parameters:
            gevent_id: The G-event GraceDB identifier.
            source: The GraceDB instance name from which events are downloaded,
                such as `production` or `playground`.
            disabled: If true, bypass the cache and always download the event
                data files.
            cache_path: The top-level path of the cache.

        Raises:
            RuntimeError: When the input G-event does not have ans associated
                S-event.
        """
        gevent_data = GEventCacheEntry.from_id(
            gevent_id, source, disabled, cache_path
        ).get_description()
        sevent_id = gevent_data.superevent

        return SEventValidator.from_sevent_id(sevent_id, source, disabled, cache_path)

    def validate(self, save_plot_to: Path | None) -> None:
        """Superevent validation method.

        Get S-event description, recover labels and file info,
        validate and produce a plot.

        Raises:
            RuntimeError: When the validation fails.
        """
        self.sevent_data = self.get_description().sevent_data
        self.sevent_id = self.sevent_data['sevent']['superevent_id']
        self.t_0 = self.sevent_data['sevent']['t_0']
        self.sub_time = datetime.strptime(
            self.sevent_data['sevent']['created'], self.datetime_format
        )
        logger.info(f'Validating {self.sevent_id} submitted {str(self.sub_time)}')

        # Get history of S-event
        history_data = AnalizeLogsSuperEvents(self.sevent_data['logs']['log'], self.t_0)
        self.history_properties = history_data[0]
        self.history_alerts = history_data[1]
        self.history_dataproducts = history_data[2]
        # Get properties G-events and groups
        self.group_events, self.group_fars = AnalizePipelinesSEvents(
            self.sevent_data['sevent'], self.sevent_data['gevents'], log=False
        )

        self.sev_values = self.sevent_data['sevent']
        self.gev_values = self.sevent_data['sevent']['preferred_event_data']
        self.group = self.gev_values['group'].lower()
        self.pipeline = self.gev_values['pipeline'].lower()
        self.search = self.gev_values['search'].lower()
        self.superevent_id = self.sev_values['superevent_id']
        self.is_significant = is_significant(self.gev_values)
        self.should_publish = should_publish(self.gev_values)

        # #################################
        # Perform validation checks
        # #################################
        self.labels_dict = self._get_labels()
        self.files_dict = self._get_files()

        adv_ok = self._validate_advocate() if self.is_significant else True
        labels_ok = self._validate_labels() if self.should_publish else True
        files_ok = self._validate_files() if self.should_publish else True

        if not save_plot_to:
            save_plot_to = self.path
        self._save_analize_sev_history(save_plot_to)
        self._save_data(save_plot_to)
        self._plot(save_plot_to)

        if not all([labels_ok, adv_ok, files_ok]):
            err_str = f'Validation failed for S-event {self.sevent_id}\n'
            if not labels_ok:
                err_str += 'Missing labels:'
                for key in LABELS_CHECKLIST:
                    if not self.labels_dict[key]['found']:
                        err_str += f' {key}'
                err_str += '\n'
            if not adv_ok:
                err_str += 'Missing ADV label (either ADVOK / ADVNO).\n'
            if not files_ok:
                err_str += 'Missing files:'
                for key in self.files_dict:
                    if not self.files_dict[key]['found']:
                        err_str += f' {key}'

            raise MEGValidationFailed(err_str)

    def _get_labels(self) -> dict[str, Any]:
        """Load labels info into a dictionary."""
        logs = self.sevent_data['labels']
        labels_dict = {
            key: self.data_template.copy() for key in LABELS_CHECKLIST + ADV_LABELS
        }
        for row in logs:
            labelname = row['name']
            log_time = datetime.strptime(row['created'], self.datetime_format)
            # logger.info(f'Label {labelname} created {str(log_time)}')
            if labelname in LABELS_CHECKLIST + ADV_LABELS:
                labels_dict[labelname]['found'] = True
                labels_dict[labelname]['time'] = str(log_time)
                labels_dict[labelname]['latency'] = (
                    log_time - self.sub_time
                ).total_seconds()

        return labels_dict

    def _get_files(self) -> dict[str, Any]:
        """Load files info into a dictionary."""
        logs = self.sevent_data['logs']['log']
        files_dict = {
            key.format(self.pipeline): self.data_template.copy()
            for key in FILES_CHECKLIST
        }
        for row in logs:
            filename = row['filename']
            log_time = datetime.strptime(row['created'], self.datetime_format)
            if filename:
                pass
                # logger.info(f'File {filename} created {str(log_time)}')
            if filename in files_dict:
                files_dict[filename]['found'] = True
                files_dict[filename]['time'] = str(log_time)
                files_dict[filename]['latency'] = (
                    log_time - self.sub_time
                ).total_seconds()

        return files_dict

    def _validate_labels(self) -> bool:
        """Returns True if all labels are found."""
        labels_created = [self.labels_dict[key]['found'] for key in LABELS_CHECKLIST]

        return all(labels_created)

    def _validate_advocate(self) -> bool:
        """Returns True if advocate label (either ADVOK, ADVNO or ADV_REG) is found."""
        adv_created = [self.labels_dict[key]['found'] for key in ADV_LABELS]

        return any(adv_created)

    def _validate_files(self) -> bool:
        """Returns True if all filenames are found."""
        files_created = [self.files_dict[key]['found'] for key in self.files_dict]

        return all(files_created)

    def _save_data(self, outdir: Path) -> None:
        """Saves latency data to json files..

        Parameters:
            outdir: Output directory.
        """
        data_dict = {
            'sub_time': str(self.sub_time),
            'labels': self.labels_dict,
            'files': self.files_dict,
            'superevent_id': self.sevent_id,
            't_0': self.t_0,
            'history_properties': self.history_properties,
            'history_alerts': self.history_alerts,
            'history_dataproducts': self.history_dataproducts,
            'sev_values': self.sev_values,
            'gev_values': self.gev_values,
        }
        filename = outdir / ('%s_latency_data.json' % str(self.sevent_id))
        with open(filename, 'w') as stream:
            json.dump(data_dict, stream, indent=4)
        logger.info(f'Data saved to {str(filename)}')

    def _plot(self, outdir: Path) -> None:
        """Plots timeline of label and filename creation.

        Parameters:
            outdir: Output directory.
        """
        self._init_figure()
        self._add_entries_to_plot(self.axes[0], self.labels_dict)
        self._add_entries_to_plot(self.axes[1], self.files_dict)

        x_span = (
            self.axes[1].get_xlim()[1]  # type: ignore[attr-defined]
            - self.axes[1].get_xlim()[0]  # type: ignore[attr-defined]
        )  # type: ignore[attr-defined]
        self.axes[1].set_xlim(  # type: ignore[attr-defined]
            self.axes[1].get_xlim()[0],  # type: ignore[attr-defined]
            self.axes[1].get_xlim()[1] + 0.2 * x_span,  # type: ignore[attr-defined]
        )
        textstr = ''
        for key in ['superevent_id', 'category', 'submitter', 'created', 't_0']:
            textstr += '{}: {}\n'.format(key, self.sevent_data['sevent'][key])
        self.axes[1].text(  # type: ignore[attr-defined]
            0.01,
            0.05,
            textstr[:-2],
            fontsize=10,
            transform=self.axes[1].transAxes,  # type: ignore[attr-defined]
            va='bottom',
            ha='left',
            bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.6},
        )

        plt.tight_layout()  # type: ignore[attr-defined]
        plt.subplots_adjust(hspace=0)

        filename = outdir / ('%s_latency_plot.png' % str(self.sevent_id))
        plt.savefig(filename)
        logger.info(f'Plot saved to {str(filename)}')

    def _init_figure(self) -> None:
        """Init matplotlib objects."""
        plt.rc('font', size=10)  # type: ignore[attr-defined]
        self.fig = plt.figure(figsize=(10, 5))
        self.axes = []

        self.axes.append(self.fig.add_subplot(2, 1, 1))
        self.axes[0].grid(ls='--')  # type: ignore[call-arg]
        self.axes[0].set_ylim(0, 1)
        self.axes[0].tick_params(  # type: ignore[attr-defined]
            axis='both', labelbottom=False, left=False, labelleft=False
        )

        self.axes.append(
            self.fig.add_subplot(2, 1, 2, sharex=self.axes[0], sharey=self.axes[0])
        )
        self.axes[1].grid(ls='--')  # type: ignore[call-arg]
        self.axes[1].tick_params(  # type: ignore[attr-defined]
            axis='both', left=False, labelleft=False
        )
        self.axes[1].set_xlabel(r'Seconds since t$_0$')

    def _add_entries_to_plot(self, ax: plt.Axes, entries: dict[str, Any]) -> None:
        """Adds entries to a plot.

        Parameters:
            ax: instance of matplotlib Axes
            entries: dict as returned by self._get_labels() or self._get_files()
        """
        i = 0
        for key, item in entries.items():
            y_loc = i / len(entries.keys()) * 0.9 + 0.05
            if item['found']:
                ax.axvline(
                    item['latency'], ls='-', color=self.cmap(y_loc)
                )  # type: ignore[call-arg]
                ax.plot(
                    [item['latency'], item['latency'] + 15],
                    [y_loc, y_loc],
                    color=self.cmap(y_loc),
                )
                ax.text(  # type: ignore[attr-defined]
                    item['latency'] + 17,
                    y_loc,
                    key,
                    color=self.cmap(y_loc),
                    va='center',
                )
            i += 1

    def _save_analize_sev_history(self, outdir: Path) -> None:
        """Saves the dump of AnalizeLogsSuperEvents and AnalizePipelinesSEvents.

        Parameters:
            outdir: Output directory.
        """
        filename = outdir / ('%s_analize_sev_history.txt' % str(self.sevent_id))

        dump_log_lines = []

        # -------------------------------
        # Ouput data event
        # -------------------------------
        # -------------------------------
        # Ouput log LABELS
        # -------------------------------
        dump_log_lines.append(
            '  ================== S-event        ============================'
        )

        dump_log_lines.append(
            '   superevent_id: {}'.format(self.sev_values['superevent_id'])
        )
        dump_log_lines.append('      preferd_id: {}'.format(self.gev_values['graceid']))
        dump_log_lines.append('           group: {}'.format(self.gev_values['group']))
        dump_log_lines.append(
            '        pipeline: {}'.format(self.gev_values['pipeline'])
        )
        dump_log_lines.append(f'  is_significant: {self.is_significant}')
        dump_log_lines.append(f'  should_publish: {self.should_publish}')

        # -------------------------------
        # Ouput log upload events
        # -------------------------------
        for iteration, history_index in enumerate(
            ['initial', 'added', 'initial', 'prefered']
        ):
            data_upload_events = self.history_properties[history_index]
            if iteration == 0:
                dump_log_lines.append(
                    '  ================== EVENT HISTORY ============================='
                )
            elif iteration == 2:
                dump_log_lines.append(
                    '  ================== PREFER EVENT HISTORY ======================'
                )
            for data_upload_event in data_upload_events:
                id_event = data_upload_event[1]
                try:
                    data_event = self.sevent_data['gevents'][id_event]
                except KeyError:
                    data_event = {'pipeline': '-----', 'search': '-----', 'far': 0.0}
                dump_log_lines.append(
                    '  {:8} {:10} {:8.1f}s  FAR={:8.3} {}'.format(
                        history_index,
                        id_event,
                        data_upload_event[0],
                        data_event['far'],
                        str((data_event['pipeline'], data_event['search'])),
                    )
                )
        # -------------------------------
        # Ouput log LABELS
        # -------------------------------
        dump_log_lines.append(
            '  ================== LABELS HISTORY ============================'
        )
        data_lables = self.history_properties['lables']
        for data_lable in data_lables:
            dump_log_lines.append('  {:8.1f}s {:30} - log({})'.format(*data_lable))
        data_lables = self.history_properties['rlables']
        dump_log_lines.append('  Removed label:')
        for data_lable in data_lables:
            dump_log_lines.append('  {:8.1f}s {:30} - log({})'.format(*data_lable))

        # -------------------------------
        # Ouput log G-events and groups
        # -------------------------------
        dump_log_lines.append(
            '  ==================     EVENTS TYPE   ============================'
        )
        for group_event in self.group_events:
            dump_log_lines.append(
                '  -- {:25} FAR={:8.3} : {}'.format(
                    str((group_event[0], group_event[1])),
                    np.min(self.group_fars[group_event]),
                    self.group_events[group_event],
                )
            )

        # -------------------------------
        # Ouput alert History
        # -------------------------------
        dump_log_lines.append(
            '  ==================    ALERT HISTORY    ============================'
        )
        for alert_kind in self.history_alerts:
            dump_log_lines.append(f'  KIND {alert_kind}')
            for alert in self.history_alerts[alert_kind]:
                dump_log_lines.append(
                    '{:10.1f}s {:15} {:36} - log({})'.format(
                        alert[0], alert[1], alert[2] + ',' + str(alert[3]), alert[4]
                    )
                )

        # -------------------------------
        # Ouput Data Product  History
        # -------------------------------
        dump_log_lines.append(
            '  ==================    DATA PRODUCTS HISTORY     ==================='
        )
        for alert_kind in self.history_dataproducts:
            dump_log_lines.append(f'  KIND {alert_kind}')
            for dataproduct in self.history_dataproducts[alert_kind]:
                dump_log_lines.append(
                    '{:10.1f}s file= {:30} ...{} - log({})'.format(
                        dataproduct[0],
                        dataproduct[1] + ',' + str(dataproduct[2]),
                        dataproduct[3][-12:],
                        dataproduct[4],
                    )
                )
        dump_log_lines.append(
            '  ==================================================================='
        )

        for line in dump_log_lines:
            logger.info(line)

        with open(filename, 'w') as stream:
            stream.writelines(line + '\n' for line in dump_log_lines)
        logger.info(f'History saved to {str(filename)}')
