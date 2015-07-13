__author__ = 'Miha Jenko'

import json

import numpy
from sklearn.cluster import KMeans


def projects_backed_per_user(users):
    counts = {}
    nr_of_projects = 0
    for uid, projects in users.items():
        # how many projects did the user back?
        projects_supported = len(projects)
        # figure out the number of projects in total
        last_project = numpy.amax(projects)
        # count them
        if last_project > nr_of_projects:
            nr_of_projects = last_project
        if projects_supported in counts:
            counts[projects_supported] += 1
        else:
            counts[projects_supported] = 1

    total_backs = len(users)

    print('Projects backed\t\tBackers\t\t%')
    print('===========================================')
    for p_backed in range(len(counts)):
        backed_key = p_backed + 1
        print('{}\t\t\t\t\t{}\t\t{:.1f}%'
              .format(backed_key, counts[backed_key],
                      counts[backed_key] * 100 / total_backs))


def two_backed_followup(users):
    # filter: only those that backed two
    two = {}
    for uid, projects in users.items():
        if len(projects) == 2:
            two[uid] = projects
    # when was the next one?
    next_one = []
    for uid, projects in two.items():
        first, second = projects
        next_one.append(second - first)
    print('\nUsers that backed two projects:')
    print('Next backed project (avg): {:.2f}'.format(numpy.average(next_one)))


def three_backed_followup(users):
    # filter: only those that backed two
    two = {}
    for uid, projects in users.items():
        if len(projects) == 3:
            two[uid] = projects
    # when was the next one?
    next_one = []
    next_two_after_first = []
    next_two_after_second = []
    for uid, projects in two.items():
        first, second, third = projects
        next_one.append(second - first)
        next_two_after_first.append(third - first)
        next_two_after_second.append(third - second)
    print('\nUsers that backed three projects:')
    print('Next backed project (avg): {:.2f}'.format(numpy.average(next_one)))
    print('Next backed project (avg): {:.2f}'.format(
        numpy.average(next_two_after_second))
    )
    print('Difference between first and third (avg): {:.2f}'.format(
        numpy.average(next_two_after_first))
    )


def two_backed_clusters(users):
    two = []
    for uid, projects in users.items():
        if len(projects) == 2:
            two.append(projects)
    km = KMeans(n_clusters=2, n_jobs=3)
    km.fit(two)

    # First cluster means
    f1 = 0
    s1 = 0
    n1 = 0
    for pair, label in zip(two, km.labels_):
        if label == 0:
            f1 += pair[0]
            s1 += pair[1]
            n1 += 1
    # Second cluster means
    f2 = 0
    s2 = 0
    n2 = 0
    for pair, label in zip(two, km.labels_):
        if label == 1:
            f2 += pair[0]
            s2 += pair[1]
            n2 += 1

    print('\nAverage ordinal project pairs cl.1: [{:.1f}, {:.1f}]'. format(
        (f1 / n1) + 1, (s1 / n1) + 1
    ))
    print('Members: {}'.format(n1))
    print('Average ordinal project pairs cl.2: [{:.1f}, {:.1f}]'. format(
        (f2 / n2) + 1, (s2 / n2) + 1
    ))
    print('Members: {}'.format(n2))


def three_backed_clusters(users):
    three = []
    for uid, projects in users.items():
        if len(projects) == 3:
            three.append(projects)
    km = KMeans(n_clusters=2, n_jobs=3)
    km.fit(three)

    # First cluster means
    f1 = 0
    s1 = 0
    t1 = 0
    n1 = 0
    for tripplet, label in zip(three, km.labels_):
        if label == 0:
            f1 += tripplet[0]
            s1 += tripplet[1]
            t1 += tripplet[2]
            n1 += 1
    # Second cluster means
    f2 = 0
    s2 = 0
    t2 = 0
    n2 = 0
    for tripplet, label in zip(three, km.labels_):
        if label == 1:
            f2 += tripplet[0]
            s2 += tripplet[1]
            t2 += tripplet[2]
            n2 += 1

    print('\nAverage ordinal project tripples cl.1: [{:.1f}, {:.1f}, {:.1f}]'
          .format((f1 / n1) + 1, (s1 / n1) + 1, (t1 / n1) + 1))
    print('Members: {}'.format(n1))
    print('Average ordinal project tripplets cl.2: [{:.1f}, {:.1f}, {:.1f}]'
          .format((f2 / n2) + 1, (s2 / n2) + 1, (t2 / n2) + 1))
    print('Members: {}'.format(n2))


def produce_d3json(users):
    """
    TODO: Make it usable for all queries
    """
    matr = numpy.zeros((6, 6), dtype=numpy.int32)
    for uid, projects in users.items():
        if len(projects) == 2:
            for i in range(6):
                for j in range(6):
                    if i != j and (i in projects and j in projects):
                        matr[i, j] += 1

    project_names = {0: 'WORLD END ECONOMiCA',
                     1: 'fault milestone',
                     2: 'WAS',
                     3: 'CLANNAD',
                     4: 'The Grisaia Trilogy',
                     5: 'Memory\'s Dogma\n'}
    d3data = {'project_names': project_names,
              'relation_matrix': matr.tolist()}

    print(d3data)
    with open('d3data.json', 'w', encoding='UTF-8') as f:
        json.dump(d3data, f)


if __name__ == '__main__':
    with open('userdata.json') as fp:
        data = json.load(fp)
    projects_backed_per_user(data)
    # two_backed_followup(data)     # pretty useless
    # three_backed_followup(data)   # pretty useless
    two_backed_clusters(data)
    three_backed_clusters(data)
    # produce_d3json(data)          # not generalized enough
