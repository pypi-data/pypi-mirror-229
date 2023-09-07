from tqdm import tqdm

from leap_labs_test.logging_handler import Logger
from leap_labs_test.objectives import *
from leap_labs_test.transforms import *
from leap_labs_test.utils import *


def generator(
    config,
    model,
    target_mask,
    input,
    objectives=[default_objective],
    objective_weights=None,
    transforms=[torch.nn.Identity()],
    post_processing=[torch.nn.Identity()],
    optim=torch.optim.Adam,
    alpha_mask=None,
    type="prototype",
    base_classes=None,
    logit_clamp=False,
    logger=None,
):
    if logger is None:
        logger = Logger(config, target_mask, objectives,
                        transforms, base_classes, type)
    else:
        logger.update(config, target_mask, objectives,
                      transforms, base_classes, type)

    device = config.device

    if objective_weights is None:
        objective_weights = torch.ones(len(objectives)).to(device)
    else:
        objective_weights = torch.Tensor(objective_weights).to(device)

    input = torch.Tensor(input).to(device)
    target_mask = torch.Tensor(target_mask).to(device)
    post_processing = compose(post_processing)

    model.to(device)
    model.eval()

    orig_input = input.clone().detach() if "minimise_diff" in str(objectives) else None
    orig_logits = (
        model(input[:, :-1]).clone().detach()
        if config.use_alpha
        else model(input).clone().detach()
    )

    orig_probs = torch.softmax(orig_logits, dim=-1)

    if config.alpha_only:
        img = input[:, :-1].clone().detach()
        a = input[:, -1:].clone().detach()
        input = torch.nn.Parameter(a)
    else:
        input = torch.nn.Parameter(input)

    lr = config.lr if type in ['prototype',
                               'baseline'] else config.isolation_lr
    optimiser = optim([input], lr=lr)
    transforms_a = transforms[0]
    transforms = compose(transforms)

    for i in tqdm(range(config.max_steps)):
        if config.alpha_only:
            input_a = torch.cat([img, input], dim=1)
        else:
            input_a = input

        transformed_input = transforms(input_a)

        logits = model(transformed_input) * config.logit_scale
        probs = torch.softmax(logits, dim=-1)

        if logit_clamp:
            logits = torch.minimum(logits, orig_logits)

        stacked_losses = torch.stack(
            [
                o(
                    input=input_a,
                    orig_input=orig_input,
                    orig_logits=orig_logits,
                    logits=logits,
                    target_mask=target_mask,
                    alpha_mask=alpha_mask,
                )
                for o in objectives
            ]
        )

        losses = stacked_losses * objective_weights.reshape(-1, 1)
        loss = losses.mean()

        with torch.no_grad():
            if (i % config.log_freq == 0) and (i != config.max_steps - 1):
                if type == "saliency":
                    logits = orig_logits
                    probs = orig_probs
                post_proc = post_processing(input_a)
                post_proc_alpha_collapsed = post_processing(input_a)
                if config.use_alpha:
                    post_proc_alpha_collapsed = post_processing(
                        transforms_a(input_a)
                    )
                logger.verbose_log(
                    i,
                    logits.detach().cpu().numpy(),
                    probs.detach().cpu().numpy(),
                    losses.detach().cpu().numpy(),
                    transformed_input.detach().cpu().numpy(),
                    post_proc.detach().cpu().numpy(),
                    post_proc_alpha_collapsed.detach().cpu().numpy(),
                    orig_logits.detach().cpu().numpy(),
                    final=False,
                )  # images etc
            elif config.verbose > 1:
                if type == "saliency":
                    logits = orig_logits
                    probs = orig_probs
                logger.step_log(
                    i,
                    logits.detach().cpu().numpy(),
                    probs.detach().cpu().numpy(),
                    losses.detach().cpu().numpy(),
                )  # basic log

        if type == "baseline":
            halt_criterion = loss < 0.01
        else:
            halt_criterion = False

        if halt_criterion:
            break

        optimiser.zero_grad()
        loss.backward()
        optimiser.step()

    with torch.no_grad():
        post_proc = post_processing(input_a)
        post_proc_alpha_collapsed = post_processing(input_a)
        if config.use_alpha:
            post_proc_alpha_collapsed = post_processing(
                transforms_a(input_a))
        logger.verbose_log(
            i,
            logits.detach().cpu().numpy(),
            probs.detach().cpu().numpy(),
            losses.detach().cpu().numpy(),
            transformed_input.detach().cpu().numpy(),
            post_proc.detach().cpu().numpy(),
            post_proc_alpha_collapsed.detach().cpu().numpy(),
            orig_logits.detach().cpu().numpy(),
            final=True,
        )

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    return input_a.detach().cpu().numpy(), logits.detach().cpu().numpy(), logger
