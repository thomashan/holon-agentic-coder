import subprocess
import unittest

import pytest


@pytest.mark.integration_test
class TestPlannerIntegration(unittest.TestCase):
    def test_planner_docker_usage(self):
        """Test that running the orchestrator image with the planner role and no arguments
        correctly routes to planner.py and exits with usage instructions.
        """
        # Run docker command
        cmd = ["docker", "run", "--rm", "-e", "HOLON_ROLE=planner", "holon/orchestrator"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.fail(f"Failed to execute docker run command: {e}")

        # Verify it exited with code 1 and printed the usage message
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage: planner.py <intent_branch> <agent_name> <model_name>", result.stdout)

    def test_planner_docker_execution_all_agents_fail_fast(self):
        """Test that running the orchestrator with the planner role fails fast
        (returns non-zero exit code and does not push branches) when agent commands fail
        (due to missing API keys / missing local tools in the test environment).
        """
        import json
        import os
        import re
        import tempfile
        import time

        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_dir):
            self.skipTest("SSH directory ~/.ssh not found, skipping integration test.")

        # Create a temp directory for our intent.json
        with tempfile.TemporaryDirectory() as tmp_dir:
            intent_json_path = os.path.join(tmp_dir, "intent.json")
            intent_data = {
                "slug": "test-planner-integration",
                "description": "Integration test description for planner",
                "goal": "Verify planner fail-fast via docker",
                "target_branch": "main",
            }
            with open(intent_json_path, "w") as f:
                json.dump(intent_data, f)

            creator_cmd = [
                "docker",
                "run",
                "--rm",
                "-e",
                "HOLON_ROLE=intent-creator",
                "-e",
                "GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=no",
                "-v",
                f"{ssh_dir}:/home/holon/.ssh:ro",
                "-v",
                f"{intent_json_path}:/tmp/intent.json",
                "holon/orchestrator",
            ]

            try:
                creator_result = subprocess.run(creator_cmd, capture_output=True, text=True, timeout=60)
            except Exception as e:
                self.fail(f"Failed to execute intent-creator: {e}")

            self.assertEqual(creator_result.returncode, 0, f"Failed to create intent branch: {creator_result.stderr}")

            match = re.search(
                r"Intent branch '(I-\d+-test-planner-integration/_)' created and intent logged",
                creator_result.stdout,
            )
            self.assertTrue(match, f"Could not find success message in output:\n{creator_result.stdout}")
            intent_branch = match.group(1)

            agents = [
                "pi-agent",
                "open-codex-agent",
                "claude-agent",
                "gemini-agent",
                "opencode-agent",
                "codex-agent",
                "hermes-agent",
                "antigravity-agent",
            ]

            try:
                for agent in agents:
                    with self.subTest(agent=agent):
                        # Introduce a short delay to guarantee a unique timestamp for the plan
                        time.sleep(1)

                        agent_images = {
                            "pi-agent": "holon/agent-pi",
                            "open-codex-agent": "holon/agent-open-codex",
                            "claude-agent": "holon/agent-claude",
                            "gemini-agent": "holon/agent-gemini",
                            "opencode-agent": "holon/agent-opencode",
                            "codex-agent": "holon/agent-codex",
                            "hermes-agent": "holon/agent-hermes",
                            "antigravity-agent": "holon/agent-antigravity",
                        }
                        image_name = agent_images.get(agent, "holon/orchestrator")

                        cmd = [
                            "docker",
                            "run",
                            "--rm",
                            "-e",
                            "HOLON_ROLE=planner",
                            "-e",
                            "GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=no",
                            "-v",
                            f"{ssh_dir}:/home/holon/.ssh:ro",
                            image_name,
                            intent_branch,
                            agent,
                            "gemini-2.0-flash",
                        ]

                        # Run docker run (with a generous 60-second timeout to allow cloning and execution)
                        try:
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        except subprocess.TimeoutExpired:
                            self.fail(f"Docker run command for {agent} timed out after 60 seconds.")
                        except Exception as e:
                            self.fail(f"Failed to execute docker run command for {agent}: {e}")

                        # The container should exit with a non-zero code due to fail-fast
                        # behavior on missing API keys or missing commands
                        self.assertNotEqual(
                            result.returncode,
                            0,
                            f"Docker run for {agent} should have failed but returned 0.\n"
                            f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}",
                        )

                        # Check for either the error run output or exception output
                        has_error = (
                            "Error: agent command failed" in result.stdout
                            or "Error: Exception running agent" in result.stdout
                        )
                        self.assertTrue(
                            has_error,
                            f"Stdout did not contain expected fail-fast error message for {agent}.\n"
                            f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}",
                        )

                        # Verify that no success/push message was printed
                        self.assertNotIn("successfully created, committed, and pushed", result.stdout)
            finally:
                # Clean up: Delete the remote branch from origin
                subprocess.run(["git", "push", "origin", "--delete", intent_branch], capture_output=True)


if __name__ == "__main__":
    unittest.main()
