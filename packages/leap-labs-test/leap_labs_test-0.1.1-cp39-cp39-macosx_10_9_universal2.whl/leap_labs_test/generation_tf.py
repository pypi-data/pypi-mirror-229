from tqdm import tqdm
import tensorflow as tf
import numpy as np
from leap_labs_test.logging_handler import Logger
from leap_labs_test.objectives_tf import *
from leap_labs_test.transforms_tf import *
from leap_labs_test.utils import *


def generator(
    config,
    model,
    target_mask,
    input,
    objectives=[default_objective],
    objective_weights=None,
    transforms=[tf.identity],
    post_processing=[tf.identity],
    optim=tf.optimizers.Adam,
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

    with tf.device(device):
        if objective_weights is None:
            objective_weights = tf.ones(len(objectives))
        else:
            objective_weights = tf.convert_to_tensor(
                objective_weights, dtype=tf.float32
            )

        input = tf.convert_to_tensor(input, dtype=tf.float32)
        target_mask = tf.convert_to_tensor(target_mask, dtype=tf.float32)
        model.trainable = False
        post_processing = compose(post_processing)

        orig_input = tf.identity(
            input) if "minimise_diff" in str(objectives) else None
        orig_logits = model(input[:, :, :, :-1]
                            ) if config.use_alpha else model(input)
        orig_probs = tf.nn.softmax(orig_logits, axis=-1)

        if config.alpha_only:
            img = tf.identity(input[:, :, :, :-1])
            a = tf.identity(input[:, :, :, -1:])
            input = tf.Variable(a, trainable=True)
        else:
            input = tf.Variable(input, trainable=True)

        lr = config.lr if type in ['prototype',
                                   'baseline'] else config.isolation_lr
        optimizer = optim(learning_rate=lr)
        transforms_a = transforms[0]
        transforms = compose(transforms)

        for i in tqdm(range(config.max_steps)):
            with tf.GradientTape() as tape:
                tape.watch(input)
                if config.alpha_only:
                    input_a = tf.concat([img, input], axis=-1)
                else:
                    input_a = input
                transformed_input = transforms(input_a)
                logits = model(transformed_input) * config.logit_scale
                probs = tf.nn.softmax(logits, axis=-1)

                if logit_clamp:
                    logits = tf.minimum(logits, orig_logits)

                stacked_losses = tf.stack(
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

                losses = stacked_losses * \
                    tf.reshape(objective_weights, (-1, 1))
                loss = tf.reduce_mean(losses)

            if (i % config.log_freq == 0) and (i != config.max_steps - 1):
                if type == "saliency":
                    logits = orig_logits
                    probs = orig_probs
                post_proc = post_processing(input_a)
                post_proc_alpha_collapsed = post_processing(input_a)
                if config.use_alpha:
                    post_proc_alpha_collapsed = post_processing(
                        transforms_a(input_a))
                logger.verbose_log(
                    i,
                    logits.numpy(),
                    probs.numpy(),
                    losses.numpy(),
                    transformed_input.numpy(),
                    post_proc.numpy(),
                    post_proc_alpha_collapsed.numpy(),
                    orig_logits.numpy(),
                    final=False,
                )  # images etc
            elif config.verbose > 1:
                if type == "saliency":
                    logits = orig_logits
                    probs = orig_probs
                logger.step_log(
                    i,
                    logits.numpy(),
                    probs.numpy(),
                    losses.numpy(),
                )  # basic log

            if type == "baseline":
                halt_criterion = loss < 0.01
            else:
                halt_criterion = False

            if halt_criterion:
                break

            grads = tape.gradient(loss, [input])
            optimizer.apply_gradients(zip(grads, [input]))

        post_proc = post_processing(input_a)
        post_proc_alpha_collapsed = post_processing(input_a)
        if config.use_alpha:
            post_proc_alpha_collapsed = post_processing(
                transforms_a(input_a))
        logger.verbose_log(
            i,
            logits.numpy(),
            probs.numpy(),
            losses.numpy(),
            transformed_input.numpy(),
            post_proc.numpy(),
            post_proc_alpha_collapsed.numpy(),
            orig_logits.numpy(),
            final=True,
        )

    return input_a.numpy(), logits.numpy(), logger
