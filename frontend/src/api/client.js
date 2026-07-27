/**
 * API Client for Insurance Claims Automation Platform.
 * Reads VITE_API_URL from environment — never hardcodes localhost in production.
 */

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== null) {
    opts.body = JSON.stringify(body)
  }

  const res = await fetch(`${BASE_URL}${path}`, opts)

  if (!res.ok) {
    const errText = await res.text()
    let errMsg = `API error ${res.status}`
    try {
      const errJson = JSON.parse(errText)
      errMsg = errJson.detail || errMsg
    } catch (_) { /* raw text */ }
    throw new Error(errMsg)
  }

  return res.json()
}

// ─── Claims ───────────────────────────────────────────────────────────────

/**
 * Submit a structured claim object.
 */
export function createClaim(claimData) {
  return request('POST', '/claims', claimData)
}

/**
 * Submit a raw text/narrative claim for Groq AI extraction.
 */
export function createUnstructuredClaim(rawText) {
  return request('POST', '/claims/unstructured', { raw_text: rawText })
}

/**
 * List claims with optional filters.
 * @param {Object} params - { status, min_score, limit, offset }
 */
export function listClaims({ status, min_score, limit = 50, offset = 0 } = {}) {
  const qp = new URLSearchParams()
  if (status) qp.set('status', status)
  if (min_score != null) qp.set('min_score', min_score)
  qp.set('limit', limit)
  qp.set('offset', offset)
  return request('GET', `/claims?${qp.toString()}`)
}

/**
 * Get full claim detail by database ID.
 */
export function getClaim(id) {
  return request('GET', `/claims/${id}`)
}

/**
 * Override claim status (approve / reject / manual_review).
 */
export function updateClaimStatus(id, status) {
  return request('PATCH', `/claims/${id}/status`, { status })
}

// ─── Scoring ──────────────────────────────────────────────────────────────

/**
 * Get live score + SHAP explanation for an existing claim.
 */
export function scoreClaim(id) {
  return request('GET', `/claims/${id}/score`)
}

/**
 * Get stored ML model training metrics.
 */
export function getModelMetrics() {
  return request('GET', '/model-metrics')
}

/**
 * Health check.
 */
export function healthCheck() {
  return request('GET', '/health')
}
