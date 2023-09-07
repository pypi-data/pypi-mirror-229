import os
import subprocess


class S5Commander:

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
        assert self.bucket[-1] == "/", "bucket name must end with '/'"
        assert self.local_path[-1] == "/", "local path must end with '/'"
        if not "s3://" in self.bucket:
            self.bucket = f"s3://{self.bucket}"

        # set up environment variables for s5cmd
        self.env = os.environ.copy()
        self.env["S3_ENDPOINT_URL"] = self.endpoint_url
        self.env["AWS_ACCESS_KEY_ID"] = access_key
        self.env["AWS_SECRET_ACCESS_KEY"] = secret_key
        self.env["AWS_REGION"] = region

    def ls(self, path: str = "") -> list:
        command = f"s5cmd ls {self.bucket}{path}"
        s5cmd_output = subprocess.run(command.split(),
                                      env=self.env,
                                      capture_output=True)
        s5cmd_output = s5cmd_output.stdout.decode("utf-8").split("\n")

        return [i.split(" ")[-1] for i in s5cmd_output if i != ""]

    def cp(self, from_path: str, to_path: str) -> None:
        # command = f"s5cmd cp {self.bucket}{path} {self.local_path}"
        # subprocess.run(command.split(), env=self.env, capture_output=True)
        raise NotImplementedError

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
