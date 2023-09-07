import numpy as np
import torch
import torch.nn.functional as F
from torchvision.transforms.functional import gaussian_blur
from tqdm import tqdm

from leap_labs_test.logging_handler import Logger
from leap_labs_test.transforms import normalise_each


def normalise(x):
    return (x - x.min()) / max(x.max() - x.min(), 0.0001)


def hierarchical_perturbation(
    config,
    model,
    target_mask,
    input,
    post_processing=[torch.nn.Identity()],
    type="feature_isolation",
    base_classes=None,
    substrate="noise",
    threshold_mode="mid-range",
    interp_mode="bilinear",
    max_depth=-1,
    logger=None,
):
    if logger is None:
        logger = Logger(
            config, target_mask, [], [torch.nn.Identity()], base_classes, type
        )
    else:
        logger.update(
            config, target_mask, [], [torch.nn.Identity()], base_classes, type
        )
    device = config.device
    input = torch.Tensor(input).to(device)
    model.to(device)
    model.eval()
    class_ix = [(t == 1).nonzero()[0].tolist() for t in target_mask]

    with torch.no_grad():
        _, channels, input_y_dim, input_x_dim = input.shape
        dim = min(input_x_dim, input_y_dim)
        total_masks = 0
        depth = 0
        num_cells = int(max(np.ceil(np.log2(dim)), 1) / 2)
        base_max_depth = int(np.log2(dim / num_cells)) - 1
        if max_depth == -1 or max_depth > base_max_depth:
            max_depth = base_max_depth

        num_classes = len(class_ix)
        output = model(input)[:, class_ix]

        saliency = torch.zeros(
            (num_classes, 1, input_y_dim, input_x_dim), device=device
        )
        depth_saliency = torch.zeros(
            (max_depth + 1, num_classes, 1, input_y_dim, input_x_dim), device=device
        )

        k_size = int(np.sqrt(max(input.shape)))
        if k_size % 2 == 0:
            k_size += 1
        if substrate == "blur":
            substrate = gaussian_blur(input.clone(), k_size).to(device)
        if substrate == "noise":
            substrate = torch.rand_like(input).to(device)
        if substrate == "fade":
            substrate = torch.zeros_like(input).to(device)

        while depth < max_depth:
            masks_list = []
            class_masks = []
            subs_list = []
            num_cells *= 2
            depth += 1

            if threshold_mode == "mean":
                threshold = torch.mean(saliency, dim=(-1, -2))
            else:
                threshold = torch.amin(saliency, dim=(-1, -2)) + (
                    (
                        torch.amax(saliency, dim=(-1, -2))
                        - torch.amin(saliency, dim=(-1, -2))
                    )
                    / 2
                )
            if threshold_mode == "var":
                threshold = -torch.var(threshold, dim=(-1, -2))

            y_ixs = range(-1, num_cells)
            x_ixs = range(-1, num_cells)
            x_cell_dim = input_x_dim // num_cells
            y_cell_dim = input_y_dim // num_cells

            for x in tqdm(x_ixs):
                for y in y_ixs:
                    x1, y1 = max(0, x), max(0, y)
                    x2, y2 = min(x + 2, num_cells), min(y + 2, num_cells)

                    mask = torch.zeros(
                        (num_classes, 1, num_cells, num_cells), device=device
                    )
                    mask[:, :, y1:y2, x1:x2] = 1.0

                    local_saliency = (
                        F.interpolate(
                            mask,
                            (input_y_dim, input_x_dim),
                            mode=interp_mode,
                            align_corners=True,
                        )
                        * saliency
                    )

                    if threshold_mode == "var":
                        local_saliency = -torch.var(
                            torch.amax(local_saliency, dim=(-1, -2))
                        )
                    else:
                        local_saliency = torch.amax(
                            torch.relu(local_saliency), dim=(-1, -2)
                        )

                    # If salience of region is greater than the average, generate higher resolution mask
                    class_threshold_mask = (
                        local_saliency.reshape(-1) >= threshold.reshape(-1)
                    ).int()
                    if class_threshold_mask.sum() >= 1 or depth == 0:
                        class_masks.append(class_threshold_mask)
                        masks_list.append(abs(mask - 1))
                        subs = input.clone()
                        subs[
                            :,
                            :,
                            y1 * y_cell_dim: y2 * y_cell_dim,
                            x1 * x_cell_dim: x2 * x_cell_dim,
                        ] = substrate[
                            :,
                            :,
                            y1 * y_cell_dim: y2 * y_cell_dim,
                            x1 * x_cell_dim: x2 * x_cell_dim,
                        ]
                        subs_list.append(subs)

            num_masks = len(masks_list)
            if num_masks == 0:
                break
            total_masks += num_masks

            for r in tqdm(range(len(subs_list))):
                # TODO batching?
                subs_in = subs_list.pop()
                class_mask = class_masks.pop()
                masks = masks_list.pop()

                masks = F.interpolate(
                    masks,
                    (input_y_dim, input_x_dim),
                    mode=interp_mode,
                    align_corners=True,
                )
                perturbed_outputs = torch.relu(
                    output - model(subs_in)[:, class_ix])
                sal = (
                    perturbed_outputs.reshape(-1, 1, 1, 1) *
                    torch.abs(masks - 1)
                ) * class_mask.reshape(-1, 1, 1, 1)
                saliency += sal
                depth_saliency[depth: depth + 1] += sal

            n_saliency = depth_saliency.clone() + 1
            n_saliency = normalise_each(n_saliency.prod(dim=(0)))

            n_input = normalise_each(input).repeat(num_classes, 1, 1, 1)

            input_a = torch.cat([n_input, n_saliency], dim=1)
            input_c = (n_input * n_saliency) + (substrate * (1 - n_saliency))
            logits = model(input_c)
            probs = torch.softmax(logits, dim=-1)
            step = int((depth / max_depth) * config.max_steps)
            if depth != max_depth:
                logger.verbose_log(
                    step,
                    logits.detach().cpu().numpy(),
                    probs.detach().cpu().numpy(),
                    None,
                    input_c.detach().cpu().numpy(),
                    input_a.detach().cpu().numpy(),
                    n_input.detach().cpu().numpy(),
                    None,
                    final=False,
                )  # images etc

        logger.verbose_log(
            step,
            logits.detach().cpu().numpy(),
            probs.detach().cpu().numpy(),
            None,
            input_c.detach().cpu().numpy(),
            input_a.detach().cpu().numpy(),
            n_input.detach().cpu().numpy(),
            None,
            final=True,
        )  # images etc

    return input_c.detach(), logits.detach(), logger
