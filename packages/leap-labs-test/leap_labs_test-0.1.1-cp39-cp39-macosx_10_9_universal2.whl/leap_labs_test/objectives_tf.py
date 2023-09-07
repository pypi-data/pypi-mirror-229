import tensorflow as tf
from leap_labs_test.transforms_tf import normalise_each


# Optimisation objectives


def default_objective(logits, target_mask, **kwargs):
    masked_logits = logits * target_mask
    return -tf.reduce_mean(masked_logits, axis=-1)


def normalised_objective(logits, target_mask, **kwargs):
    normed = normalise_each(logits)
    masked = (normed / tf.reduce_sum(normed,
              axis=-1, keepdims=True)) * target_mask
    return -tf.reduce_mean(masked, axis=-1)


def prob_objective(logits, target_mask, **kwargs):
    masked_probs = tf.nn.softmax(logits, axis=-1) * target_mask
    return -tf.reduce_sum(masked_probs, axis=-1)


def log_prob_objective(logits, target_mask, **kwargs):
    masked_probs = tf.nn.softmax(logits, axis=-1) * target_mask
    return -tf.reduce_sum(tf.math.log(masked_probs), axis=-1)


# Baseline objectives


def minimise_logit_variance(input, logits, **kwargs):
    vars = tf.stack(
        [tf.math.reduce_variance(logits[c]) for c in range(tf.shape(input)[0])]
    )
    return vars


def minimise_prob_variance(input, logits, **kwargs):
    probs = tf.nn.softmax(logits, axis=-1)
    vars = tf.stack(
        [tf.math.reduce_variance(probs[c]) for c in range(tf.shape(input)[0])]
    )
    return vars


def minimise_prob_range(input, logits, **kwargs):
    probs = tf.nn.softmax(logits, axis=-1)
    ranges = tf.stack(
        [
            tf.reduce_max(probs[c]) - tf.reduce_min(probs[c])
            for c in range(tf.shape(input)[0])
        ]
    )
    return ranges


def minimise_logit_range(input, logits, **kwargs):
    ranges = tf.stack(
        [
            tf.reduce_max(logits[c]) - tf.reduce_min(logits[c])
            for c in range(tf.shape(input)[0])
        ]
    )
    return ranges


# Input regularisation objectives


def minimise_diff(input, orig_input, **kwargs):
    return tf.reduce_mean(
        tf.abs(input - orig_input), axis=list(range(1, len(input.shape)))
    )


def alpha_objective(input, **kwargs):
    alpha = tf.reduce_mean(
        tf.sigmoid(input[:, :, :, -1:]), axis=list(range(1, len(input.shape)))
    )
    return alpha


def contrast_alpha_objective(input):
    alpha = tf.sigmoid(input[:, :, :, -1:])
    contrast = tf.math.reduce_std(alpha, axis=list(range(1, len(input.shape))))
    return -contrast


def masked_alpha_objective(input, alpha_mask, **kwargs):
    alpha = tf.sigmoid(input[:, :, :, -1:]) * (1 - alpha_mask)
    return tf.reduce_mean(alpha, axis=list(range(1, len(input.shape))))


def maximise_diversity(input, **kwargs):
    num_tensors = tf.shape(input)[0]
    nt = normalise_each(input)
    diff_sum = 0
    c = 0
    for i in range(num_tensors):
        for j in range(i + 1, num_tensors):
            diff_sum += tf.reduce_mean(nt[i] - nt[j])
            c += 1
    return -(tf.repeat(diff_sum, num_tensors) / (c**2))


def minimise_hf(input, **kwargs):
    shift_input = tf.identity(input)

    # Shift the input tensor along the x-axis
    shifted_x_input = tf.concat(
        [shift_input[:, 1:, :, :], shift_input[:, :1, :, :]], axis=1)

    # Shift the input tensor along the y-axis
    shifted_y_input = tf.concat(
        [shift_input[:, :, 1:, :], shift_input[:, :, :1, :]], axis=2)

    # Shift the input tensor along the diagonal
    shifted_diag_input = tf.concat(
        [shifted_x_input[:, :, 1:, :], shifted_x_input[:, :, :1, :]], axis=2
    )

    # Calculate the absolute difference along each axis and take the mean
    var_x = tf.math.reduce_mean(tf.math.abs(
        shift_input - shifted_x_input), axis=[1, 2, 3])
    var_y = tf.math.reduce_mean(tf.math.abs(
        shift_input - shifted_y_input), axis=[1, 2, 3])
    var_diag = tf.math.reduce_mean(
        tf.math.abs(input - shifted_diag_input), axis=[1, 2, 3]
    )

    # Average the mean differences
    return (var_x + var_y + var_diag) / 3


def minimise_alpha_hf(input, **kwargs):
    return minimise_hf(input[:, :, :, -1:])


def minimise_var(input, **kwargs):
    mean_centered = input - tf.reduce_mean(
        input, axis=list(range(1, len(input.shape))), keepdims=True
    )
    loss = tf.reduce_mean(
        tf.square(mean_centered), axis=list(range(1, len(input.shape)))
    )
    return loss
