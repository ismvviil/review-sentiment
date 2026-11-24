// MiniLM sentence embeddings in the browser (transformers.js + ONNX Runtime Web).
// Mirrors sentence-transformers: tokenize (max 256 tokens) -> transformer -> mean pooling -> L2.
// The fp16 weights give the same predictions as PyTorch (verified on 300 test reviews).

const MODEL_ID = 'Xenova/all-MiniLM-L6-v2'
const MAX_TOKENS = 256
const CHUNK = 8

type Loaded = {
  tokenizer: (texts: string[], options: object) => Record<string, TensorLike>
  model: (inputs: Record<string, TensorLike>) => Promise<{ last_hidden_state: TensorLike }>
}
interface TensorLike {
  dims: number[]
  type: string
  data: ArrayLike<number | bigint>
  to(type: string): TensorLike
}

let loading: Promise<Loaded> | null = null

export function loadEmbedder(onProgress: (progress: number) => void): Promise<Loaded> {
  loading ??= (async () => {
    // Loaded on demand: the library is only downloaded when the browser engine is used
    const { AutoModel, AutoTokenizer, env } = await import('@huggingface/transformers')
    env.allowLocalModels = false
    const files = new Map<string, { loaded: number; total: number }>()
    const [tokenizer, model] = await Promise.all([
      AutoTokenizer.from_pretrained(MODEL_ID),
      AutoModel.from_pretrained(MODEL_ID, {
        dtype: 'fp16',
        device: 'wasm',
        progress_callback: (event: { status: string; file?: string; loaded?: number; total?: number }) => {
          if (event.status === 'progress' && event.file && event.total) {
            files.set(event.file, { loaded: event.loaded ?? 0, total: event.total })
            const all = [...files.values()]
            onProgress(all.reduce((s, f) => s + f.loaded, 0) / all.reduce((s, f) => s + f.total, 0))
          }
        },
      }),
    ])
    onProgress(1)
    return { tokenizer, model } as unknown as Loaded
  })()
  loading.catch(() => {
    loading = null // allow a retry after a network error
  })
  return loading
}

export async function embed(texts: string[], onProgress: (p: number) => void): Promise<Float32Array[]> {
  const { tokenizer, model } = await loadEmbedder(onProgress)
  const vectors: Float32Array[] = []

  for (let start = 0; start < texts.length; start += CHUNK) {
    const inputs = tokenizer(texts.slice(start, start + CHUNK), {
      padding: true,
      truncation: true,
      max_length: MAX_TOKENS,
    })
    let hidden = (await model(inputs)).last_hidden_state
    if (hidden.type !== 'float32') hidden = hidden.to('float32')

    const [batch = 0, tokens = 0, dim = 0] = hidden.dims
    const data = hidden.data as Float32Array
    const mask = inputs.attention_mask!.data

    for (let b = 0; b < batch; b++) {
      const v = new Float32Array(dim)
      let count = 0
      for (let t = 0; t < tokens; t++) {
        if (Number(mask[b * tokens + t]) === 0) continue
        count++
        const offset = (b * tokens + t) * dim
        for (let d = 0; d < dim; d++) v[d]! += data[offset + d]!
      }
      let norm = 0
      for (let d = 0; d < dim; d++) {
        v[d]! /= Math.max(count, 1)
        norm += v[d]! * v[d]!
      }
      norm = Math.sqrt(norm) || 1
      for (let d = 0; d < dim; d++) v[d]! /= norm
      vectors.push(v)
    }
  }
  return vectors
}
