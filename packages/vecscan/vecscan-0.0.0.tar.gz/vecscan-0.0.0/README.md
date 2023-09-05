# vecscan v2
vecscan: linear-scan based dense vector search engine

## Introduction

The vecscan is a dense vector search engine that performs similarity search for embedding databases in linear and greedy way by using CUDA and SIMD instructions (such as AVX2, AVX512, or AMX) through PyTorch.

The vecscan is a simple implementation of linear search, and it does not cause quantization errors that tend to be a problem with approximate neighborhood searches like faiss, the vecscan makes it very easy to build your applications.

The default dtype of embedding vectors is `torch.bfloat16` and the binary file format of embedding database is `safetensors` in vecscan. The embedding database, which holds 1 million records of 768-dimensional bfloat16 vectors, occupies 1.5GB of main memory (or GPU memory). If you're using 8x Sapphire Rapids vCPUs, `VectorScanner.search()` takes only 0.1[sec] for entire similarity scoring and sorting. The benchmark results for major CPUs and GPUs can be found in later sections.

### Preparation

For both CPU and GPU with CUDA 11.7:
```console
git clone git@github.com:rit-git/vecscan.git
cd vecscan
pip install -r requirements.txt
```

If you need to use CUDA 11.8 or later version, install specific torch version with "--index-url":
```console
pip install -U torch --index-url https://download.pytorch.org/whl/cu118
```

### How to Search

The latency and the throughput of `VectorScanner.search()` depend on the FLOPs of the processors.
We recommend you to use the latest XEON platform (such as GCP C3 instance which supports AMX) or a CUDA GPU device (such as NVIDIA L4) with enough memory to load entire safetensors vector file.

