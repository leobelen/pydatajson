#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Módulo 'search' de Pydatajson

Contiene los métodos para navegar un data.json iterando y buscando entidades de
un catálogo.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement

from functools import partial

from time_series import distribution_has_time_index, dataset_has_time_series
from readers import read_catalog
import custom_exceptions as ce


def get_themes(catalog):
    return catalog.get("themeTaxonomy")


def get_datasets(catalog, filter_in=None, filter_out=None, meta_field=None,
                 exclude_meta_fields=None, only_time_series=False):
    filter_in = filter_in or {}
    filter_out = filter_out or {}
    catalog = read_catalog(catalog)

    filtered_datasets = filter(
        lambda x: _filter_dictionary(
            x, filter_in.get("dataset"), filter_out.get("dataset")),
        catalog["dataset"]
    )

    # realiza filtros especiales
    if only_time_series:
        filtered_datasets = filter(
            dataset_has_time_series, filtered_datasets)

    if meta_field:
        return [dataset[meta_field] for dataset in filtered_datasets
                if meta_field in dataset]

    if exclude_meta_fields:
        meta_filtered_datasets = []
        for dataset in filtered_datasets:
            dataset_meta_filtered = dataset.copy()
            for excluded_meta_field in exclude_meta_fields:
                dataset_meta_filtered.pop(excluded_meta_field, None)
            meta_filtered_datasets.append(dataset_meta_filtered)

        return meta_filtered_datasets

    else:
        return filtered_datasets


def get_distributions(catalog, filter_in=None, filter_out=None,
                      meta_field=None, exclude_meta_fields=None,
                      only_time_series=False):
    filter_in = filter_in or {}
    filter_out = filter_out or {}
    catalog = read_catalog(catalog)

    distributions = []
    for dataset in get_datasets(catalog, filter_in, filter_out):
        for distribution in dataset["distribution"]:
            # agrega el id del dataset
            distribution["dataset_identifier"] = dataset["identifier"]
            distributions.append(distribution)

    filtered_distributions = filter(
        lambda x: _filter_dictionary(
            x, filter_in.get("distribution"), filter_out.get("distribution")),
        distributions
    )

    # realiza filtros especiales
    if only_time_series:
        filtered_distributions = filter(
            distribution_has_time_index, filtered_distributions)

    if meta_field:
        return [distribution[meta_field]
                for distribution in filtered_distributions
                if meta_field in distribution]

    if exclude_meta_fields:
        meta_filtered_distributions = []
        for distribution in filtered_distributions:
            distribution_meta_filtered = distribution.copy()
            for excluded_meta_field in exclude_meta_fields:
                distribution_meta_filtered.pop(excluded_meta_field, None)
            meta_filtered_distributions.append(distribution_meta_filtered)

        return meta_filtered_distributions

    else:
        return filtered_distributions


def get_fields(catalog, filter_in=None, filter_out=None, meta_field=None):
    filter_in = filter_in or {}
    filter_out = filter_out or {}
    catalog = read_catalog(catalog)

    fields = []
    for distribution in get_distributions(catalog, filter_in, filter_out):
        if "field" in distribution and isinstance(distribution["field"], list):
            for field in distribution["field"]:
                # agrega el id del dataset
                field["dataset_identifier"] = distribution[
                    "dataset_identifier"]
                # agrega el id de la distribución
                field["distribution_identifier"] = distribution["identifier"]
                fields.append(field)

    filtered_fields = filter(
        lambda x: _filter_dictionary(
            x, filter_in.get("field"), filter_out.get("field")),
        fields
    )

    if meta_field:
        return [field[meta_field] for field in filtered_fields
                if meta_field in field]
    else:
        return filtered_fields


def get_dataset(catalog, identifier=None, title=None):
    msg = "Se requiere un 'identifier' o 'title' para buscar el dataset."
    assert identifier or title, msg
    catalog = read_catalog(catalog)

    if identifier:
        filtered_datasets = get_datasets(
            catalog, {"dataset": {"identifier": identifier}})
    elif title:
        filtered_datasets = get_datasets(
            catalog, {"dataset": {"title": title}})

    if len(filtered_datasets) > 1:
        if identifier:
            raise ce.DatasetIdRepetitionError(
                identifier, filtered_datasets)
        elif title:
            raise ce.DatasetTitleRepetitionError(
                title, filtered_datasets)
    elif len(filtered_datasets) == 0:
        return None
    else:
        return filtered_datasets[0]


