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

from .. import Job as _Job_20682b42
from ..python import (
    PipInstallRequirementsProps as _PipInstallRequirementsProps_47c04e0d
)


class GitlabScripts(
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.gitlab.GitlabScripts",
):
    '''GitlabScripts Class Documentation.

    The ``GitlabScripts`` class provides utility methods for performing various Git-related actions in the context of GitLab.
    '''

    @jsii.member(jsii_name="cloneRepository")
    @builtins.classmethod
    def clone_repository(
        cls,
        path: builtins.str,
        branch: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Clones a repository from a remote Git server using the Git command.

        :param path: - The path of the repository to clone. Should start with a forward slash ("/").
        :param branch: - (Optional) The branch name to clone from the remote repository. Currently, only "main" is supported.

        :return: A Git clone command as a string with the provided branch and repository path.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bd5b76126699d26330d7dfeb3122212a724ea05dd5a006bbd12e60b24819200)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "cloneRepository", [path, branch]))


@jsii.interface(jsii_type="@gcix/gcix.gitlab.IPagesAsciiDoctor")
class IPagesAsciiDoctor(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="outFile")
    def out_file(self) -> builtins.str:
        '''Output HTML file.'''
        ...

    @out_file.setter
    def out_file(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''Source .adoc files to translate to HTML files.'''
        ...

    @source.setter
    def source(self, value: builtins.str) -> None:
        ...


class _IPagesAsciiDoctorProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.gitlab.IPagesAsciiDoctor"

    @builtins.property
    @jsii.member(jsii_name="outFile")
    def out_file(self) -> builtins.str:
        '''Output HTML file.'''
        return typing.cast(builtins.str, jsii.get(self, "outFile"))

    @out_file.setter
    def out_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd96129bc7b3ec7f5fc2b940829e9c4525d97ed64c6ca6556ea8b654fc40adfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outFile", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''Source .adoc files to translate to HTML files.'''
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daa927abf8a1764801389a1d4bd5ceda060dc48e44bd8f849427f25a3ac33cd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPagesAsciiDoctor).__jsii_proxy_class__ = lambda : _IPagesAsciiDoctorProxy


@jsii.interface(jsii_type="@gcix/gcix.gitlab.IPagesPdoc3")
class IPagesPdoc3(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="module")
    def module(self) -> builtins.str:
        '''The Python module name.

        This may be an import path resolvable in the
        current environment, or a file path to a Python module or package.
        '''
        ...

    @module.setter
    def module(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        '''A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to.

        Defaults to "/".
        '''
        ...

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        ...


class _IPagesPdoc3Proxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.gitlab.IPagesPdoc3"

    @builtins.property
    @jsii.member(jsii_name="module")
    def module(self) -> builtins.str:
        '''The Python module name.

        This may be an import path resolvable in the
        current environment, or a file path to a Python module or package.
        '''
        return typing.cast(builtins.str, jsii.get(self, "module"))

    @module.setter
    def module(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d79360750e78801d011c581261289c9ca486b80b91be49f4327351da5531cd77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "module", value)

    @builtins.property
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        '''A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to.

        Defaults to "/".
        '''
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19da3cfd45526d41641528ea3850429e1ec6fc3b49453102ad980d3707550fd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputPath", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPagesPdoc3).__jsii_proxy_class__ = lambda : _IPagesPdoc3Proxy


@jsii.interface(jsii_type="@gcix/gcix.gitlab.IPagesSphinx")
class IPagesSphinx(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="pip")
    def pip(self) -> typing.Optional[_PipInstallRequirementsProps_47c04e0d]:
        ...

    @pip.setter
    def pip(
        self,
        value: typing.Optional[_PipInstallRequirementsProps_47c04e0d],
    ) -> None:
        ...


class _IPagesSphinxProxy:
    __jsii_type__: typing.ClassVar[str] = "@gcix/gcix.gitlab.IPagesSphinx"

    @builtins.property
    @jsii.member(jsii_name="pip")
    def pip(self) -> typing.Optional[_PipInstallRequirementsProps_47c04e0d]:
        return typing.cast(typing.Optional[_PipInstallRequirementsProps_47c04e0d], jsii.get(self, "pip"))

    @pip.setter
    def pip(
        self,
        value: typing.Optional[_PipInstallRequirementsProps_47c04e0d],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f955d53cb3a7bd57c5a933176e7269b81c87bcfc92576b689bd946dae41f8555)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pip", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPagesSphinx).__jsii_proxy_class__ = lambda : _IPagesSphinxProxy


@jsii.implements(IPagesAsciiDoctor)
class PagesAsciiDoctor(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.gitlab.PagesAsciiDoctor",
):
    '''Translate the AsciiDoc source FILE as Gitlab Pages HTML5 file.

    Runs ``asciidoctor {source} -o public{out_file}``and stores the output
    as artifact under the ``public`` directory.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: asciidoctor-pages
    - stage: build
    - image: ruby:3-alpine
    - artifacts: Path 'public'
    '''

    def __init__(
        self,
        *,
        out_file: builtins.str,
        source: builtins.str,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param out_file: Output HTML file.
        :param source: Source .adoc files to translate to HTML files.
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        '''
        props = PagesAsciiDoctorProps(
            out_file=out_file, source=source, job_name=job_name, job_stage=job_stage
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
    @jsii.member(jsii_name="outFile")
    def out_file(self) -> builtins.str:
        '''Output HTML file.'''
        return typing.cast(builtins.str, jsii.get(self, "outFile"))

    @out_file.setter
    def out_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2d1861ba62c52ef1ac9c3754a95089b61216ff321934e5ba1b2bc9104bdf509)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outFile", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''Source .adoc files to translate to HTML files.'''
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04ff6c14a34079cce033a8c3100ab964fdb9ef73fc55907e821517e61c45e512)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)


