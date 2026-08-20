"""Tests for the Qdrant candidate vector index."""

from unittest.mock import MagicMock

from candidate_intelligence.vector.index import CandidateVectorIndex


def test_index_creates_collection_if_missing() -> None:
    """Verify the collection is created when it does not already exist."""
    client = MagicMock()
    client.collection_exists.return_value = False

    CandidateVectorIndex(client, collection_name="candidates", vector_size=768)

    client.collection_exists.assert_called_once_with("candidates")
    client.create_collection.assert_called_once()


def test_index_skips_collection_creation_if_exists() -> None:
    """Verify the collection is not recreated when it already exists."""
    client = MagicMock()
    client.collection_exists.return_value = True

    CandidateVectorIndex(client, collection_name="candidates", vector_size=768)

    client.create_collection.assert_not_called()


def test_upsert_calls_client_with_point() -> None:
    """Verify upsert sends a point with the correct id and vector."""
    client = MagicMock()
    client.collection_exists.return_value = True
    index = CandidateVectorIndex(client, collection_name="candidates", vector_size=3)

    index.upsert("candidate-1", [0.1, 0.2, 0.3])

    client.upsert.assert_called_once()
    call_kwargs = client.upsert.call_args.kwargs
    assert call_kwargs["collection_name"] == "candidates"
    points = call_kwargs["points"]
    assert len(points) == 1
    assert points[0].id == "candidate-1"
    assert points[0].vector == [0.1, 0.2, 0.3]


def test_search_returns_candidate_results() -> None:
    """Verify search returns parsed CandidateSearchResult objects."""
    client = MagicMock()
    client.collection_exists.return_value = True
    mock_point = MagicMock()
    mock_point.payload = {"candidate_id": "candidate-1"}
    mock_point.score = 0.87
    client.query_points.return_value = MagicMock(points=[mock_point])
    index = CandidateVectorIndex(client, collection_name="candidates", vector_size=3)

    results = index.search([0.1, 0.2, 0.3], limit=5)

    assert len(results) == 1
    assert results[0].candidate_id == "candidate-1"
    assert results[0].score == 0.87
