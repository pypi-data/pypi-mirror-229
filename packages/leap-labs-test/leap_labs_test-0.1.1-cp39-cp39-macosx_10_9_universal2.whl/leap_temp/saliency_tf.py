import tensorflow as tf
import numpy as np

from tqdm import tqdm

from leap_labs_test.logging_handler import Logger
from leap_labs_test.transforms_tf import normalise_each


def normalise(x):
    return (x - tf.reduce_min(x)) / tf.maximum(
        tf.reduce_max(x) - tf.reduce_min(x), 0.0001
    )


def hierarchical_perturbation(
    config,
    model,
    target_mask,
    input,
    post_processing=[tf.identity],
    type="feature_isolation",
    base_classes=None,
    substrate="noise",
    threshold_mode="mid-range",
    interp_mode="bilinear",
    max_depth=-1,
    logger=None,
):
    if logger is None:
        logger = Logger(config, target_mask, [], [
                        tf.identity], base_classes, type)
    else:
        logger.update(config, target_mask, [], [
                      tf.identity], base_classes, type)

    device = config.device  # Assumed to be defined in config
    input = tf.convert_to_tensor(input, dtype=tf.float32)
    model.trainable = False

    class_ix = [tf.where(tf.equal(t, 1))[:, 0] for t in target_mask]

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

    saliency = tf.zeros((num_classes, 1, input_y_dim,
                        input_x_dim), dtype=tf.float32)
    depth_saliency = tf.zeros(
        (max_depth + 1, num_classes, 1, input_y_dim, input_x_dim), dtype=tf.float32
    )

    k_size = int(np.sqrt(max(input.shape)))
    if k_size % 2 == 0:
        k_size += 1
    if substrate == "blur":
        substrate = tf.image.gaussian_filter2d(
            input, filter_shape=k_size
        )  # Assumes a 4D tensor
    if substrate == "noise":
        substrate = tf.random.uniform(tf.shape(input), dtype=tf.float32)
    if substrate == "fade":
        substrate = tf.zeros_like(input)

    while depth < max_depth:
        masks_list = []
        class_masks = []
        subs_list = []
        num_cells *= 2
        depth += 1

        if threshold_mode == "mean":
            threshold = tf.reduce_mean(saliency, axis=(-1, -2))
        else:
            threshold = tf.reduce_min(saliency, axis=(-1, -2)) + (
                (
                    tf.reduce_max(saliency, axis=(-1, -2))
                    - tf.reduce_min(saliency, axis=(-1, -2))
                )
                / 2
            )
        if threshold_mode == "var":
            threshold = -tf.math.reduce_variance(threshold, axis=(-1, -2))

        y_ixs = range(-1, num_cells)
        x_ixs = range(-1, num_cells)
        x_cell_dim = input_x_dim // num_cells
        y_cell_dim = input_y_dim // num_cells

        for x in tqdm(x_ixs):
            for y in y_ixs:
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(x + 2, num_cells), min(y + 2, num_cells)

                mask = tf.zeros(
                    (num_classes, 1, num_cells, num_cells), dtype=tf.float32
                )
                mask[:, :, y1:y2, x1:x2].assign(1.0)

                local_saliency = mask * tf.image.resize(
                    saliency, (input_y_dim, input_x_dim), method=interp_mode
                )

                if threshold_mode == "var":
                    local_saliency = -tf.math.reduce_variance(
                        tf.reduce_max(local_saliency, axis=(-1, -2))
                    )
                else:
                    local_saliency = tf.reduce_max(
                        tf.nn.relu(local_saliency), axis=(-1, -2)
                    )

                class_threshold_mask = tf.cast(
                    tf.reshape(local_saliency, [-1]
                               ) >= tf.reshape(threshold, [-1]),
                    tf.int32,
                )
                if tf.reduce_sum(class_threshold_mask) >= 1 or depth == 0:
                    class_masks.append(class_threshold_mask)
                    masks_list.append(tf.math.abs(mask - 1))
                    subs = tf.identity(input)
                    subs[
                        :,
                        :,
                        y1 * y_cell_dim: y2 * y_cell_dim,
                        x1 * x_cell_dim: x2 * x_cell_dim,
                    ].assign(
                        substrate[
                            :,
                            :,
                            y1 * y_cell_dim: y2 * y_cell_dim,
                            x1 * x_cell_dim: x2 * x_cell_dim,
                        ]
                    )
                    subs_list.append(subs)

        num_masks = len(masks_list)
        if num_masks == 0:
            break
        total_masks += num_masks

        for r in tqdm(range(len(subs_list))):
            subs_in = subs_list.pop()
            class_mask = class_masks.pop()
            masks = masks_list.pop()

            masks = tf.image.resize(
                masks, (input_y_dim, input_x_dim), method=interp_mode
            )
            perturbed_outputs = tf.nn.relu(
                output - model(subs_in)[:, class_ix])
            sal = (
                tf.reshape(perturbed_outputs,
                           [-1, 1, 1, 1]) * tf.math.abs(masks - 1)
            ) * tf.reshape(class_mask, [-1, 1, 1, 1])
            saliency += sal
            depth_saliency = depth_saliency + sal

        n_saliency = depth_saliency + 1
        n_saliency = normalise_each(
            tf.math.reduce_prod(n_saliency, axis=0)
        )  # Assuming normalise_each is defined

        n_input = normalise_each(input)  # Assuming normalise_each is defined
        n_input = tf.tile(n_input, [num_classes, 1, 1, 1])

        input_a = tf.concat([n_input, n_saliency], axis=1)
        input_c = (n_input * n_saliency) + (substrate * (1 - n_saliency))
        logits = model(input_c)
        probs = tf.nn.softmax(logits, axis=-1)
        step = int((depth / max_depth) * config.max_steps)
        if depth != max_depth:
            logger.verbose_log(
                step,
                logits.numpy(),
                probs.numpy(),
                None,
                input_c.numpy(),
                input_a.numpy(),
                n_input.numpy(),
                None,
                final=False,
            )

    logger.verbose_log(
        step,
        logits.numpy(),
        probs.numpy(),
        None,
        input_c.numpy(),
        input_a.numpy(),
        n_input.numpy(),
        None,
        final=True,
    )

    return input_c.numpy(), logits.numpy(), logger
