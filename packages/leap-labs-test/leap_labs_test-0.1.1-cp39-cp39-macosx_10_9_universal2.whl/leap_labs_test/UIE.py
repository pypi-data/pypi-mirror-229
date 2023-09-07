import tensorflow as tf
from IPython.core.display import display, HTML
from PIL import Image
import numpy as np
import pandas as pd
from leap_labs_test.utils import *
from leap_labs_test.config_handler import Config


def generate(
    project_name,
    model,
    class_list,
    target_classes=None,
    preprocessing=None,
    samples=None,
    config=None,
    device=None,
    mode="pt",
):

    if mode == "tf":
        print("Tensorflow mode enabled.")
        import leap_labs_test.transforms_tf as tran
        import leap_labs_test.objectives_tf as obj
        import leap_labs_test.saliency_tf as sal
        from leap_labs_test.generation_tf import generator

    elif mode == "pt":
        print("Pytorch mode enabled.")
        import leap_labs_test.transforms as tran
        import leap_labs_test.objectives as obj
        import leap_labs_test.saliency as sal
        from leap_labs_test.generation import generator

    if device is None:
        device = get_device(mode)

    else:
        print('Invalid mode. Please set mode = either "pt" or "tf".')
        exit()

    config = Config(
        project_name,
        model,
        class_list,
        target_classes,
        samples,
        user_config=config,
        device=device,
        mode=mode,
    )

    if samples is not None:
        config.isolation = True

    num_classes = len(class_list)

    set_seed(config.seed)
    objectives = [obj.default_objective, obj.minimise_hf]
    objective_weights = [1, config.hf_weight]
    post_processing = [lambda x: x]
    logger = None

    if config.alpha_mask:
        config.use_alpha = True
        alpha_mask = tran.get_mask(config.input_dim[-2:])
        objectives = objectives + [obj.masked_alpha_objective]
        objective_weights = objective_weights + [1]
    else:
        alpha_mask = None

    transforms = tran.get_transforms(
        config.transform, preprocessing, config.use_alpha)

    target_masks = np.zeros((len(config.target_classes), num_classes))
    for i, t in enumerate(config.target_classes):
        target_masks[i, t] = 1
    if samples is None:
        init_dim = [1] + config.input_dim
        if config.use_alpha:
            if mode == "pt":
                init_dim[1] += 1
            if mode == "tf":
                init_dim[-1] += 1
            if config.baseline_init == "r":
                baseline_init_input = np.random.rand(init_dim)
            else:
                baseline_init_input = np.ones(init_dim) * config.baseline_init

            if mode == "pt":
                baseline_init_input[:, -1:] = 1
            if mode == "tf":
                baseline_init_input[:, :, :, -1:] = 1
        else:
            if config.baseline_init == "r":
                baseline_init_input = np.random.rand(init_dim)
            else:
                baseline_init_input = np.ones(init_dim) * config.baseline_init

        if not config.use_baseline:
            baseline_input = baseline_init_input
        else:
            print("Generating baseline...")
            baseline_input, _, logger = generator(
                config=config,
                model=model,
                target_mask=np.zeros((1, len(class_list))),
                input=baseline_init_input,
                objectives=[obj.minimise_prob_range] + objectives[1:],
                objective_weights=objective_weights,
                post_processing=post_processing,
                transforms=transforms,
                alpha_mask=alpha_mask,
                type="baseline",
                logger=logger,
            )

    if len(config.target_classes) > len(set(tuple(c) for c in config.target_classes)):
        for i in range(len(config.target_classes)):
            for j in range(1, len(config.target_classes)):
                if config.target_classes[i] == config.target_classes[j]:
                    baseline_input[j] += (
                        np.random.rand_like(baseline_input[j]) - 0.5
                    ) * 0.01

        objectives = objectives + [obj.maximise_diversity]
        objective_weights = objective_weights + [config.diversity_weight]

    if samples is None:
        print("Generating class prototypes...")
        baseline_input = np.concatenate(
            [baseline_input] * len(config.target_classes))

        opt_inputs, opt_logits, logger = generator(
            config=config,
            model=model,
            target_mask=target_masks,
            input=baseline_input,
            objectives=objectives,
            objective_weights=objective_weights,
            post_processing=post_processing,
            transforms=transforms,
            alpha_mask=alpha_mask,
            logger=logger,
            type="prototype",
        )

    if config.isolation:
        print("Isolating salient features...")

        config.alpha_only = True
        config.use_alpha = True

        if samples is not None:
            if mode == "pt":
                opt_logits = model(samples).detach().numpy()
                opt_inputs = samples.detach().numpy()
            if mode == "tf":
                opt_logits = model(samples).numpy()
                opt_inputs = samples.numpy()

        for i, c_input in enumerate(opt_inputs):
            base_classes = config.target_classes[i] if samples is None else None

            if config.isolate_classes is None:
                sorted_ix = np.argsort(-opt_logits[i])
                ix = sorted_ix[: config.max_isolate_classes]
            else:
                ix = config.isolate_classes

            print(f"Isolating features for: {[class_list[x] for x in ix]}")

            if mode == "pt":
                alpha_exists = c_input.shape[0] == config.input_dim[0] + 1
            if mode == "tf":
                alpha_exists = c_input.shape[-1] == config.input_dim[-1] + 1

            if alpha_exists:
                aa = tran.add_alpha()
                c_input = aa(np.copy(c_input)[np.newaxis, ...])
            else:
                c_input = np.copy(c_input)[np.newaxis, ...]

            target_masks = np.zeros((config.max_isolate_classes, num_classes))
            for it, t in enumerate(ix):
                target_masks[it, t] = 1

            if mode == "tf" and config.use_hipe:
                print(
                    "Hierarchicial perturbation (HiPe) not yet implemented for Tensorflow, sorry! Using default instead."
                )
            if config.use_hipe and mode == "pt":
                _, _, logger = sal.hierarchical_perturbation(
                    config=config,
                    model=model,
                    target_mask=target_masks,
                    input=c_input,
                    post_processing=post_processing,
                    type="saliency" if samples is not None else "isolation",
                    base_classes=base_classes,
                    logger=logger,
                )

            else:
                if mode == "pt":
                    input = np.concatenate(
                        [c_input, np.ones_like(c_input[:, -1:])], axis=1
                    )
                if mode == "tf":
                    input = np.concatenate(
                        [c_input, np.ones_like(c_input[:, :, :, -1:])], axis=-1
                    )

                input = np.concatenate([input] * config.max_isolate_classes)

                _, _, logger = generator(
                    config=config,
                    model=model,
                    target_mask=target_masks,
                    input=input,
                    objectives=[
                        obj.default_objective,
                        obj.minimise_alpha_hf,
                        obj.alpha_objective,
                    ],
                    objective_weights=[1, config.isolation_hf_weight, 1],
                    post_processing=post_processing,
                    transforms=[tran.add_alpha()],
                    alpha_mask=alpha_mask,
                    type="saliency" if samples is not None else "isolation",
                    base_classes=base_classes,
                    logit_clamp=True,
                    logger=logger,
                )

    results = logger.get_table()
    logger.finish()
    if samples is not None:
        return pd.DataFrame(columns=results[0], data=results[1]).sort_values(
            by=["probs"], ascending=False
        )
    else:
        return pd.DataFrame(columns=results[0], data=results[1]).sort_values(
            by=["entanglement", "target_class"], ascending=False
        )


def display_results(df):
    html = df.reset_index(drop=True).to_html(
        escape=False,
        formatters=dict(
            input=lambda path: f'<img src="{path}" width="300" >' if path else ""
        ),
    )
    display(HTML(html))
