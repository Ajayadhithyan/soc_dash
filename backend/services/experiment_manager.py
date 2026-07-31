"""
Experiment Management System for Research.
Handles experiment configuration, seeding, and metadata tracking.
"""
import os
import yaml
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import numpy as np

logger = logging.getLogger("soc_backend")

class ExperimentManager:
    def __init__(self, config_dir: str = "experiments"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.current_experiment: Optional[Dict[str, Any]] = None
        self.experiment_history: List[Dict[str, Any]] = []
        self.global_seed: Optional[int] = None
        self._load_experiments()

    def _load_experiments(self):
        """Load all experiment configurations from the experiments directory."""
        self.experiments = {}
        for exp_file in self.config_dir.glob("*.yaml"):
            try:
                with open(exp_file, 'r') as f:
                    exp_config = yaml.safe_load(f)
                exp_id = exp_file.stem
                self.experiments[exp_id] = exp_config
                logger.info(f"Loaded experiment configuration: {exp_id}")
            except Exception as e:
                logger.error(f"Failed to load experiment {exp_file}: {e}")

        for exp_file in self.config_dir.glob("*.json"):
            try:
                with open(exp_file, 'r') as f:
                    exp_config = json.load(f)
                exp_id = exp_file.stem
                self.experiments[exp_id] = exp_config
                logger.info(f"Loaded experiment configuration: {exp_id}")
            except Exception as e:
                logger.error(f"Failed to load experiment {exp_file}: {e}")

    def create_experiment(self, exp_id: str, config: Dict[str, Any]) -> bool:
        """Create a new experiment configuration."""
        try:
            # Add metadata
            config['_metadata'] = {
                'created_at': datetime.now().isoformat(),
                'id': exp_id,
                'version': config.get('version', '1.0.0')
            }

            # Save to file
            exp_file = self.config_dir / f"{exp_id}.yaml"
            with open(exp_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            self.experiments[exp_id] = config
            logger.info(f"Created experiment: {exp_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create experiment {exp_id}: {e}")
            return False

    def start_experiment(self, exp_id: str, seed: Optional[int] = None) -> bool:
        """Start an experiment with optional seeding for reproducibility."""
        if exp_id not in self.experiments:
            logger.error(f"Experiment {exp_id} not found")
            return False

        try:
            self.current_experiment = self.experiments[exp_id].copy()

            # Handle seeding for reproducibility
            if seed is not None:
                self.global_seed = seed
                np.random.seed(seed)
                # Note: Python's random module seeding would need to be handled
                # wherever it's used in the codebase
                logger.info(f"Set global seed to {seed} for reproducible experiments")

            # Add runtime metadata
            self.current_experiment['_runtime_metadata'] = {
                'started_at': datetime.now().isoformat(),
                'seed': seed
            }

            logger.info(f"Started experiment: {exp_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start experiment {exp_id}: {e}")
            return False

    def stop_experiment(self) -> Optional[Dict[str, Any]]:
        """Stop the current experiment and return its metadata."""
        if self.current_experiment is None:
            logger.warning("No experiment currently running")
            return None

        # Add completion metadata
        self.current_experiment['_runtime_metadata']['ended_at'] = datetime.now().isoformat()
        self.experiment_history.append(self.current_experiment.copy())

        exp_id = self.current_experiment.get('_metadata', {}).get('id', 'unknown')
        logger.info(f"Stopped experiment: {exp_id}")

        completed_exp = self.current_experiment
        self.current_experiment = None
        self.global_seed = None
        # Note: In a real implementation, we'd need to restore previous random states

        return completed_exp

    def get_current_experiment(self) -> Optional[Dict[str, Any]]:
        """Get the currently active experiment configuration."""
        return self.current_experiment

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific experiment configuration by ID."""
        return self.experiments.get(exp_id)

    def list_experiments(self) -> List[str]:
        """List all available experiment IDs."""
        return list(self.experiments.keys())

    def is_in_experiment(self) -> bool:
        """Check if currently running an experiment."""
        return self.current_experiment is not None

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from the current experiment."""
        if self.current_experiment is None:
            return default

        # Support nested key access with dot notation
        keys = key.split('.')
        value = self.current_experiment
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def should_enable_feature(self, feature_name: str) -> bool:
        """Check if a research feature should be enabled."""
        return self.get_config_value(f"features.{feature_name}", False)

    def get_sampling_rate(self) -> float:
        """Get the sampling rate for research data collection."""
        return self.get_config_value("research.sampling_rate", 0.0)

    def get_batch_size(self) -> int:
        """Get batch size for research processing."""
        return self.get_config_value("research.batch_size", 1)

    def generate_experiment_id(self) -> str:
        """Generate a unique experiment ID based on timestamp and random component."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_component = hashlib.md5(str(np.random.randint(0, 10000)).encode()).hexdigest()[:6]
        return f"exp_{timestamp}_{random_component}"