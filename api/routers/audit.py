from fastapi import APIRouter, HTTPException
from models.audit_models import (
    RiskClassificationInput, RiskTierResult,
    SupplyChainInput, ProvenanceReport,
    HumanOversightInput, OversightResult,
    BiasAssessmentInput, BiasReport,
    DPIAInput, DPIAReport,
    AdversarialTestInput, AdversarialReport,
    WeightedScoreInput, WeightedAuditScore,
    DriftMonitorInput, DriftAlert
)
from services.risk_classifier import RiskClassifierService
from services.supply_chain import SupplyChainService
from services.oversight_verifier import OversightVerifierService
from services.bias_engine import BiasEngineService
from services.dpia_generator import DPIAGeneratorService
from services.adversarial_tester import AdversarialTesterService
from services.weighted_scorer import WeightedScorerService
from services.drift_monitor import DriftMonitorService

router = APIRouter(prefix="/audit", tags=["audit"])

risk_service = RiskClassifierService()
supply_chain_service = SupplyChainService()
oversight_service = OversightVerifierService()
bias_service = BiasEngineService()
dpia_service = DPIAGeneratorService()
adversarial_service = AdversarialTesterService()
weighted_service = WeightedScorerService()
drift_service = DriftMonitorService()

@router.post("/classify-risk", response_model=RiskTierResult)
async def classify_risk(input_data: RiskClassificationInput):
    return risk_service.classify(input_data)

@router.post("/supply-chain", response_model=ProvenanceReport)
async def audit_supply_chain(input_data: SupplyChainInput):
    return supply_chain_service.audit(input_data)

@router.post("/human-oversight", response_model=OversightResult)
async def verify_human_oversight(input_data: HumanOversightInput):
    return oversight_service.verify(input_data)

@router.post("/bias-assessment", response_model=BiasReport)
async def run_bias_assessment(input_data: BiasAssessmentInput):
    return bias_service.assess(input_data)

@router.post("/dpia", response_model=DPIAReport)
async def generate_dpia(input_data: DPIAInput):
    return dpia_service.generate(input_data)

@router.post("/adversarial-tests", response_model=AdversarialReport)
async def run_adversarial_tests(input_data: AdversarialTestInput):
    return adversarial_service.test(input_data)

@router.post("/weighted-score", response_model=WeightedAuditScore)
async def score_audit_weighted(input_data: WeightedScoreInput):
    return weighted_service.calculate(input_data)

@router.post("/monitor-drift", response_model=DriftAlert)
async def monitor_model_drift(input_data: DriftMonitorInput):
    return drift_service.monitor(input_data)
