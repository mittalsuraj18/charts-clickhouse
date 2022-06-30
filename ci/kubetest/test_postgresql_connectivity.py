import pytest

from helpers.utils import (
    NAMESPACE,
    cleanup_k8s,
    create_namespace_if_not_exists,
    exec_subprocess,
    install_chart,
    install_custom_resources,
    wait_for_pods_to_be_ready,
)

VALUES_INTERNAL_POSTGRESQL_OVERRIDES = """
postgresql:
  nameOverride: kubetest-pg
  postgresqlDatabase: kubetest_db
  postgresqlPassword: kubetest_password
"""

VALUES_INTERNAL_POSTGRESQL_WITH_EXISTING_SECRET = """
postgresql:
  existingSecret: postgresql-existing-secret
"""

VALUES_EXTERNAL_POSTGRESQL_WITH_PASSWORD = """
postgresql:
  enabled: false

externalPostgresql:
  postgresqlHost: "postgresql-external.posthog.svc.cluster.local"
  postgresqlDatabase: kubetest_db
  postgresqlUsername: kubetest_user
  postgresqlPassword: kubetest_password
"""

VALUES_EXTERNAL_POSTGRESQL_WITH_EXISTING_SECRET = """
postgresql:
  enabled: false

externalPostgresql:
  postgresqlHost: "postgresql-external.posthog.svc.cluster.local"
  postgresqlDatabase: kubetest_db
  postgresqlUsername: kubetest_user

  existingSecret: postgresql-existing-secret
  existingSecretPasswordKey: postgresql-password
"""


@pytest.mark.parametrize(
    "values,resources_to_install",
    [
        pytest.param("", [], id="INTERNAL_POSTGRESQL_DEFAULTS"),
        pytest.param(VALUES_INTERNAL_POSTGRESQL_OVERRIDES, [], id="INTERNAL_POSTGRESQL_OVERRIDES"),
        pytest.param(
            VALUES_INTERNAL_POSTGRESQL_WITH_EXISTING_SECRET,
            ["./custom_k8s_resources/postgresql_existing_secret.yaml"],
            id="INTERNAL_POSTGRESQL_WITH_EXISTING_SECRET",
        ),
        pytest.param(
            VALUES_EXTERNAL_POSTGRESQL_WITH_PASSWORD,
            ["./custom_k8s_resources/postgresql_external.yaml"],
            id="EXTERNAL_POSTGRESQL_WITH_PASSWORD",
        ),
        pytest.param(
            VALUES_EXTERNAL_POSTGRESQL_WITH_EXISTING_SECRET,
            [
                "./custom_k8s_resources/postgresql_existing_secret.yaml",
                "./custom_k8s_resources/postgresql_external.yaml",
            ],
            id="EXTERNAL_POSTGRESQL_WITH_EXISTING_SECRET",
        ),
    ],
)
def test_can_connect_from_web_pod(values, resources_to_install, kube):
    cleanup_k8s()
    exec_subprocess("kubectl delete pvc --all --all-namespaces")
    create_namespace_if_not_exists()

    for resource in resources_to_install:
        install_custom_resources(resource)

    install_chart(values)
    wait_for_pods_to_be_ready(kube)

