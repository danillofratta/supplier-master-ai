from __future__ import annotations

from urllib.parse import urlparse


class OpenSearchClientConfigurationError(RuntimeError):
    pass


def create_opensearch_client(
    *,
    endpoint: str,
    region: str,
    service: str = "aoss",
):
    """Create an IAM/SigV4 authenticated OpenSearch client.

    Imports AWS/OpenSearch SDKs lazily so the API can start without the
    optional retrieval dependencies installed.
    """
    try:
        import boto3
        from opensearchpy import (
            AWSV4SignerAuth,
            OpenSearch,
            RequestsHttpConnection,
        )
    except ModuleNotFoundError as exc:
        raise OpenSearchClientConfigurationError(
            "OpenSearch support is not installed. Install the 'retrieval' extra."
        ) from exc

    parsed = urlparse(endpoint)
    host = parsed.hostname or endpoint.replace("https://", "").replace("http://", "")
    if not host:
        raise OpenSearchClientConfigurationError("OPENSEARCH_ENDPOINT is invalid.")

    credentials = boto3.Session().get_credentials()
    if credentials is None:
        raise OpenSearchClientConfigurationError(
            "AWS credentials are required to access Amazon OpenSearch."
        )

    auth = AWSV4SignerAuth(credentials, region, service)

    return OpenSearch(
        hosts=[{"host": host, "port": parsed.port or 443}],
        http_auth=auth,
        use_ssl=(parsed.scheme != "http"),
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )
