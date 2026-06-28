from fastapi import APIRouter, HTTPException
from models.certificate_models import CertificateInput, CertificateResult
from services.certificate_issuer import CertificateIssuerService

router = APIRouter(prefix="/audit", tags=["certificates"])
issuer_service = CertificateIssuerService()

@router.post("/generate-certificate", response_model=CertificateResult)
async def generate_certificate(input_data: CertificateInput):
    try:
        return issuer_service.issue(input_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
