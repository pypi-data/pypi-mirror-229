"""Test for data conversion functions."""

import json
from math import ceil
from operator import itemgetter
import os
import sys
import tempfile
import time
import unittest

import networkx as nx
import numpy as np
import pytest
import scipy.sparse as sp

from qci_client.data_converter import (
    compute_results_step_len,
    data_to_json,
    load_json_file,
    multipart_file,
)


@pytest.mark.offline
class TestDataConverter(unittest.TestCase):
    """Test suite for data conversion."""

    def test_load_json_file(self):
        """Test loading a JSON file."""
        test_dict = {
            "str": "hello",
            "int": 56,
            "float": 8.6,
            "list": [1, 2, 3],
            "nestlist": [{"i": 1, "j": 1, "val": 0.1}, {"i": 1, "j": 1, "val": 0.1}],
        }

        # Serializing json
        json_object = json.dumps(test_dict)
        # write to tempdir
        test_dir = tempfile.mkdtemp()
        file_name = str(os.path.join(test_dir, "test.json"))
        with open(file_name, "w", encoding="utf-8") as file_out:
            file_out.write(json_object)
        dict_load = load_json_file(file_name=file_name)
        self.assertDictEqual(test_dict, dict_load)


@pytest.mark.offline
class TestDataToJson(unittest.TestCase):
    """Test suite for data conversion to JSON."""

    def test_file_type_assert(self):
        """Test file generation for bad file type."""
        # test file_type assertion
        with self.assertRaises(AssertionError):
            data_to_json(data=[], file_type="err_file_type")

    def test_filename_blank(self):
        """Test file generation for missing file name."""
        # test file_name change if blank
        name_change = data_to_json(data=[], file_type="rhs")
        self.assertEqual(name_change["file_name"], "rhs.json")

    def test_file_type_and_name(self):
        """Test file generation for file type and name."""
        file_name_check = data_to_json(
            data=[], file_type="rhs", file_name="other_name.json"
        )
        self.assertEqual(file_name_check["file_type"], "rhs")
        self.assertEqual(file_name_check["file_name"], "other_name.json")

    def test_graph_file_body(self):
        """Test file generation for graph data."""
        graph = nx.Graph()
        graph.add_edge(1, 2)
        graph.add_edge(1, 3)
        graph_dict_check = {
            "file_type": "graph",
            "file_name": "graph.json",
            "directed": False,
            "multigraph": False,
            "graph": {},
            "nodes": [{"id": 1}, {"id": 2}, {"id": 3}],
            "links": [{"source": 1, "target": 2}, {"source": 1, "target": 3}],
        }

        graph_body = data_to_json(data=graph, file_type="graph")
        self.assertDictEqual(graph_dict_check, graph_body)

        with self.assertRaises(AssertionError) as context:
            data_to_json(data=np.array([]), file_type="graph")

        self.assertEqual(
            str(context.exception), "'graph' file_type must be type networkx.Graph"
        )

    @pytest.mark.timing
    def test_large_data_conversion(self):
        """Test file generation for large data is sufficiently fast."""
        large_qubo = np.random.normal(size=(3000, 3000))
        large_qubo = large_qubo + large_qubo.T
        start = time.perf_counter()
        data_to_json(data=large_qubo, file_type="qubo")
        end = time.perf_counter()
        conversion_time = end - start

        self.assertTrue(
            conversion_time < 5,
            msg=f"Matrix conversion to JSON took too long: 5s <= {conversion_time}s.",
        )

    def test_type_not_graph_check(self):
        """Test file generation for mismatched data and problem types."""
        with self.assertRaises(AssertionError) as context:
            graph = nx.Graph()
            data_to_json(data=graph, file_type="qubo")

        self.assertEqual(
            str(context.exception),
            "file_types ['rhs', 'objective', 'qubo', 'constraints', 'constraint_penalties', 'hamiltonian'] do not support networkx.Graph type",
        )

    def test_rhs_file_body(self):  # pylint: disable=too-many-locals
        """Test file generation for right-hand-side data."""
        rhs_list = [1, 2, 3]
        rhs_np = np.array([1, 2, 3])
        rhs_np_long = np.array([[1], [2], [3]])
        rhs_sp = sp.csr_matrix(rhs_np)
        rhs_sp_long = sp.csr_matrix(rhs_np_long)

        rhs_body_check = {
            "file_type": "rhs",
            "file_name": "rhs.json",
            "num_constraints": 3,
            "data": [1, 2, 3],
        }

        rhs_list_body = data_to_json(file_type="rhs", data=rhs_list)
        self.assertDictEqual(rhs_body_check, rhs_list_body)
        rhs_np_body = data_to_json(file_type="rhs", data=rhs_np)
        self.assertDictEqual(rhs_body_check, rhs_np_body)
        rhs_sp_body = data_to_json(file_type="rhs", data=rhs_sp)
        self.assertDictEqual(rhs_body_check, rhs_sp_body)
        rhs_np_long_body = data_to_json(file_type="rhs", data=rhs_np_long)
        self.assertDictEqual(rhs_body_check, rhs_np_long_body)
        rhs_sp_long_body = data_to_json(file_type="rhs", data=rhs_sp_long)
        self.assertDictEqual(rhs_body_check, rhs_sp_long_body)

        constraint_penalties_list = [1, 2, 3]
        constraint_penalties_np = np.array([1, 2, 3])
        constraint_penalties_np_long = np.array([[1], [2], [3]])
        constraint_penalties_sp = sp.csr_matrix(constraint_penalties_np)
        constraint_penalties_sp_long = sp.csr_matrix(constraint_penalties_np_long)

        constraint_penalties_body_check = {
            "file_type": "constraint_penalties",
            "file_name": "constraint_penalties.json",
            "num_constraints": 3,
            "data": [1, 2, 3],
        }

        constraint_penalties_list_body = data_to_json(
            file_type="constraint_penalties", data=constraint_penalties_list
        )
        self.assertDictEqual(
            constraint_penalties_body_check, constraint_penalties_list_body
        )
        constraint_penalties_np_body = data_to_json(
            file_type="constraint_penalties", data=constraint_penalties_np
        )
        self.assertDictEqual(
            constraint_penalties_body_check, constraint_penalties_np_body
        )
        constraint_penalties_sp_body = data_to_json(
            file_type="constraint_penalties", data=constraint_penalties_sp
        )
        self.assertDictEqual(
            constraint_penalties_body_check, constraint_penalties_sp_body
        )
        constraint_penalties_np_long_body = data_to_json(
            file_type="constraint_penalties", data=constraint_penalties_np_long
        )
        self.assertDictEqual(
            constraint_penalties_body_check, constraint_penalties_np_long_body
        )
        constraint_penalties_sp_long_body = data_to_json(
            file_type="constraint_penalties", data=constraint_penalties_sp_long
        )
        self.assertDictEqual(
            constraint_penalties_body_check, constraint_penalties_sp_long_body
        )

    def test_assert_types_objective_matrix(self):
        """Test file generation for improperly formatted qubo data."""
        with self.assertRaises(AssertionError) as context:
            data_to_json(data=[[1, -1], [-1, 1]], file_type="qubo")

        self.assertEqual(
            str(context.exception),
            "file_types = ['qubo', 'objective', 'constraints', 'hamiltonian'] only support types np.ndarray and scipy.sparse.spmatrix",
        )

    def test_qubo_hamiltonian_constraints_objective_file_body(self):
        """
        Test file generation for a qubo and hamiltonian objectives with constraints.
        """
        # will be used for both qubo and objective since same shape
        q_obj_np = np.array([[-1, 1], [1, -1]])
        q_obj_sp = sp.csr_matrix(q_obj_np)
        # is in i,j sorted order to allow for exact match of lists
        q_obj_data = [
            {"i": 0, "j": 0, "val": -1.0},
            {"i": 0, "j": 1, "val": 1.0},
            {"i": 1, "j": 0, "val": 1.0},
            {"i": 1, "j": 1, "val": -1.0},
        ]

        # using for hamiltonian and constraints
        ham_cons_np = np.array([[-1, 1, 1], [1, -1, 1]])
        ham_cons_sp = sp.csr_matrix(ham_cons_np)
        # is i, j sorted order to allow for exact match of lists
        ham_cons_data = [
            {"i": 0, "j": 0, "val": -1.0},
            {"i": 0, "j": 1, "val": 1.0},
            {"i": 0, "j": 2, "val": 1.0},
            {"i": 1, "j": 0, "val": 1.0},
            {"i": 1, "j": 1, "val": -1.0},
            {"i": 1, "j": 2, "val": 1.0},
        ]

        json_template = {
            "file_type": "placeholder",
            "file_name": "placeholder",
            "data": "placeholder",
        }

        # start from using fewest fields to most so can use update on same json_template
        # qubo
        file_type = "qubo"
        json_template.update(
            {
                "file_type": file_type,
                "file_name": file_type + ".json",
                "data": q_obj_data,
                "num_variables": 2,
            }
        )
        qubo_np_body = data_to_json(data=q_obj_np, file_type=file_type)
        qubo_np_body["data"] = sorted(qubo_np_body["data"], key=itemgetter("i", "j"))
        self.assertDictEqual(json_template, qubo_np_body)
        # objective
        file_type = "objective"
        json_template.update({"file_type": file_type, "file_name": file_type + ".json"})
        objective_sp_body = data_to_json(data=q_obj_sp, file_type=file_type)
        objective_sp_body["data"] = sorted(
            objective_sp_body["data"], key=itemgetter("i", "j")
        )
        self.assertDictEqual(json_template, objective_sp_body)
        # hamiltonian
        file_type = "hamiltonian"
        # don't have to update num_variables becaues is the same as was used for qubo and objective
        json_template.update(
            {
                "file_type": file_type,
                "file_name": file_type + ".json",
                "data": ham_cons_data,
            }
        )
        ham_np_body = data_to_json(data=ham_cons_np, file_type=file_type)
        ham_np_body["data"] = sorted(ham_np_body["data"], key=itemgetter("i", "j"))
        self.assertDictEqual(json_template, ham_np_body)
        # objective
        file_type = "constraints"
        json_template.update(
            {
                "file_type": file_type,
                "file_name": file_type + ".json",
                "num_variables": 3,
                "num_constraints": 2,
            }
        )
        constraints_sp_body = data_to_json(data=ham_cons_sp, file_type=file_type)
        constraints_sp_body["data"] = sorted(
            constraints_sp_body["data"], key=itemgetter("i", "j")
        )
        self.assertDictEqual(json_template, constraints_sp_body)


