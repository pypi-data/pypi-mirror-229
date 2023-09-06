"""
Missing tests:
 - failures should be accounted for under the BaseApi
 - Each job should also be covered for process_job only 3/5 currently are.
"""

from contextlib import redirect_stdout
from datetime import datetime
import io
from math import ceil
from typing import Optional
import unittest
import unittest.mock

import networkx as nx
import numpy as np
import pytest
import requests
import scipy.sparse as sp

from qci_client import (
    JobStatus,
    QciClient,
    compute_results_step_len,
    data_to_json,
    multipart_file,
)


@pytest.mark.offline
class TestJobStatus(unittest.TestCase):
    """JobStatus-related test suite."""

    def test_jobstatus(self):
        """Test all job statuses."""
        job_status = JobStatus()
        self.assertEqual(job_status.QUEUED, "QUEUED")
        self.assertEqual(job_status.SUBMITTED, "SUBMITTED")
        self.assertEqual(job_status.RUNNING, "RUNNING")
        self.assertEqual(job_status.COMPLETED, "COMPLETED")
        self.assertEqual(job_status.ERROR, "ERROR")
        self.assertEqual(job_status.CANCELLED, "CANCELLED")


class TestQciClientFiles(unittest.TestCase):
    """Files-API-related test suite."""

    @classmethod
    def setUpClass(cls):
        cls.q1 = QciClient()
        cls.graph_dict_input = {
            "file_type": "graph",
            "file_name": "graph.json",
            "directed": False,
            "multigraph": False,
            "graph": {},
            "nodes": [{"id": 1}, {"id": 2}, {"id": 3}],
            "links": [{"source": 1, "target": 2}, {"source": 1, "target": 3}],
        }

        cls.q_dict_input = {
            "file_type": "qubo",
            "file_name": "qubo.json",
            "data": [
                {"i": 0, "j": 0, "val": -1.0},
                {"i": 0, "j": 1, "val": 1.0},
                {"i": 1, "j": 0, "val": 1.0},
                {"i": 1, "j": 1, "val": -1.0},
            ],
            "num_variables": 2,
        }

        cls.objective_dict_input = {
            "file_type": "objective",
            "file_name": "objective.json",
            "data": [
                {"i": 0, "j": 0, "val": -1.0},
                {"i": 0, "j": 1, "val": 1.0},
                {"i": 1, "j": 0, "val": 1.0},
                {"i": 1, "j": 1, "val": -1.0},
            ],
            "num_variables": 2,
        }

        cls.constraint_dict_input = {
            "file_type": "constraints",
            "file_name": "constraints.json",
            "data": [
                {"i": 0, "j": 0, "val": -1.0},
                {"i": 0, "j": 1, "val": 1.0},
                {"i": 1, "j": 0, "val": 1.0},
                {"i": 1, "j": 1, "val": -1.0},
            ],
            "num_variables": 2,
            "num_constraints": 2,
        }

        cls.rhs_dict_input = {
            "file_type": "rhs",
            "file_name": "rhs.json",
            "data": [1, 2],
            "num_constraints": 2,
        }

        cls.hamiltonian_dict_input = {
            "file_type": "hamiltonian",
            "file_name": "hamiltonian.json",
            "num_variables": 2,
            "data": [
                {"i": 0, "j": 0, "val": 1.0},
                {"i": 0, "j": 1, "val": 1.0},
                {"i": 1, "j": 0, "val": 2.0},
                {"i": 1, "j": 2, "val": 1.0},
            ],
        }

        cls.graph_file_id = cls.q1.upload_file(data=cls.graph_dict_input)["file_id"]
        cls.qubo_file_id = cls.q1.upload_file(data=cls.q_dict_input)["file_id"]
        cls.obj_file_id = cls.q1.upload_file(data=cls.objective_dict_input)["file_id"]
        cls.rhs_file_id = cls.q1.upload_file(data=cls.rhs_dict_input)["file_id"]
        cls.constraints_file_id = cls.q1.upload_file(data=cls.constraint_dict_input)[
            "file_id"
        ]
        cls.hamiltonian_file_id = cls.q1.upload_file(data=cls.hamiltonian_dict_input)[
            "file_id"
        ]

        cls.all_statuses = [
            JobStatus.QUEUED,
            JobStatus.SUBMITTED,
            JobStatus.RUNNING,
            JobStatus.COMPLETED,
            JobStatus.ERROR,
            JobStatus.CANCELLED,
        ]

        cls.final_status = [JobStatus.COMPLETED, JobStatus.ERROR, JobStatus.CANCELLED]

        cls.job_info = set(("job_id", "details", "results", "submission", "metrics"))
        cls.result_keys = ["samples", "energies", "file_name", "file_type"]

        cls.graph_job_body = {
            "job_name": "job_0",
            "graph_file_id": cls.graph_file_id,
            "params": {"sampler_type": "csample", "n_samples": 1}
        }

        cls.qubo_job_body = {
            "job_name": "job_0",
            "qubo_file_id": cls.qubo_file_id,
            "params": {"sampler_type": "csample", "n_samples": 1}
        }

        cls.objective_job_body = {
            "job_name": "job_0",
            "objective_file_id": cls.obj_file_id,
            "constraints_file_id": cls.constraints_file_id,
            "rhs_file_id": cls.rhs_file_id,
            "params": {"sampler_type": "csample", "n_samples": 1}
        }

        cls.hamiltonian_job_body = {
            "job_name": "job_0",
            "hamiltonian_file_id": cls.hamiltonian_file_id,
            "params": {"sampler_type": "eqc1", "n_samples": 2},
        }

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

    def test_add_headers(self):
        """Test adding headers to client's requests."""
        q_h = QciClient(_add_headers={"X-Job-Id": "fake-job", "X-Job-Type": "job_type"})
        self.assertTrue(q_h.headers["X-Job-Id"], "fake-job")
        self.assertTrue(q_h.headers["X-Job-Type"], "job-type")

    def test_get_file_metadata(self):
        """Test getting file metadata by specified file ID."""
        metadata = self.q1.get_file_metadata(self.qubo_file_id)

        self.assertEqual(metadata["file_type"], self.q_dict_input["file_type"])
        self.assertEqual(metadata["num_variables"], self.q_dict_input["num_variables"])

    def test_upload_file_error(self):
        """Test uploading improperly formatted file."""
        with self.assertRaises(KeyError):
            error_input = {
                "file_type": "graph",
                "file_name": "qubo.json",
                "data": [
                    {"i": 0, "j": 0, "val": -1.0},
                    {"i": 0, "j": 1, "val": 1.0},
                    {"i": 1, "j": 0, "val": 1.0},
                    {"i": 1, "j": 1, "val": -1.0},
                ],
                "num_variables": 2,
            }
            self.q1.upload_file(data=error_input)

    def test_upload_file(self):
        """Test uploading of various file types."""
        # create graph data
        graph = nx.Graph()
        graph.add_edge(1, 2)
        graph.add_edge(1, 3)
        # create rhs data
        rhs_list = [1, 2]
        # create objective data
        objective_np = np.array([[1, -1], [-1, 1]])
        cons_hamiltonian_sp = sp.csr_matrix(np.array([[1, 1, -1], [2, -1, 1]]))

        graph_dict_upload = self.q1.upload_file(data=self.graph_dict_input)
        self.assertIn("file_id", graph_dict_upload)
        self.assertIsInstance(graph_dict_upload["file_id"], str)

        qubo_dict_upload = self.q1.upload_file(data=self.q_dict_input)
        self.assertIn("file_id", qubo_dict_upload)
        self.assertIsInstance(qubo_dict_upload["file_id"], str)

        rhs_dict_upload = self.q1.upload_file(data=self.rhs_dict_input)
        self.assertIn("file_id", rhs_dict_upload)
        self.assertIsInstance(rhs_dict_upload["file_id"], str)

        rhs_list_upload = self.q1.upload_file(data=rhs_list, file_type="rhs")
        self.assertIn("file_id", rhs_list_upload)
        self.assertIsInstance(rhs_list_upload["file_id"], str)

        g_nx_upload = self.q1.upload_file(data=graph, file_type="graph")
        self.assertIn("file_id", g_nx_upload)
        self.assertIsInstance(g_nx_upload["file_id"], str)

        obj_np_upload = self.q1.upload_file(data=objective_np, file_type="objective")
        self.assertIn("file_id", obj_np_upload)
        self.assertIsInstance(obj_np_upload["file_id"], str)

        ham_sp_upload = self.q1.upload_file(
            data=cons_hamiltonian_sp, file_type="hamiltonian"
        )
        self.assertIn("file_id", ham_sp_upload)
        self.assertIsInstance(ham_sp_upload["file_id"], str)

        cons_sp_upload = self.q1.upload_file(
            data=cons_hamiltonian_sp, file_type="constraints"
        )
        self.assertIn("file_id", cons_sp_upload)
        self.assertIsInstance(cons_sp_upload["file_id"], str)

    def test_validate_job_type(self):
        """Test validation of job type against whitelist."""
        test_job_type = "fake_job_type"
        expected_err_str = f"Provided job_type '{test_job_type}' is not one of {self.q1._supported_job_types}"  # pylint: disable=protected-access

        with self.assertRaises(AssertionError) as context:
            self.q1.validate_job_type(job_type=test_job_type)

        # TODO: consider asserting on exception type instead of specific text of assert msg
        # because aserting on the specific text of the assert msg makes this test fairly fragile
        self.assertEqual(
            str(context.exception),
            expected_err_str
        )

        try:
            self.q1.validate_job_type(job_type="sample-qubo")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.fail(
                f"validate_job_type failed with exception '{exc}' with supported job_type"
            )

    def test_build_job_body(self):
        """Test building of various jobs' request bodies."""
        # don't need to revalidate validate_job_type
        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(
                job_type="sample-qubo",
                qubo_file_id="qubo_file_id",
                objective_file_id="objective_file_id",
            )

        self.assertEqual(
            str(context.exception),
            "Only one of qubo_file_id, hamiltonian_file_id, objective_file_id, or graph_file_id can be specified",
        )

        job_template = {"job_name": "job_0", "job_tags": [], "params": {}}

        # Validate sample-constraint
        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(job_type="sample-constraint", qubo_file_id="q_fid")

        self.assertEqual(
            str(context.exception),
            "objective_file_id, constraints_file_id, and rhs_file_id must all be specified for job_type='sample-constraint'",
        )

        constraint_template = {
            "objective_file_id": "obj_fid",
            "constraints_file_id": "cons_fid",
            "rhs_file_id": "rhs_fid",
        }

        constraint_template.update(job_template)

        constraint_body = self.q1.build_job_body(
            job_type="sample-constraint",
            objective_file_id="obj_fid",
            constraints_file_id="cons_fid",
            rhs_file_id="rhs_fid",
        )

        self.assertDictEqual(constraint_body, constraint_template)

        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(job_type="sample-qubo", objective_file_id="obj_fid")

        self.assertEqual(
            str(context.exception),
            "objective_file_id, constraints_file_id, and rhs_file_id are not available for selected job_type",
        )

        # Validate sample-qubo
        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(
                job_type="sample-qubo", hamiltonian_file_id="obj_fid"
            )

        self.assertEqual(
            str(context.exception),
            "qubo_file_id must be specified for job_type='sample-qubo'",
        )

        qubo_template = {"qubo_file_id": "q_fid"}
        qubo_template.update(job_template)

        qubo_body = self.q1.build_job_body(job_type="sample-qubo", qubo_file_id="q_fid")

        self.assertDictEqual(qubo_template, qubo_body)

        # Validate sample-hamiltonian
        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(job_type="sample-hamiltonian", qubo_file_id="q_fid")

        self.assertEqual(
            str(context.exception),
            "hamiltonian_file_id must be specified for job_type='sample-hamiltonian'",
        )

        hamiltonian_template = {"hamiltonian_file_id": "h_fid"}
        hamiltonian_template.update(job_template)

        hamiltonian_body = self.q1.build_job_body(
            job_type="sample-hamiltonian", hamiltonian_file_id="h_fid"
        )

        self.assertDictEqual(hamiltonian_template, hamiltonian_body)

        # Validate graph problems
        with self.assertRaises(AssertionError) as context:
            self.q1.build_job_body(
                job_type="graph-partitioning", hamiltonian_file_id="obj_fid"
            )

        self.assertEqual(
            str(context.exception),
            "graph_file_id must be specified for the given job_type",
        )

        graph_template = {"graph_file_id": "g_fid"}
        graph_template.update(job_template)

        graph_body = self.q1.build_job_body(
            job_type="bipartite-community-detection", graph_file_id="g_fid"
        )

        self.assertDictEqual(graph_template, graph_body)

        # test other params
        name_body = self.q1.build_job_body(
            job_type="unipartite-community-detection",
            graph_file_id="g_fid",
            job_name="fake_job",
        )
        graph_template.update({"job_name": "fake_job", "job_tags": []})

        self.assertDictEqual(graph_template, name_body)

        tag_body = self.q1.build_job_body(
            job_type="unipartite-community-detection",
            graph_file_id="g_fid",
            job_tags=["tag1", "tag2"],
        )
        graph_template.update({"job_name": "job_0", "job_tags": ["tag1", "tag2"]})
        self.assertDictEqual(graph_template, tag_body)

        job_params_body = self.q1.build_job_body(
            job_type="unipartite-community-detection",
            graph_file_id="g_fid",
            job_params={"n_shots": 100, "device": "ionq"},
        )
        graph_template.update(job_template)
        graph_template.update({"params": {"n_shots": 100, "device": "ionq"}})
        self.assertDictEqual(graph_template, job_params_body)

    def test_print_job_log(self):
        """Test printing of job log messages."""
        string_io = io.StringIO()
        with redirect_stdout(string_io):
            self.q1.print_job_log(message="fake message")
        out = string_io.getvalue()
        date_now = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))[0:10]
        self.assertTrue(out.startswith(f"fake message: {date_now}"))


