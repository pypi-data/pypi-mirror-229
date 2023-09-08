import pkg_resources

from c8connector import C8Connector, ConfigProperty, ConfigAttributeType, Sample, Schema


class S3TargetConnector(C8Connector):
    """S3TargetConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "S3"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-target-s3"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution("macrometa_target_s3").version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "target"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Send data into a S3 bucket."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        pass

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the given configurations."""
        return []

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        return []

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty(
                "bucket",
                "Bucket",
                ConfigAttributeType.STRING,
                True,
                False,
                description="S3 Bucket Name.",
                placeholder_value="Customers",
            ),
            ConfigProperty(
                "region",
                "Region",
                ConfigAttributeType.STRING,
                True,
                False,
                description="AWS region of the bucket.",
                placeholder_value="us-east-2",
            ),
            ConfigProperty(
                "profile_name",
                "Profile Name",
                ConfigAttributeType.INT,
                False,
                False,
                description="AWS profile name.",
                placeholder_value="profile",
            ),
            ConfigProperty(
                "access_key",
                "Access Key",
                ConfigAttributeType.PASSWORD,
                True,
                False,
                description="AWS access key.",
                placeholder_value="access key",
            ),
            ConfigProperty(
                "secret_access_key",
                "Secret Access Key",
                ConfigAttributeType.PASSWORD,
                True,
                False,
                description="AWS secret access key.",
                placeholder_value="password",
            ),
            ConfigProperty(
                "format",
                "Format",
                ConfigAttributeType.STRING,
                True,
                True,
                description="Target file format. Supported formats: json, parquet",
                placeholder_value="'json' or 'parquet'",
            ),
            ConfigProperty(
                "prefix",
                "Prefix",
                ConfigAttributeType.STRING,
                False,
                False,
                description="S3 bucket prefix.",
                placeholder_value="/active/",
            ),
            ConfigProperty(
                "batch_flush_interval",
                "Batch Flush Interval (Seconds)",
                ConfigAttributeType.INT,
                False,
                False,
                description="Time between batch flush executions.",
                default_value="60",
            ),
        ]

    def capabilities(self) -> list[str]:
        """Return the capabilities[1] of the connector."""
        return []
