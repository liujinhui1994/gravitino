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
    SchemaChange,
    Schema,
)

from tests.integration.integration_test_env import IntegrationTestEnv

logger = logging.getLogger(__name__)


class TestSchema(IntegrationTestEnv):
    metalake_name: str = "TestSchema_metalake" + str(randint(1, 10000))

    catalog_name: str = "testCatalog"
    catalog_location_prop: str = "location"  # Fileset Catalog must set `location`
    catalog_provider: str = "hadoop"

    schema_name: str = "testSchema"
    schema_new_name = schema_name + "_new"

    schema_comment: str = "schema_comment"
    schema_properties_key1: str = "schema_properties_key1"
    schema_properties_value1: str = "schema_properties_value1"
    schema_properties_key2: str = "schema_properties_key2"
    schema_properties_value2: str = "schema_properties_value2"
    schema_properties: Dict[str, str] = {
        schema_properties_key1: schema_properties_value1,
        schema_properties_key2: schema_properties_value2,
    }

    catalog_ident: NameIdentifier = NameIdentifier.of_catalog(
        metalake_name, catalog_name
    )
    schema_ident: NameIdentifier = NameIdentifier.of_schema(
        metalake_name, catalog_name, schema_name
    )
    schema_new_ident: NameIdentifier = NameIdentifier.of_schema(
        metalake_name, catalog_name, schema_new_name
    )

    gravitino_admin_client: GravitinoAdminClient = GravitinoAdminClient(
        uri="http://localhost:8090"
    )
    gravitino_client: GravitinoClient = None

    def setUp(self):
        self.init_test_env()

    def tearDown(self):
        self.clean_test_data()

    def init_test_env(self):
        self.gravitino_admin_client.create_metalake(
            self.metalake_name, comment="", properties={}
        )
        self.gravitino_client = GravitinoClient(
            uri="http://localhost:8090", metalake_name=self.metalake_name
        )
        self.gravitino_client.create_catalog(
            name=self.catalog_name,
            catalog_type=Catalog.Type.FILESET,
            provider=self.catalog_provider,
            comment="",
            properties={self.catalog_location_prop: "/tmp/test_schema"},
        )

    def clean_test_data(self):
        try:
            self.gravitino_client = GravitinoClient(
                uri="http://localhost:8090", metalake_name=self.metalake_name
            )
            catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
            logger.info(
                "Drop schema %s[%s]",
                self.schema_ident,
                catalog.as_schemas().drop_schema(self.schema_ident, cascade=True),
            )
            logger.info(
                "Drop schema %s[%s]",
                self.schema_new_ident,
                catalog.as_schemas().drop_schema(self.schema_new_ident, cascade=True),
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

    def create_schema(self) -> Schema:
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        return catalog.as_schemas().create_schema(
            ident=self.schema_ident,
            comment=self.schema_comment,
            properties=self.schema_properties,
        )

    def test_create_schema(self):
        schema = self.create_schema()
        self.assertEqual(schema.name(), self.schema_name)
        self.assertEqual(schema.comment(), self.schema_comment)
        self.assertEqual(schema.properties(), self.schema_properties)
        self.assertEqual(schema.audit_info().creator(), "anonymous")

    def test_drop_schema(self):
        self.create_schema()
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        self.assertTrue(
            catalog.as_schemas().drop_schema(ident=self.schema_ident, cascade=True)
        )

    def test_list_schema(self):
        self.create_schema()
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        schema_list: List[NameIdentifier] = catalog.as_schemas().list_schemas(
            namespace=self.schema_ident.namespace()
        )
        self.assertTrue(any(item.name() == self.schema_name for item in schema_list))

    def test_load_schema(self):
        self.create_schema()
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        schema = catalog.as_schemas().load_schema(ident=self.schema_ident)
        self.assertIsNotNone(schema)
        self.assertEqual(schema.name(), self.schema_name)
        self.assertEqual(schema.comment(), self.schema_comment)
        self.assertEqual(schema.properties(), self.schema_properties)
        self.assertEqual(schema.audit_info().creator(), "anonymous")

    def test_alter_schema(self):
        self.create_schema()
        schema_propertie_new_value = self.schema_properties_value2 + "_new"

        changes = (
            SchemaChange.remove_property(self.schema_properties_key1),
            SchemaChange.set_property(
                self.schema_properties_key2, schema_propertie_new_value
            ),
        )
        catalog = self.gravitino_client.load_catalog(name=self.catalog_name)
        schema_new = catalog.as_schemas().alter_schema(self.schema_ident, *changes)
        self.assertEqual(
            schema_new.properties().get(self.schema_properties_key2),
            schema_propertie_new_value,
        )
        self.assertTrue(self.schema_properties_key1 not in schema_new.properties())