@pytest.mark.offline
class TestMultiPartFiles(unittest.TestCase):
    """Test suite for data conversion for multipart files."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.BIG = 500

    def _get_soln_size(self, soln):
        """
        TODO:    For graph solutions:
            {'node_id': Any, 'class': int}
            +
            decoded solutions

        All others work for lists as below.

        """
        return sys.getsizeof(soln[0]) * len(soln)

    def test_multipart_data(self):
        """TODO"""
        array = np.random.normal(size=(self.BIG, self.BIG))
        qubo = array + array.T

        # QUBO
        expected_data = data_to_json(
            qubo, file_type="qubo", file_name="test-qubo-multipart"
        )

        # test compressed QUBO
        compress = True
        compress_factor = 200000
        test_res_compress = list(multipart_file(expected_data, compress))
        expected_chunks_compress = float(self.BIG * self.BIG / compress_factor)

        # the last chunk can be smaller than the others so we need the ceiling value
        self.assertEqual(len(test_res_compress), int(ceil(expected_chunks_compress)))

        # test uncompressed QUBO
        uncompressed_factor = 10000
        test_res_uncompressed = list(
            multipart_file(expected_data)
        )  # compress is False by default
        expected_chunks_uncompressed = int(self.BIG * self.BIG / uncompressed_factor)

        self.assertEqual(len(test_res_uncompressed), expected_chunks_uncompressed)
        self.assertEqual(
            len(test_res_uncompressed[0][0]["data"]),
            len(test_res_uncompressed[1][0]["data"]),
        )

        # CONSTRAINTS -- just make sure there is no issue with changing file type
        expected_data = data_to_json(
            qubo, file_type="constraints", file_name="test-constraints-multipart"
        )
        test_res = list(multipart_file(expected_data))

        self.assertGreater(len(test_res), 1)
        self.assertEqual(len(test_res[0][0]["data"]), len(test_res[1][0]["data"]))

    def test_multipart_results(self):
        """Test multipart file generation for a large sampling result."""
        # Non-Graph RESULTS
        num_vars = 10000
        samples = np.ones((self.BIG, num_vars))
        counts = np.ones((self.BIG,))
        energies = np.ones((self.BIG,))

        resdata = {
            "file_name": "test-file.json",
            "file_type": "job_results_sample_qubo",
            "organization_id": "5ddf5db3fed87d53b6bf392a",
            "username": "emccaleb",
            "counts": counts,
            "energies": energies,
            "samples": samples,
        }

        step_len = compute_results_step_len(samples[0])
        expected_chunks = ceil(self.BIG / step_len)

        test_res = list(multipart_file(resdata))

        self.assertEqual(len(test_res), expected_chunks)
        self.assertEqual(len(test_res[0][0]["samples"]), len(test_res[1][0]["samples"]))

    def test_multipart_file_results_graph_partitioning(self):
        """Test multipart file generation for a graph partitioning problem."""
        # vectors we can reuse for testing
        test_vec = np.arange(self.BIG)

        samples = [
            [
                {"id": np.random.randint(0, 10), "class": np.random.randint(0, 3)}
                for _ in range(100)
            ]  # pretend we have a graph with 100 nodes
            for _ in range(self.BIG)  # and we asked for 1000 samples
        ]

        gp_results = {
            "file_name": "test-file.json",
            "file_type": "job_results_graph_partitioning",
            "organization_id": "test-end-user's-org-id",
            "username": "test-end-user",
            "balance": test_vec,
            "counts": test_vec,
            "cut_size": test_vec,
            "energies": test_vec,
            "is_feasible": [1] * self.BIG,
            "samples": samples,
        }

        step_len = compute_results_step_len(samples[0])
        expected_chunks = ceil(self.BIG / step_len)
        test_res = list(multipart_file(gp_results))

        self.assertEqual(len(test_res), expected_chunks)
        self.assertGreaterEqual(
            len(test_res[0][0]["samples"]), len(test_res[1][0]["samples"])
        )

    def test_multipart_file_results_community_detection(self):
        """Test multipart file generation for a community detection problem."""
        # vectors we can reuse for testing
        test_vec = np.arange(self.BIG)

        samples = [
            [
                {"id": np.random.randint(0, 10), "class": np.random.randint(0, 3)}
                for _ in range(100)
            ]  # pretend we have a graph with 100 nodes
            for _ in range(self.BIG)  # and we asked for 1000 samples
        ]

        cd_results = {
            "file_name": "test-file.json",
            "file_type": "job_results_unipartite_community_detection",
            "organization_id": "test-end-user's-org-id",
            "username": "test-end-user",
            "counts": test_vec,
            "energies": test_vec,
            "is_feasible": [1]
            * self.BIG,  # just a vector of the expected length and type
            "samples": samples,
            "modularity": np.ones(self.BIG) / 2,  # modularities == 0.5 \in [0,1]
        }

        test_res = list(multipart_file(cd_results))
        self.assertGreater(len(test_res), 1)
        self.assertGreaterEqual(
            len(test_res[0][0]["samples"]), len(test_res[1][0]["samples"])
        )

    def test_multipart_graph(self):
        """Test file generation for a larger graph problem."""
        num_nodes = 300  # Needs to generate at least two full parts.
        nodes = [{"id": ix} for ix in range(num_nodes)]
        links = []
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                links.append({"source": i, "target": j})

        graph_dict_check = {
            "file_type": "graph",
            "file_name": "graph.json",
            "directed": False,
            "multigraph": False,
            "graph": {},
            "nodes": nodes,
            "links": links,
        }

        test_res = list(multipart_file(graph_dict_check))

        self.assertGreater(len(test_res), 1)
        self.assertGreaterEqual(
            len(test_res[0][0]["nodes"]), len(test_res[1][0]["nodes"])
        )
        self.assertEqual(len(test_res[0][0]["links"]), len(test_res[1][0]["links"]))
        # The final chunk should be no larger than any chunks before it
        self.assertGreaterEqual(
            len(test_res[0][0]["links"]), len(test_res[-1][0]["links"])
        )

    def test_small_graph(self):
        """Test file generation for a small graph problem."""
        graph = nx.Graph()
        edge_wt = 1.0
        graph.add_nodes_from(range(7))

        for node in graph.nodes:
            if node in [0, 1, 2, 3]:
                graph.nodes[node].update({"bipartite": 0})
            else:
                graph.nodes[node].update({"bipartite": 1})

        graph.add_edges_from(
            [
                (0, 4, {"weight": edge_wt}),
                (0, 6, {"weight": edge_wt}),
                (1, 4, {"weight": edge_wt}),
                (2, 5, {"weight": edge_wt}),
                (3, 5, {"weight": edge_wt}),
            ]
        )

        graph_dict_check = {
            "file_type": "graph",
            "file_name": "graph.json",
            "directed": False,
            "multigraph": False,
            "graph": {},
            "nodes": list(graph.nodes(data=True)),
            "links": list(graph.edges(data=True)),
        }

        # get the first element (only one), and also remove the part_num (second tuple element)
        test_res = list(multipart_file(graph_dict_check))[0][0]

        self.assertEqual(len(test_res["nodes"]), graph.number_of_nodes())
        self.assertEqual(len(test_res["links"]), graph.number_of_edges())
