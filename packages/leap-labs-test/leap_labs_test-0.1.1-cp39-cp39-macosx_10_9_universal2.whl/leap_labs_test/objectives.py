from leap_labs_test.transforms import normalise_each
from leap_labs_test.utils import *


# Optimisation objectives


def default_objective(logits, target_mask, **kwargs):
    masked_logits = logits * target_mask
    return -masked_logits.mean(dim=-1)


def normalised_objective(logits, target_mask, **kwargs):
    normed = normalise_each(logits)
    masked = (normed / normed.sum(dim=-1)) * target_mask
    return -masked.mean(dim=-1)


def prob_objective(logits, target_mask, **kwargs):
    masked_probs = torch.softmax(logits, dim=-1) * target_mask
    return -masked_probs.sum(dim=-1)


def log_prob_objective(logits, target_mask, **kwargs):
    masked_probs = torch.softmax(logits, dim=-1) * target_mask
    return -torch.log(masked_probs).sum(dim=-1)


# Baseline objectives


def minimise_logit_variance(input, logits, **kwargs):
    vars = torch.stack([logits[c].var() for c in range(input.shape[0])])
    return vars


def minimise_prob_variance(input, logits, **kwargs):
    probs = torch.softmax(logits, dim=-1)
    vars = torch.stack([probs[c].var() for c in range(input.shape[0])])
    return vars


def minimise_prob_range(input, logits, **kwargs):
    probs = torch.softmax(logits, dim=-1)
    ranges = torch.stack(
        [probs[c].max() - probs[c].min() for c in range(input.shape[0])]
    )
    return ranges


def minimise_logit_range(input, logits, **kwargs):
    ranges = torch.stack(
        [logits[c].max() - logits[c].min() for c in range(input.shape[0])]
    )
    return ranges


# Input regularisation objectives


def minimise_diff(input, orig_input, **kwargs):
    return torch.abs(input - orig_input).mean(dim=(range(1, len(input.shape))))


def alpha_objective(input, **kwargs):
    alpha = torch.sigmoid(
        input[:, -1:]).mean(dim=tuple(range(1, len(input.shape))))
    return alpha


def contrast_alpha_objective(input):
    alpha = torch.sigmoid(input[:, -1:])
    contrast = torch.std(alpha, dim=tuple(range(1, len(input.shape))))
    return -contrast


def masked_alpha_objective(input, alpha_mask, **kwargs):
    alpha = torch.sigmoid(input[:, -1:]) * (1 - alpha_mask)
    return alpha.mean(dim=tuple(range(1, len(input.shape))))


def maximise_diversity(input, **kwargs):
    num_tensors = input.shape[0]
    nt = normalise_each(input)
    diff_sum = 0
    c = 0
    for i in range(num_tensors):
        for j in range(i + 1, num_tensors):
            diff_sum += (nt[i] - nt[j]).mean()
            c += 1
    return -(diff_sum.repeat(num_tensors) / (c**2))


def minimise_hf(input, **kwargs):
    shifted_x_input = input.clone().detach()
    shifted_y_input = input.clone().detach()
    shifted_z_input = input.clone().detach()
    shifted_x_input[:, :, :-1, :] = input[:, :, 1:, :]
    shifted_y_input[:, :, :, :-1] = input[:, :, :, 1:]
    shifted_z_input[:, :, :-1, :-1] = input[:, :, 1:, 1:]
    var_x = torch.abs(input - shifted_x_input).mean(
        dim=tuple(range(1, len(input.shape)))
    )
    var_y = torch.abs(input - shifted_y_input).mean(
        dim=tuple(range(1, len(input.shape)))
    )
    var_z = torch.abs(input - shifted_z_input).mean(
        dim=tuple(range(1, len(input.shape)))
    )
    return (var_x + var_y + var_z) / 3


def minimise_alpha_hf(input, **kwargs):
    return (minimise_hf(input[:, -1:]))


def minimise_var(input, **kwargs):
    loss = (
        (
            input
            - input.mean(dim=tuple(range(1, len(input.shape)))).reshape(
                input.shape[0], 1, 1, 1
            )
        )
        ** 2
    ).mean(dim=tuple(range(1, len(input.shape))))
    return loss
