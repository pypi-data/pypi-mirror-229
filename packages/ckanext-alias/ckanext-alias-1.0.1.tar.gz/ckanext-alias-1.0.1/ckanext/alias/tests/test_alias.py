from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
import ckan.tests.factories as factories
import pytest
from ckan.tests.helpers import call_action

import ckanext.alias.config as alias_config
import ckanext.alias.utils as alias_utils


@pytest.fixture
def sysadmin_env():
    user = factories.SysadminWithToken()
    env = {"Authorization": user["token"]}  # type: ignore
    return env


@pytest.mark.usefixtures("with_plugins")
class TestAliasConfiguration:
    @pytest.mark.ckan_config("ckanext.alias.dataset_types", "package")
    def test_extension_is_misconfigured(self):
        with pytest.raises(AssertionError):
            alias_utils.extension_is_configured()

    @pytest.mark.ckan_config("ckanext.alias.dataset_types", "dataset")
    def test_extension_is_configured_properly(self):
        alias_utils.extension_is_configured()


@pytest.mark.usefixtures("reset_db_once", "clean_index", "with_plugins")
class TestAutomaticAlias:
    @pytest.mark.ckan_config("ckanext.alias.autosave_alias", "true")
    def test_automatic_alias_is_enabled(self):
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore
        old_name = dataset["name"]

        dataset = call_action("package_patch", id=dataset["id"], name="name-1")
        assert dataset[alias_config.get_alias_fieldname()] == [old_name]

        dataset = call_action("package_patch", id=dataset["id"], name="name-2")
        assert len(dataset[alias_config.get_alias_fieldname()]) == 2
        assert old_name in dataset[alias_config.get_alias_fieldname()]
        assert "name-1" in dataset[alias_config.get_alias_fieldname()]

    def test_automatic_alias_is_disabled_by_default(self):
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore

        dataset = call_action("package_patch", id=dataset["id"], name="new_name")

        assert alias_config.get_alias_fieldname() not in dataset


@pytest.mark.usefixtures("reset_db_once", "clean_index", "with_plugins")
class TestAliasRedirect:
    def test_without_alias(self, app):
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore

        response = app.get(tk.url_for("dataset.read", id=dataset["name"]))
        assert response.status_code == 200

        response = app.get(tk.url_for("dataset.read", id="xxx"))
        assert response.status_code == 404

    def test_with_alias(self, app):
        dataset: dict[str, Any] = factories.Dataset(alias="xxx")  # type: ignore

        response = app.get(tk.url_for("dataset.read", id=dataset["name"]))
        assert response.status_code == 200

        response = app.get(tk.url_for("dataset.read", id="xxx"))
        assert response.status_code == 200

    def test_with_multiple_aliases(self, app):
        test_aliases = ["alias1", "alias2"]
        dataset: dict[str, Any] = factories.Dataset(alias=test_aliases)  # type: ignore

        response = app.get(tk.url_for("dataset.read", id=dataset["name"]))
        assert response.status_code == 200

        for alias in test_aliases:
            response = app.get(tk.url_for("dataset.read", id=alias))
            assert response.status_code == 200


@pytest.mark.usefixtures("reset_db_once", "clean_index", "with_plugins")
class TestAliasValidators:
    def test_alias_is_not_unique(self):
        with pytest.raises(
            tk.ValidationError, match="Alias must be unique. Remove duplicates"
        ):
            factories.Dataset(alias=["alias", "alias"])

    def test_alias_is_occupied(self):
        factories.Dataset(alias=["alias"])

        with pytest.raises(
            tk.ValidationError, match="Alias 'alias' is already occupied"
        ):
            factories.Dataset(alias=["alias"])

    def test_name_is_occupied_by_alias(self):
        factories.Dataset(alias=["alias"])

        with pytest.raises(
            tk.ValidationError, match="Name 'alias' is already occupied by an alias"
        ):
            factories.Dataset(name="alias")

    @pytest.mark.parametrize(
        ("alias", "valid"),
        [
            ("new-alias", True),
            ("one-two-tree", True),
            ("new_alias", True),
            ("123", True),
            ("not an alias", False),
            ("$100", False),
        ],
    )
    def test_alias_must_be_proper_slug(self, alias: str, valid: bool):
        if valid:
            factories.Dataset(alias=alias)
        else:
            with pytest.raises(tk.ValidationError):
                factories.Dataset(alias=alias)

    def test_alias_is_occupied_by_name(self):
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore

        with pytest.raises(
            tk.ValidationError, match="Alias points to an existing dataset name or ID"
        ):
            factories.Dataset(alias=dataset["name"])

    def test_alias_is_occupied_by_id(self):
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore

        with pytest.raises(
            tk.ValidationError, match="Alias points to an existing dataset name or ID"
        ):
            factories.Dataset(alias=dataset["id"])

    def test_allow_setting_alias_same_as_current_pkg_name_or_id(self):
        """Why do we need it? We have a autoalias creating feature. When the user
        updates the dataset and changing the `name`, we are saving it as alias."""
        dataset: dict[str, Any] = factories.Dataset()  # type: ignore

        dataset = call_action("package_patch", id=dataset["id"], alias=dataset["name"])
        dataset = call_action("package_patch", id=dataset["id"], alias=dataset["id"])


@pytest.mark.usefixtures("reset_db_once", "clean_index", "with_plugins")
class TestAliasView:
    def test_new_endpoint_is_accessible(self, app, sysadmin_env):
        response = app.get(tk.url_for("dataset.new"), extra_environ=sysadmin_env)

        assert response.status_code == 200
        assert "/dataset/new" in response.request.url

        response = app.post(
            tk.url_for("dataset.new"),
            extra_environ=sysadmin_env,
            data={
                "name": "new-dataset",
            },
            follow_redirects=False,
        )

        assert call_action("package_show", id="new-dataset")
