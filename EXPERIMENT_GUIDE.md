# Experiment Management System - Usage Guide

## Overview
The Experiment Management System allows researchers to run controlled experiments on the Zenith SOC platform while maintaining real-time dashboard functionality. It provides deterministic operation, configuration management, and experiment tracking.

## Key Features
1. **Deterministic Mode** - Ensures reproducible results through controlled random seeding
2. **Experiment Configuration** - YAML/JSON based experiment definitions
3. **Feature Flags** - Enable/disable research features without code changes
4. **Metadata Tracking** - Automatic experiment lifecycle tracking
5. **Non-intrusive** - Research features can be disabled for production use

## Using the Experiment System

### 1. Available Endpoints
- `GET /api/stats/experiment` - Get current experiment status and configuration

### 2. Creating Experiments
Experiments are defined in YAML or JSON files in the `/backend/experiments/` directory.

See `default_research.yaml` for a complete example configuration.

### 3. Environment Variables for Experiment Control
Set these in your `.env` file:
```
# Enable/disable experiment system (default: false)
EXPERIMENT_ENABLED=true

# Default experiment to start on startup (optional)
DEFAULT_EXPERIMENT=default_research

# Global seed for deterministic mode (optional)
EXPERIMENT_SEED=42
```

### 4. Programmatic Access
The experiment manager is available through the dependency injection container:

```python
# In any route or service
from backend.services.container import get_container, AppContainer
from fastapi import Depends

async def your_endpoint(
    container: AppContainer = Depends(get_container)
):
    exp_manager = container.experiment_manager
    
    # Start an experiment
    exp_manager.start_experiment("my_experiment", seed=123)
    
    # Check if in experiment mode
    if exp_manager.is_in_experiment():
        current_exp = exp_manager.get_current_experiment()
        # Access configuration values
        sampling_rate = exp_manager.get_config_value("research.sampling_rate", 0.0)
        feature_enabled = exp_manager.should_enable_feature("advanced_features")
    
    # Stop experiment when done
    exp_manager.stop_experiment()
```

### 5. Example Research Workflow

1. **Define Experiment**: Create `my_experiment.yaml` in `/backend/experiments/`

```yaml
version: '1.0.0'
name: 'ml_model_comparison'
description: 'Comparing Isolation Forest vs LOF for anomaly detection'
research:
  enabled: true
  deterministic_mode: true
  random_seed: 42
  sampling_rate: 1.0
features:
  alt_anomaly_detection: true
  model_explainability: true
models:
  anomaly_detector:
    type: 'LOF'  # Local Outlier Factor instead of default IsolationForest
    parameters:
      n_neighbors: 20
      contamination: 0.1
```

2. **Start Experiment**: 
   - Via API: The system can be configured to auto-start experiments
   - Or manually start it through code as shown above

3. **Run Research**: The system will now use the LOF algorithm instead of Isolation Forest for anomaly detection
   with deterministic behavior due to the fixed seed

4. **Collect Results**: Use the existing APIs to collect metrics, alerts, and performance data
   - `/api/stats/overview` - Basic statistics
   - `/api/stats/mitre` - ATT&CK technique distribution
   - `/api/alerts` - Detailed alert data (filtered by experiment if sampling < 1.0)

### 6. Best Practices for Research

#### A/B Testing
1. Create baseline experiment (A)
2. Create variant experiment (B) with one change
3. Run both for equal time periods
4. Compare metrics using standard statistical tests

#### Longitudinal Studies
1. Use the same experiment configuration over time
2. Track metric trends using the time-series endpoints
3. The deterministic mode ensures consistent baseline behavior

#### Feature Studies
1. Enable/disable specific features using the feature flags
2. Measure impact on detection performance and system latency
3. Use the experiment metadata to track which features were active

### 7. Safety Notes
- All research features include circuit breakers and graceful degradation
- The system will revert to basic operation if research components fail
- Memory and CPU limits prevent research features from overwhelming the system
- In production environments, consider setting `EXPERIMENT_ENABLED=false`

### 8. Configuration Reference
See `default_research.yaml` for complete configuration options with descriptions.

## Example API Response
GET /api/stats/experiment
```json
{
  "experiment_active": true,
  "experiment_id": "exp_20240115_143022_abc123",
  "experiment_name": "baseline_research_mode",
  "description": "Default research configuration for Zenith SOC system - enables deterministic operation and experiment tracking",
  "started_at": "2024-01-15T14:30:22.123456",
  "seed": 42,
  "features_enabled": {
    "alt_anomaly_detection": false,
    "advanced_features": false,
    "experimental_risk_scoring": false,
    "attack_pattern_analysis": true,
    "model_explainability": false,
    "ab_testing": false
  },
  "research_settings": {
    "enabled": true,
    "sampling_rate": 1.0,
    "batch_size": 100,
    "experiment_tracking": true,
    "deterministic_mode": true,
    "random_seed": 42,
    "collect_intermediate_features": true,
    "performance_profiling": true
  },
  "available_experiments": [
    "default_research",
    "baseline_test"
  ]
}
```