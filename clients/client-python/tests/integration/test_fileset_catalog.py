"""
Copyright 2024 Datastrato Pvt Ltd.
This software is licensed under the Apache License version 2.
"""

import logging
from random import randint
from typing import Dict, List

from gravitino import (
    NameIdentifier,
    GravitinoAdminClient,
    GravitinoClient,
    Catalog,
    Fileset,
    FilesetChange,
)
from tests.integration.integration_test_env import IntegrationTestEnv

logger = logging.getLogger(__name__)


class TestFilesetCatalog(IntegrationTestEnv):
    metalake_name: str = "TestFilesetCatalog_metalake" + str(randint(1, 10000))
    catalog_name: str = "catalog"
    catalog_location_prop: str = "location"  # Fileset Catalog must set `location`
    catalog_provider: str = "hadoop"

    schema_name: str = "schema"

    fileset_name: str = "fileset"
    fileset_alter_name: str = fileset_name + "Alter"
    fileset_comment: str = "fileset_comment"

    fileset_location: str = "/tmp/TestFilesetCatalog"
    fileset_properties_key1: str = "fileset_properties_key1"
    fileset_properties_value1: str = "fileset_properties_value1"
    fileset_properties_key2: str = "fileset_properties_key2"
    fileset_properties_value2: str = "fileset_properties_value2"
    fileset_properties: Dict[str, str] = {
        fileset_properties_key1: fileset_properties_value1,
        fileset_properties_key2: fileset_properties_value2,
    }
    fileset_new_name = fileset_name + "_new"

    catalog_ident: NameIdentifier = NameIdentifier.of_catalog(
        metalake_name, catalog_name
    )
    schema_ident: NameIdentifier = NameIdentifier.of_schema(
        metalake_name, catalog_name, schema_name
    )
    fileset_ident: NameIdentifier = NameIdentifier.of_fileset(
        metalake_name, catalog_name, schema_name, fileset_name
    )
    fileset_new_ident: NameIdentifier = NameIdentifier.of_fileset(
        metalake_name, catalog_name, schema_name, fileset_new_name
    )

    gravitino_admin_client: GravitinoAdminClient = GravitinoAdminClient(
        uri="http://localhost:8090"
    )
    gravitino_client: GravitinoClient = None

    def setUp(self):
        self.init_test_env()

    def tearDown(self):
        self.clean_test_data()

    def clean_test_data(self):
        try:
            self.gravitino_client = GravitinoClient(
                uri="http://localhost:8090", metalake_name=self.metalake_name
            )
            catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
            logger.info(
                "Drop fileset %s[%s]",
                self.fileset_ident,
                catalog.as_fileset_catalog().drop_fileset(ident=self.fileset_ident),
            )
            logger.info(
                "Drop fileset %s[%s]",
                self.fileset_new_ident,
                catalog.as_fileset_catalog().drop_fileset(ident=self.fileset_new_ident),
            )
            logger.info(
                "Drop schema %s[%s]",
                self.schema_ident,
                catalog.as_schemas().drop_schema(ident=self.schema_ident, cascade=True),
            )
            logger.info(
                "Drop catalog %s[%s]",
                self.catalog_ident,
                self.gravitino_client.drop_catalog(name=self.catalog_name),
            )
            logger.info(
                "Drop metalake %s[%s]",
                self.metalake_name,
                self.gravitino_admin_client.drop_metalake(self.metalake_name),
            )
        except Exception as e:
            logger.error("Clean test data failed: %s", e)

    def init_test_env(self):
        self.gravitino_admin_client.create_metalake(
            self.metalake_name, comment="", properties={}
        )
        self.gravitino_client = GravitinoClient(
            uri="http://localhost:8090", metalake_name=self.metalake_name
        )
        catalog = self.gravitino_client.create_catalog(
            name=self.catalog_name,
            catalog_type=Catalog.Type.FILESET,
            provider=self.catalog_provider,
            comment="",
            properties={self.catalog_location_prop: "/tmp/test1"},
        )
        catalog.as_schemas().create_schema(
            ident=self.schema_ident, comment="", properties={}
        )

    def create_fileset(self) -> Fileset:
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        return catalog.as_fileset_catalog().create_fileset(
            ident=self.fileset_ident,
            fileset_type=Fileset.Type.MANAGED,
            comment=self.fileset_comment,
            storage_location=self.fileset_location,
            properties=self.fileset_properties,
        )

    def test_create_fileset(self):
        fileset = self.create_fileset()
        self.assertIsNotNone(fileset)
        self.assertEqual(fileset.type(), Fileset.Type.MANAGED)
        self.assertEqual(fileset.comment(), self.fileset_comment)
        self.assertEqual(fileset.properties(), self.fileset_properties)

    def test_drop_fileset(self):
        self.create_fileset()
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        self.assertTrue(
            catalog.as_fileset_catalog().drop_fileset(ident=self.fileset_ident)
        )

    def test_list_fileset(self):
        self.create_fileset()
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        fileset_list: List[NameIdentifier] = catalog.as_fileset_catalog().list_filesets(
            namespace=self.fileset_ident.namespace()
        )
        self.assertTrue(any(item.name() == self.fileset_name for item in fileset_list))

    def test_load_fileset(self):
        self.create_fileset()
        fileset = (
            self.gravitino_client.load_catalog(name=self.catalog_name)
            .as_fileset_catalog()
            .load_fileset(ident=self.fileset_ident)
        )
        self.assertIsNotNone(fileset)
        self.assertEqual(fileset.name(), self.fileset_name)
        self.assertEqual(fileset.comment(), self.fileset_comment)
        self.assertEqual(fileset.properties(), self.fileset_properties)
        self.assertEqual(fileset.audit_info().creator(), "anonymous")

    def test_alter_fileset(self):
        self.create_fileset()
        fileset_propertie_new_value = self.fileset_properties_value2 + "_new"

        changes = (
            FilesetChange.remove_property(self.fileset_properties_key1),
            FilesetChange.set_property(
                self.fileset_properties_key2, fileset_propertie_new_value
            ),
        )
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        fileset_new = catalog.as_fileset_catalog().alter_fileset(
            self.fileset_ident, *changes
        )
        self.assertEqual(
            fileset_new.properties().get(self.fileset_properties_key2),
            fileset_propertie_new_value,
        )
        self.assertTrue(self.fileset_properties_key1 not in fileset_new.properties())