If you use the OpenAI API, you need to install `openai` package and set api key to environmental variable. See [Embeding](#embedding-text-by-openais-text-embedding-ada-002) section for details.

```Python
from vecscan import VectorScanner, Vectorizer

# load safetensors file
scanner = VectorScanner.load_file("path_to_safetensors")

# use OpenAI's text-embedding-ada-002 with the environmental variable "OPENAI_API_KEY" 
vectorizer = Vectorizer.create(vectorizer_type="openai_api", model_path="text-embedding-ada-002")

# get query embedding
query_vec = vectorizer.vectorize(["some query text"])[0]
# execute search and get similarity scores and corresponding document ids in descendant order
sim_scores, doc_ids = scanner.search(query_vec)
```

## APIs

### Class Structure

```
vecscan/ -+- scanner ----+- VectorScanner
          |              |
          |              +- Similarity (Enum)
          |                 +- Dot
          |                 +- Cosine
          |                 +- L1
          |                 +- L2
          |
          +- vectorizer -+- Vectorizer
                            +- VectorizerOpenAIAPI
                            +- VectorizerBertCLS
                            +- VectorizerSBert
```

### VectorScanner

- Import
```Python
from vecscan import VectorScanner
```
- `VectorScanner(vectors: torch.Tensor)`
  - Instanciate VectorScanner and set `vectors`` to `self.vectors`
  - Args
    - `vectors`: A dense 2d Tensor instance which stores the search target embedding vectors
      - shape: [records, dim]
      - dtype: Any (vecscan is optimized for torch.bfloat16 or torch.float32)
      - device: Any (vecscan is optimized for "cpu" or "cuda")
- `to(device) -> VectorScanner`
  - Convert self.vectros to device
  - Return
    - `self`
- `score(self, query_vector: torch.Tensor, similarity_func=Similarity.Dot) -> torch.Tensor`
  - Calculate the similarity scores between `self.vectors` and `query_vector` by using `similarity_func`
  - Args
    - `query_vector`: A dense 1d Tensor instance which stores the embedding vector of query text
      - shape: [dim]
      - dtype: Assumed to be the same as self.vectors.dtype
      - device: Assumed to be the same as self.vectors.device
    - Return
      - A dense 1d Tensor instance which stores the similarity scores
      - shape: [records]
      - dtype: Assumed to be the same as self.vectors.dtype
      - device: Assumed to be the same as self.vectors.device
- `search(self, query_vector: torch.Tensor, target_ids: Optional[Union[List[int], torch.Tensor]]=None, n_best: int=1000, similarity_func=Similarity.Dot) -> torch.Tensor`
  - Calculate the similarity scores between `self.vectors` and `query_vector` by using `similarity_func`
  - Args
    - `query_vector`: A dense 1d Tensor instance which stores the embedding vector of query text
      - shape: [dim]
      - dtype: Assumed to be the same as self.vectors.dtype
      - device: Assumed to be the same as self.vectors.device
    - Return
      - A dense 1d Tensor instance which stores the similarity scores
      - shape: [records]
      - dtype: Assumed to be the same as self.vectors.dtype
      - device: Assumed to be the same as self.vectors.device

## Embedding Examples

### Embedding text by OpenAI's `text-embedding-ada-002`

```console
$ export HISTCONTROL=ignorespace  # do not save blankspace-started commands to history
$  export OPENAI_API_KEY=xxxx    # get secret key from https://platform.openai.com/account/api-keys
$ pip install openai
$ python -m vecscan.vectorizer -t openai_api -m text-embedding-ada-002 -o ada-002 < input.txt

2023-08-29 07:28:44,514 INFO:__main__: Will create following files:
2023-08-29 07:28:44,514 INFO:__main__:   ada-002.vec
2023-08-29 07:28:44,514 INFO:__main__:   ada-002.vec.info
2023-08-29 07:28:44,514 INFO:__main__:   ada-002.safetensors
2023-08-29 07:28:44,514 INFO:__main__: embedding started
1000it [00:03, 293.99it/s]
2023-08-29 07:28:48,702 INFO:__main__: {
 "vec_dim": 1536,
 "vec_count": 1000,
 "vec_dtype": "float32",
 "vectorizer_type": "openai_api",
 "model_path": "text-embedding-ada-002"
}
2023-08-29 07:28:48,702 INFO:__main__: embedding finished
2023-08-29 07:28:48,702 INFO:__main__: convert to safetensors
2023-08-29 07:28:48,718 INFO:__main__: convert finished
2023-08-29 07:28:48,719 INFO:__main__: ada-002.vec removed
```

### Embedding text by `cl-tohoku/bert-japanese-base-v3`

You need to use GPUs to embed text by BERT-like transformer models.

```console
$ pip install transformers fugashi unidic-lite
$ python -m vecscan.vectorizer -t bert_cls -m cl-tohoku/bert-base-japanese-v3 -o bert-base-japanese-v3 < input.txt

Some weights of BertForSequenceClassification were not initialized from the model checkpoint at cl-tohoku/bert-base-japanese-v3 and are newly initialized: ['classifier.weight', 'classifier.bias']
You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
2023-08-29 07:26:04,673 INFO:__main__: Will create following files:
2023-08-29 07:26:04,673 INFO:__main__:   bert-base-japanese-v3.vec
2023-08-29 07:26:04,673 INFO:__main__:   bert-base-japanese-v3.vec.info
2023-08-29 07:26:04,673 INFO:__main__:   bert-base-japanese-v3.safetensors
2023-08-29 07:26:04,673 INFO:__main__: embedding started
1000it [00:04, 240.00027it/s]
2023-08-29 07:26:11,736 INFO:__main__: {
 "vec_dim": 768,
 "vec_count": 1000,
 "vec_dtype": "float32",
 "vectorizer_type": "bert_cls",
 "model_path": "cl-tohoku/bert-base-japanese-v3"
}
2023-08-29 07:26:11,736 INFO:__main__: embedding finished
2023-08-29 07:26:11,739 INFO:__main__: convert to safetensors
2023-08-29 07:26:11,750 INFO:__main__: convert finished
2023-08-29 07:26:11,751 INFO:__main__: bert-base-japanese-v3.vec removed
```

### Embedding text by sentence-transformers model

```console
$ pip install transformers sentence-transformers
$ python -m vecscan.vectorizer -t sbert -m path_to_sbert_model -o sbert < input.txt

2023-08-29 07:26:53,544 INFO:__main__: Will create following files:
2023-08-29 07:26:53,544 INFO:__main__:   sbert.vec
2023-08-29 07:26:53,544 INFO:__main__:   sbert.vec.info
2023-08-29 07:26:53,544 INFO:__main__:   sbert.safetensors
2023-08-29 07:26:53,544 INFO:__main__: embedding started
1000it [00:02, 342.23it/s]
2023-08-29 07:26:56,757 INFO:__main__: {
 "vec_dim": 768,
 "vec_count": 1000,
 "vec_dtype": "float32",
 "vectorizer_type": "sbert",
 "model_path": "hysb_poor_mans_finetuned_posi/"
}
2023-08-29 07:26:56,757 INFO:__main__: embedding finished
2023-08-29 07:26:56,757 INFO:__main__: convert to safetensors
2023-08-29 07:26:56,768 INFO:__main__: convert finished
2023-08-29 07:26:56,769 INFO:__main__: sbert.vec removed
```

## Benchmarks

### Conditions and Environments

- GCP us-central1-b
  - balanced persistent disk 100GB
- ubuntu 22.04
  - cuda 11.8 (for GPUs)
- python 3.10.12
  - torch 2.0.1
- vectors
  - 768 dimension x 13,046,560 records = 10,019,758,080 elements
  - bfloat16 - 20.04[GB]
  - float32 - 40.08[GB]

### Results

<table>
<tr>
 <th rowspan=2> </th>
 <th rowspan=2>GCP Instance</th>
 <th rowspan=2>RAM</th>
 <th rowspan=2>Cost / Month</th>
 <th colspan=3>bfloat16 in [sec]</th>
 <th colspan=3>float32 in [sec]</th>
</tr><tr>
 <th>score()</th><th>search()</th><th>search() targets</th>
 <th>score()</th><th>search()</th><th>search() targets</th>
</tr><tr>
 <th colspan=11 align="left">L4 GPU x 1</th>
</tr><tr>
 <td> </td><td>g2-standard-8</td><td>24GB (GPU)</td><td>$633</td>
 <td>2.7e-4</td><td>5.3e-4</td><td>0.695</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <th colspan=11 align="left">A100 GPU x 1</th>
</tr><tr>
 <td> </td><td>a2-highgpu-1g</td><td>40GB (GPU)</td><td>$2,692</td>
 <td>2.6e-4</td><td>5.6e-4</td><td>0.696</td>
 <td>2.5e-4</td><td>6.0e-4</td><td>0.697</td>
</tr><tr>
 <th colspan=11 align="left">Sapphire Rapids (SR)</th>
</tr><tr>
 <td>#1</td><td>c3-highmem-4</td><td>32GB</td><td>$216</td>
 <td>1.072</td><td>1.802</td><td>1.994</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <td>#2</td><td>c3-standard-8</td><td>32GB</td><td>$315</td>
 <td>0.533</td><td>1.217</td><td>1.413</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <td>#3</td><td>c3-highmem-8</td><td>64GB</td><td>$421</td>
 <td>0.531</td><td>1.209</td><td>1.398</td>
 <td>0.852</td><td>2.386</td><td>2.117</td>
</tr><tr>
 <td>#4</td><td>c3-highcpu-22</td><td>44GB</td><td>$702</td>
 <td>0.231</td><td>0.887</td><td>1.077</td>
 <td>0.392</td><td>1.948</td><td>1.695</td>
</tr><tr>
 <td>#5</td><td>c3-highcpu-44</td><td>88GB</td><td>$1,394</td>
 <td>0.174</td><td>0.829</td><td>1.033</td>
 <td>0.356</td><td>1.900</td><td>1.644</td>
</tr><tr>
 <th colspan=11 align="left">Cascade Lake (CL)</th>
</tr><tr>
 <td>#1</td><td>n2-highmem-4</td><td>32GB</td><td>$163</td>
 <td>1.250</td><td>2.029</td><td>2.217</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <td>#2</td><td>n2-standard-8</td><td>32GB</td><td>$237</td>
 <td>0.643</td><td>1.388</td><td>1.671</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <td>#3</td><td>n2-highcpu-32</td><td>32GB</td><td>$702</td>
 <td>0.259</td><td>0.969</td><td>1.196</td>
 <td>-</td><td>-</td><td>-</td>
</tr><tr>
 <td>#4</td><td>n2-highmem-8</td><td>64GB</td><td>$316</td>
 <td>0.686</td><td>1.422</td><td>1.628</td>
 <td>0.923</td><td>2.410</td><td>2.255</td>
</tr><tr>
 <td>#5</td><td>n2-standard-16/td><td>64GB</td><td>$464</td>
 <td>0.375</td><td>1.084</td><td>1.307</td>
 <td>0.508</td><td>1.967</td><td>1.820</td>
</tr><tr>
 <td>#6</td><td>n2-highcpu-48</td><td>48GB</td><td>$1,015</td>
 <td>0.209</td><td>0.916</td><td>1.161</td>
 <td>0.370</td><td>1.878</td><td>1.743</td>
</tr><tr>
 <th colspan=11 align="left">Haswell (HW)</th>
</tr><tr>
 <td>#1</td><td>n1-highmem-8</td><td>52GB</td><td>$251</td>
 <td>62.317</td><td>63.095</td><td>63.461</td>
 <td>0.876</td><td>2.760</td><td>2.727</td>
</tr><tr>
 <td>#2</td><td>n1-standard-16</td><td>60GB</td><td>$398</td>
 <td>62.218</td><td>63.048</td><td>63.397</td>
 <td>0.530</td><td>2.365</td><td>2.298</td>
</tr><tr>
 <td>#3</td><td>n1-highcpu-64</td><td>57GB</td><td>$1,169</td>
 <td>62.141</td><td>63.026</td><td>63.818</td>
 <td>0.530</td><td>2.325</td><td>2.280</td>
</tr><tr>
</table>
