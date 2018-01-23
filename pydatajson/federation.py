#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from ckanapi import RemoteCKAN
from ckanapi.errors import NotFound
from .ckan_utils import map_dataset_to_package


def push_dataset_to_ckan(catalog, dataset_origin_identifier, portal_url, owner_org,
                         apikey=None, dataset_destination_identifier=None):

    dataset = catalog.get_dataset(dataset_origin_identifier)
    ckan_portal = RemoteCKAN(portal_url, apikey=apikey)
#   Create missing groups
    existing_groups = ckan_portal.call_action('group_list')
    new_groups = set(dataset['superTheme']) - set(existing_groups)
    for
    package = map_dataset_to_package(dataset)
    package['owner_org'] = owner_org
    if dataset_destination_identifier:
        package['id'] = dataset_destination_identifier
        try:
            pushed_package = ckan_portal.call_action('package_update', data_dict=package)
        except NotFound:
            pushed_package = ckan_portal.call_action('package_create', data_dict=package)
    else:
        pushed_package = ckan_portal.call_action('package_create', data_dict=package)

    return pushed_package['id']