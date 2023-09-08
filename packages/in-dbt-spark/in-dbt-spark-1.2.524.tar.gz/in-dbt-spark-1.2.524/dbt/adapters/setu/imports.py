import importlib

from dbt.events import AdapterLogger

logger = AdapterLogger("Spark")


class SetuCluster:
    """Module imports from in-dbt MP"""

    def __init__(self, cluster: str = None):
        self.cluster = cluster
        try:
            self.cluster_impl = importlib.import_module("linkedin.indbt.utils.setu_cluster")
        except Exception as e:
            logger.error(
                "Error while importing linkedin.indbt.utils.setu_cluster module,"
                "Please reach out to indbt on-call for support"
            )
            raise ModuleNotFoundError(e)

    def get_url(self):
        """
        Returns setu cluster URL based on platform
        """
        return self.cluster_impl.get_url(self.cluster)

    def get_grestin_certs_for_biz_machines(self):
        """
        Create & get grestin certs for users
        """
        return self.cluster_impl.get_grestin_certs(self.cluster)
