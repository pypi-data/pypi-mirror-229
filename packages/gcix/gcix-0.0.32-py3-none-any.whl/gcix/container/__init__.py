import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

from .. import Image as _Image_e46ac833, Job as _Job_20682b42


@jsii.data_type(
    jsii_type="@gcix/gcix.container.AWSRegistryProps",
    jsii_struct_bases=[],
    name_mapping={"account_id": "accountId", "region": "region"},
)
class AWSRegistryProps:
    def __init__(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: AWS account id. Default: AWSAccount.awsAccountId()
        :param region: AWS region where the ECR repository lives in. Default: AWSAccount.awsRegion()
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70690165055af01ed6463f1d83e17300344a1a45d59ec7b9f16882e9308da882)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account_id is not None:
            self._values["account_id"] = account_id
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''AWS account id.

        :default: AWSAccount.awsAccountId()
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''AWS region where the ECR repository lives in.

        :default: AWSAccount.awsRegion()
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AWSRegistryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gcix/gcix.container.CraneCopyProps",
    jsii_struct_bases=[],
    name_mapping={
        "dst_registry": "dstRegistry",
        "src_registry": "srcRegistry",
        "docker_client_config": "dockerClientConfig",
        "job_name": "jobName",
        "job_stage": "jobStage",
    },
)
class CraneCopyProps:
    def __init__(
        self,
        *,
        dst_registry: builtins.str,
        src_registry: builtins.str,
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dst_registry: Registry URL to copy container image to.
        :param src_registry: Registry URL to copy container image from.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__283b893e3831d11cacf41e61a68451d11197db97ea7dbe634f0b7a1c8a4b2556)
            check_type(argname="argument dst_registry", value=dst_registry, expected_type=type_hints["dst_registry"])
            check_type(argname="argument src_registry", value=src_registry, expected_type=type_hints["src_registry"])
            check_type(argname="argument docker_client_config", value=docker_client_config, expected_type=type_hints["docker_client_config"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dst_registry": dst_registry,
            "src_registry": src_registry,
        }
        if docker_client_config is not None:
            self._values["docker_client_config"] = docker_client_config
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage

    @builtins.property
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        result = self._values.get("dst_registry")
        assert result is not None, "Required property 'dst_registry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def src_registry(self) -> builtins.str:
        '''Registry URL to copy container image from.'''
        result = self._values.get("src_registry")
        assert result is not None, "Required property 'src_registry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.'''
        result = self._values.get("docker_client_config")
        return typing.cast(typing.Optional["DockerClientConfig"], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Bootstrap job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the Bootstrap job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CraneCopyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gcix/gcix.container.CranePullProps",
    jsii_struct_bases=[],
    name_mapping={
        "src_registry": "srcRegistry",
        "docker_client_config": "dockerClientConfig",
        "image_name": "imageName",
        "image_tag": "imageTag",
        "job_name": "jobName",
        "job_stage": "jobStage",
        "tar_path": "tarPath",
    },
)
class CranePullProps:
    def __init__(
        self,
        *,
        src_registry: typing.Union[builtins.str, "Registry"],
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_tag: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        tar_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param src_registry: Registry URL to pull container image from.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, to authenticate against given registries. Default: DockerClientConfig with login to the official Docker Hub and expecting credentials given as environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        :param image_name: Container image with namespace to pull from ``srcRegistry``. Default: PredefinedVariables.ciProjectName
        :param image_tag: Tag of the image which will be pulled. Default: latest
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param tar_path: Path where to save the container image tarball. Default: PredefinedVariables.ciProjectDir
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af47f2a968c387561169d8e4411bcf7ea9b8f70b4ae889ba5979fa2cf9b927b)
            check_type(argname="argument src_registry", value=src_registry, expected_type=type_hints["src_registry"])
            check_type(argname="argument docker_client_config", value=docker_client_config, expected_type=type_hints["docker_client_config"])
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument image_tag", value=image_tag, expected_type=type_hints["image_tag"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
            check_type(argname="argument tar_path", value=tar_path, expected_type=type_hints["tar_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "src_registry": src_registry,
        }
        if docker_client_config is not None:
            self._values["docker_client_config"] = docker_client_config
        if image_name is not None:
            self._values["image_name"] = image_name
        if image_tag is not None:
            self._values["image_tag"] = image_tag
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage
        if tar_path is not None:
            self._values["tar_path"] = tar_path

    @builtins.property
    def src_registry(self) -> typing.Union[builtins.str, "Registry"]:
        '''Registry URL to pull container image from.'''
        result = self._values.get("src_registry")
        assert result is not None, "Required property 'src_registry' is missing"
        return typing.cast(typing.Union[builtins.str, "Registry"], result)

    @builtins.property
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        :default:

        DockerClientConfig with login to the official Docker Hub
        and expecting credentials given as environment variables
        ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        result = self._values.get("docker_client_config")
        return typing.cast(typing.Optional["DockerClientConfig"], result)

    @builtins.property
    def image_name(self) -> typing.Optional[builtins.str]:
        '''Container image with namespace to pull from ``srcRegistry``.

        :default: PredefinedVariables.ciProjectName
        '''
        result = self._values.get("image_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tag(self) -> typing.Optional[builtins.str]:
        '''Tag of the image which will be pulled.

        :default: latest
        '''
        result = self._values.get("image_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Bootstrap job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the Bootstrap job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tar_path(self) -> typing.Optional[builtins.str]:
        '''Path where to save the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        result = self._values.get("tar_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CranePullProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gcix/gcix.container.CranePushProps",
    jsii_struct_bases=[],
    name_mapping={
        "dst_registry": "dstRegistry",
        "docker_client_config": "dockerClientConfig",
        "image_name": "imageName",
        "image_tag": "imageTag",
        "job_name": "jobName",
        "job_stage": "jobStage",
        "tar_path": "tarPath",
    },
)
class CranePushProps:
    def __init__(
        self,
        *,
        dst_registry: builtins.str,
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_tag: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        tar_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dst_registry: Registry URL to copy container image to.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, to authenticate against given registries. Defaults to a ``DockerClientConfig`` with login to the official Docker Hub and expecting credentials given as environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        :param image_name: Container image name, searched for in ``imagePath`` and gets ``.tar`` appended. Default: PredefinedVariables.ciProjectName
        :param image_tag: The tag the image will be tagged with. Default: PredefinedVariables.ciCommitTag
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param tar_path: Path where to find the container image tarball. Default: PredefinedVariables.ciProjectDir
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f279a64e767394ea6f700643ba7fa4e3c39b4660a7236b0921fdbf6d52462b4)
            check_type(argname="argument dst_registry", value=dst_registry, expected_type=type_hints["dst_registry"])
            check_type(argname="argument docker_client_config", value=docker_client_config, expected_type=type_hints["docker_client_config"])
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument image_tag", value=image_tag, expected_type=type_hints["image_tag"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
            check_type(argname="argument tar_path", value=tar_path, expected_type=type_hints["tar_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dst_registry": dst_registry,
        }
        if docker_client_config is not None:
            self._values["docker_client_config"] = docker_client_config
        if image_name is not None:
            self._values["image_name"] = image_name
        if image_tag is not None:
            self._values["image_tag"] = image_tag
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage
        if tar_path is not None:
            self._values["tar_path"] = tar_path

    @builtins.property
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        result = self._values.get("dst_registry")
        assert result is not None, "Required property 'dst_registry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        Defaults to a ``DockerClientConfig``
        with login to the official Docker Hub and expecting credentials given as
        environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        result = self._values.get("docker_client_config")
        return typing.cast(typing.Optional["DockerClientConfig"], result)

    @builtins.property
    def image_name(self) -> typing.Optional[builtins.str]:
        '''Container image name, searched for in ``imagePath`` and gets ``.tar`` appended.

        :default: PredefinedVariables.ciProjectName
        '''
        result = self._values.get("image_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tag(self) -> typing.Optional[builtins.str]:
        '''The tag the image will be tagged with.

        :default: PredefinedVariables.ciCommitTag
        '''
        result = self._values.get("image_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Bootstrap job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the Bootstrap job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tar_path(self) -> typing.Optional[builtins.str]:
        '''Path where to find the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        result = self._values.get("tar_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CranePushProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gcix/gcix.container.DiveScanProps",
    jsii_struct_bases=[],
    name_mapping={
        "highest_user_wasted_percent": "highestUserWastedPercent",
        "highest_wasted_bytes": "highestWastedBytes",
        "ignore_errors": "ignoreErrors",
        "image_name": "imageName",
        "image_path": "imagePath",
        "job_name": "jobName",
        "job_stage": "jobStage",
        "lowest_efficiency": "lowestEfficiency",
        "source": "source",
    },
)
class DiveScanProps:
    def __init__(
        self,
        *,
        highest_user_wasted_percent: typing.Optional[jsii.Number] = None,
        highest_wasted_bytes: typing.Optional[jsii.Number] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_path: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        lowest_efficiency: typing.Optional[jsii.Number] = None,
        source: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param highest_user_wasted_percent: Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail. Default: 0.1
        :param highest_wasted_bytes: Highest allowable bytes wasted, otherwise CI validation will fail.
        :param ignore_errors: Ignore image parsing errors and run the analysis anyway. Default: false
        :param image_name: Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``. Default: PredefinedVariables.ciProjectName
        :param image_path: Path to the image can be either a remote container registry, as well as a local path to an image. Default: PredefinedVariables.ciProjectPath
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param lowest_efficiency: Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail. Default: 0.9
        :param source: The container engine to fetch the image from. Allowed values: docker, podman, docker-archive Default: "docker-archive
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af56cecc923ccf6759959ff9339129db7a8008203f8a2629f79606ebf173cd8e)
            check_type(argname="argument highest_user_wasted_percent", value=highest_user_wasted_percent, expected_type=type_hints["highest_user_wasted_percent"])
            check_type(argname="argument highest_wasted_bytes", value=highest_wasted_bytes, expected_type=type_hints["highest_wasted_bytes"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument image_path", value=image_path, expected_type=type_hints["image_path"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
            check_type(argname="argument lowest_efficiency", value=lowest_efficiency, expected_type=type_hints["lowest_efficiency"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if highest_user_wasted_percent is not None:
            self._values["highest_user_wasted_percent"] = highest_user_wasted_percent
        if highest_wasted_bytes is not None:
            self._values["highest_wasted_bytes"] = highest_wasted_bytes
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if image_name is not None:
            self._values["image_name"] = image_name
        if image_path is not None:
            self._values["image_path"] = image_path
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage
        if lowest_efficiency is not None:
            self._values["lowest_efficiency"] = lowest_efficiency
        if source is not None:
            self._values["source"] = source

    @builtins.property
    def highest_user_wasted_percent(self) -> typing.Optional[jsii.Number]:
        '''Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.1
        '''
        result = self._values.get("highest_user_wasted_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def highest_wasted_bytes(self) -> typing.Optional[jsii.Number]:
        '''Highest allowable bytes wasted, otherwise CI validation will fail.'''
        result = self._values.get("highest_wasted_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''Ignore image parsing errors and run the analysis anyway.

        :default: false
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def image_name(self) -> typing.Optional[builtins.str]:
        '''Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``.

        :default: PredefinedVariables.ciProjectName
        '''
        result = self._values.get("image_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_path(self) -> typing.Optional[builtins.str]:
        '''Path to the image can be either a remote container registry, as well as a local path to an image.

        :default: PredefinedVariables.ciProjectPath
        '''
        result = self._values.get("image_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Bootstrap job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the Bootstrap job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lowest_efficiency(self) -> typing.Optional[jsii.Number]:
        '''Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.9
        '''
        result = self._values.get("lowest_efficiency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''The container engine to fetch the image from.

        Allowed values: docker, podman, docker-archive

        :default: "docker-archive
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DiveScanProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gcix/gcix.container.DockerClientConfigProps",
    jsii_struct_bases=[],
    name_mapping={"config_file_path": "configFilePath"},
)
class DockerClientConfigProps:
    def __init__(
        self,
        *,
        config_file_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_file_path: Docker client config path. Default: $HOME/.docker/config.json
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__206d2b583e918e93a1ff212d6af4cd76afeb3ac91bd0bf5e2193df801f76b70d)
            check_type(argname="argument config_file_path", value=config_file_path, expected_type=type_hints["config_file_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_file_path is not None:
            self._values["config_file_path"] = config_file_path

    @builtins.property
    def config_file_path(self) -> typing.Optional[builtins.str]:
        '''Docker client config path.

        :default: $HOME/.docker/config.json
        '''
        result = self._values.get("config_file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerClientConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@gcix/gcix.container.ICraneCopy")
class ICraneCopy(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        ...

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> builtins.str:
        '''Registry URL to copy container image from.'''
        ...

    @src_registry.setter
    def src_registry(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.'''
        ...

    @docker_client_config.setter
    def docker_client_config(
        self,
        value: typing.Optional["DockerClientConfig"],
    ) -> None:
        ...


class _ICraneCopyProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.ICraneCopy"

    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        return typing.cast(builtins.str, jsii.get(self, "dstRegistry"))

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca99b3afd8175b7d4f020c4c9e008e634a6bf8ee72b9349f778e54a8100523a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dstRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> builtins.str:
        '''Registry URL to copy container image from.'''
        return typing.cast(builtins.str, jsii.get(self, "srcRegistry"))

    @src_registry.setter
    def src_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83dd0fd5c0a2473ae269ae3cbacd9ed5a8efef8426c98b32c6336a169029edf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.'''
        return typing.cast(typing.Optional["DockerClientConfig"], jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(
        self,
        value: typing.Optional["DockerClientConfig"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__572a8f78cc2839ffe9780649d73c01c2c2eeaedbebde024e455caea88ec08560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICraneCopy).__jsii_proxy_class__ = lambda : _ICraneCopyProxy


@jsii.interface(jsii_type="@gcix/gcix.container.ICranePull")
class ICranePull(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        :default:

        DockerClientConfig with login to the official Docker Hub
        and expecting credentials given as environment variables
        ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        ...

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image with namespace to pull from ``srcRegistry``.

        :default: PredefinedVariables.ciProjectName
        '''
        ...

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''Tag of the image which will be pulled.

        :default: latest
        '''
        ...

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> typing.Union[builtins.str, "Registry"]:
        '''Registry URL to pull container image from.'''
        ...

    @src_registry.setter
    def src_registry(self, value: typing.Union[builtins.str, "Registry"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to save the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        ...

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        ...


class _ICranePullProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.ICranePull"

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        :default:

        DockerClientConfig with login to the official Docker Hub
        and expecting credentials given as environment variables
        ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        return typing.cast("DockerClientConfig", jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b26b506fdcc8eaa9939599dd8489a2249519cb16cc776239041a52106891cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image with namespace to pull from ``srcRegistry``.

        :default: PredefinedVariables.ciProjectName
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99bed8506136c090c0a09432835eef1925ccb69f3d751dffb59027f5366e32d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''Tag of the image which will be pulled.

        :default: latest
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageTag"))

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cce4f64fff958d19283260f72458ea249140b49ba9e1e05a0e7cfe370cb34970)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageTag", value)

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> typing.Union[builtins.str, "Registry"]:
        '''Registry URL to pull container image from.'''
        return typing.cast(typing.Union[builtins.str, "Registry"], jsii.get(self, "srcRegistry"))

    @src_registry.setter
    def src_registry(self, value: typing.Union[builtins.str, "Registry"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5baeec5ec1b0e913e04e73cc573a5be67b6200667837d053dc99c81f8136f8bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to save the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        return typing.cast(builtins.str, jsii.get(self, "tarPath"))

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38dae25943a7ff0eebcd64fbee4b63d00d9ab3a05fc8dfd0368df7dc5c1c61f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tarPath", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICranePull).__jsii_proxy_class__ = lambda : _ICranePullProxy


@jsii.interface(jsii_type="@gcix/gcix.container.ICranePush")
class ICranePush(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        Defaults to a ``DockerClientConfig``
        with login to the official Docker Hub and expecting credentials given as
        environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        ...

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        ...

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image name, searched for in ``imagePath`` and gets ``.tar`` appended.

        :default: PredefinedVariables.ciProjectName
        '''
        ...

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''The tag the image will be tagged with.

        :default: PredefinedVariables.ciCommitTag
        '''
        ...

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to find the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        ...

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        ...


class _ICranePushProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.ICranePush"

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        Defaults to a ``DockerClientConfig``
        with login to the official Docker Hub and expecting credentials given as
        environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        return typing.cast("DockerClientConfig", jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ec746d6937d9d03d7509b01e47b2584cf0ada28b0820ce9d91dff6652f83e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)

    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        return typing.cast(builtins.str, jsii.get(self, "dstRegistry"))

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427ddd0e70a8eae02188adb4ddaefd1934bf84dacc91f364a9ac0ff3b603db37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dstRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image name, searched for in ``imagePath`` and gets ``.tar`` appended.

        :default: PredefinedVariables.ciProjectName
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d134ee48b532e485915f3ee98f970d1363ce9cb16e110f85033b752fe51e001e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''The tag the image will be tagged with.

        :default: PredefinedVariables.ciCommitTag
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageTag"))

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853d7fe77aaa83cac92bdda53480c907e1f13eb8e7fb19f4219d21e175d5faa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageTag", value)

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to find the container image tarball.

        :default: PredefinedVariables.ciProjectDir
        '''
        return typing.cast(builtins.str, jsii.get(self, "tarPath"))

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b2e53be5f9d444680eea46c38ae9a84c2ea75ecc5f0917f19a459210b7d2f6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tarPath", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICranePush).__jsii_proxy_class__ = lambda : _ICranePushProxy


@jsii.interface(jsii_type="@gcix/gcix.container.IDiveScan")
class IDiveScan(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="highestUserWastedPercent")
    def highest_user_wasted_percent(self) -> jsii.Number:
        '''Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.1
        '''
        ...

    @highest_user_wasted_percent.setter
    def highest_user_wasted_percent(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="ignoreErrors")
    def ignore_errors(self) -> builtins.bool:
        '''Ignore image parsing errors and run the analysis anyway.

        :default: false
        '''
        ...

    @ignore_errors.setter
    def ignore_errors(self, value: builtins.bool) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``.

        :default: PredefinedVariables.ciProjectName
        '''
        ...

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="imagePath")
    def image_path(self) -> builtins.str:
        '''Path to the image can be either a remote container registry, as well as a local path to an image.

        :default: PredefinedVariables.ciProjectPath
        '''
        ...

    @image_path.setter
    def image_path(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="lowestEfficiency")
    def lowest_efficiency(self) -> jsii.Number:
        '''Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.9
        '''
        ...

    @lowest_efficiency.setter
    def lowest_efficiency(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''The container engine to fetch the image from.

        Allowed values: docker, podman, docker-archive

        :default: docker-archive
        '''
        ...

    @source.setter
    def source(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="highestWastedBytes")
    def highest_wasted_bytes(self) -> typing.Optional[jsii.Number]:
        '''Highest allowable bytes wasted, otherwise CI validation will fail.'''
        ...

    @highest_wasted_bytes.setter
    def highest_wasted_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IDiveScanProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.IDiveScan"

    @builtins.property
    @jsii.member(jsii_name="highestUserWastedPercent")
    def highest_user_wasted_percent(self) -> jsii.Number:
        '''Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.1
        '''
        return typing.cast(jsii.Number, jsii.get(self, "highestUserWastedPercent"))

    @highest_user_wasted_percent.setter
    def highest_user_wasted_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe71cb94e2e06adab49f829f2ebfdbea30b54bf73742ece0aded57e3b47f4121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "highestUserWastedPercent", value)

    @builtins.property
    @jsii.member(jsii_name="ignoreErrors")
    def ignore_errors(self) -> builtins.bool:
        '''Ignore image parsing errors and run the analysis anyway.

        :default: false
        '''
        return typing.cast(builtins.bool, jsii.get(self, "ignoreErrors"))

    @ignore_errors.setter
    def ignore_errors(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81db5595c647596525c7ee87df16f1a9f3e201fe62d545ab09354b1658ca7794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreErrors", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``.

        :default: PredefinedVariables.ciProjectName
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ad28a33ef8749b49df20b2504a2caf1791478806d44864e45f63b7613c0ae87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imagePath")
    def image_path(self) -> builtins.str:
        '''Path to the image can be either a remote container registry, as well as a local path to an image.

        :default: PredefinedVariables.ciProjectPath
        '''
        return typing.cast(builtins.str, jsii.get(self, "imagePath"))

    @image_path.setter
    def image_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cde47e48e379e35ebb11187e5bddde8752550725efd4e56c78a39234e3fa8340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePath", value)

    @builtins.property
    @jsii.member(jsii_name="lowestEfficiency")
    def lowest_efficiency(self) -> jsii.Number:
        '''Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail.

        :default: 0.9
        '''
        return typing.cast(jsii.Number, jsii.get(self, "lowestEfficiency"))

    @lowest_efficiency.setter
    def lowest_efficiency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be88fcd6aff5e5b4d57e11d1636301dd72fe2a84d3f18f1b405a131cc2321849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lowestEfficiency", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''The container engine to fetch the image from.

        Allowed values: docker, podman, docker-archive

        :default: docker-archive
        '''
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6e1c3f3ab655b91291ea50630f1e7f412162f94756023c5596cdbc349155585)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="highestWastedBytes")
    def highest_wasted_bytes(self) -> typing.Optional[jsii.Number]:
        '''Highest allowable bytes wasted, otherwise CI validation will fail.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "highestWastedBytes"))

    @highest_wasted_bytes.setter
    def highest_wasted_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd759d2dcce813e15442e74e2118677cf9eec201f2b3c60db19d44e56e4092cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "highestWastedBytes", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDiveScan).__jsii_proxy_class__ = lambda : _IDiveScanProxy


@jsii.interface(jsii_type="@gcix/gcix.container.IDockerClientConfig")
class IDockerClientConfig(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IDockerClientConfigType":
        '''Docker client configuration.'''
        ...

    @config.setter
    def config(self, value: "IDockerClientConfigType") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="configFilePath")
    def config_file_path(self) -> builtins.str:
        '''Docker client config path.

        :default: $HOME/.docker/config.json
        '''
        ...

    @config_file_path.setter
    def config_file_path(self, value: builtins.str) -> None:
        ...


class _IDockerClientConfigProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.IDockerClientConfig"

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IDockerClientConfigType":
        '''Docker client configuration.'''
        return typing.cast("IDockerClientConfigType", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IDockerClientConfigType") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e083816c6ae221d335e5ff8ce0e91aa7f1e31492a64baf65024fe45cd17037fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value)

    @builtins.property
    @jsii.member(jsii_name="configFilePath")
    def config_file_path(self) -> builtins.str:
        '''Docker client config path.

        :default: $HOME/.docker/config.json
        '''
        return typing.cast(builtins.str, jsii.get(self, "configFilePath"))

    @config_file_path.setter
    def config_file_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd7a975cf87bb5d079e0e97120574ec688b6767aedfbaacb31d43ca74d1e4788)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configFilePath", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDockerClientConfig).__jsii_proxy_class__ = lambda : _IDockerClientConfigProxy


@jsii.interface(jsii_type="@gcix/gcix.container.IDockerClientConfigType")
class IDockerClientConfigType(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="auths")
    def auths(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        ...

    @auths.setter
    def auths(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="credHelpers")
    def cred_helpers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        ...

    @cred_helpers.setter
    def cred_helpers(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="credsStore")
    def creds_store(self) -> typing.Optional[builtins.str]:
        ...

    @creds_store.setter
    def creds_store(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="rawInput")
    def raw_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        ...

    @raw_input.setter
    def raw_input(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        ...


class _IDockerClientConfigTypeProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.container.IDockerClientConfigType"

    @builtins.property
    @jsii.member(jsii_name="auths")
    def auths(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "auths"))

    @auths.setter
    def auths(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c06e68bf27701f47e2c6385823c047b7c48641502ed2b70c2e6cb00bf4ff745)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auths", value)

    @builtins.property
    @jsii.member(jsii_name="credHelpers")
    def cred_helpers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "credHelpers"))

    @cred_helpers.setter
    def cred_helpers(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fbecbff16e0ecee4e2f306a4eaf894e4c91614f6ff695a7a129b9ea08b16ed3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credHelpers", value)

    @builtins.property
    @jsii.member(jsii_name="credsStore")
    def creds_store(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credsStore"))

    @creds_store.setter
    def creds_store(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82864bc1bc4d58efa2a54428508f6ebc1c52cfd22adf629cbd02e1c714987e18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credsStore", value)

    @builtins.property
    @jsii.member(jsii_name="rawInput")
    def raw_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "rawInput"))

    @raw_input.setter
    def raw_input(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f757d69a2d460924dab774a4f874fe7a6bcc483a62e890ea65eaa6e060088dfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rawInput", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDockerClientConfigType).__jsii_proxy_class__ = lambda : _IDockerClientConfigTypeProxy


class PredefinedImages(
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.PredefinedImages",
):
    '''The PredefinedImages collection supplies commonly utilized container image objects within the gcix framework.'''

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALPINE_GIT")
    def ALPINE_GIT(cls) -> _Image_e46ac833:
        '''A predefined Alpine Git container image object.

        This image is useful for Git operations within containers.
        '''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "ALPINE_GIT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="BUSYBOX")
    def BUSYBOX(cls) -> _Image_e46ac833:
        '''A predefined Busybox container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "BUSYBOX"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CRANE")
    def CRANE(cls) -> _Image_e46ac833:
        '''A predefined Crane container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "CRANE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DIVE")
    def DIVE(cls) -> _Image_e46ac833:
        '''A predefined Dive container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "DIVE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GCIP")
    def GCIP(cls) -> _Image_e46ac833:
        '''A predefined GCIP container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "GCIP"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GCIX")
    def GCIX(cls) -> _Image_e46ac833:
        '''A predefined GCIX container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "GCIX"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KANIKO")
    def KANIKO(cls) -> _Image_e46ac833:
        '''A predefined Kaniko container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "KANIKO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRIVY")
    def TRIVY(cls) -> _Image_e46ac833:
        '''A predefined Trivy container image object.'''
        return typing.cast(_Image_e46ac833, jsii.sget(cls, "TRIVY"))


class Registry(metaclass=jsii.JSIIMeta, jsii_type="@gcix/gcix.container.Registry"):
    '''Container registry urls constants.'''

    @jsii.member(jsii_name="aws")
    @builtins.classmethod
    def aws(
        cls,
        *,
        account_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Amazon Elastic Container Registry (ECR).

        If neither ``accountId`` nor ``region`` is given, the method attempts to
        evaluate ``accountId`` and ``region`` using helper functions from ``aws.AWSAccount``.
        If either of the helper functions does provide a valid value, a ``ValueError`` or ``KeyError`` exception will be raised.

        :param account_id: AWS account id. Default: AWSAccount.awsAccountId()
        :param region: AWS region where the ECR repository lives in. Default: AWSAccount.awsRegion()

        :return:

        Elastic Container Registry URL in the format of
        **${awsAccountId}.dkr.ecr.${region}.amazonaws.com**.

        :throws: {Error} If no region was found in ``aws.AWSAccount.awsRegion()``.
        '''
        props = AWSRegistryProps(account_id=account_id, region=region)

        return typing.cast(builtins.str, jsii.sinvoke(cls, "aws", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DOCKER")
    def DOCKER(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DOCKER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GCR")
    def GCR(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "GCR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="QUAY")
    def QUAY(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "QUAY"))


@jsii.implements(ICraneCopy)
class CraneCopy(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.CraneCopy",
):
    '''Creates a job to copy container images with ``crane``. See ```crane`` <https://github.com/google/go-containerregistry/tree/main/cmd/crane>`_.

    Copying an image is useful, if you want to have container images as close
    as possible to your cluster or servers.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: crane-copy
    - stage: deploy
    - image: PredefinedImages.CRANE
    '''

    def __init__(
        self,
        *,
        dst_registry: builtins.str,
        src_registry: builtins.str,
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dst_registry: Registry URL to copy container image to.
        :param src_registry: Registry URL to copy container image from.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        '''
        props = CraneCopyProps(
            dst_registry=dst_registry,
            src_registry=src_registry,
            docker_client_config=docker_client_config,
            job_name=job_name,
            job_stage=job_stage,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Any:
        '''Returns a representation of any object which implements ``IBase``.

        The rendered representation is used by the ``gcix`` to dump it
        in YAML format as part of the ``.gitlab-ci.yml`` pipeline.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        return typing.cast(builtins.str, jsii.get(self, "dstRegistry"))

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f253d7757bc4254083e30859b29145202b6682b597a7317be2303f85edaed0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dstRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> builtins.str:
        '''Registry URL to copy container image from.'''
        return typing.cast(builtins.str, jsii.get(self, "srcRegistry"))

    @src_registry.setter
    def src_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83c4b4b3430b6882f7fce62f48611ac8b4160a793c02c7e2d390d91f5342c8ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> typing.Optional["DockerClientConfig"]:
        '''Creates the Docker configuration file base on objects settings, used by crane to authenticate against given registries.'''
        return typing.cast(typing.Optional["DockerClientConfig"], jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(
        self,
        value: typing.Optional["DockerClientConfig"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853cf50eb2cf5284e5f43ff03be1857f10d0f46c3e97c0dbfa69004467ccd865)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)


@jsii.implements(ICranePull)
class CranePull(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.CranePull",
):
    '''Creates a job to pull container image from remote container registry with ``crane``.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: crane
    - stage: pull
    - image: PredefinedImages.CRANE
    '''

    def __init__(
        self,
        *,
        src_registry: typing.Union[builtins.str, Registry],
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_tag: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        tar_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param src_registry: Registry URL to pull container image from.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, to authenticate against given registries. Default: DockerClientConfig with login to the official Docker Hub and expecting credentials given as environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        :param image_name: Container image with namespace to pull from ``srcRegistry``. Default: PredefinedVariables.ciProjectName
        :param image_tag: Tag of the image which will be pulled. Default: latest
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param tar_path: Path where to save the container image tarball. Default: PredefinedVariables.ciProjectDir
        '''
        props = CranePullProps(
            src_registry=src_registry,
            docker_client_config=docker_client_config,
            image_name=image_name,
            image_tag=image_tag,
            job_name=job_name,
            job_stage=job_stage,
            tar_path=tar_path,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Any:
        '''Returns a representation of any object which implements ``IBase``.

        The rendered representation is used by the ``gcix`` to dump it
        in YAML format as part of the ``.gitlab-ci.yml`` pipeline.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.'''
        return typing.cast("DockerClientConfig", jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3f05f9ede43dbf97af83473670a3028d41eb17c74c0a35998790dfcbcf7779f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image with namespace to pull from ``srcRegistry``.'''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c04f6d7e0856ea05e199b824d1fef5e77743333145a563615df3b6e24e38a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''Tag of the image which will be pulled.'''
        return typing.cast(builtins.str, jsii.get(self, "imageTag"))

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc52d1cbcbb774ca91c8fe7b76204e751812162fa4f52451e91b4a7dd2c00219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageTag", value)

    @builtins.property
    @jsii.member(jsii_name="srcRegistry")
    def src_registry(self) -> typing.Union[builtins.str, Registry]:
        '''Registry URL to pull container image from.'''
        return typing.cast(typing.Union[builtins.str, Registry], jsii.get(self, "srcRegistry"))

    @src_registry.setter
    def src_registry(self, value: typing.Union[builtins.str, Registry]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c92b854c26778a2e53e5fd7d02e43103e86f5c58f3a4965d756f1c1db56dc9c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to save the container image tarball.'''
        return typing.cast(builtins.str, jsii.get(self, "tarPath"))

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710f217da8e365150a4d44b7525ded0d915488f00e3eba17d7d4aaf3bc2ca7dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tarPath", value)


@jsii.implements(ICranePush)
class CranePush(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.CranePush",
):
    '''Creates a job to push container image to remote container registry with ``crane``.

    The image to copy must be in a ``tarball`` format. It gets validated with crane
    and is pushed to ``dst_registry`` destination registry.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: crane-push
    - stage: deploy
    - image: PredefinedImages.CRANE
    '''

    def __init__(
        self,
        *,
        dst_registry: builtins.str,
        docker_client_config: typing.Optional["DockerClientConfig"] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_tag: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        tar_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dst_registry: Registry URL to copy container image to.
        :param docker_client_config: Creates the Docker configuration file base on objects settings, to authenticate against given registries. Defaults to a ``DockerClientConfig`` with login to the official Docker Hub and expecting credentials given as environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        :param image_name: Container image name, searched for in ``imagePath`` and gets ``.tar`` appended. Default: PredefinedVariables.ciProjectName
        :param image_tag: The tag the image will be tagged with. Default: PredefinedVariables.ciCommitTag
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param tar_path: Path where to find the container image tarball. Default: PredefinedVariables.ciProjectDir
        '''
        props = CranePushProps(
            dst_registry=dst_registry,
            docker_client_config=docker_client_config,
            image_name=image_name,
            image_tag=image_tag,
            job_name=job_name,
            job_stage=job_stage,
            tar_path=tar_path,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Any:
        '''Returns a representation of any object which implements ``IBase``.

        The rendered representation is used by the ``gcix`` to dump it
        in YAML format as part of the ``.gitlab-ci.yml`` pipeline.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="dockerClientConfig")
    def docker_client_config(self) -> "DockerClientConfig":
        '''Creates the Docker configuration file base on objects settings, to authenticate against given registries.

        Defaults to a ``DockerClientConfig``
        with login to the official Docker Hub and expecting credentials given as
        environment variables ``REGISTRY_USER`` and ``REGISTRY_LOGIN``.
        '''
        return typing.cast("DockerClientConfig", jsii.get(self, "dockerClientConfig"))

    @docker_client_config.setter
    def docker_client_config(self, value: "DockerClientConfig") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b240e50c52eeff890833592e36cd4323ce92803e128ca9f1d211521ad7823a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerClientConfig", value)

    @builtins.property
    @jsii.member(jsii_name="dstRegistry")
    def dst_registry(self) -> builtins.str:
        '''Registry URL to copy container image to.'''
        return typing.cast(builtins.str, jsii.get(self, "dstRegistry"))

    @dst_registry.setter
    def dst_registry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e69659a083b47f4fcb86bc9dba5e55c5feff7c5a98afba50b0345f9250655ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dstRegistry", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Container image name, searched for in ``imagePath`` and gets ``.tar`` appended.'''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__964f4192a0d90ea2897d6b0177a51f2e018be9de3f7838e0eeae353375d3b6fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imageTag")
    def image_tag(self) -> builtins.str:
        '''The tag the image will be tagged with.'''
        return typing.cast(builtins.str, jsii.get(self, "imageTag"))

    @image_tag.setter
    def image_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe70150d68a7adbc49d4b4cef8662ee7abe851bc67419fbbe29f96728a645c70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageTag", value)

    @builtins.property
    @jsii.member(jsii_name="tarPath")
    def tar_path(self) -> builtins.str:
        '''Path where to find the container image tarball.'''
        return typing.cast(builtins.str, jsii.get(self, "tarPath"))

    @tar_path.setter
    def tar_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72be2fe328749fcc98e785a7c9bd4a8947866df926aeca145e7ac0d5c4e374b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tarPath", value)


@jsii.implements(IDiveScan)
class DiveScan(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.DiveScan",
):
    '''Scan your images with `wagoodman/dive <https://github.com/wagoodman/dive>`_.

    ``dive`` will scan your container image layers and will output the efficency
    of each layer. You can see which layer and which file is consuming the most
    storage and optimize the layers if possible. It prevents container images
    and its layers beeing polluted with files like apt or yum cache's.
    The output produced by ``dive`` is uploaded as an artifact to the
    GitLab instance.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: dive
    - stage: check
    - image: PredefinedImages.DIVE
    - artifacts: Path 'dive.txt'
    '''

    def __init__(
        self,
        *,
        highest_user_wasted_percent: typing.Optional[jsii.Number] = None,
        highest_wasted_bytes: typing.Optional[jsii.Number] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        image_name: typing.Optional[builtins.str] = None,
        image_path: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        lowest_efficiency: typing.Optional[jsii.Number] = None,
        source: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param highest_user_wasted_percent: Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail. Default: 0.1
        :param highest_wasted_bytes: Highest allowable bytes wasted, otherwise CI validation will fail.
        :param ignore_errors: Ignore image parsing errors and run the analysis anyway. Default: false
        :param image_name: Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``. Default: PredefinedVariables.ciProjectName
        :param image_path: Path to the image can be either a remote container registry, as well as a local path to an image. Default: PredefinedVariables.ciProjectPath
        :param job_name: The name of the Bootstrap job.
        :param job_stage: The stage of the Bootstrap job.
        :param lowest_efficiency: Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail. Default: 0.9
        :param source: The container engine to fetch the image from. Allowed values: docker, podman, docker-archive Default: "docker-archive
        '''
        props = DiveScanProps(
            highest_user_wasted_percent=highest_user_wasted_percent,
            highest_wasted_bytes=highest_wasted_bytes,
            ignore_errors=ignore_errors,
            image_name=image_name,
            image_path=image_path,
            job_name=job_name,
            job_stage=job_stage,
            lowest_efficiency=lowest_efficiency,
            source=source,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Any:
        '''Returns a representation of any object which implements ``IBase``.

        The rendered representation is used by the ``gcix`` to dump it
        in YAML format as part of the ``.gitlab-ci.yml`` pipeline.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="highestUserWastedPercent")
    def highest_user_wasted_percent(self) -> jsii.Number:
        '''Highest allowable percentage of bytes wasted (as a ratio between 0-1), otherwise CI validation will fail.'''
        return typing.cast(jsii.Number, jsii.get(self, "highestUserWastedPercent"))

    @highest_user_wasted_percent.setter
    def highest_user_wasted_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00feadced743630d8fff9e0c98a5aa109a170f97e0798c875aee4ba3138e5d3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "highestUserWastedPercent", value)

    @builtins.property
    @jsii.member(jsii_name="ignoreErrors")
    def ignore_errors(self) -> builtins.bool:
        '''Ignore image parsing errors and run the analysis anyway.'''
        return typing.cast(builtins.bool, jsii.get(self, "ignoreErrors"))

    @ignore_errors.setter
    def ignore_errors(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e2101e114e5cb63051f57e91cd6b02ae1803c957432f222515e1291bf93699e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreErrors", value)

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        '''Name of the container image to scan, if ``source`` is ``docker-archive`` argument gets prefix ``.tar``.'''
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc74e395f342425d17a81a5aa0b965fa5cff57253448e9f008c16d64bffeacf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value)

    @builtins.property
    @jsii.member(jsii_name="imagePath")
    def image_path(self) -> builtins.str:
        '''Path to the image can be either a remote container registry, as well as a local path to an image.'''
        return typing.cast(builtins.str, jsii.get(self, "imagePath"))

    @image_path.setter
    def image_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc2d9f92ed7ed2479318fd3de66586a822f474479721e44c9dcb83573a6520ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePath", value)

    @builtins.property
    @jsii.member(jsii_name="lowestEfficiency")
    def lowest_efficiency(self) -> jsii.Number:
        '''Lowest allowable image efficiency (as a ratio between 0-1), otherwise CI validation will fail.'''
        return typing.cast(jsii.Number, jsii.get(self, "lowestEfficiency"))

    @lowest_efficiency.setter
    def lowest_efficiency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67dfbfb7975e89718235bb870ef7c02c5757d22d2a1599c9432ad7cfdd3bf64a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lowestEfficiency", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''The container engine to fetch the image from.

        Allowed values: docker, podman, docker-archive
        '''
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8c5856866591955ea5a6bceb75c2ac2cbff9be938475dd0c6f00861d3d4f974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="highestWastedBytes")
    def highest_wasted_bytes(self) -> typing.Optional[jsii.Number]:
        '''Highest allowable bytes wasted, otherwise CI validation will fail.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "highestWastedBytes"))

    @highest_wasted_bytes.setter
    def highest_wasted_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e9e7f9db878dcbed1cf0192862548a658efdec7bba7166accfc20e0ace60e2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "highestWastedBytes", value)


@jsii.implements(IDockerClientConfig)
class DockerClientConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.container.DockerClientConfig",
):
    '''Class which represents a docker client configuration.

    After creating an instance of this class you can add new credential helper,
    basic authentication settings or default credential store.
    '''

    def __init__(
        self,
        *,
        config_file_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_file_path: Docker client config path. Default: $HOME/.docker/config.json
        '''
        props = DockerClientConfigProps(config_file_path=config_file_path)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addAuth")
    def add_auth(
        self,
        registry: builtins.str,
        username_env_var: typing.Optional[builtins.str] = None,
        password_env_var: typing.Optional[builtins.str] = None,
    ) -> "DockerClientConfig":
        '''Adds basic authentication ``auths`` setting to the configuration.

        This method acts a little special, because of some security aspects.
        The method, takse three arguments, ``registry``, ``username_env_var`` and ``password_env_var``.
        Arguments ending wit *_env_var, are ment to be available as a ``gcip.Job`` variable.

        :param registry: Name of the container registry to set ``creds_helper`` for.
        :param username_env_var: Name of the environment variable which as the registry username stored.
        :param password_env_var: Name of the environment variable which as the registry password stored.

        :default: REGISTRY_PASSWORD
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a16b4dbc6af5a7a4ba47b59ec2cb53f8fb6ed6b5c3898839e49ed85d425ea61)
            check_type(argname="argument registry", value=registry, expected_type=type_hints["registry"])
            check_type(argname="argument username_env_var", value=username_env_var, expected_type=type_hints["username_env_var"])
            check_type(argname="argument password_env_var", value=password_env_var, expected_type=type_hints["password_env_var"])
        return typing.cast("DockerClientConfig", jsii.invoke(self, "addAuth", [registry, username_env_var, password_env_var]))

    @jsii.member(jsii_name="addCredHelper")
    def add_cred_helper(
        self,
        registry: builtins.str,
        cred_helper: builtins.str,
    ) -> "DockerClientConfig":
        '''Adds a Credentials helper ``credHelpers`` for a registry.

        See `docker login#credential-helpers <https://docs.docker.com/engine/reference/commandline/login/#credential-helpers>`_

        :param registry: Name of the container registry to set ``creds_helper`` for.
        :param cred_helper: Name of the credential helper to use together with the ``registry``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfca338a2c1a05056f09278d2f0db7b0ce9db5c5286249628fdd525526c4db40)
            check_type(argname="argument registry", value=registry, expected_type=type_hints["registry"])
            check_type(argname="argument cred_helper", value=cred_helper, expected_type=type_hints["cred_helper"])
        return typing.cast("DockerClientConfig", jsii.invoke(self, "addCredHelper", [registry, cred_helper]))

    @jsii.member(jsii_name="addRaw")
    def add_raw(
        self,
        raw_input: typing.Mapping[builtins.str, typing.Any],
    ) -> "DockerClientConfig":
        '''Adds arbitrary settings to configuration.

        Be aware and warned! You can overwrite any predefined settings with this method.
        This method is intendet to be used, if non suitable method is available and you
        have to set a configuration setting.

        :param raw_input: Dictionary of non-available settings to be set.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135e6468f74e369fb5865e1eab067d96d6111ef919e2616630228a8d67e6568f)
            check_type(argname="argument raw_input", value=raw_input, expected_type=type_hints["raw_input"])
        return typing.cast("DockerClientConfig", jsii.invoke(self, "addRaw", [raw_input]))

    @jsii.member(jsii_name="assignCredsStore")
    def assign_creds_store(self, creds_store: builtins.str) -> "DockerClientConfig":
        '''Sets the ``credsStore`` setting for clients. See `docker login#credentials-store <https://docs.docker.com/engine/reference/commandline/login/#credentials-store>`_.

        Be aware, that if you set the ``credsStore`` and add creds_helper or
        username and password authentication, those authentication methods
        are not used.

        Clients which can authenticate against a registry can handle the credential
        store itself, mostly you do not want to set the ``credsStore``.
        Use ``credsHelpers`` instead.

        :param creds_store: Should be the suffix of the program to use (i.e. everything after docker-credential-). ``osxkeychain``, to use docker-credential-osxkeychain or ``ecr-login``, to use docker-crendential-ecr-login.

        :return: DockerClientConfig
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cfa1b99ea08ac61e5f6cae6f49e0cfd6be19103a30962e4a55d362648a7c6ad)
            check_type(argname="argument creds_store", value=creds_store, expected_type=type_hints["creds_store"])
        return typing.cast("DockerClientConfig", jsii.invoke(self, "assignCredsStore", [creds_store]))

    @jsii.member(jsii_name="shellCommand")
    def shell_command(self) -> typing.List[builtins.str]:
        '''Renders the shell command for creating the docker client config.

        The render method uses ``json.dumps()`` to dump the configuration as a json
        string and escapes it for the shell. In Jobs which needed the
        configuration the rendered output should be redirected to the appropriate
        destination e.g. ~/.docker/config.json. This ensures, that environment
        variables are substituted.

        :return:

        Returns a list with ``mkdir -p config_file_path`` and a shell escaped JSON string
        echoed to ``config_file_path``/``config_file_name``
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "shellCommand", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IDockerClientConfigType:
        '''Docker client configuration.'''
        return typing.cast(IDockerClientConfigType, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IDockerClientConfigType) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__956c622101e4f8531772774959f890318bfeac5a399ea3bd389ef92cdbd4fa4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value)

    @builtins.property
    @jsii.member(jsii_name="configFilePath")
    def config_file_path(self) -> builtins.str:
        '''Docker client config path.'''
        return typing.cast(builtins.str, jsii.get(self, "configFilePath"))

    @config_file_path.setter
    def config_file_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed52c1fe7e09eedf49e79aea025fe55bde8cc4141e6dbcb7aa1eb47b6c5c261)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configFilePath", value)


__all__ = [
    "AWSRegistryProps",
    "CraneCopy",
    "CraneCopyProps",
    "CranePull",
    "CranePullProps",
    "CranePush",
    "CranePushProps",
    "DiveScan",
    "DiveScanProps",
    "DockerClientConfig",
    "DockerClientConfigProps",
    "ICraneCopy",
    "ICranePull",
    "ICranePush",
    "IDiveScan",
    "IDockerClientConfig",
    "IDockerClientConfigType",
    "PredefinedImages",
    "Registry",
]

publication.publish()

def _typecheckingstub__70690165055af01ed6463f1d83e17300344a1a45d59ec7b9f16882e9308da882(
    *,
    account_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__283b893e3831d11cacf41e61a68451d11197db97ea7dbe634f0b7a1c8a4b2556(
    *,
    dst_registry: builtins.str,
    src_registry: builtins.str,
    docker_client_config: typing.Optional[DockerClientConfig] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af47f2a968c387561169d8e4411bcf7ea9b8f70b4ae889ba5979fa2cf9b927b(
    *,
    src_registry: typing.Union[builtins.str, Registry],
    docker_client_config: typing.Optional[DockerClientConfig] = None,
    image_name: typing.Optional[builtins.str] = None,
    image_tag: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
    tar_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f279a64e767394ea6f700643ba7fa4e3c39b4660a7236b0921fdbf6d52462b4(
    *,
    dst_registry: builtins.str,
    docker_client_config: typing.Optional[DockerClientConfig] = None,
    image_name: typing.Optional[builtins.str] = None,
    image_tag: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
    tar_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af56cecc923ccf6759959ff9339129db7a8008203f8a2629f79606ebf173cd8e(
    *,
    highest_user_wasted_percent: typing.Optional[jsii.Number] = None,
    highest_wasted_bytes: typing.Optional[jsii.Number] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    image_name: typing.Optional[builtins.str] = None,
    image_path: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
    lowest_efficiency: typing.Optional[jsii.Number] = None,
    source: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__206d2b583e918e93a1ff212d6af4cd76afeb3ac91bd0bf5e2193df801f76b70d(
    *,
    config_file_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca99b3afd8175b7d4f020c4c9e008e634a6bf8ee72b9349f778e54a8100523a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83dd0fd5c0a2473ae269ae3cbacd9ed5a8efef8426c98b32c6336a169029edf0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__572a8f78cc2839ffe9780649d73c01c2c2eeaedbebde024e455caea88ec08560(
    value: typing.Optional[DockerClientConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b26b506fdcc8eaa9939599dd8489a2249519cb16cc776239041a52106891cc(
    value: DockerClientConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99bed8506136c090c0a09432835eef1925ccb69f3d751dffb59027f5366e32d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cce4f64fff958d19283260f72458ea249140b49ba9e1e05a0e7cfe370cb34970(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5baeec5ec1b0e913e04e73cc573a5be67b6200667837d053dc99c81f8136f8bb(
    value: typing.Union[builtins.str, Registry],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38dae25943a7ff0eebcd64fbee4b63d00d9ab3a05fc8dfd0368df7dc5c1c61f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ec746d6937d9d03d7509b01e47b2584cf0ada28b0820ce9d91dff6652f83e2(
    value: DockerClientConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427ddd0e70a8eae02188adb4ddaefd1934bf84dacc91f364a9ac0ff3b603db37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d134ee48b532e485915f3ee98f970d1363ce9cb16e110f85033b752fe51e001e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853d7fe77aaa83cac92bdda53480c907e1f13eb8e7fb19f4219d21e175d5faa3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b2e53be5f9d444680eea46c38ae9a84c2ea75ecc5f0917f19a459210b7d2f6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe71cb94e2e06adab49f829f2ebfdbea30b54bf73742ece0aded57e3b47f4121(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81db5595c647596525c7ee87df16f1a9f3e201fe62d545ab09354b1658ca7794(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ad28a33ef8749b49df20b2504a2caf1791478806d44864e45f63b7613c0ae87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde47e48e379e35ebb11187e5bddde8752550725efd4e56c78a39234e3fa8340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be88fcd6aff5e5b4d57e11d1636301dd72fe2a84d3f18f1b405a131cc2321849(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6e1c3f3ab655b91291ea50630f1e7f412162f94756023c5596cdbc349155585(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd759d2dcce813e15442e74e2118677cf9eec201f2b3c60db19d44e56e4092cc(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e083816c6ae221d335e5ff8ce0e91aa7f1e31492a64baf65024fe45cd17037fd(
    value: IDockerClientConfigType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd7a975cf87bb5d079e0e97120574ec688b6767aedfbaacb31d43ca74d1e4788(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c06e68bf27701f47e2c6385823c047b7c48641502ed2b70c2e6cb00bf4ff745(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fbecbff16e0ecee4e2f306a4eaf894e4c91614f6ff695a7a129b9ea08b16ed3(
    value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82864bc1bc4d58efa2a54428508f6ebc1c52cfd22adf629cbd02e1c714987e18(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f757d69a2d460924dab774a4f874fe7a6bcc483a62e890ea65eaa6e060088dfe(
    value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f253d7757bc4254083e30859b29145202b6682b597a7317be2303f85edaed0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c4b4b3430b6882f7fce62f48611ac8b4160a793c02c7e2d390d91f5342c8ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853cf50eb2cf5284e5f43ff03be1857f10d0f46c3e97c0dbfa69004467ccd865(
    value: typing.Optional[DockerClientConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3f05f9ede43dbf97af83473670a3028d41eb17c74c0a35998790dfcbcf7779f(
    value: DockerClientConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1c04f6d7e0856ea05e199b824d1fef5e77743333145a563615df3b6e24e38a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc52d1cbcbb774ca91c8fe7b76204e751812162fa4f52451e91b4a7dd2c00219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92b854c26778a2e53e5fd7d02e43103e86f5c58f3a4965d756f1c1db56dc9c1(
    value: typing.Union[builtins.str, Registry],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710f217da8e365150a4d44b7525ded0d915488f00e3eba17d7d4aaf3bc2ca7dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b240e50c52eeff890833592e36cd4323ce92803e128ca9f1d211521ad7823a(
    value: DockerClientConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e69659a083b47f4fcb86bc9dba5e55c5feff7c5a98afba50b0345f9250655ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__964f4192a0d90ea2897d6b0177a51f2e018be9de3f7838e0eeae353375d3b6fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe70150d68a7adbc49d4b4cef8662ee7abe851bc67419fbbe29f96728a645c70(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72be2fe328749fcc98e785a7c9bd4a8947866df926aeca145e7ac0d5c4e374b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00feadced743630d8fff9e0c98a5aa109a170f97e0798c875aee4ba3138e5d3d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e2101e114e5cb63051f57e91cd6b02ae1803c957432f222515e1291bf93699e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc74e395f342425d17a81a5aa0b965fa5cff57253448e9f008c16d64bffeacf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc2d9f92ed7ed2479318fd3de66586a822f474479721e44c9dcb83573a6520ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67dfbfb7975e89718235bb870ef7c02c5757d22d2a1599c9432ad7cfdd3bf64a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c5856866591955ea5a6bceb75c2ac2cbff9be938475dd0c6f00861d3d4f974(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e9e7f9db878dcbed1cf0192862548a658efdec7bba7166accfc20e0ace60e2a(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a16b4dbc6af5a7a4ba47b59ec2cb53f8fb6ed6b5c3898839e49ed85d425ea61(
    registry: builtins.str,
    username_env_var: typing.Optional[builtins.str] = None,
    password_env_var: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfca338a2c1a05056f09278d2f0db7b0ce9db5c5286249628fdd525526c4db40(
    registry: builtins.str,
    cred_helper: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135e6468f74e369fb5865e1eab067d96d6111ef919e2616630228a8d67e6568f(
    raw_input: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cfa1b99ea08ac61e5f6cae6f49e0cfd6be19103a30962e4a55d362648a7c6ad(
    creds_store: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__956c622101e4f8531772774959f890318bfeac5a399ea3bd389ef92cdbd4fa4c(
    value: IDockerClientConfigType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed52c1fe7e09eedf49e79aea025fe55bde8cc4141e6dbcb7aa1eb47b6c5c261(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
