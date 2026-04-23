import express from 'express'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const app = express()
const __dirname = dirname(fileURLToPath(import.meta.url))

app.use(express.json())
app.use(express.static(__dirname))

const CENTAUR_API = 'https://svc-ai.dayno.xyz'
const CENTAUR_KEY = process.env.CENTAUR_API_KEY

// ── Venue scout endpoint ───────────────────────────────────────────────────
// Receives the brief from the web app and runs it through Centaur's skill
app.post('/api/scout', async (req, res) => {
  const { brief } = req.body
  if (!brief) return res.status(400).json({ error: 'brief required' })

  try {
    const response = await fetch(`${CENTAUR_API}/agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': CENTAUR_KEY,
      },
      body: JSON.stringify({
        skill: 'venue_scout',
        input: brief,
        stream: false,
      }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `Centaur API error ${response.status}`)
    }

    const data = await response.json()
    res.json(data)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

// ── Record booking (feedback loop for Centaur memory) ─────────────────────
app.post('/api/booking', async (req, res) => {
  const { venue_name, brief, feedback } = req.body
  if (!venue_name) return res.status(400).json({ error: 'venue_name required' })

  try {
    const response = await fetch(`${CENTAUR_API}/agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': CENTAUR_KEY,
      },
      body: JSON.stringify({
        skill: 'venue_scout',
        action: 'record_booking',
        input: { venue_name, brief, feedback },
        stream: false,
      }),
    })

    const data = await response.json()
    res.json(data)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => console.log(`Venue Scout running on :${PORT}`))
