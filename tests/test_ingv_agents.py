import pytest
from unittest.mock import MagicMock, patch
from agents.dataset_analyzer import analyze_dataset, summarize_earthquake_data
from agents.embedding_agent import EarthquakeEmbeddingAgent
from agents.metadata_recommender import suggest
from agents.content_improver import improve
from agents.qa_agent import EarthquakeQAAgent
from agents.reviewer import review

class TestINGVDatasetAnalyzer:

    @patch("agents.dataset_analyzer.load_files_from_directory")
    def test_analyze_dataset_parses_txt_files(self, mock_load):

        mock_load.return_value = [
            {
                "path": "eventi.txt",
                "content": (
                    "EventID|Time|Latitude|Longitude|Depth_Km|Author|Catalog|"
                    "Contributor|ContributorID|MagType|Magnitude|MagAuthor|"
                    "EventLocationName|EventType\n"
                    "1|2023-01-01|42.1|12.5|10|INGV|CAT|INGV|001|ML|3.2|INGV|Roma|earthquake"
                )
            }
        ]

        result = analyze_dataset("fake_dir")

        assert result["total_events"] == 1
        assert result["txt_ingv_files"] == 1
        assert result["events"][0]["EventID"] == "1"
        assert result["events"][0]["Magnitude"] == "3.2"


    def test_summarize_earthquake_data(self):
        events = [
            {"Magnitude": "3.0", "Depth_Km": "5"},
            {"Magnitude": "4.0", "Depth_Km": "12"}
        ]

        summary = summarize_earthquake_data(events)

        assert summary["min_magnitude"] == 3.0
        assert summary["max_magnitude"] == 4.0
        assert summary["avg_magnitude"] == 3.5
        assert summary["min_depth"] == 5.0
        assert summary["max_depth"] == 12.0
        assert summary["avg_depth"] == 8.5
        assert summary["total_events"] == 2



class TestEarthquakeEmbeddingAgent:

    @patch("sentence_transformers.SentenceTransformer")
    @patch("agents.embedding_agent.qdrant")   
    def test_embedding_and_upsert(self, mock_qdrant, mock_model):

        # Mock model
        mock_model_instance = MagicMock()
        mock_model_instance.encode.return_value = [[0.1, 0.2, 0.3]]
        mock_model.return_value = mock_model_instance

        # ✅ MOCK COMPLETO QDRANT
        mock_qdrant.get_collections.return_value = MagicMock(collections=[])
        mock_qdrant.create_collection.return_value = True
        mock_qdrant.upsert.return_value = True

        agent = EarthquakeEmbeddingAgent()

        events = [{
            "EventID": "1",
            "Time": "2023-01-01",
            "Latitude": "42.1",
            "Longitude": "12.5",
            "Depth_Km": "10",
            "Magnitude": "3.2",
            "MagType": "ML",
            "EventLocationName": "Roma",
            "EventType": "earthquake"
        }]

        agent.add_earthquake_events(events)

        mock_model_instance.encode.assert_called_once()
        mock_qdrant.upsert.assert_called_once()


    @patch("sentence_transformers.SentenceTransformer")
    @patch("agents.embedding_agent.qdrant")
    def test_semantic_search(self, mock_qdrant, mock_model):

        # mock modello
        mock_model_instance = MagicMock()
        mock_model_instance.encode.return_value = [[0.4, 0.5, 0.6]]
        mock_model.return_value = mock_model_instance

        # mock Qdrant
        mock_qdrant.get_collections.return_value = MagicMock(collections=["earthquake_events"])
        mock_qdrant.create_collection.return_value = True

        # ✅ MOCK CORRETTO: query_points (non search)
        mock_qdrant.query_points.return_value = MagicMock(
            points=[
                MagicMock(score=0.9, payload={"EventID": "2", "Magnitude": "4.0"})
            ]
        )

        agent = EarthquakeEmbeddingAgent()
        results = agent.semantic_search("test query")

        assert len(results) == 1
        assert results[0]["score"] == 0.9
        assert results[0]["event"]["EventID"] == "2"



@patch("agents.metadata_recommender.generate_titles")
@patch("agents.metadata_recommender.generate_one_line_summary")
@patch("agents.metadata_recommender.generate_tags")
@patch("agents.metadata_recommender.generate_reasoning")
def test_metadata_suggest(mock_reasoning, mock_tags, mock_one_line, mock_titles):

    mock_titles.return_value = ["Title 1", "Title 2"]
    mock_one_line.return_value = "One line summary"
    mock_tags.return_value = ["tag1", "tag2"]
    mock_reasoning.return_value = {"magnitude_range": "ok"}

    fake_summary = {
        "events": [{"Magnitude": "3.0"}],
        "summary": {"total_events": 1}
    }

    result = suggest(fake_summary)

    assert result["title_alternatives"] == ["Title 1", "Title 2"]
    assert result["one_line_summary"] == "One line summary"
    assert result["tags"] == ["tag1", "tag2"]
    assert result["reasoning"] == {"magnitude_range": "ok"}




def test_content_improver_basic():

    dataset_summary = {
        "summary": {
            "total_events": 2,
            "min_magnitude": 2.0,
            "max_magnitude": 4.0,
            "avg_magnitude": 3.0,
            "min_depth": 5,
            "max_depth": 10,
            "avg_depth": 7.5
        },
        "events": [{}, {}]
    }

    metadata = {"tag": "ok"}

    result = improve(dataset_summary, metadata)

    assert "improved_text" in result
    assert result["metadata_used"] == metadata
    assert result["events_processed"] == 2

@patch("agents.qa_agent.co")
@patch("agents.qa_agent.EarthquakeEmbeddingAgent")
def test_qa_agent(mock_emb_agent, mock_co):

    # Mock risultati ricerca semantica
    mock_emb_instance = MagicMock()
    mock_emb_instance.semantic_search.return_value = [
        {
            "score": 0.9,
            "event": {
                "EventID": "1",
                "Time": "2023",
                "Magnitude": "3.1",
                "MagType": "ML",
                "Depth_Km": "10",
                "Location": "Roma",
                "EventType": "earthquake"
            }
        }
    ]
    mock_emb_agent.return_value = mock_emb_instance

    # Mock Cohere
    mock_co.chat.return_value = MagicMock(text="Risposta test")

    agent = EarthquakeQAAgent()
    result = agent.answer("Test question")

    assert result == "Risposta test"
    mock_emb_instance.semantic_search.assert_called_once()
    mock_co.chat.assert_called_once()




@patch("agents.reviewer._is_single_area", return_value=True)
@patch("agents.reviewer.calculate_health_score_earthquakes", return_value=80)
@patch("agents.reviewer.generate_action_items_earthquakes", return_value=["fix1"])
@patch("agents.reviewer.get_priority_fixes_earthquakes", return_value=["priority"])
def test_reviewer_basic(mock_fix, mock_action, mock_score, mock_area):

    dataset = {
        "events": [
            {"EventID": "1", "Time": "2023", "Latitude": "1", "Longitude": "1",
             "Magnitude": "3.0", "Depth_Km": "10", "EventLocationName": "Roma"}
        ],
        "summary": {"max_magnitude": 3}
    }

    result = review(dataset)

    assert result["validation_results"]["overall_health"] == 80
    assert result["action_items"] == ["fix1"]
    assert result["priority_fixes"] == ["priority"]
