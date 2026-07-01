import crypto from 'node:crypto';
import axios from 'axios';
import { Phase8InputSchema, Phase8OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function issueComplianceCertificate(input: any) {
  const parsed = Phase8InputSchema.parse(input);
  const { run_id, verify_all_phases_passed } = parsed;

  const findings: Finding[] = [];

  // Verify orchestrator state for all phases
  let certificationIssued = false;
  let proofValue = '';
  let merkleRoot = '';
  let timestampToken = '';

  try {
    const statusResp = await axios.get(`${ORCHESTRATOR_URL}/audit/${run_id}/status`, { timeout: 10000 });
    const runStatus = statusResp.data;

    if (verify_all_phases_passed) {
      const phases = runStatus.phases || {};
      const allPassed = Object.values(phases).every((s: any) => s === 'PASS');
      const blockers = runStatus.blocker_findings || [];

      if (!allPassed) {
        findings.push({
          finding_id: crypto.randomUUID(),
          severity: 'BLOCKER',
          regulation: 'EU AI Act',
          article: 'Art. 26',
          description: 'Cannot issue certificate — not all phases passed certification requirements',
          remediation: 'Address all non-passing phase findings and re-run affected phases',
        });
      }

      if (blockers.length > 0) {
        findings.push({
          finding_id: crypto.randomUUID(),
          severity: 'BLOCKER',
          regulation: 'EU AI Act',
          article: 'Art. 26',
          description: `Cannot issue certificate — ${blockers.length} blocker finding(s) exist in audit pipeline`,
          remediation: 'Resolve all BLOCKER severity findings before requesting certificate issuance',
        });
      }

      if (allPassed && blockers.length === 0) {
        // Simulate EdDSA signing and Merkle root computation
        const signingPayload = `ai-compliance-certificate:${run_id}:${Date.now()}`;
        const signingDigest = crypto.createHash('sha256').update(signingPayload).digest();
        proofValue = 'z' + signingDigest.toString('base58');

        // Build Merkle tree from phase artifact hashes
        const artifactHashes = (runStatus.artifacts || []).map((a: any) => a.artifact_hash);
        if (artifactHashes.length > 0) {
          merkleRoot = buildMerkleRoot(artifactHashes);
        } else {
          merkleRoot = crypto.createHash('sha256').update(run_id).digest('hex');
        }

        // Simulate RFC 3161 timestamp token
        timestampToken = Buffer.from(JSON.stringify({
          ts: new Date().toISOString(),
          serial: crypto.randomBytes(8).toString('hex'),
          algo: 'sha256',
        })).toString('base64');

        certificationIssued = true;

        // Persist certificate
        await axios.post(`${ORCHESTRATOR_URL}/certificate/issue`, {
          run_id,
          proof_value: proofValue,
          merkle_root: merkleRoot,
          timestamp_token: timestampToken,
          issued_at: new Date().toISOString(),
        }, { timeout: 10000 });

        logger.info('Certificate issued', { run_id, merkleRoot });
      }
    }
  } catch (error: any) {
    logger.error('Certificate issuance orchestrator call failed', { run_id, error: error.message });
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'BLOCKER',
      regulation: 'EU AI Act',
      article: 'Art. 26',
      description: `Orchestrator communication failed: ${error.message}`,
      remediation: 'Ensure orchestrator is running and audit status is accessible',
    });
  }

  const vc_json = certificationIssued ? {
    '@context': ['https://www.w3.org/ns/credentials/v2'],
    type: ['VerifiableCredential', 'AIAuditCertificate'],
    issuer: process.env.ISSUER_DID || 'did:key:placeholder',
    issuanceDate: new Date().toISOString(),
    credentialSubject: {
      id: `did:audit:${run_id}`,
      auditRunId: run_id,
      complianceStatus: 'Compliant',
      merkle_root: merkleRoot,
      rfc3161_timestamp: {
        token_base64: timestampToken,
        tsa_url: process.env.TSA_URL || 'http://timestamp.yourorg.internal',
      },
    },
    proof: {
      type: 'Ed25519Signature2020',
      created: new Date().toISOString(),
      verificationMethod: `${process.env.ISSUER_DID || 'did:key:placeholder'}#${process.env.ISSUER_DID?.split(':').pop() || 'placeholder'}`,
      proofPurpose: 'assertionMethod',
      proofValue: proofValue,
    },
  } : undefined;

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  const output = Phase8OutputSchema.parse({
    run_id,
    phase: 8,
    phase_result: findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS',
    certification_issued: certificationIssued,
    vc_json,
    proof_value: proofValue || undefined,
    merkle_root: merkleRoot || undefined,
    timestamp_token: timestampToken || undefined,
    findings,
    artifact_hash,
    next_phase: 9,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}

function buildMerkleRoot(hashes: string[]): string {
  if (hashes.length === 1) return hashes[0];
  let level = hashes.map(h => Buffer.from(h, 'hex'));
  while (level.length > 1) {
    const next: Buffer[] = [];
    for (let i = 0; i < level.length; i += 2) {
      if (i + 1 < level.length) {
        const combined = Buffer.concat([level[i], level[i + 1]]);
        next.push(crypto.createHash('sha256').update(combined).digest());
      } else {
        next.push(level[i]);
      }
    }
    level = next;
  }
  return level[0].toString('hex');
}
