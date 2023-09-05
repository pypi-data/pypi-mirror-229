import hashlib
import http.server
import io
import json
import logging
import os
import shutil
import textwrap
import threading
import webbrowser
import zipfile
from functools import partial
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen

from ..procret import registry


__all__ = 'run',

logger = logging.getLogger('procpath')


def install_sqliteviz(zip_url: str, target_dir: Path):
    response = urlopen(zip_url)
    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
        z.extractall(target_dir)

    bundle = json.dumps(get_visualisation_bundle(), sort_keys=True)
    (target_dir / 'inquiries.json').write_text(bundle)


def get_line_chart_config(title: str) -> dict:
    return {
        'data': [{
            'meta': {'columnNames': {'x': 'ts', 'y': 'value'}},
            'mode': 'lines',
            'type': 'scatter',
            'x': None,
            'xsrc': 'ts',
            'y': None,
            'ysrc': 'value',
            'transforms': [{
                'groups': None,
                'groupssrc': 'pid',
                'meta': {'columnNames': {'groups': 'pid'}},
                'styles': [],
                'type': 'groupby',
            }],
        }],
        'frames': [],
        'layout': {
            'autosize': True,
            'title': {'text': title},
            'xaxis': {
                'autorange': True,
                'range': [],
                'type': 'date'
            },
            'yaxis': {
                'autorange': True,
                'range': [],
                'type': 'linear'
            },
        },
    }


def get_visualisation_bundle() -> dict:
    """Get Sqliteviz import-able visualisation bundle."""

    inquiries = []
    result = {'version': 2, 'inquiries': inquiries}

    for query in registry.values():
        query_text = query.get_short_query(ts_as_milliseconds=True)
        inquiries.append({
            'id': hashlib.md5(query_text.encode()).hexdigest()[:21],
            'createdAt': '2023-09-03T12:00:00Z',
            'name': query.title,
            'query': textwrap.dedent(query_text).strip(),
            'viewType': 'chart',
            'viewOptions': get_line_chart_config(query.title),
        })

    inquiries.extend(get_sqliteviz_only_charts())

    return result


def get_sqliteviz_only_charts():
    return [
        # Process Timeline
        {
            'id': 'csfOTEpzlFfYz7OUc2aGI',
            'createdAt': '2023-09-03T12:00:00Z',
            'name': 'Process Timeline',
            'query': textwrap.dedent('''
                SELECT
                    ts * 1000 AS ts,
                    stat_pid,
                    stat_pid || ' ' || stat_comm pid_comm,
                    iif(
                        length(cmdline) > 0,
                        substr(cmdline, 0, 75) || iif(length(cmdline) > 75, '...', ''),
                        stat_comm
                    ) cmd
                FROM record
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [{
                    'type': 'scattergl',
                    'mode': 'markers',
                    'meta': {'columnNames': {'x': 'ts', 'y': 'stat_pid', 'text': 'cmd'}},
                    'transforms': [{
                        'type': 'groupby',
                        'styles': [],
                        'meta': {'columnNames': {'groups': 'pid_comm'}},
                        'groups': None,
                        'groupssrc': 'pid_comm',
                    }],
                    'y': None,
                    'ysrc': 'stat_pid',
                    'x': None,
                    'xsrc': 'ts',
                    'text': None,
                    'textsrc': 'cmd',
                    'marker': {'size': 12, 'maxdisplayed': 0},
                    'line': {'width': 3},
                    'hoverinfo': 'x+text',
                }],
                'layout': {
                    'xaxis': {
                        'type': 'date',
                        'range': [],
                        'autorange': True,
                    },
                    'yaxis': {
                        'type': 'category',
                        'range': [],
                        'autorange': True,
                        'showticklabels': False,
                    },
                    'title': {'text': 'Process Timeline'},
                    'hovermode': 'closest',
                },
                'frames': [],
            },
        },
        # Total Memory Consumption
        {
            'id': 'boSs15w7Endl5V9bABjXv',
            'createdAt': '2023-09-03T12:00:00Z',
            'name': 'Total Resident Set Size, MiB',
            'query': textwrap.dedent('''
                SELECT
                  ts * 1000 ts,
                  -- Comment "stat_pid" group and uncomment this to have coarser grouping
                  -- CASE
                  --   WHEN cmdline LIKE '%firefox%' THEN '1. firefox'
                  --   WHEN cmdline LIKE '%chromium%' THEN '2. chromium'
                  --   ELSE '3. other'
                  -- END "group",
                  stat_pid "group",
                  SUM(stat_rss)
                    / 1024.0 / 1024 * (SELECT value FROM meta WHERE key = 'page_size') value
                FROM record
                GROUP BY 1, 2
                ORDER BY 2
            ''').strip(),
            'viewType': 'chart',
            'viewOptions': {
                'data': [{
                    'type': 'scatter',
                    'mode': 'lines',
                    'meta': {'columnNames': {'x': 'ts', 'y': 'rss'}},
                    'transforms': [{
                        'type': 'groupby',
                        'groupssrc': 'group',
                        'groups': None,
                        'styles': [],
                        'meta': {'columnNames': {'groups': 'group'}},
                    }],
                    'stackgroup': 1,
                    'x': None,
                    'xsrc': 'ts',
                    'y': None,
                    'ysrc': 'value',
                }],
                'layout': {
                    'xaxis': {
                        'type': 'date',
                        'range': [],
                        'autorange': True,
                    },
                    'yaxis': {
                        'type': 'linear',
                        'range': [],
                        'autorange': True,
                        'separatethousands': True,
                    },
                    'title': {'text': 'Total Resident Set Size, MiB'},
                    'hovermode': 'closest',
                },
                'frames': []
            },
        }
    ]


def serve_dir(bind: str, port: int, directory: str):
    server_cls = http.server.ThreadingHTTPServer
    handler_cls = partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    with server_cls((bind, port), handler_cls) as httpd:
        httpd.serve_forever()


def symlink_database(database_file: str, sqliteviz_dir: Path) -> Path:
    db_path = Path(database_file)
    if not db_path.exists():
        raise FileNotFoundError

    sym_path = sqliteviz_dir / 'db.sqlite'
    sym_path.unlink(missing_ok=True)
    sym_path.symlink_to(db_path)
    return sym_path


def run(
    bind: str,
    port: int,
    open_in_browser: bool,
    reinstall: bool,
    build_url: str,
    database_file: Optional[str] = None,
):
    user_cache_dir = Path(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')))
    sqliteviz_dir = user_cache_dir / 'procpath' / 'sqliteviz'
    if not sqliteviz_dir.exists() or reinstall:
        shutil.rmtree(sqliteviz_dir, ignore_errors=True)
        sqliteviz_dir.mkdir(parents=True)
        logger.info('Downloading %s into %s', build_url, sqliteviz_dir)
        install_sqliteviz(build_url, sqliteviz_dir)
    else:
        logger.info('Serving existing Sqliteviz from %s', sqliteviz_dir)

    url = 'http://{host}:{port}/'.format(port=port, host=bind or 'localhost')
    logger.info('Serving Sqliteviz at %s', url)

    server_fn = partial(serve_dir, bind, port, str(sqliteviz_dir))
    server = threading.Thread(target=server_fn, daemon=True)
    server.start()

    if database_file:
        try:
            sym_path = symlink_database(database_file, sqliteviz_dir)
        except FileNotFoundError:
            logger.warning('Database file %s does not exist', database_file)
        else:
            params = urlencode({'data_url': url + sym_path.name, 'data_format': 'sqlite'})
            url += f'#/load?{params}'

    if open_in_browser:
        webbrowser.open(url)

    server.join()
