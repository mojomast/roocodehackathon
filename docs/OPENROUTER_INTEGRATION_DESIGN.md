# Technical Design: OpenRouter Integration and Model Selection

## 1. Introduction

This document outlines the technical design for integrating OpenRouter as a new LLM provider and adding the capability for users to select the provider and specific model for documentation generation jobs. This will enhance the flexibility of the platform by allowing users to choose the most suitable model for their needs.

## 2. Backend Design

### 2.1. Worker Changes (`worker/ai_orchestrator.py`)

To support OpenRouter, a new provider class will be created.

#### `OpenRouterProvider`

A new class, `OpenRouterProvider`, will be added to `worker/ai_orchestrator.py`. It will inherit from the abstract base class `LLMProvider` and implement the `generate` method. This class will handle the specifics of interacting with the OpenRouter API.

```python
class OpenRouterProvider(LLMProvider):
    """LLM Provider for OpenRouter models."""
    def __init__(self, api_key: str = None):
        # In a real implementation, we would use the 'openai' library
        # configured with OpenRouter's base_url.
        self.client = openai
        if api_key:
            self.client.api_key = api_key
        # The base_url would be set to "https://openrouter.ai/api/v1"
        # self.client.base_url = "https://openrouter.ai/api/v1"


    def generate(self, system_prompt: str, user_prompt: str, model_config: dict) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model=model_config.get("model"), # The model name will be passed from the job
            messages=messages,
            temperature=model_config.get("temperature", 0.1),
            max_tokens=model_config.get("max_tokens", 4096)
        )
        return response.choices[0].message.content
```

#### `AIOrchestrator` Modifications

The `AIOrchestrator`'s `__init__` method will be updated to recognize and initialize the `OpenRouterProvider`. It will also need to be modified to accept the `provider` and `model_name` from the job details.

```python
# In AIOrchestrator.__init__
def __init__(self, provider: str = None, model_name: str = None):
    # ... existing code ...
    provider_name = provider or os.environ.get("LLM_PROVIDER", "openai").lower()
    self.model_config = {
        'temperature': 0.1,
        'max_tokens': 4096,
        'model': model_name # Set the model from the parameter
    }

    if provider_name == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY") # A new env var will be needed
        self.llm_provider = OpenRouterProvider(api_key=api_key)
        self.logger.info(f"Initialized with OpenRouter LLM provider for model {model_name}.")
    elif provider_name == "anthropic":
        # ... existing code ...
    elif provider_name == "openai":
        # ... existing code ...
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")

```

### 2.2. Database Model Changes (`backend/models.py`)

The `Job` model in `backend/models.py` will be extended to store the selected provider and model name for each job.

```python
# In backend/models.py
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"))
    status = Column(String, default=JobStatusEnum.PENDING.value)
    # ... existing fields ...
    provider = Column(String, nullable=True, default="openai") # New field
    model_name = Column(String, nullable=True, default="gpt-4-turbo") # New field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    repository = relationship("Repo", back_populates="jobs")
```

### 2.3. API Changes (`backend/main.py`)

The `/api/docs/run` endpoint will be updated to accept `provider` and `model_name` in the request body.

#### `JobCreateRequest` Model

The `JobCreateRequest` Pydantic model will be updated to include the new optional fields.

```python
# In backend/main.py
class JobCreateRequest(BaseModel):
    repo_id: int
    provider: str | None = "openai"
    model_name: str | None = "gpt-4-turbo"
```

#### Endpoint Implementation

The `trigger_documentation_run` function will be modified to use these new fields when creating a `Job`.

```python
# In backend/main.py
@app.post("/api/docs/run", dependencies=[Depends(verify_auth_token)])
async def trigger_documentation_run(request: JobCreateRequest, db: Session = Depends(get_db)):
    # ... existing repo lookup ...

    new_job = Job(
        repo_id=request.repo_id,
        status="pending",
        provider=request.provider,
        model_name=request.model_name,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Dispatch task to Celery worker
    process_documentation_job(new_job.id)

    return {"message": "Documentation run triggered", "job_id": new_job.id, "status": "pending"}
```

### 2.4. Job Processing

The Celery task `process_documentation_job` in `worker/worker.py` will need to be updated to fetch the `provider` and `model_name` from the `Job` record and pass them to the `AIOrchestrator`.

```python
# In worker/worker.py
@celery.task
def process_documentation_job(job_id: int):
    # ... get db session and job ...
    job = db.query(Job).filter(Job.id == job_id).first()
    # ...
    orchestrator = AIOrchestrator(provider=job.provider, model_name=job.model_name)
    # ...
```

## 3. Frontend Design

### 3.1. UI Controls (`frontend/src/app/repos/page.tsx`)

On the Repositories page, where users can trigger an analysis, new UI elements will be added within each repository card.

1.  **Provider Selection:** A dropdown menu (`<select>`) will be added to allow users to choose an LLM provider (e.g., "OpenAI", "Anthropic", "OpenRouter").
2.  **Model Name Input:** A text input (`<input type="text">`) will be added for the user to specify the model name (e.g., "gpt-4-turbo", "claude-3-opus-20240229", "google/gemini-pro").

These controls will be part of the repository card, likely appearing near the "Run Analysis" button. State will be managed using `useState` for each repository's selected provider and model.

```jsx
// In frontend/src/app/repos/page.tsx

// Inside the component, manage state for the inputs
const [provider, setProvider] = useState('openai');
const [modelName, setModelName] = useState('gpt-4-turbo');

// Inside the repo card mapping
<div key={repo.id} ...>
  {/* ... existing repo info ... */}
  <div>
    <label htmlFor={`provider-${repo.id}`}>Provider</label>
    <select id={`provider-${repo.id}`} value={provider} onChange={(e) => setProvider(e.target.value)}>
      <option value="openai">OpenAI</option>
      <option value="anthropic">Anthropic</option>
      <option value="openrouter">OpenRouter</option>
    </select>
  </div>
  <div>
    <label htmlFor={`model-${repo.id}`}>Model Name</label>
    <input
      type="text"
      id={`model-${repo.id}`}
      value={modelName}
      onChange={(e) => setModelName(e.target.value)}
    />
  </div>
  <button onClick={() => handleRunAnalysis(repo.id, provider, modelName)} ...>
    Run Analysis
  </button>
</div>
```

### 3.2. API Interaction

The `handleRunAnalysis` function will be updated to accept the selected `provider` and `modelName` and include them in the API call to the `/api/docs/run` endpoint.

```typescript
// In frontend/src/app/repos/page.tsx

const handleRunAnalysis = async (repoId: number, provider: string, modelName: string) => {
  setRunningAnalysis(repoId);
  try {
    const data = await apiClient.createJob({
      repo_id: repoId,
      provider: provider,
      model_name: modelName
    });
    setConnectMessage(data.message || 'Analysis triggered successfully!');
  } catch (error) {
    // ... error handling ...
  } finally {
    setRunningAnalysis(null);
  }
};

// The apiClient.createJob method in `utils/apiClient.ts` will also need to be updated
// to accept the new parameters in its payload.