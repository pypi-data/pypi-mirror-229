import unittest
from unittest.mock import patch
from tw_pywrap import tower
import json
import subprocess


class TestTower(unittest.TestCase):
    def setUp(self):
        self.tw = tower.Tower()

    @patch("subprocess.Popen")
    def test_run_with_jsonout_command(self, mock_subprocess):
        mock_pipelines_json = {
            "id": "5lWcpupLHnHkq9fM5JYaOn",
            "computeEnvId": "403VpC7AetAmj42MnMOAwJ",
            "pipeline": "https://github.com/nextflow-io/hello",
            "workDir": "s3://myworkdir/test",
            "revision": "",
            "configText": "",
            "paramsText": "",
            "resume": "false",
            "pullLatest": "false",
            "stubRun": "false",
            "dateCreated": "2023-02-15T13:14:30Z",
        }
        # Mock the stdout of the Popen process
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps(mock_pipelines_json).encode(),
            b"",
        )

        # Dynamically get the pipelines command
        command = getattr(self.tw, "pipelines")

        # Run the command with arguments
        result = command("view", "--name", "pipeline_name", to_json=True)

        # Check that Popen was called with the right arguments
        mock_subprocess.assert_called_once_with(
            "tw -o json pipelines view --name pipeline_name",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )

        # Check that the output was decoded correctly
        self.assertEqual(result, mock_pipelines_json)

    def test_resource_exists_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource already exists' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Resource already exists",
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the error is raised
            with self.assertRaises(tower.ResourceExistsError):
                command("arg1", "arg2")

    def test_resource_creation_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource creation failed' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Resource creation failed",
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the error is raised
            with self.assertRaises(tower.ResourceCreationError):
                command("import", "my_pipeline.json", "--name", "pipeline_name")

    def test_json_parsing(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Mock the stdout of the Popen process to return JSON
            mock_subprocess.return_value.communicate.return_value = (
                b'{"key": "value"}',
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the JSON is parsed correctly
            self.assertEqual(command("arg1", "arg2", to_json=True), {"key": "value"})


if __name__ == "__main__":
    unittest.main()
