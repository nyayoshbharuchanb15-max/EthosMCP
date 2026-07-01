import pytest


@pytest.fixture
def sample_system_json():
    return {
        "system_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "system_name": "CandidateMatchPro",
        "system_version": "2.3.1",
        "vendor": "HireTech Solutions GmbH",
        "deployment_environment": "production",
        "data_lineage": {
            "sources": ["job_descriptions", "candidate_cvs"],
            "transformations": ["nlp_parsing", "candidate_scoring"],
            "destinations": ["ats_system", "recruiter_dashboard"],
        },
        "jurisdictions": ["EU", "UK", "IN"],
        "requested_by": "compliance@example.com",
    }


@pytest.fixture
def sample_run_id():
    return "550e8400-e29b-41d4-a716-446655440000"
