#!/usr/bin/env python3

import json
import networkx as nx
import os
import pickle
import requests as req
import time
import xml.etree.ElementTree as et
from itertools import combinations
from matplotlib import pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def save_titles_from_ann(id_end, filepath):
    """
    Batch requests to ANN Encyclopedia API. Find highest ID manually with
    bisection.

    :param id_end: Highest anime ID, integer
    :param filename: Filename for dumping retrieved data to.

    https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=5013
    """
    base_ann = 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime'
    xml_dbb = []

    results = []
    # loop through anime id ranges
    step = 50
    idx, idx_end = 1, 50
    while idx_end < id_end:
        print('Getting Anime ID range: {0}:{1}'.format(idx, idx_end))

        # build anime ID list and make request to ANN API
        aid_list = '/'.join([str(i) for i in range(idx, idx_end + 1)])
        resp = req.get('{0}={1}'.format(base_ann, aid_list))
        if resp.status_code != req.codes.ok:
            print('Error, retrying ...')
            time.sleep(3)
            continue

        # append results, housecleaning
        results.append(resp.text)
        idx += step
        idx_end += step
        time.sleep(3)
    else:
        print('Getting LAST Anime ID range: {0}:{1}'.format(idx, id_end))

        # build anime ID list and make request to ANN API
        aid_list = '/'.join([str(i) for i in range(idx, id_end + 1)])
        resp = req.get('{0}={1}'.format(base_ann, aid_list))
        if resp.status_code != req.codes.ok:
            print('Error, retrying ...')

        # append results
        results.append(resp.text)

    # save to pickle
    with open(filepath, 'wb') as fp:
        pickle.dump(results, fp)


def convert_dataset(load_path, save_path=None):
    """
    Convert a pickled list of XML documents to JSON-like data structure.

    :param filepath: If filepath is specified, save to JSON text file.

    :return: JSON-like data structure. Example:

    {
        "anime": {
            344: {
                "title": "Name 1",
                "creators": [1, 2, 465],
                "date": "1999-03-14",
            }
        },
        "creators": {
            1: {
                "names": ["Name 1", "Name 2", ...],
                "works": [314, 3455],
            },
        },
    }
    """

    try:
        with open(load_path, 'rb') as fp:
            dbb = pickle.load(fp)
    except IOError:
        print('Pickle "{0}" not found.'.format(load_path.rsplit('/')[1]))
        return None

    data = {'anime': {}, 'creators': {}}
    anime_data = data['anime']
    creators_data = data['creators']

    for text in dbb:
        # load one instance of saved XML
        root = et.fromstring(text)
        # loop through anime in XML instance
        for anime in root:
            aid = anime.attrib.get('id')                    # anime id

            this = {
                'title': anime.attrib.get('name') or '???',  # anime title
                'creators': set([]),
                'date': '????-??-??',
            }

            # iterate over "info" nodes
            for info in anime.iter('info'):
                type_text = info.attrib.get('type')
                if type_text and type_text == 'Vintage':
                    date_str = info.text.split(' ', 1)[0]   # anime date
                    if len(date_str):
                        this['date'] = date_str
                    break

            # iterate over "staff" nodes
            for staff in anime.iter('staff'):
                person = staff[1]
                pid = person.attrib.get('id')               # staff id
                name = person.text                          # staff name

                try:  # getting person id first if it exists, else create dict
                    creator_node = creators_data[pid]
                except KeyError:
                    creator_node = creators_data[pid] = {
                        'names': set([]),
                        'works': set([]),
                    }
                # save staff id
                creator_node['names'].add(name)
                # save anime id
                creator_node['works'].add(aid)
                # save staff id
                this['creators'].add(pid)

            # save anime
            anime_data[aid] = this

    # convert sets for JSON-serializability
    for aid, anime in anime_data.items():
        anime_data[aid]['creators'] = list(anime['creators'])
    for pid, person in creators_data.items():
        creators_data[pid]['works'] = list(person['works'])
        creators_data[pid]['names'] = list(person['names'])

    if save_path:  # save to JSON
        with open(save_path, 'w') as fp:
            json.dump(data, fp)

    return data


def create_network(data, include_names=False):
    """
    Create a NetworkX graph from dataset. Optionally, save network plot.
    Dataset must have the following structure:

    {
        "anime": {
            344: {
                "title": "Name 1",
                "creators": [1, 2, 465],
                "date": "1999-03-14",
            }
        },
        "creators": {
            1: {
                "names": ["Name 1", "Name 2", ...],
                "works": [314, 3455],
            },
        },
    }

    :param data: JSON-like dataset, dict
    :param include_names: Set as True if nodes carry attribute "c"
                          (as "creator") with string value of creator's name.
                          This requires significantly more memory with each
                          node.

    :return: NetworkX Graph object
    """
    creators = data['creators']

    graph = nx.Graph()
    # build edges between each anime's creators creators
    for aid, anime in data['anime'].items():
        for v1, v2 in combinations(anime['creators'], 2):
            graph.add_edge(v1, v2)
            try:
                graph.edge[v1][v2]['Weight'] += 1
            except:
                graph.edge[v1][v2]['Weight'] = 1

            if include_names:
                graph.node[v1]['Label'] = creators[v1]['names'][0]
                graph.node[v2]['Label'] = creators[v2]['names'][0]

    return graph


def draw_network(graph, plot_path):
    """
    Draw network using matplotlib.

    :param graph: NetworkX Graph object
    :param plot_path: File path for saving network plot, string
    """

    graph_pos = nx.spring_layout(graph)
    # nx.draw_networkx_nodes(graph, graph_pos, node_size=2, node_color='blue',
    #                        alpha=0.8, linewidths=0.1, label='Anime Creators')
    nx.draw_networkx_edges(graph, graph_pos, width=0.3, alpha=1,
                           arrows=False, label='Collaboration')
    plt.axis('off')
    plt.savefig(plot_path, dpi=72)

if __name__ == '__main__':
    # save_titles_from_ann(5013, os.path.join(BASE_DIR, 'titles.pkl'))
    # lp = os.path.join(BASE_DIR, 'titles.pkl')
    sp = os.path.join(BASE_DIR, 'dataset.json')
    # convert_dataset(lp, sp)

    with open(sp, 'r') as fp:
        _dataset = json.load(fp)

    # pp = os.path.join(BASE_DIR, 'graph.png')
    graphml_path = os.path.join(BASE_DIR, 'network_named.graphml')
    net = create_network(_dataset, include_names=True)
    nx.write_graphml(net, graphml_path)
    # # draw_network(net, pp)
    with open('network_named.pkl', 'wb') as fp:
        pickle.dump(net, fp)