class TestMultipartUpload(unittest.TestCase):
    """Multipart-file upload test suite."""

    @classmethod
    def setUpClass(cls):
        cls.q1 = QciClient()

    def test_multipart_upload_and_download(self):
        """
        Tests multipart upload:
            - expected upload size
            - expected parts returned
            - full matrix (using get_file_whole) is correct
        """
        dim = 150
        array = np.random.normal(size=(dim, dim))
        qubo = array + array.T

        expected_data = data_to_json(
            qubo, file_type="qubo", file_name="test-upload-file-multipart"
        )
        expected_parts = list(multipart_file(expected_data))
        self.assertGreater(len(expected_parts), 1)

        resp = self.q1.upload_file(
            qubo, file_type="qubo", file_name="test-upload-file-multipart"
        )
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], len(expected_parts))

        test_return = list(self.q1.get_file(resp["file_id"]))
        self.assertEqual(len(test_return), len(expected_parts))
        self.assertEqual(len(test_return[0]["data"]), len(expected_parts[0][0]["data"]))

        test_return_whole = self.q1.get_file_whole(resp["file_id"])
        test_mat = np.empty((dim, dim))
        for datum in test_return_whole["data"]:
            i_j = int(datum["i"]), int(datum["j"])
            test_mat[i_j] = float(datum["val"])
        self.assertTrue(np.allclose(test_mat, qubo))

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_process_job(self):
        """Test job processing for multipart qubo input file.."""
        dim = 150
        array = np.random.normal(size=(dim, dim))
        qubo = array + array.T

        expected_data = data_to_json(
            qubo, file_type="qubo", file_name="test-upload-file-multipart"
        )
        expected_parts = list(multipart_file(expected_data))
        self.assertGreater(len(expected_parts), 1)

        resp = self.q1.upload_file(
            qubo, file_type="qubo", file_name="test-upload-file-multipart"
        )
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], len(expected_parts))

        qubo_job_body = {"job_name": "job_0", "qubo_file_id": resp["file_id"], "params": {"sampler_type": "csample", "n_samples": 1}}
        job_resp = self.q1.process_job(job_type="sample-qubo", job_body=qubo_job_body)
        self.assertEqual(len(job_resp["results"]["samples"][0]), dim)

        status = self.q1.get_job_status(job_id=job_resp["job_info"]["job_id"])
        self.assertEqual(status["status"], JobStatus.COMPLETED)

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_graph_upload_and_download(self):
        """Test uploading/downloading multipart graph input file."""
        dim = 150
        nodes = [{"id": ix} for ix in range(dim)]
        links = []
        for i in range(dim):
            # no self-edges
            for j in range(i + 1, dim):
                links.append({"source": i, "target": j})

        graph_dict_check = {
            "file_type": "graph",
            "file_name": "graph.json",
            "directed": False,
            "multigraph": False,
            "graph": "test_graph",
            "nodes": nodes,
            "links": links,
        }

        expected_parts = list(multipart_file(graph_dict_check))
        self.assertGreater(len(expected_parts), 1)

        resp = self.q1.upload_file(graph_dict_check)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], len(expected_parts))

        test_return = list(self.q1.get_file(resp["file_id"]))
        self.assertEqual(len(test_return), len(expected_parts))

        test_whole = self.q1.get_file_whole(resp["file_id"])
        self.assertEqual(len(test_whole["links"]), len(graph_dict_check["links"]))

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_results_upload_and_download(self):
        """Test uploading/downloading multipart qubo results file."""
        # BIG number of samples, each one num_vars in length
        num_vars = 1700
        num_samp = 300
        samples = np.ones((num_samp, num_vars)).astype(int)
        counts = np.ones((num_samp, 1)).astype(int)
        energies = np.ones((num_samp, 1))

        resdata = {
            "file_name": "test-file.json",
            "file_type": "job_results_sample_qubo",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "test_user",
            "counts": counts.flatten().tolist(),
            "energies": energies.flatten().tolist(),
            "samples": samples.tolist(),
        }

        step_len = compute_results_step_len(resdata["samples"][0])
        expected_parts = ceil(num_samp / step_len)
        self.assertGreater(expected_parts, 1)

        resp = self.q1.upload_file(resdata)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], expected_parts)

        test_res_whole = self.q1.get_file_whole(resp["file_id"])
        self.assertEqual(len(test_res_whole["counts"]), counts.shape[0])
        self.assertEqual(len(test_res_whole["energies"]), energies.shape[0])
        self.assertEqual(len(test_res_whole["samples"]), samples.shape[0])
        self.assertEqual(len(test_res_whole["samples"][0]), samples.shape[1])

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_results_upload_and_download_hamiltonian(self):
        """Test uploading/downloading multipart hamiltonian results file."""
        # Tests float uploads, so we use Hamiltonian job type so the API can handle floats
        num_vars = 20000
        num_samp = 30
        samples = np.ones((num_samp, num_vars)).astype(float)
        counts = np.ones((num_samp, 1)).astype(int)
        energies = np.ones((num_samp, 1))

        resdata = {
            "file_name": "test-file.json",
            "file_type": "job_results_sample_hamiltonian",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "test_user",
            "solution_type": "continuous",
            "counts": counts.flatten().tolist(),
            "energies": energies.flatten().tolist(),
            "samples": samples.tolist(),
        }

        step_len = compute_results_step_len(resdata["samples"][0])
        expected_parts = ceil(num_samp / step_len)
        self.assertGreater(expected_parts, 1)

        resp = self.q1.upload_file(resdata)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], expected_parts)

        test_res_whole = self.q1.get_file_whole(resp["file_id"])
        self.assertEqual(len(test_res_whole["counts"]), counts.shape[0])
        self.assertEqual(len(test_res_whole["energies"]), energies.shape[0])
        self.assertEqual(len(test_res_whole["samples"]), samples.shape[0])
        self.assertEqual(len(test_res_whole["samples"][0]), samples.shape[1])

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_results_upload_and_download_huge(self):
        """Test uploading/downloading very large multipart qubo results file."""
        # Now try something too large
        # BIG number of samples, each one num_vars in length
        num_vars = 100000
        num_samp = 300
        samples = np.ones((num_samp, num_vars)).astype(int)
        counts = np.ones((num_samp, 1)).astype(int)
        energies = np.ones((num_samp, 1))

        resdata = {
            "file_name": "test-file.json",
            "file_type": "job_results_sample_qubo",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "test_user",
            "counts": counts.flatten().tolist(),
            "energies": energies.flatten().tolist(),
            "samples": samples.tolist(),
        }

        step_len = compute_results_step_len(samples[0])
        expected_parts = ceil(num_samp / step_len)
        self.assertGreater(expected_parts, 1)

        resp = self.q1.upload_file(resdata)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], expected_parts)

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_graph_partitioning_results_upload_and_download(self):
        """Test uploading/downloading multipart graph-partitioning results file."""
        num_samples = 10
        num_nodes = 10000
        test_vec = np.arange(num_samples)
        test_vec_int = np.arange(num_samples).astype(int)

        samples = [
            [
                {"id": int(np.random.randint(0, 10)), "class": np.random.randint(0, 3)}
                for _ in range(num_nodes)
            ]  # pretend we have a graph with 100 nodes
            for _ in range(num_samples)  # and we asked for 1000 samples
        ]

        gp_results = {
            "file_name": "test-file.json",
            "file_type": "job_results_graph_partitioning",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "test_user",
            "balance": test_vec.tolist(),
            "counts": test_vec.tolist(),
            "cut_size": test_vec_int.tolist(),
            "energies": test_vec.tolist(),
            "is_feasible": [True] * num_samples,
            "samples": samples,
        }

        step_len = compute_results_step_len(samples[0])
        expected_parts = ceil(num_samples / step_len)
        self.assertGreater(expected_parts, 1)

        resp = self.q1.upload_file(gp_results)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], expected_parts)

        test_res_whole = self.q1.get_file_whole(resp["file_id"])
        self.assertEqual(len(test_res_whole["counts"]), len(test_vec_int))
        self.assertEqual(len(test_res_whole["energies"]), test_vec.shape[0])
        self.assertEqual(len(test_res_whole["samples"]), num_samples)
        self.assertEqual(len(test_res_whole["samples"][0]), num_nodes)

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1

    def test_multipart_community_detection_results_upload_and_download(self):
        """Test uploading/downloading multipart community-detection results file."""
        num_samples = 1000
        num_nodes = 50
        test_vec = np.arange(num_samples)
        test_vec_int = np.arange(num_samples).astype(int)

        samples = [
            [
                {"id": int(np.random.randint(0, 10)), "class": np.random.randint(0, 3)}
                for _ in range(num_nodes)
            ]  # pretend we have a graph with 100 nodes
            for _ in range(num_samples)  # and we asked for 1000 samples
        ]

        resdata = {
            "file_name": "test-file.json",
            "file_type": "job_results_bipartite_community_detection",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "test_user",
            "modularity": test_vec.tolist(),
            "counts": test_vec.tolist(),
            "energies": test_vec.tolist(),
            "is_feasible": [True] * num_samples,
            "samples": samples,
        }

        step_len = compute_results_step_len(resdata["samples"][0])
        expected_parts = ceil(num_samples / step_len)
        self.assertGreater(expected_parts, 1)

        resp = self.q1.upload_file(resdata)
        meta = self.q1.get_file_metadata(resp["file_id"])
        self.assertEqual(meta["num_parts"], expected_parts)

        test_res_whole = self.q1.get_file_whole(resp["file_id"])
        self.assertEqual(len(test_res_whole["counts"]), len(test_vec_int))
        self.assertEqual(len(test_res_whole["energies"]), test_vec.shape[0])
        self.assertEqual(len(test_res_whole["samples"]), num_samples)
        self.assertEqual(len(test_res_whole["samples"][0]), num_nodes)

        del_resp = self.q1.delete_file(resp["file_id"])
        assert del_resp["num_deleted"] == 1