def get_distribution(catalog, identifier=None, title=None,
                     dataset_identifier=None):
    msg = "Se requiere un 'identifier' o 'title' para buscar el distribution."
    assert identifier or title, msg
    catalog = read_catalog(catalog)

    # 1. BUSCA las distribuciones en el catálogo
    # toma la distribution que tenga el id único
    if identifier:
        filtered_distributions = get_distributions(
            catalog, {"distribution": {"identifier": identifier}})
    # toma la distribution que tenga el título único, dentro de un dataset
    elif title and dataset_identifier:
        filtered_distributions = get_distributions(
            catalog, {
                "dataset": {"identifier": dataset_identifier},
                "distribution": {"title": title}
            }
        )
    # toma las distribution que tengan el título (puede haber más de una)
    elif title:
        filtered_distributions = get_distributions(
            catalog, {"distribution": {"title": title}})

    # 2. CHEQUEA que la cantidad de distribuciones es consistente
    if len(filtered_distributions) > 1:
        if identifier:
            raise ce.DistributionIdRepetitionError(
                identifier, filtered_distributions)
        elif title and dataset_identifier:
            # el título de una distribution no puede repetirse en un dataset
            raise ce.DistributionTitleRepetitionError(
                title, filtered_distributions)
        elif title:
            # el título de una distribution puede repetirse en el catalogo
            return filtered_distributions
    elif len(filtered_distributions) == 0:
        return None
    else:
        return filtered_distributions[0]


def get_field_location(catalog, identifier=None, title=None,
                       distribution_identifier=None):
    catalog = read_catalog(catalog)

    field_location = None

    for dataset in catalog["dataset"]:
        for distribution in dataset["distribution"]:
            if (not distribution_identifier or
                    distribution_identifier == distribution["identifier"]):
                if "field" in distribution and isinstance(distribution["field"], list):
                    for field in distribution["field"]:
                        if (identifier and "id" in field and
                            field["id"] == identifier
                                or title and field["title"] == title):

                            field_location = {
                                "dataset_identifier": dataset["identifier"],
                                "dataset_title": dataset["title"],
                                "distribution_identifier": distribution[
                                    "identifier"],
                                "distribution_title": distribution["title"],
                                "field_id": field["id"],
                                "field_title": field["title"]
                            }

                            return field_location

    return field_location


def get_field(catalog, identifier=None, title=None,
              distribution_identifier=None):
    msg = "Se requiere un 'id' o 'title' para buscar el field."
    assert identifier or title, msg

    # 1. BUSCA los fields en el catálogo
    if identifier:
        filtered_fields = get_fields(
            catalog, {"field": {"id": identifier}})
    elif title and distribution_identifier:
        filtered_fields = get_fields(
            catalog, {
                "distribution": {"identifier": distribution_identifier},
                "field": {"title": title}
            }
        )
    elif title:
        filtered_fields = get_fields(
            catalog, {"field": {"title": title}})

    # 2. CHEQUEA que la cantidad de fields es consistente
    if len(filtered_fields) > 1:
        if identifier:
            raise ce.FieldIdRepetitionError(
                identifier, filtered_fields)
        elif title and distribution_identifier:
            # el título de un field no puede repetirse en una distribution
            raise ce.FieldTitleRepetitionError(
                title, filtered_fields)
        elif title:
            # el título de un field puede repetirse
            return filtered_fields
    elif len(filtered_fields) == 0:
        return None
    else:
        return filtered_fields[0]


def get_catalog_metadata(catalog, exclude_meta_fields=None):
    """Devuelve sólo la metadata de nivel catálogo."""
    exclude_meta_fields = exclude_meta_fields or []
    catalog_dict_copy = catalog.copy()
    del catalog_dict_copy["dataset"]

    for excluded_meta_field in exclude_meta_fields:
        catalog_dict_copy.pop(excluded_meta_field, None)

    return catalog_dict_copy


def _filter_dictionary(dictionary, filter_in=None, filter_out=None):
    # print(filter_in, filter_out)
    if filter_in:
        # chequea que el objeto tenga las propiedades de filtro positivo
        for key, value in filter_in.iteritems():
            if dictionary.get(key) != value:
                return False

    if filter_out:
        # chequea que el objeto NO tenga las propiedades de filtro negativo
        for key, value in filter_out.iteritems():
            if dictionary.get(key) == value:
                return False

    return True
