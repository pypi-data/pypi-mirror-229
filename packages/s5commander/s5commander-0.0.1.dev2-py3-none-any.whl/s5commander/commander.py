import os
import subprocess
from typing import List, Literal, Optional
import logging

log = logging.getLogger(__name__)


class S5Commander:
    """ S5Commander is a wrapper around s5cmd, a command line tool to interact
    with S3 buckets. It is a thin wrapper around s5cmd, and is not meant to
    replace it. It is meant to be used in a python environment, and to be
    extended to fit the needs of the user.

    Args:
        access_key (str): access key of the S3 bucket
        secret_key (str): secret key of the S3 bucket
        region (str): region of the S3 bucket
        endpoint_url (str): endpoint url of the S3 bucket
        bucket (str): name of the S3 bucket
        local_path (str): local path to download files to
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        endpoint_url: str,
        bucket: str,
        local_path: str,
    ) -> None:
        # before everything, check if s5cmd is installed
        assert subprocess.run(["s5cmd", "--help"],
                              capture_output=True).returncode == 0, \
            "s5cmd is not installed"

        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.local_path = local_path

        # sanity checks
        if self.bucket[-1] != "/":
            self.bucket += "/"
            log.warning(
                "bucket name must end with '/', automatically added '/'")
        if self.local_path[-1] != "/":
            self.local_path += "/"
            log.warning("local path must end with '/', automatically added '/'")
        if self.local_path[0] == "~":
            self.local_path = os.path.expanduser(self.local_path)
        if not "s3://" in self.bucket:
            self.bucket = f"s3://{self.bucket}"

        # set up environment variables for s5cmd
        self.env = os.environ.copy()
        self.env["S3_ENDPOINT_URL"] = self.endpoint_url
        self.env["AWS_ACCESS_KEY_ID"] = access_key
        self.env["AWS_SECRET_ACCESS_KEY"] = secret_key
        self.env["AWS_REGION"] = region

    def ls(self,
           path: Optional[str] = "",
           pattern: str = "",
           options: str = "") -> List[str]:
        """ List buckets and files in a bucket
        
        Args:
            path (str): path to list
            pattern (str): pattern to match
            options (str): options to pass to s5cmd

        Returns:
            List[str]: list of files in the bucket

        Raises:
            Exception: if s5cmd returns an error

        Examples:
            >>> s5cmd.ls(path=None)  # lists available buckets
            ['s3://s5commander-input/']
            >>> s5cmd.ls(pattern="*.sh")  # lists all files ending with .sh
            ['test.sh']
        """

        if path is None:
            command = f"s5cmd ls {options}"
        else:
            command = f"s5cmd ls {options} {self.bucket}{path}{pattern}"

        s5cmd_output = subprocess.run(command.split(),
                                      env=self.env,
                                      capture_output=True)

        if s5cmd_output.returncode != 0:
            raise Exception(s5cmd_output.stderr.decode("utf-8"))

        s5cmd_output = s5cmd_output.stdout.decode("utf-8").split("\n")

        return [i.split(" ")[-1] for i in s5cmd_output if i != ""]

    def cp(self, from_path: str, to_path: str) -> None:
        # command = f"s5cmd cp {path} {self.local_path}"
        # subprocess.run(command.split(), env=self.env, capture_output=True)
        raise NotImplementedError

    def download(self,
                 from_path: str,
                 to_path: str = "",
                 pattern: str = "*",
                 mode: Literal["cp", "sync"] = "sync",
                 options: str = "") -> None:
        """ Download files from a bucket to a local path

        Args:
            from_path (str): path to download from
            to_path (str): path to download to
            pattern (str): pattern to match
            mode (str): mode to use, either 'cp' or 'sync'
            options (str): options to pass to s5cmd

        Raises:
            Exception: if s5cmd returns an error

        Examples:
            >>> s5cmd.download(from_path="test.sh")  # downloads test.sh to local path
            >>> s5cmd.download(from_path="test.sh", to_path="test2.sh")  # downloads test.sh to local path
            >>> s5cmd.download(from_path="folder1", to_path="local_folder", pattern="*.py")  # downloads all files ending with .py to a local folder
        """
        command = f"s5cmd {mode} {options} {self.bucket}{from_path}{pattern} {self.local_path}{to_path}"
        s5cmd_output = subprocess.run(command.split(),
                                      env=self.env,
                                      capture_output=True)

        if s5cmd_output.returncode != 0:
            raise Exception(s5cmd_output.stderr.decode("utf-8"))

    def upload(self,
               from_path: str,
               to_path: str = "",
               pattern: str = "*",
               mode: Literal["cp", "sync"] = "sync",
               options: str = "") -> None:
        """ Upload files from a local path to a bucket

        Args:
            from_path (str): path to upload from
            to_path (str): path to upload to
            pattern (str): pattern to match
            mode (str): mode to use, either 'cp' or 'sync'
            options (str): options to pass to s5cmd

        Raises:
            Exception: if s5cmd returns an error

        Examples:
            >>> s5cmd.upload(from_path="/home/user/test.sh")  # uploads test.sh to bucket
            >>> s5cmd.upload(from_path="/home/user/test.sh", to_path="test2.sh")  # uploads test.sh to bucket as test2.sh
            >>> s5cmd.upload(from_path="/home/user/folder1/", to_path="bucket_folder/", pattern="*")  # uploads all files of folder1 to bucket/bucket_folder
        """
        command = f"s5cmd {mode} {options} {from_path}{pattern} {self.bucket}{to_path}"
        s5cmd_output = subprocess.run(command.split(),
                                      env=self.env,
                                      capture_output=True)

        if s5cmd_output.returncode != 0:
            raise Exception(s5cmd_output.stderr.decode("utf-8"))

    def rm(self, path: str) -> None:
        raise NotImplementedError

    def mv(self, from_path: str, to_path: str) -> None:
        raise NotImplementedError

    def mb(self) -> None:
        raise NotImplementedError

    def rb(self) -> None:
        raise NotImplementedError

    def select(self) -> None:
        raise NotImplementedError

    def du(self) -> None:
        raise NotImplementedError

    def cat(self) -> None:
        raise NotImplementedError

    def pipe(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError

    def sync(self) -> None:
        raise NotImplementedError