@jsii.data_type(
    jsii_type="@gcix/gcix.gitlab.PagesAsciiDoctorProps",
    jsii_struct_bases=[],
    name_mapping={
        "out_file": "outFile",
        "source": "source",
        "job_name": "jobName",
        "job_stage": "jobStage",
    },
)
class PagesAsciiDoctorProps:
    def __init__(
        self,
        *,
        out_file: builtins.str,
        source: builtins.str,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param out_file: Output HTML file.
        :param source: Source .adoc files to translate to HTML files.
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__785bd136cb09e7394e3fa254707c0bc4b01b6bf4298c7ac058f2e52f44acf94c)
            check_type(argname="argument out_file", value=out_file, expected_type=type_hints["out_file"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "out_file": out_file,
            "source": source,
        }
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage

    @builtins.property
    def out_file(self) -> builtins.str:
        '''Output HTML file.'''
        result = self._values.get("out_file")
        assert result is not None, "Required property 'out_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> builtins.str:
        '''Source .adoc files to translate to HTML files.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesAsciiDoctorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPagesPdoc3)
class PagesPdoc3(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.gitlab.PagesPdoc3",
):
    '''Generate a HTML API documentation of you python code as Gitlab Pages.

    Runs ``pdoc3 --html -f --skip-errors --output-dir public{path} {module}`` and stores the output
    as artifact under the ``public`` directory.

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: pdoc3-pages
    - stage: build
    - artifacts: Path 'public'
    '''

    def __init__(
        self,
        *,
        module: builtins.str,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param module: The Python module name. This may be an import path resolvable in the current environment, or a file path to a Python module or package.
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        :param output_path: A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to. Defaults to "/".
        '''
        props = PagesPdoc3Props(
            module=module,
            job_name=job_name,
            job_stage=job_stage,
            output_path=output_path,
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
    @jsii.member(jsii_name="module")
    def module(self) -> builtins.str:
        '''The Python module name.

        This may be an import path resolvable in the
        current environment, or a file path to a Python module or package.
        '''
        return typing.cast(builtins.str, jsii.get(self, "module"))

    @module.setter
    def module(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a002cfc8ff71b45b79fb417d315227d8595b8120c5d5d28c55eb85bad12e1bed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "module", value)

    @builtins.property
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        '''A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to.

        Defaults to "/".
        '''
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe885f549da5e67959dd86af4bbf045302315a951fabc48e0dc3c39a7299dca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputPath", value)


@jsii.data_type(
    jsii_type="@gcix/gcix.gitlab.PagesPdoc3Props",
    jsii_struct_bases=[],
    name_mapping={
        "module": "module",
        "job_name": "jobName",
        "job_stage": "jobStage",
        "output_path": "outputPath",
    },
)
class PagesPdoc3Props:
    def __init__(
        self,
        *,
        module: builtins.str,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param module: The Python module name. This may be an import path resolvable in the current environment, or a file path to a Python module or package.
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        :param output_path: A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to. Defaults to "/".
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89406ee4e281cbb76873c2506f6ccd87a37b467387f5f77deb88aba154197ee7)
            check_type(argname="argument module", value=module, expected_type=type_hints["module"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "module": module,
        }
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage
        if output_path is not None:
            self._values["output_path"] = output_path

    @builtins.property
    def module(self) -> builtins.str:
        '''The Python module name.

        This may be an import path resolvable in the
        current environment, or a file path to a Python module or package.
        '''
        result = self._values.get("module")
        assert result is not None, "Required property 'module' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''A sub path of the Gitlab Pages ``public`` directory to output generated HTML/markdown files to.

        Defaults to "/".
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesPdoc3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPagesSphinx)
class PagesSphinx(
    _Job_20682b42,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gcix/gcix.gitlab.PagesSphinx",
):
    '''Runs ``sphinx-build -b html -E -a docs public/${CI_COMMIT_REF_NAME}`` and installs project requirements. Uses: (``PythonScripts.PipInstallRequirements()``).

    - Requires a ``docs/requirements.txt`` in your project folder``containing at least``sphinx`
    - Creates artifacts for Gitlab Pages under ``pages``

    This subclass of ``Job`` will configure following defaults for the superclass:

    - name: sphinx-pages
    - stage: build
    - artifacts: Path 'public'
    '''

    def __init__(
        self,
        *,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        pip: typing.Optional[typing.Union[_PipInstallRequirementsProps_47c04e0d, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        :param pip: 
        '''
        props = PagesSphinxProps(job_name=job_name, job_stage=job_stage, pip=pip)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Any:
        '''Returns a representation of any object which implements ``IBase``.

        The rendered representation is used by the ``gcix`` to dump it
        in YAML format as part of the ``.gitlab-ci.yml`` pipeline.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="pip")
    def pip(self) -> typing.Optional[_PipInstallRequirementsProps_47c04e0d]:
        return typing.cast(typing.Optional[_PipInstallRequirementsProps_47c04e0d], jsii.get(self, "pip"))

    @pip.setter
    def pip(
        self,
        value: typing.Optional[_PipInstallRequirementsProps_47c04e0d],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbe85ab4fb0553e837846fb19ae75d6ec1eb46f85c338285fe54137fd513d67c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pip", value)


@jsii.data_type(
    jsii_type="@gcix/gcix.gitlab.PagesSphinxProps",
    jsii_struct_bases=[],
    name_mapping={"job_name": "jobName", "job_stage": "jobStage", "pip": "pip"},
)
class PagesSphinxProps:
    def __init__(
        self,
        *,
        job_name: typing.Optional[builtins.str] = None,
        job_stage: typing.Optional[builtins.str] = None,
        pip: typing.Optional[typing.Union[_PipInstallRequirementsProps_47c04e0d, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param job_name: The name of the job.
        :param job_stage: The stage of the job.
        :param pip: 
        '''
        if isinstance(pip, dict):
            pip = _PipInstallRequirementsProps_47c04e0d(**pip)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab710d6ccc8482bd7266e270cfac416cfaeaacae90c1ff3aa4dac62d737cd908)
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_stage", value=job_stage, expected_type=type_hints["job_stage"])
            check_type(argname="argument pip", value=pip, expected_type=type_hints["pip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_stage is not None:
            self._values["job_stage"] = job_stage
        if pip is not None:
            self._values["pip"] = pip

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job.'''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_stage(self) -> typing.Optional[builtins.str]:
        '''The stage of the job.'''
        result = self._values.get("job_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pip(self) -> typing.Optional[_PipInstallRequirementsProps_47c04e0d]:
        result = self._values.get("pip")
        return typing.cast(typing.Optional[_PipInstallRequirementsProps_47c04e0d], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesSphinxProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GitlabScripts",
    "IPagesAsciiDoctor",
    "IPagesPdoc3",
    "IPagesSphinx",
    "PagesAsciiDoctor",
    "PagesAsciiDoctorProps",
    "PagesPdoc3",
    "PagesPdoc3Props",
    "PagesSphinx",
    "PagesSphinxProps",
]

publication.publish()

def _typecheckingstub__2bd5b76126699d26330d7dfeb3122212a724ea05dd5a006bbd12e60b24819200(
    path: builtins.str,
    branch: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd96129bc7b3ec7f5fc2b940829e9c4525d97ed64c6ca6556ea8b654fc40adfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daa927abf8a1764801389a1d4bd5ceda060dc48e44bd8f849427f25a3ac33cd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d79360750e78801d011c581261289c9ca486b80b91be49f4327351da5531cd77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19da3cfd45526d41641528ea3850429e1ec6fc3b49453102ad980d3707550fd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f955d53cb3a7bd57c5a933176e7269b81c87bcfc92576b689bd946dae41f8555(
    value: typing.Optional[_PipInstallRequirementsProps_47c04e0d],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2d1861ba62c52ef1ac9c3754a95089b61216ff321934e5ba1b2bc9104bdf509(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04ff6c14a34079cce033a8c3100ab964fdb9ef73fc55907e821517e61c45e512(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785bd136cb09e7394e3fa254707c0bc4b01b6bf4298c7ac058f2e52f44acf94c(
    *,
    out_file: builtins.str,
    source: builtins.str,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a002cfc8ff71b45b79fb417d315227d8595b8120c5d5d28c55eb85bad12e1bed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe885f549da5e67959dd86af4bbf045302315a951fabc48e0dc3c39a7299dca8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89406ee4e281cbb76873c2506f6ccd87a37b467387f5f77deb88aba154197ee7(
    *,
    module: builtins.str,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe85ab4fb0553e837846fb19ae75d6ec1eb46f85c338285fe54137fd513d67c(
    value: typing.Optional[_PipInstallRequirementsProps_47c04e0d],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab710d6ccc8482bd7266e270cfac416cfaeaacae90c1ff3aa4dac62d737cd908(
    *,
    job_name: typing.Optional[builtins.str] = None,
    job_stage: typing.Optional[builtins.str] = None,
    pip: typing.Optional[typing.Union[_PipInstallRequirementsProps_47c04e0d, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