@pytest.mark.offline
class TestJobsApiWithRequestMocks(unittest.TestCase):
    """Jobs-API-related test suite that can be run without backend."""

    def setUp(self):
        self.qci_client = QciClient(
            api_token="test_api_token", url="test_url", set_bearer_token_on_init=False
        )
        self.job_id = "63b717a22da68618ec444eac"
        self.job_type = "sample-hamiltonian"
        self.file_id = "73b717a22da68618ec444eab"

        # Bad GET jobs response.
        self.get_response_bad = requests.Response()
        self.get_response_bad.status_code = 404

    def test_jobs_url(self) -> None:
        """Test getting jobs URL."""
        self.assertEqual(self.qci_client.jobs_url, "test_url/jobs")

    def test_get_job_type_url(self) -> None:
        """Test getting jobs URL for given job type."""
        self.assertEqual(
            self.qci_client.get_job_type_url(self.job_type),
            f"test_url/jobs/{self.job_type}",
        )

    def test_get_job_type_job_id_url(self) -> None:
        """Test getting jobs URL for given job type and ID."""
        self.assertEqual(
            self.qci_client.get_job_type_job_id_url(self.job_type, self.job_id),
            f"test_url/jobs/{self.job_type}/{self.job_id}",
        )

    def test_get_job_id_url(self) -> None:
        """Test getting jobs URL for given job ID."""
        self.assertEqual(
            self.qci_client.get_job_id_url(self.job_id), f"test_url/jobs/{self.job_id}"
        )

    def test_get_job_statuses_url(self) -> None:
        """Test getting jobs-statuses URL for given job ID."""
        self.assertEqual(
            self.qci_client.get_job_statuses_url(self.job_id),
            f"test_url/jobs/{self.job_id}/statuses",
        )

    def test_get_job_metrics_url(self) -> None:
        """Test getting jobs-metrics URL for given job ID."""
        self.assertEqual(
            self.qci_client.get_job_metrics_url(self.job_id),
            f"test_url/jobs/{self.job_id}/metrics",
        )

    def test_get_job_metrics_provider_url(self) -> None:
        """Test getting jobs-metrics-provider URL for given job ID."""
        self.assertEqual(
            self.qci_client.get_job_metrics_provider_url(self.job_id),
            f"test_url/jobs/{self.job_id}/metrics/provider",
        )

    def test_files_url(self) -> None:
        """Test getting files URL."""
        self.assertEqual(self.qci_client.files_url, "test_url/files")

    def test_get_file_id_url(self) -> None:
        """Test getting files URL for given file ID."""
        self.assertEqual(
            self.qci_client.get_file_id_url(self.file_id),
            f"test_url/files/{self.file_id}",
        )

    def test_get_job_type_from_job_id(self) -> None:
        """Test getting job type from job ID."""
        # GET short jobs response.
        get_jobs_response_short = requests.Response()
        get_jobs_response_short.status_code = 200
        get_jobs_response_short._content = (  # pylint: disable=protected-access
            b"""{
    "job_id": "%b",
    "status": "COMPLETED",
    "type": "sample_hamiltonian",
    "organization_id": "6edf5db3def87d53b6bf375b",
    "username": "test_user"
}"""
            % self.job_id.encode()
        )

        self.qci_client.session.request = unittest.mock.MagicMock(
            return_value=get_jobs_response_short
        )
        self.assertEqual(
            self.qci_client.get_job_type_from_job_id(self.job_id), self.job_type
        )

        self.qci_client.session.request = unittest.mock.MagicMock(
            return_value=self.get_response_bad
        )
        with self.assertRaises(AssertionError):
            self.qci_client.get_job_type_from_job_id(self.job_id)
