import json

import numpy as np


class Config:
    def __init__(
        self,
        project_name,
        model,
        class_list,
        target_classes,
        samples,
        user_config=None,
        device=None,
        mode="pt",
    ):
        config = {
            "leap_logging": True,
            "use_alpha": False,
            "alpha_mask": False,
            "alpha_only": False,
            "auto_balance_loss": False,
            "baseline_init": 0,
            "diversity_weight": 0,
            "isolate_classes": None,
            "hf_weight": 0,
            "isolation_hf_weight": 1,
            "input_dim": [224, 224, 3] if mode == "tf" else [3, 224, 224],
            "isolation": True,
            "log_freq": 100,
            "lr": 0.05,
            "isolation_lr": 0.05,
            "max_isolate_classes": min(5, len(class_list)),
            "max_steps": 1000,
            "seed": 0,
            "use_baseline": False,
            "transform": "xl",
            "target_classes": [0] if target_classes is None else target_classes,
            "use_hipe": False,
            "verbose": 1,
            "wandb_api_key": None,
            "wandb_entity": None,
            "logit_scale": 1,
        }

        if user_config is not None:
            if type(user_config) is str:
                with open(user_config) as f:
                    user_config = json.load(f)

        if user_config["leap_api_key"] is False:

            print("Oops, you don't seem to have a valid Leap API key. Head over to https://app.leap-labs.com/ to generate one.")
            exit()

        self.leap_api_key = user_config["leap_api_key"]
        del user_config["leap_api_key"]

        if (
            "wandb_api_key" in user_config.keys()
            and "wandb_api_key" in user_config.keys()
        ):
            self.wandb_api_key = user_config["wandb_api_key"]
            self.wandb_entity = user_config["wandb_entity"]
            del user_config["wandb_api_key"]
            del user_config["wandb_entity"]
        else:
            self.wandb_api_key = None
            self.wandb_entity = None

        user_config.update(
            {"class_list": class_list, "project_name": project_name, "device": device}
        )

        config.update(user_config)

        self.alpha_mask = config["alpha_mask"]
        self.alpha_only = config["alpha_only"]
        self.auto_balance_loss = config["auto_balance_loss"]
        self.baseline_init = config["baseline_init"]
        self.class_list = config["class_list"]
        self.device = config["device"]
        self.diversity_weight = config["diversity_weight"]
        self.isolate_classes = config["isolate_classes"]

        self.hf_weight = config["hf_weight"]
        self.isolation_hf_weight = config["isolation_hf_weight"]
        self.input_dim = config["input_dim"]
        self.isolation = config["isolation"] if samples is None else True
        self.leap_logging = config["leap_logging"]
        self.log_freq = config["log_freq"]
        self.logit_scale = config["logit_scale"]
        self.lr = config["lr"]
        self.isolation_lr = config["isolation_lr"]
        self.max_isolate_classes = min(
            config["max_isolate_classes"], len(class_list)
        ) or len(config["isolate_classes"])

        self.max_steps = config["max_steps"]
        self.mode = mode
        self.steps_per_it = self.max_steps // 3
        self.project_name = config["project_name"]
        self.seed = config["seed"]
        self.use_baseline = config["use_baseline"]
        if len(np.array(config["target_classes"]).shape) == 1:
            config["target_classes"] = [[c] for c in config["target_classes"]]
        self.target_classes = config["target_classes"]

        self.target_class_ix = [cix[0] for cix in self.target_classes]
        self.transform = config["transform"]
        self.use_hipe = config["use_hipe"]
        self.use_alpha = config["use_alpha"]
        self.verbose = config["verbose"]
