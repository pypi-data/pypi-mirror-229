"""Test suite for jobs run on a remote backend."""

from typing import Optional

import numpy as np

from qci_client import JobStatus
from tests.test_qci_client import TestQciClientFiles


class TestQciClientRemoteJobs(TestQciClientFiles):
    """Collection of tests for remote jobs."""

    def run_end_end(
        self, job_type: str, job_body: dict, results_key: Optional[list] = None
    ):
        """
        Utility function for testing end to end pipeline.
        :param job_type: one of _supported_job_types
        :param job_body: a validate job request
        Testing each in series:
            - submit_job
            - get_job_status
            - get_job_response
            - get_file
        """

        result_keys = self.result_keys if results_key is None else results_key

        job_id = self.q1.submit_job(json_dict=job_body, job_type=job_type)

        self.assertIn("job_id", job_id)
        self.assertIsInstance(job_id["job_id"], str)

        status = self.q1.get_job_status(job_id=job_id["job_id"])
        self.assertIn("status", status)
        self.assertIn(status["status"], self.all_statuses)

        while status["status"] not in self.final_status:
            status = self.q1.get_job_status(job_id=job_id["job_id"])

        self.assertEqual(JobStatus.COMPLETED, status["status"])
        response = self.q1.get_job_response(job_id=job_id["job_id"], job_type=job_type)

        # test job info has appropriate keys
        self.assertEqual(self.job_info, set(response.keys()))

        result = self.q1.get_file(file_id=response["results"]["file_id"])

        result = list(result)
        self.assertTrue(all(i in result[0] for i in result_keys))

    def process_job_check(self, job_type, job_body):
        """Utility function for checking job types."""
        process_key = ["job_info", "results"]
        job_output = self.q1.process_job(
            job_type=job_type, job_body=job_body, wait=True
        )
        self.assertTrue(all(key in process_key for key in list(job_output.keys())))

    def test_large_job(self):
        """Test large sample-qubo job."""
        large_qubo = np.random.normal(size=(6000, 6000))
        large_qubo = large_qubo + large_qubo.T
        large_file_id = self.q1.upload_file(data=large_qubo, file_type="qubo")[
            "file_id"
        ]
        print("LARGE FILE ID", large_file_id)
        large_job_body = {
            "job_name": "large_job",
            "qubo_file_id": large_file_id,
            "params": {"sampler_type": "eqc1", "n_samples": 2},
        }

        self.process_job_check(job_type="sample-qubo", job_body=large_job_body)

    def test_process_qubo(self):
        """Test that sample-qubo job process can be checked."""
        self.process_job_check(job_type="sample-qubo", job_body=self.qubo_job_body)

    def test_process_constraint(self):
        """Test that sample-constraint job process can be checked."""
        self.process_job_check(job_type="sample-constraint", job_body=self.objective_job_body)

    def test_graph_partitioning(self):
        """Test graph-partitioning job."""
        job_type = "graph-partitioning"

        self.run_end_end(job_type=job_type, job_body=self.graph_job_body)

    def test_sample_qubo(self):
        """Test sample-qubo job."""
        job_type = "sample-qubo"

        self.run_end_end(job_type=job_type, job_body=self.qubo_job_body)

    def test_sample_constraint(self):
        """Test sample-constraint job."""
        job_type = "sample-constraint"

        self.run_end_end(job_type=job_type, job_body=self.objective_job_body)

    def test_uni_cd(self):
        """Test unipartite-community-detection job."""
        job_type = "unipartite-community-detection"

        self.run_end_end(job_type=job_type, job_body=self.graph_job_body)

    def test_process_hamiltonian(self):
        """Test that sample-hamiltonian job process can be checked."""
        self.process_job_check(
            job_type="sample-hamiltonian", job_body=self.hamiltonian_job_body
        )

    def test_sample_hamiltonian(self):
        """Test sample-hamiltonian job."""
        job_type = "sample-hamiltonian"

        self.run_end_end(job_type=job_type, job_body=self.hamiltonian_job_body)
