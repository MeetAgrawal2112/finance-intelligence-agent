// src/components/transactions/CSVImport.tsx
import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react'
import { useImportCSV } from '../../hooks/useTransactions'

export default function CSVImport({ onClose }: { onClose: () => void }) {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const importMutation = useImportCSV()

  const handleFile = (f: File) => {
    if (!f.name.endsWith('.csv')) {
      alert('Only CSV files allowed!')
      return
    }
    setFile(f)
    setResult(null)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleImport = async () => {
    if (!file) return
    try {
      const res = await importMutation.mutateAsync(file)
      setResult(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: 'white', borderRadius: '1rem',
        padding: '1.5rem', width: '100%', maxWidth: '480px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
      }}>
        <h2 style={{ margin: '0 0 1rem', fontSize: '1.1rem', fontWeight: 600 }}>
          Import CSV
        </h2>

        {/* CSV Format Info */}
        <div style={{
          background: '#f0f9ff', borderRadius: '0.625rem',
          padding: '0.75rem', marginBottom: '1rem', fontSize: '0.8rem',
          color: '#0284c7',
        }}>
          <strong>Format:</strong> date, amount, type (debit/credit), description, merchant
        </div>

        {/* Drop Zone */}
        {!result && (
          <div
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => fileRef.current?.click()}
            style={{
              border: `2px dashed ${dragOver ? '#0284c7' : '#e2e8f0'}`,
              borderRadius: '0.75rem', padding: '2rem',
              textAlign: 'center', cursor: 'pointer',
              background: dragOver ? '#f0f9ff' : '#f8fafc',
              transition: 'all 0.2s', marginBottom: '1rem',
            }}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            {file ? (
              <div>
                <FileText size={32} color="#0284c7" style={{ margin: '0 auto 0.5rem' }} />
                <p style={{ margin: 0, fontWeight: 500, color: '#0f172a' }}>
                  {file.name}
                </p>
                <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#64748b' }}>
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            ) : (
              <div>
                <Upload size={32} color="#94a3b8" style={{ margin: '0 auto 0.5rem' }} />
                <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>
                  CSV file drag karo ya click karo
                </p>
              </div>
            )}
          </div>
        )}

        {/* Import Result */}
        {result && (
          <div style={{
            background: '#f0fdf4', borderRadius: '0.75rem',
            padding: '1rem', marginBottom: '1rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <CheckCircle size={18} color="#16a34a" />
              <span style={{ fontWeight: 600, color: '#15803d' }}>Import Complete!</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#374151' }}>
              ✅ Imported: <strong>{result.imported}</strong> transactions
            </p>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', color: '#374151' }}>
              ⏭️ Skipped: <strong>{result.skipped}</strong>
            </p>
            {result.errors?.length > 0 && (
              <div style={{ marginTop: '0.5rem' }}>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#dc2626' }}>
                  Errors:
                </p>
                {result.errors.slice(0, 3).map((e: string, i: number) => (
                  <p key={i} style={{ margin: '0.2rem 0 0', fontSize: '0.7rem', color: '#dc2626' }}>
                    {e}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
          <button onClick={onClose} className="btn-secondary">
            {result ? 'Close' : 'Cancel'}
          </button>
          {!result && (
            <button
              onClick={handleImport}
              disabled={!file || importMutation.isPending}
              className="btn-primary"
              style={{
                width: 'auto', display: 'flex',
                alignItems: 'center', gap: '0.5rem',
              }}
            >
              {importMutation.isPending ? (
                <><Loader2 size={15} className="animate-spin" /> Importing...</>
              ) : (
                <><Upload size={15} /> Import</>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}